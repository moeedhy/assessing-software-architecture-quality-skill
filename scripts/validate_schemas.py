#!/usr/bin/env python3
"""Development-only JSON Schema validation; runtime CLI remains stdlib-only."""
import argparse
import importlib.util
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    raise SystemExit('Install development dependencies: python -m pip install -r requirements-dev.txt')

ROOT = Path(__file__).resolve().parents[1]


def validators(root=ROOT):
    registry = Registry()
    schemas = {}
    for path in sorted((root / 'schemas').glob('*.schema.json')):
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        # Absolute local IDs ensure all relative references resolve locally.
        schema['$id'] = path.resolve().as_uri()
        schemas[path.name] = schema
        registry = registry.with_resource(schema['$id'], Resource.from_contents(schema))
    return {name: Draft202012Validator(schema, registry=registry) for name, schema in schemas.items()}


def validate_examples(root=ROOT):
    checks = validators(root)
    spec = importlib.util.spec_from_file_location('architecture_quality', root / 'scripts/architecture_quality.py')
    aq = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(aq)
    model = aq.load_json(root / 'references/architecture-quality-model.json')
    paths = sorted((root / 'examples').glob('*.json'))
    for path in paths:
        data = aq.load_json(path)
        checks['assessment.schema.json'].validate(data)
        aq.validate_assessment(data, model, for_scoring=data['score_requested'])
        for evidence in data['evidence']:
            checks['evidence.schema.json'].validate(evidence)
        checks['assessment-result.schema.json'].validate(aq.score_assessment(data, model))
    return len(paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        count = validate_examples(args.root.resolve())
    except Exception as exc:
        print(f'Schema validation: FAILED: {exc}', file=sys.stderr)
        return 1
    print(f'JSON Schema draft 2020-12: OK (all schemas; {count} assessments, evidence and scoring results)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
