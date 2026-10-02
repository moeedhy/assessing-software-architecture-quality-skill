"""Checkpoint persistence and validation regressions; no model calls required."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('aq', ROOT / 'scripts/architecture_quality.py')
aq = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(aq)
MODEL = json.loads((ROOT / 'references/architecture-quality-model.json').read_text())


def checkpoint():
    data = json.loads((ROOT / 'examples/assessment-template.json').read_text())
    data['schema_version'] = '2.1'
    data['evidence'] = [{
        'id': 'EV-001', 'source': 'repository', 'locator': 'src/bootstrap.ts:8',
        'scope': 'startup', 'time_window': None, 'evidence_kind': 'OBSERVATION',
        'claim_status': 'OBSERVED', 'confidence': 'HIGH', 'factor_ids': ['AQ-A01'],
        'summary': 'Bootstrap installs a second dependency registry.'
    }]
    data['review_context'] = {
        'decision_frame': {'decision': 'Keep or replace the second registry?',
                           'scope': 'API startup', 'constraints': ['Preserve worker support'],
                           'assumptions': [], 'unknowns': ['Installed NestJS version']},
        'inspected_scope': ['src/bootstrap.ts:1-30'],
        'scenarios': [{'id': 'SC-001', 'stimulus': 'Add a worker host',
                       'environment': 'startup', 'affected_component': 'composition root',
                       'expected_response': 'Reuse capability wiring',
                       'acceptance_criteria': None, 'priority': 'HIGH'}],
        'findings': [{'id': 'F-001', 'title': 'Second registry needs semantic comparison',
                      'priority': 'P2', 'factor_ids': ['AQ-A01'], 'evidence_ids': ['EV-001'],
                      'observation': 'Second registry exists', 'interpretation': 'Duplication is a hypothesis',
                      'recommendation': 'Compare lifecycle behavior', 'verification': 'Exercise both hosts',
                      'framework_assessment': {
                          'framework': 'NestJS', 'version': None,
                          'requirement': 'Support API and worker wiring', 'capability': 'Custom providers',
                          'capability_evidence_ids': [], 'fit_gap': 'Version and lifecycle fit unknown',
                          'classification': 'UNKNOWN', 'migration_cost': 'Unknown until wiring is traced'}}],
        'alternatives': [{'id': 'ALT-001', 'description': 'Keep and constrain the registry',
                          'tradeoffs': 'Lower migration cost; two wiring systems remain',
                          'scenario_ids': ['SC-001']}],
        'contradictions': [{'id': 'CON-001', 'evidence_ids': ['EV-001'],
                            'description': 'ADR claims only one registry; ADR not inspected yet',
                            'status': 'OPEN', 'resolution': None,
                            'next_check': 'Read ADR and compare startup traces'}],
        'pending_work': ['Verify installed version', 'Inspect ADR'],
        'provisional_decision': None,
        'methods': ['ATAM_INSPIRED']
    }
    return data


class CheckpointTests(unittest.TestCase):
    def test_round_trip_preserves_unresolved_work_and_does_not_mutate(self):
        data = checkpoint()
        original = copy.deepcopy(data)
        aq.validate_assessment(data, MODEL)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'checkpoint.json'
            path.write_text(json.dumps(data))
            resumed = aq.load_json(path)
            aq.validate_assessment(resumed, MODEL)
        self.assertEqual(data, original)
        self.assertEqual(resumed, original)
        self.assertEqual(resumed['review_context']['contradictions'][0]['status'], 'OPEN')

    def test_legacy_and_new_context_produce_identical_scoring_results(self):
        old = json.loads((ROOT / 'examples/deep-assessment.json').read_text())
        new = copy.deepcopy(old)
        new['schema_version'] = '2.1'
        new['review_context'] = checkpoint()['review_context']
        new['evidence'].extend(checkpoint()['evidence'])
        self.assertEqual(aq.score_assessment(old, MODEL), aq.score_assessment(new, MODEL))
        self.assertNotIn('review_context', old)

    def test_context_requires_version_21(self):
        data = checkpoint()
        data['schema_version'] = '2.0'
        with self.assertRaisesRegex(ValueError, 'review_context requires'):
            aq.validate_assessment(data, MODEL)

    def test_bad_context_shapes_and_references_rejected(self):
        mutations = [
            lambda c: c.update(extra='unsupported'),
            lambda c: c.update(pending_work='not a list'),
            lambda c: c['findings'][0].update(evidence_ids=['EV-MISSING']),
            lambda c: c['findings'][0].update(factor_ids=['AQ-Z99']),
            lambda c: c['findings'].append(copy.deepcopy(c['findings'][0])),
            lambda c: c['alternatives'][0].update(scenario_ids=['SC-MISSING']),
            lambda c: c['contradictions'][0].update(status='RESOLVED'),
            lambda c: c['findings'][0]['framework_assessment'].update(classification='EXCELLENT'),
            lambda c: c['findings'][0]['framework_assessment'].update(capability_evidence_ids=['EV-MISSING']),
            lambda c: c['findings'][0].update(factor_ids=['AQ-C01']),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                data = checkpoint()
                mutation(data['review_context'])
                with self.assertRaises(ValueError):
                    aq.validate_assessment(data, MODEL)

    def test_resolved_contradiction_requires_resolution(self):
        data = checkpoint()
        data['review_context']['contradictions'][0].update(status='RESOLVED', resolution='ADR superseded by runtime trace')
        aq.validate_assessment(data, MODEL)

    def test_summary_must_be_nonempty_string(self):
        for value in ('', '  ', 42, None):
            data = checkpoint()
            data['evidence'][0]['summary'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                aq.validate_assessment(data, MODEL)

    def test_unsupported_schema_vocabulary_fails_closed(self):
        # The offline engine is a closed subset; anything it cannot enforce must reject.
        specs = [
            {'type': 'object', 'properties': {}, 'additionalProperties': {'type': 'string'}},
            {'type': 'object', 'additionalProperties': True},
            {'allOf': [{'type': 'object'}]},
            {'anyOf': [{'type': 'object'}]},
            {'not': {'type': 'object'}},
            {'type': 'object', 'maxProperties': 1},
            {'type': 'integer'},
        ]
        for spec in specs:
            with self.subTest(spec=sorted(spec)):
                with self.assertRaisesRegex(ValueError, 'unsupported checkpoint schema'):
                    aq._checkpoint_shape({'undeclared': 'value'}, spec, {}, 'context')

    def test_version_unknown_does_not_invent_support(self):
        data = checkpoint()
        aq.validate_assessment(data, MODEL)
        self.assertIsNone(data['review_context']['findings'][0]['framework_assessment']['version'])


if __name__ == '__main__':
    unittest.main()
