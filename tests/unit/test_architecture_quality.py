import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "architecture_quality.py"
MODEL = ROOT / "references" / "architecture-quality-model.json"
GOLDEN = ROOT / "tests" / "golden" / "uniform-health-3.md"


def load_module():
    spec = importlib.util.spec_from_file_location("architecture_quality", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ArchitectureQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.aq = load_module()
        cls.model = json.loads(MODEL.read_text(encoding="utf-8"))

    def assessment(self, *, health=3, assessed=True):
        factors = []
        factor_ids = []
        for domain in self.model["domains"]:
            for factor in domain["factors"]:
                factor_ids.append(factor["id"])
                factors.append(
                    {
                        "id": factor["id"],
                        "applicability": "ASSESSED" if assessed else "UNKNOWN",
                        "health": health if assessed else None,
                        "confidence": "HIGH" if assessed else "UNKNOWN",
                        "evidence_ids": ["EV-001"] if assessed else [],
                    }
                )
        return {
            "schema_version": "2.0",
            "mode": "REVIEW",
            "depth": "DEEP",
            "score_requested": True,
            "context_profiles": [],
            "custom_domain_weights": None,
            "evidence": [
                {
                    "id": "EV-001",
                    "source": "repository",
                    "locator": "src/example.ts:1",
                    "scope": "example",
                    "time_window": None,
                    "evidence_kind": "OBSERVATION",
                    "claim_status": "OBSERVED",
                    "confidence": "HIGH",
                    "factor_ids": factor_ids,
                }
            ],
            "factors": factors,
            "gates": {
                name: {"status": "PASS", "evidence_ids": ["EV-001"]}
                for name in (
                    "security",
                    "data_integrity",
                    "recovery",
                    "safety_compliance",
                )
            },
        }

    def test_model_has_expected_structure_and_weight_totals(self):
        summary = self.aq.validate_model(self.model)
        self.assertEqual(summary["domains"], 8)
        self.assertEqual(summary["factors"], 49)
        self.assertAlmostEqual(summary["base_weight"], 100.0)

    def test_uniform_health_three_scores_seventy_five(self):
        result = self.aq.score_assessment(self.assessment(), self.model)
        self.assertEqual(result["scoring"]["status"], "computed")
        self.assertEqual(result["scoring"]["composite"], 75)
        self.assertEqual(result["scoring"]["label"], "Healthy")
        self.assertEqual(result["scoring"]["mean_health"], 3.0)
        self.assertEqual(result["scoring"]["coverage_percent"], 100)

    def test_uniform_health_maps_to_its_own_band_not_a_lower_one(self):
        """Regression: uniform health h must score 25h and land in the band that
        names that health level. Reusing percentage-style thresholds previously
        reported a uniformly Acceptable system as Critical."""
        expected = {0: 0, 1: 25, 2: 50, 3: 75, 4: 100}
        bands = {1: "Fragile", 2: "Adequate", 3: "Healthy", 4: "Exemplary"}
        for health, composite in expected.items():
            with self.subTest(health=health):
                result = self.aq.score_assessment(
                    self.assessment(health=health), self.model
                )
                self.assertEqual(result["scoring"]["composite"], composite)
                self.assertEqual(result["scoring"]["mean_health"], float(health))
                if health in bands:
                    self.assertEqual(result["scoring"]["label"], bands[health])

    def test_band_labels_never_reuse_health_scale_words(self):
        """The two vocabularies must stay disjoint so a band cannot be misread
        as a factor health level."""
        health_words = {v.lower() for v in self.model["health_scale"].values()}
        band_words = {b["label"].lower() for b in self.model["score_bands"]}
        self.assertEqual(health_words & band_words, set())

    def test_gate_failure_demotes_the_composite_in_rendered_output(self):
        assessment = self.assessment(health=4)
        assessment["gates"]["security"] = {
            "status": "FAIL",
            "evidence_ids": assessment["factors"][0]["evidence_ids"],
        }
        result = self.aq.score_assessment(assessment, self.model)
        rendered = self.aq.markdown_result(result)
        self.assertEqual(result["overall_status"], "CRITICAL_GATE_FAILURE")
        self.assertIn("Diagnostic composite (NOT the verdict)", rendered)
        self.assertIn("Failed critical gates: **security**", rendered)
        self.assertNotIn("Architecture Health: **", rendered)

    def test_markdown_result_matches_golden_contract(self):
        result = self.aq.score_assessment(self.assessment(), self.model)
        self.assertEqual(
            self.aq.markdown_result(result), GOLDEN.read_text(encoding="utf-8")
        )

    def test_scoring_is_not_computed_without_explicit_request(self):
        assessment = self.assessment()
        assessment["score_requested"] = False
        assessment["depth"] = "STANDARD"
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["status"], "not_requested")
        self.assertIsNone(result["scoring"]["composite"])

    def test_empty_standard_checkpoint_is_partial_with_zero_coverage(self):
        assessment = self.assessment()
        assessment.update(
            depth="STANDARD",
            score_requested=False,
            evidence=[],
            factors=[],
            gates={
                name: {"status": "UNKNOWN", "evidence_ids": []}
                for name in (
                    "security",
                    "data_integrity",
                    "recovery",
                    "safety_compliance",
                )
            },
        )
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["overall_status"], "PARTIAL_ASSESSMENT")
        self.assertEqual(result["scoring"]["coverage_percent"], 0)

    def test_low_coverage_withholds_score(self):
        assessment = self.assessment()
        for factor in assessment["factors"][10:]:
            factor.update(
                applicability="UNKNOWN",
                health=None,
                confidence="UNKNOWN",
                evidence_ids=[],
            )
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["status"], "withheld")
        self.assertIn("evidence coverage is below 70%", result["scoring"]["reasons"])

    def test_unknown_critical_gate_withholds_score(self):
        assessment = self.assessment()
        assessment["gates"]["recovery"]["status"] = "UNKNOWN"
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["status"], "withheld")
        self.assertIn("one or more critical gates are UNKNOWN", result["scoring"]["reasons"])

    def test_failed_gate_overrides_favorable_composite(self):
        assessment = self.assessment(health=4)
        assessment["gates"]["security"]["status"] = "FAIL"
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["overall_status"], "CRITICAL_GATE_FAILURE")
        self.assertEqual(result["scoring"]["composite"], 100)

    def test_design_composite_is_labeled_design_readiness(self):
        assessment = self.assessment()
        assessment["mode"] = "DESIGN"
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["kind"], "Design Readiness")

    def test_all_not_applicable_factors_withhold_score(self):
        assessment = self.assessment()
        for factor in assessment["factors"]:
            factor.update(
                applicability="NOT_APPLICABLE",
                health=None,
                confidence="UNKNOWN",
                evidence_ids=[],
            )
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["status"], "withheld")
        self.assertIn(
            "no applicable factor weight was assessed", result["scoring"]["reasons"]
        )

    def test_custom_domain_weights_override_context_profiles(self):
        assessment = self.assessment()
        assessment["context_profiles"] = ["high-scale-distributed"]
        assessment["custom_domain_weights"] = {
            "A": 5,
            "B": 10,
            "C": 10,
            "D": 10,
            "E": 20,
            "F": 10,
            "G": 5,
            "H": 30,
        }
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["adjusted_domain_weights"]["H"], 30.0)
        self.assertEqual(result["adjusted_domain_weights"]["A"], 5.0)

    def test_combined_profile_multiplier_is_capped_before_normalization(self):
        assessment = self.assessment()
        assessment["context_profiles"] = ["security-critical-regulated", "ai-system"]
        result = self.aq.score_assessment(assessment, self.model)
        ratio = (
            result["adjusted_domain_weights"]["H"]
            / result["adjusted_domain_weights"]["A"]
        )
        self.assertAlmostEqual(ratio, 26 / 11, places=2)

    def test_more_than_half_unknown_in_domain_withholds_score(self):
        assessment = self.assessment()
        for factor in assessment["factors"]:
            if factor["id"].startswith("AQ-A") and factor["id"] != "AQ-A01":
                factor.update(
                    applicability="UNKNOWN",
                    health=None,
                    confidence="UNKNOWN",
                    evidence_ids=[],
                )
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["status"], "withheld")
        self.assertTrue(
            any("domain A" in reason for reason in result["scoring"]["reasons"])
        )

    def test_not_applicable_factors_are_removed_from_coverage_denominator(self):
        assessment = self.assessment()
        for factor in assessment["factors"][:8]:
            factor.update(
                applicability="NOT_APPLICABLE",
                health=None,
                confidence="UNKNOWN",
                evidence_ids=[],
            )
        result = self.aq.score_assessment(assessment, self.model)
        self.assertEqual(result["scoring"]["coverage_percent"], 100)

    def test_missing_factor_is_rejected_for_deep_scoring(self):
        assessment = self.assessment()
        assessment["factors"].pop()
        with self.assertRaisesRegex(ValueError, "all 49 factors"):
            self.aq.score_assessment(assessment, self.model)

    def test_factor_evidence_must_link_back_to_factor(self):
        assessment = self.assessment()
        assessment["evidence"][0]["factor_ids"] = ["AQ-A01"]
        with self.assertRaisesRegex(ValueError, "does not declare that factor"):
            self.aq.validate_assessment(assessment, self.model, for_scoring=True)

    def test_invalid_container_is_reported_as_validation_error(self):
        assessment = self.assessment()
        assessment["evidence"] = ["not-an-object"]
        with self.assertRaisesRegex(ValueError, "evidence item 1 must be an object"):
            self.aq.validate_assessment(assessment, self.model)

    def test_unknown_top_level_field_is_rejected(self):
        assessment = self.assessment()
        assessment["unmodeled_state"] = True
        with self.assertRaisesRegex(ValueError, "unsupported fields: unmodeled_state"):
            self.aq.validate_assessment(assessment, self.model)

    def test_missing_required_evidence_field_is_rejected(self):
        assessment = self.assessment()
        del assessment["evidence"][0]["time_window"]
        with self.assertRaisesRegex(ValueError, "missing fields: time_window"):
            self.aq.validate_assessment(assessment, self.model)

    def test_package_validation_cli_passes(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "validate-package", str(ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        self.assertIn("Package validation: OK", completed.stdout)


if __name__ == "__main__":
    unittest.main()
