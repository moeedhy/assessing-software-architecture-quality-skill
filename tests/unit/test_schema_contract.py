"""Compare the offline schema engine with CLI structural acceptance.

Cross-record integrity (references, unique IDs, totals) is additionally checked
by the CLI; JSON Schema alone cannot express these relationships.
"""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

from test_checkpoints import MODEL, ROOT, aq, checkpoint

HAS_JSONSCHEMA = importlib.util.find_spec('jsonschema') is not None
if HAS_JSONSCHEMA:
    spec = importlib.util.spec_from_file_location('schema_checks', ROOT / 'scripts/validate_schemas.py')
    schema_checks = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema_checks)


@unittest.skipUnless(HAS_JSONSCHEMA, 'Development check: install requirements-dev.txt')
class SchemaContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = schema_checks.validators()['assessment.schema.json']

    def test_all_shipped_examples_and_results_conform(self):
        self.assertGreaterEqual(schema_checks.validate_examples(), 3)

    def test_valid_legacy_new_empty_and_full_context_agree(self):
        legacy = json.loads((ROOT / 'examples/deep-assessment.json').read_text())
        for data in (legacy, checkpoint(), {**legacy, 'schema_version': '2.1'}):
            with self.subTest(version=data['schema_version'], context='review_context' in data):
                self.validator.validate(data)
                aq.validate_assessment(data, MODEL)

    def test_invalid_shapes_rejected_by_both_validators(self):
        mutations = [
            lambda a: a.update(schema_version='2.0'),
            lambda a: a.update(schema_version='3.0'),
            lambda a: a.update(review_context=None),
            lambda a: a['evidence'][0].update(summary=' '),
            lambda a: a['review_context'].update(pending_work='not an array'),
            lambda a: a['review_context']['decision_frame'].update(scope=''),
            lambda a: a['review_context']['scenarios'][0].update(priority='P1'),
            lambda a: a['review_context']['scenarios'][0].update(acceptance_criteria=False),
            lambda a: a['review_context']['findings'][0].update(score=80),
            lambda a: a['review_context']['findings'][0].update(evidence_ids=[]),
            lambda a: a['review_context']['contradictions'][0].update(status='RESOLVED'),
            lambda a: a['review_context']['contradictions'][0].update(next_check=None),
            lambda a: a['review_context']['contradictions'][0].update(resolution='Resolved despite OPEN'),
            lambda a: a['review_context'].update(methods=['C4', 'C4']),
            lambda a: a['review_context']['findings'][0]['framework_assessment'].update(version=12),
            lambda a: a['review_context']['findings'][0]['framework_assessment'].update(classification='BEST'),
        ]
        for index, mutate in enumerate(mutations):
            data = checkpoint()
            mutate(data)
            with self.subTest(case=index):
                self.assertFalse(self.validator.is_valid(data))
                with self.assertRaises(ValueError):
                    aq.validate_assessment(data, MODEL)

    def test_cross_record_integrity_requires_cli_beyond_json_schema(self):
        data = checkpoint()
        data['review_context']['findings'][0]['evidence_ids'] = ['EV-MISSING']
        self.validator.validate(data)  # ID shape is valid; the reference is not.
        with self.assertRaisesRegex(ValueError, 'unknown IDs'):
            aq.validate_assessment(data, MODEL)


if __name__ == '__main__':
    unittest.main()
