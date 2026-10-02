import json
import shutil
import tempfile
import unittest
from pathlib import Path

from test_checkpoints import ROOT, MODEL, aq


class PackageValidationTests(unittest.TestCase):
    def package(self, folder):
        root = Path(folder) / ROOT.name
        root.mkdir()
        for name in ('SKILL.md', 'README.md', 'CHANGELOG.md'):
            shutil.copy2(ROOT / name, root / name)
        for name in ('scripts', 'schemas', 'references', 'examples', 'agents', 'tests'):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__'))
        return root

    def test_nested_markdown_links_are_relative_to_document(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'references').mkdir()
            (root / 'examples').mkdir()
            (root / 'examples/payload.json').write_text('{}')
            link = root / 'references/nested.md'
            link.write_text('[example](../examples/payload.json)')
            aq.validate_markdown_links(root)
            link.write_text('[missing](../examples/missing.json)')
            with self.assertRaisesRegex(ValueError, 'references/nested.md'):
                aq.validate_markdown_links(root)

    def test_every_example_is_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.package(folder)
            (root / 'examples/invalid.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'missing required fields'):
                aq.validate_package(root)

    def test_target_package_schema_used_for_checkpoint_validation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = self.package(folder)
            path = root / 'schemas/assessment.schema.json'
            schema = json.loads(path.read_text())
            schema['$defs']['review_context']['required'].append('unexpected_field')
            path.write_text(json.dumps(schema))
            with self.assertRaisesRegex(ValueError, 'missing required fields'):
                aq.validate_package(root)

    def test_validate_assessment_enforces_score_requested_completeness(self):
        data = json.loads((ROOT / 'examples/deep-assessment.json').read_text())
        data['factors'].pop()
        with self.assertRaisesRegex(ValueError, 'all 49 factors'):
            aq.validate_assessment(data, MODEL)

    def test_code_samples_are_not_mistaken_for_links(self):
        samples = (
            '```markdown\n[see](missing.md)\n```\n',
            '~~~\n[see](missing.md)\n~~~\n',
            'Write `[label](missing.md)` inline.\n',
            'Escaped \\[not a link\\](missing.md).\n',
        )
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'references').mkdir()
            document = root / 'sample.md'
            for sample in samples:
                document.write_text(sample)
                with self.subTest(sample=sample.splitlines()[0]):
                    aq.validate_markdown_links(root)
            document.write_text('Prose [link](missing.md) outside any code sample.\n')
            with self.assertRaisesRegex(ValueError, 'missing.md'):
                aq.validate_markdown_links(root)

    def test_link_titles_and_angle_destinations_resolve(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'target.md').write_text('target')
            document = root / 'sample.md'
            for link in ('[x](target.md "Title")', "[x](target.md 'Title')", '[x](<target.md>)'):
                document.write_text(link)
                with self.subTest(link=link):
                    aq.validate_markdown_links(root)
            document.write_text('[x](absent.md "Title")')
            with self.assertRaisesRegex(ValueError, 'absent.md'):
                aq.validate_markdown_links(root)

    def test_eval_activation_expected_must_be_boolean(self):
        cases = [
            json.loads(line)
            for line in (ROOT / 'tests/evals/cases.jsonl').read_text().splitlines()
            if line.strip()
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cases.jsonl'
            for value in ('true', 1, None, 'MISSING'):
                mutated = [dict(case) for case in cases]
                if value == 'MISSING':
                    mutated[0].pop('activation_expected')
                else:
                    mutated[0]['activation_expected'] = value
                path.write_text('\n'.join(json.dumps(case) for case in mutated))
                with self.subTest(value=value), self.assertRaises(ValueError):
                    aq.validate_eval_cases(path)

    def test_custom_weights_require_finite_numbers(self):
        for value in ('12.5', True, float('inf'), float('nan')):
            data = json.loads((ROOT / 'examples/deep-assessment.json').read_text())
            data['custom_domain_weights'] = dict.fromkeys('ABCDEFGH', 12.5)
            data['custom_domain_weights']['A'] = value
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'finite numbers'):
                aq.validate_assessment(data, MODEL)


if __name__ == '__main__':
    unittest.main()
