#!/usr/bin/env python3
"""Deterministic validation and scoring for the architecture-quality skill."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


MODES = {"DESIGN", "REVIEW", "CHANGE", "MODERNIZATION", "INCIDENT"}
DEPTHS = {"TRIAGE", "STANDARD", "DEEP"}
APPLICABILITY = {"ASSESSED", "UNKNOWN", "NOT_APPLICABLE"}
CONFIDENCE = {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}
GATE_STATUS = {"PASS", "FAIL", "UNKNOWN", "NOT_APPLICABLE"}
DOMAIN_IDS = tuple("ABCDEFGH")

# Deliberate canary: bump only when the canonical model gains or loses a factor.
EXPECTED_FACTORS = 49
SKILL_VERSION = "2.2.0"


def load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc


def flatten_model(model: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    domains: dict[str, Any] = {}
    factors: dict[str, Any] = {}
    domain_items = model.get("domains", [])
    if not isinstance(domain_items, list):
        raise ValueError("model domains must be a list")
    for index, domain in enumerate(domain_items, 1):
        if not isinstance(domain, dict):
            raise ValueError(f"model domain {index} must be an object")
        domain_id = domain.get("id")
        if domain_id in domains:
            raise ValueError(f"duplicate domain id: {domain_id}")
        domains[domain_id] = domain
        factor_items = domain.get("factors", [])
        if not isinstance(factor_items, list):
            raise ValueError(f"model domain {domain_id} factors must be a list")
        for factor_index, factor in enumerate(factor_items, 1):
            if not isinstance(factor, dict):
                raise ValueError(
                    f"model domain {domain_id} factor {factor_index} must be an object"
                )
            factor_id = factor.get("id")
            if factor_id in factors:
                raise ValueError(f"duplicate factor id: {factor_id}")
            factors[factor_id] = {**factor, "domain_id": domain_id}
    return domains, factors


def validate_model(model: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(model, dict):
        raise ValueError("model must be a JSON object")
    if model.get("schema_version") != "2.0":
        raise ValueError("model schema_version must be 2.0")
    domains, factors = flatten_model(model)
    if set(domains) != set(DOMAIN_IDS):
        raise ValueError("model must define domains A through H exactly once")
    if len(factors) != EXPECTED_FACTORS:
        raise ValueError(
            f"model must define {EXPECTED_FACTORS} factors, found {len(factors)}"
        )

    id_pattern = re.compile(r"^AQ-([A-H])(\d{2})$")
    total = 0.0
    for domain_id, domain in domains.items():
        expected_prefix = f"AQ-{domain_id}"
        domain_total = 0.0
        for factor in domain.get("factors", []):
            factor_id = factor.get("id", "")
            match = id_pattern.fullmatch(factor_id)
            if not match or not factor_id.startswith(expected_prefix):
                raise ValueError(f"invalid factor id {factor_id} in domain {domain_id}")
            weight = float(factor.get("weight", -1))
            if weight < 0:
                raise ValueError(f"factor {factor_id} has invalid weight")
            if factor.get("metric_class") not in {"M1", "M2", "M3", "M4", "M5"}:
                raise ValueError(f"factor {factor_id} has invalid metric_class")
            if factor.get("role") not in {"primary", "supporting", "diagnostic"}:
                raise ValueError(f"factor {factor_id} has invalid role")
            domain_total += weight
        declared = float(domain.get("weight", -1))
        if round(domain_total, 6) != round(declared, 6):
            raise ValueError(
                f"domain {domain_id} factor weights total {domain_total}, expected {declared}"
            )
        total += declared
    if round(total, 6) != 100.0:
        raise ValueError(f"base domain weights total {total}, expected 100")

    profiles = model.get("context_profiles", {})
    for name, multipliers in profiles.items():
        if set(multipliers) != set(DOMAIN_IDS):
            raise ValueError(f"context profile {name} must define domains A through H")
        if any(float(value) <= 0 for value in multipliers.values()):
            raise ValueError(f"context profile {name} contains a non-positive multiplier")

    return {"domains": len(domains), "factors": len(factors), "base_weight": total}


def validate_assessment(
    assessment: dict[str, Any], model: dict[str, Any], *, for_scoring: bool = False,
    schema_path: Path | None = None,
) -> dict[str, Any]:
    if not isinstance(assessment, dict):
        raise ValueError("assessment must be a JSON object")
    validate_model(model)
    _, model_factors = flatten_model(model)

    required = {
        "schema_version",
        "mode",
        "depth",
        "score_requested",
        "context_profiles",
        "custom_domain_weights",
        "evidence",
        "factors",
        "gates",
    }
    missing = sorted(required - set(assessment))
    if missing:
        raise ValueError(f"assessment is missing required fields: {', '.join(missing)}")
    extra = sorted(set(assessment) - required - {"review_context"})
    if extra:
        raise ValueError(f"assessment has unsupported fields: {', '.join(extra)}")
    if assessment["schema_version"] not in ("2.0", "2.1"):
        raise ValueError("assessment schema_version must be 2.0 or 2.1")
    if "review_context" in assessment and assessment["schema_version"] != "2.1":
        raise ValueError("review_context requires assessment schema_version 2.1")
    if assessment["mode"] not in MODES:
        raise ValueError(f"invalid assessment mode: {assessment['mode']}")
    if assessment["depth"] not in DEPTHS:
        raise ValueError(f"invalid assessment depth: {assessment['depth']}")
    if not isinstance(assessment["score_requested"], bool):
        raise ValueError("score_requested must be a boolean")
    if assessment["score_requested"] and assessment["depth"] != "DEEP":
        raise ValueError("score_requested=true requires depth=DEEP")

    profiles = assessment["context_profiles"]
    if (
        not isinstance(profiles, list)
        or any(not isinstance(profile, str) for profile in profiles)
        or len(profiles) != len(set(profiles))
    ):
        raise ValueError("context_profiles must be a unique list")
    unknown_profiles = sorted(set(profiles) - set(model.get("context_profiles", {})))
    if unknown_profiles:
        raise ValueError(f"unknown context profiles: {', '.join(unknown_profiles)}")

    custom = assessment["custom_domain_weights"]
    if custom is not None:
        if not isinstance(custom, dict):
            raise ValueError("custom_domain_weights must be an object or null")
        if set(custom) != set(DOMAIN_IDS):
            raise ValueError("custom_domain_weights must define domains A through H")
        if any(isinstance(custom[key], bool) or not isinstance(custom[key], (int, float))
               or not math.isfinite(custom[key]) for key in DOMAIN_IDS):
            raise ValueError("custom_domain_weights values must be finite numbers")
        try:
            values = [float(custom[key]) for key in DOMAIN_IDS]
        except (TypeError, ValueError) as exc:
            raise ValueError("custom_domain_weights values must be numbers") from exc
        if any(value < 0 for value in values):
            raise ValueError("custom_domain_weights cannot contain negative values")
        if round(sum(values), 6) != 100.0:
            raise ValueError("custom_domain_weights must total 100")

    evidence_items = assessment["evidence"]
    if not isinstance(evidence_items, list):
        raise ValueError("evidence must be a list")
    evidence_ids: set[str] = set()
    evidence_by_id: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(evidence_items, 1):
        if not isinstance(item, dict):
            raise ValueError(f"evidence item {index} must be an object")
        evidence_fields = {
            "id",
            "source",
            "locator",
            "scope",
            "time_window",
            "evidence_kind",
            "claim_status",
            "confidence",
            "factor_ids",
        }
        missing_fields = sorted(evidence_fields - set(item))
        if missing_fields:
            raise ValueError(
                f"evidence item {index} missing fields: {', '.join(missing_fields)}"
            )
        extra_fields = sorted(set(item) - evidence_fields - {"summary"})
        if extra_fields:
            raise ValueError(
                f"evidence item {index} has unsupported fields: {', '.join(extra_fields)}"
            )
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not re.fullmatch(r"EV-[A-Z0-9-]+", evidence_id):
            raise ValueError(f"invalid evidence id: {evidence_id}")
        if evidence_id in evidence_ids:
            raise ValueError(f"duplicate evidence id: {evidence_id}")
        evidence_ids.add(evidence_id)
        if item.get("evidence_kind") not in {
            "MEASUREMENT",
            "OBSERVATION",
            "DOCUMENTED_CLAIM",
        }:
            raise ValueError(f"evidence {evidence_id} has invalid evidence_kind")
        if item.get("claim_status") not in {"OBSERVED", "INFERRED", "ASSUMED"}:
            raise ValueError(f"evidence {evidence_id} has invalid claim_status")
        if item.get("confidence") not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError(f"evidence {evidence_id} has invalid confidence")
        time_window = item.get("time_window")
        if time_window is not None and not isinstance(time_window, str):
            raise ValueError(f"evidence {evidence_id} time_window must be string or null")
        factor_refs = item.get("factor_ids", [])
        if (
            not isinstance(factor_refs, list)
            or any(not isinstance(ref, str) for ref in factor_refs)
            or len(factor_refs) != len(set(factor_refs))
        ):
            raise ValueError(f"evidence {evidence_id} factor_ids must be a unique list")
        unknown_factor_refs = sorted(set(factor_refs) - set(model_factors))
        if unknown_factor_refs:
            raise ValueError(
                f"evidence {evidence_id} references unknown factors: "
                + ", ".join(unknown_factor_refs)
            )
        for field in ("source", "locator", "scope"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"evidence {evidence_id} requires non-empty {field}")
        if "summary" in item and (
            not isinstance(item["summary"], str) or not item["summary"].strip()
        ):
            raise ValueError(f"evidence {evidence_id} summary must be a non-empty string")
        evidence_by_id[evidence_id] = item

    factor_items = assessment["factors"]
    if not isinstance(factor_items, list):
        raise ValueError("factors must be a list")
    assessment_factors: dict[str, Any] = {}
    for index, factor in enumerate(factor_items, 1):
        if not isinstance(factor, dict):
            raise ValueError(f"factor item {index} must be an object")
        factor_fields = {"id", "applicability", "health", "confidence", "evidence_ids"}
        missing_fields = sorted(factor_fields - set(factor))
        if missing_fields:
            raise ValueError(
                f"factor item {index} missing fields: {', '.join(missing_fields)}"
            )
        extra_fields = sorted(set(factor) - factor_fields)
        if extra_fields:
            raise ValueError(
                f"factor item {index} has unsupported fields: {', '.join(extra_fields)}"
            )
        factor_id = factor.get("id")
        if factor_id not in model_factors:
            raise ValueError(f"unknown assessment factor: {factor_id}")
        if factor_id in assessment_factors:
            raise ValueError(f"duplicate assessment factor: {factor_id}")
        applicability = factor.get("applicability")
        if applicability not in APPLICABILITY:
            raise ValueError(f"factor {factor_id} has invalid applicability")
        health = factor.get("health")
        confidence = factor.get("confidence")
        refs = factor.get("evidence_ids", [])
        if (
            not isinstance(refs, list)
            or any(not isinstance(ref, str) for ref in refs)
            or len(refs) != len(set(refs))
        ):
            raise ValueError(f"factor {factor_id} evidence_ids must be a unique list")
        if confidence not in CONFIDENCE:
            raise ValueError(f"factor {factor_id} has invalid confidence")
        unknown_refs = sorted(set(refs) - evidence_ids)
        if unknown_refs:
            raise ValueError(
                f"factor {factor_id} references unknown evidence: {', '.join(unknown_refs)}"
            )
        if applicability == "ASSESSED":
            if not isinstance(health, int) or isinstance(health, bool) or not 0 <= health <= 4:
                raise ValueError(f"assessed factor {factor_id} requires integer health 0-4")
            if confidence == "UNKNOWN":
                raise ValueError(f"assessed factor {factor_id} requires known confidence")
            if not refs:
                raise ValueError(f"assessed factor {factor_id} requires evidence")
            if not any(factor_id in evidence_by_id[ref]["factor_ids"] for ref in refs):
                raise ValueError(
                    f"factor {factor_id} cites evidence that does not declare that factor"
                )
        elif health is not None:
            raise ValueError(f"unassessed factor {factor_id} must have health=null")
        assessment_factors[factor_id] = factor

    if (for_scoring or assessment["score_requested"]) and set(assessment_factors) != set(model_factors):
        raise ValueError(
            f"DEEP scoring requires all {EXPECTED_FACTORS} factors exactly once"
        )

    required_gates = set(model["critical_gates"])
    gates = assessment["gates"]
    if not isinstance(gates, dict) or set(gates) != required_gates:
        raise ValueError("gates must define security, data_integrity, recovery, and safety_compliance")
    for gate_name, gate in gates.items():
        if not isinstance(gate, dict):
            raise ValueError(f"gate {gate_name} must be an object")
        gate_fields = {"status", "evidence_ids"}
        missing_fields = sorted(gate_fields - set(gate))
        if missing_fields:
            raise ValueError(
                f"gate {gate_name} missing fields: {', '.join(missing_fields)}"
            )
        extra_fields = sorted(set(gate) - gate_fields)
        if extra_fields:
            raise ValueError(
                f"gate {gate_name} has unsupported fields: {', '.join(extra_fields)}"
            )
        status = gate.get("status")
        refs = gate.get("evidence_ids", [])
        if (
            not isinstance(refs, list)
            or any(not isinstance(ref, str) for ref in refs)
            or len(refs) != len(set(refs))
        ):
            raise ValueError(f"gate {gate_name} evidence_ids must be a unique list")
        if status not in GATE_STATUS:
            raise ValueError(f"gate {gate_name} has invalid status")
        unknown_refs = sorted(set(refs) - evidence_ids)
        if unknown_refs:
            raise ValueError(
                f"gate {gate_name} references unknown evidence: {', '.join(unknown_refs)}"
            )
        if status in {"PASS", "FAIL"} and not refs:
            raise ValueError(f"assessed gate {gate_name} requires evidence")

    if "review_context" in assessment:
        validate_review_context(assessment["review_context"], evidence_by_id, model_factors, schema_path)

    return {
        "evidence": len(evidence_ids),
        "factors": len(assessment_factors),
        "gates": len(gates),
    }


def _checkpoint_shape(value: Any, spec: dict[str, Any], defs: dict, path: str) -> None:
    """Validate only the closed vocabulary used by review-context definitions.

    This is not a general JSON Schema engine. Unsupported schema keywords fail
    closed; development checks also use the official draft-2020-12 validator.
    """
    supported = {"$ref", "type", "properties", "required", "additionalProperties",
                 "items", "minItems", "uniqueItems", "minLength", "pattern",
                 "enum", "const", "oneOf"}
    if set(spec) - supported:
        raise ValueError(f"unsupported checkpoint schema keyword at {path}")
    # Only the closed `false` form is enforced below; a subschema would fail open.
    if spec.get("additionalProperties", False) is not False:
        raise ValueError(f"unsupported checkpoint schema keyword at {path}")
    if "$ref" in spec:
        name = spec["$ref"].removeprefix("#/$defs/")
        if spec["$ref"] != f"#/$defs/{name}" or name not in defs:
            raise ValueError(f"unsupported checkpoint schema reference at {path}")
        _checkpoint_shape(value, defs[name], defs, path)
    if "type" in spec:
        types = spec["type"] if isinstance(spec["type"], list) else [spec["type"]]
        checks = {"object": isinstance(value, dict), "array": isinstance(value, list),
                  "string": isinstance(value, str), "null": value is None}
        if any(t not in checks for t in types):
            raise ValueError(f"unsupported checkpoint schema type at {path}")
        if not any(checks[t] for t in types):
            raise ValueError(f"{path} must have type {spec['type']}")
    if "enum" in spec and value not in spec["enum"]:
        raise ValueError(f"{path} has an invalid value")
    if "const" in spec and value != spec["const"]:
        raise ValueError(f"{path} must equal {spec['const']}")
    if isinstance(value, str):
        if len(value) < spec.get("minLength", 0):
            raise ValueError(f"{path} must not be empty")
        if "pattern" in spec and re.search(spec["pattern"], value) is None:
            raise ValueError(f"{path} has an invalid format")
    if isinstance(value, dict):
        fields = spec.get("properties", {})
        if set(spec.get("required", [])) - set(value):
            raise ValueError(f"{path} is missing required fields")
        if spec.get("additionalProperties") is False and set(value) - set(fields):
            raise ValueError(f"{path} has unsupported fields")
        for key in value.keys() & fields.keys():
            _checkpoint_shape(value[key], fields[key], defs, f"{path}.{key}")
    if isinstance(value, list):
        if len(value) < spec.get("minItems", 0):
            raise ValueError(f"{path} has too few items")
        if spec.get("uniqueItems") and any(v in value[:i] for i, v in enumerate(value)):
            raise ValueError(f"{path} must have unique items")
        if "items" in spec:
            for index, item in enumerate(value):
                _checkpoint_shape(item, spec["items"], defs, f"{path}[{index}]")
    if "oneOf" in spec:
        matches = 0
        for branch in spec["oneOf"]:
            try:
                _checkpoint_shape(value, branch, defs, path)
                matches += 1
            except ValueError:
                pass
        if matches != 1:
            raise ValueError(f"{path} must satisfy exactly one state contract")


def validate_review_context(context: dict, evidence: dict, factors: dict,
                           schema_path: Path | None = None) -> None:
    schema = load_json(schema_path or default_root() / "schemas" / "assessment.schema.json")
    defs = schema["$defs"]
    _checkpoint_shape(context, defs["review_context"], defs, "review_context")

    def references(refs: list[str], known: dict | set, path: str) -> None:
        missing = sorted(set(refs) - set(known))
        if missing:
            raise ValueError(f"{path} references unknown IDs: {', '.join(missing)}")

    ids = {}
    for collection in ("scenarios", "findings", "alternatives", "contradictions"):
        values = [item["id"] for item in context[collection]]
        if len(values) != len(set(values)):
            raise ValueError(f"review_context.{collection} has duplicate IDs")
        ids[collection] = set(values)
    for finding in context["findings"]:
        references(finding["factor_ids"], factors, finding["id"])
        references(finding["evidence_ids"], evidence, finding["id"])
        for factor in finding["factor_ids"]:
            if not any(factor in evidence[e]["factor_ids"] for e in finding["evidence_ids"]):
                raise ValueError(f"finding {finding['id']} evidence does not declare factor {factor}")
        if "framework_assessment" in finding:
            references(finding["framework_assessment"]["capability_evidence_ids"], evidence, finding["id"])
    for alternative in context["alternatives"]:
        references(alternative["scenario_ids"], ids["scenarios"], alternative["id"])
    for contradiction in context["contradictions"]:
        references(contradiction["evidence_ids"], evidence, contradiction["id"])


def adjusted_weights(
    assessment: dict[str, Any], model: dict[str, Any]
) -> tuple[dict[str, float], dict[str, float]]:
    domains, factors = flatten_model(model)
    custom = assessment.get("custom_domain_weights")
    if custom is not None:
        domain_weights = {key: float(custom[key]) for key in DOMAIN_IDS}
    else:
        cap = float(model["multiplier_cap"])
        multipliers = {key: 1.0 for key in DOMAIN_IDS}
        for profile_name in assessment.get("context_profiles", []):
            profile = model["context_profiles"][profile_name]
            for key in DOMAIN_IDS:
                multipliers[key] = min(cap, multipliers[key] * float(profile[key]))
        raw = {
            key: float(domains[key]["weight"]) * multipliers[key] for key in DOMAIN_IDS
        }
        raw_total = sum(raw.values())
        domain_weights = {key: 100.0 * raw[key] / raw_total for key in DOMAIN_IDS}

    factor_weights: dict[str, float] = {}
    for factor_id, factor in factors.items():
        domain_id = factor["domain_id"]
        domain_base = float(domains[domain_id]["weight"])
        factor_weights[factor_id] = (
            domain_weights[domain_id] * float(factor["weight"]) / domain_base
        )
    return domain_weights, factor_weights


def label_for_score(score: int, model: dict[str, Any]) -> str:
    for band in model["score_bands"]:
        if score >= int(band["minimum"]):
            return str(band["label"])
    raise ValueError("score band model does not cover zero")


def score_assessment(
    assessment: dict[str, Any], model: dict[str, Any]
) -> dict[str, Any]:
    validate_assessment(assessment, model, for_scoring=assessment.get("score_requested", False))
    domains, model_factors = flatten_model(model)
    domain_weights, factor_weights = adjusted_weights(assessment, model)
    entries = {factor["id"]: factor for factor in assessment["factors"]}

    domain_results: dict[str, Any] = {}
    assessed_total = 0.0
    applicable_total = 0.0
    numerator = 0.0
    reasons: list[str] = []

    for domain_id in DOMAIN_IDS:
        assessed_weight = 0.0
        applicable_weight = 0.0
        unknown_weight = 0.0
        domain_numerator = 0.0
        for factor_id, factor_model in model_factors.items():
            if factor_model["domain_id"] != domain_id or factor_id not in entries:
                continue
            entry = entries[factor_id]
            weight = factor_weights[factor_id]
            if entry["applicability"] == "NOT_APPLICABLE":
                continue
            applicable_weight += weight
            if entry["applicability"] == "UNKNOWN":
                unknown_weight += weight
                continue
            assessed_weight += weight
            health = int(entry["health"])
            domain_numerator += weight * health / 4.0
            numerator += weight * health / 4.0

        assessed_total += assessed_weight
        applicable_total += applicable_weight
        coverage = 100.0 if applicable_weight == 0 else 100.0 * assessed_weight / applicable_weight
        unknown_percent = 0.0 if applicable_weight == 0 else 100.0 * unknown_weight / applicable_weight
        health_score = (
            None if assessed_weight == 0 else round(100.0 * domain_numerator / assessed_weight)
        )
        domain_results[domain_id] = {
            "name": domains[domain_id]["name"],
            "adjusted_weight": round(domain_weights[domain_id], 2),
            "coverage_percent": round(coverage),
            "unknown_percent": round(unknown_percent),
            "health_score": health_score,
        }
        threshold = float(model["domain_unknown_threshold"])
        if applicable_weight > 0 and unknown_percent > threshold:
            reasons.append(
                f"domain {domain_id} has more than {threshold:g}% UNKNOWN applicable weight"
            )

    overall_coverage = (
        0.0 if applicable_total == 0 else 100.0 * assessed_total / applicable_total
    )
    coverage_percent = round(overall_coverage)
    gate_statuses = {
        name: assessment["gates"][name]["status"] for name in model["critical_gates"]
    }
    if "UNKNOWN" in gate_statuses.values():
        reasons.append("one or more critical gates are UNKNOWN")
    coverage_threshold = float(model["coverage_threshold"])
    if overall_coverage < coverage_threshold:
        reasons.append(f"evidence coverage is below {coverage_threshold:g}%")
    if assessed_total == 0:
        reasons.append("no applicable factor weight was assessed")

    score_requested = assessment["score_requested"]
    if not score_requested:
        scoring_status = "not_requested"
        reasons = []
        composite = None
        mean_health = None
        label = None
        score_kind = None
    elif reasons:
        scoring_status = "withheld"
        composite = None
        mean_health = None
        label = None
        score_kind = "Design Readiness" if assessment["mode"] == "DESIGN" else "Architecture Health"
    else:
        scoring_status = "computed"
        composite = round(100.0 * numerator / assessed_total) if assessed_total else None
        mean_health = round(4.0 * numerator / assessed_total, 2) if assessed_total else None
        label = label_for_score(composite, model) if composite is not None else None
        score_kind = "Design Readiness" if assessment["mode"] == "DESIGN" else "Architecture Health"

    any_gate_failure = "FAIL" in gate_statuses.values()
    if any_gate_failure:
        overall_status = "CRITICAL_GATE_FAILURE"
    elif (
        scoring_status == "withheld"
        or "UNKNOWN" in gate_statuses.values()
        or not entries
        or any(factor["applicability"] == "UNKNOWN" for factor in entries.values())
    ):
        overall_status = "PARTIAL_ASSESSMENT"
    else:
        overall_status = "ASSESSED"

    return {
        "schema_version": "2.0",
        "overall_status": overall_status,
        "critical_gates": gate_statuses,
        "adjusted_domain_weights": {
            key: round(domain_weights[key], 2) for key in DOMAIN_IDS
        },
        "domains": domain_results,
        "scoring": {
            "status": scoring_status,
            "kind": score_kind,
            "reasons": reasons,
            "coverage_percent": coverage_percent,
            "composite": composite,
            "mean_health": mean_health,
            "label": label,
        },
    }


def markdown_result(result: dict[str, Any]) -> str:
    lines = [
        "# Architecture Quality Profile",
        "",
        f"Overall status: **{result['overall_status']}**",
        f"Scoring: **{result['scoring']['status']}**",
        f"Evidence coverage: **{result['scoring']['coverage_percent']}%**",
    ]
    scoring = result["scoring"]
    if scoring["composite"] is not None:
        detail = (
            f"{scoring['composite']}/100 — {scoring['label']} "
            f"(mean factor health {scoring['mean_health']}/4)"
        )
        if result["overall_status"] == "CRITICAL_GATE_FAILURE":
            # A composite must never read as the verdict when a gate has failed.
            lines.append(f"Diagnostic composite (NOT the verdict): {detail}")
        else:
            lines.append(f"{scoring['kind']}: **{detail}**")
    if result["overall_status"] == "CRITICAL_GATE_FAILURE":
        failed = [name for name, status in result["critical_gates"].items() if status == "FAIL"]
        lines.append(f"Failed critical gates: **{', '.join(failed)}**")
    if scoring["reasons"]:
        lines.extend(["", "Score withheld because:"])
        lines.extend(f"- {reason}" for reason in scoring["reasons"])
    lines.extend(
        [
            "",
            "| Domain | Weight | Coverage | Health |",
            "|---|---:|---:|---:|",
        ]
    )
    for domain_id, domain in result["domains"].items():
        health = "—" if domain["health_score"] is None else str(domain["health_score"])
        lines.append(
            f"| {domain_id}. {domain['name']} | {domain['adjusted_weight']:.2f} | "
            f"{domain['coverage_percent']}% | {health} |"
        )
    return "\n".join(lines) + "\n"


def read_frontmatter(skill_path: Path) -> dict[str, str]:
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    block = match.group(1)
    result: dict[str, str] = {}
    for key in ("name", "description", "license", "compatibility"):
        field_match = re.search(rf"^{key}:\s*[\"']?(.*?)[\"']?\s*$", block, re.MULTILINE)
        if field_match:
            result[key] = field_match.group(1).strip().strip('"').strip("'")
    for key in ("version", "model-version", "factors", "domains"):
        metadata_match = re.search(
            rf"^\s+{re.escape(key)}:\s*[\"']?([^\"'\n]+)", block, re.MULTILINE
        )
        if metadata_match:
            result[key] = metadata_match.group(1).strip()
    return result


def validate_eval_cases(path: Path) -> int:
    if not path.exists():
        raise ValueError(f"missing evaluation corpus: {path}")
    ids: set[str] = set()
    count = 0
    required = {
        "id",
        "category",
        "prompt",
        "critical",
        "activation_expected",
        "pass",
        "fail",
    }
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid eval JSONL at line {line_number}: {exc}") from exc
        missing = sorted(required - set(case))
        if missing:
            raise ValueError(
                f"eval {case.get('id', line_number)} missing fields: {', '.join(missing)}"
            )
        if not isinstance(case.get("id"), str) or not re.fullmatch(r"E\d{2,}", case["id"]):
            raise ValueError(f"eval at line {line_number} has invalid id")
        if case["id"] in ids:
            raise ValueError(f"duplicate eval id: {case['id']}")
        for field in ("category", "prompt", "pass", "fail"):
            if not isinstance(case.get(field), str) or not case[field].strip():
                raise ValueError(f"eval {case['id']} requires non-empty {field}")
        for field in ("critical", "activation_expected"):
            if not isinstance(case.get(field), bool):
                raise ValueError(f"eval {case['id']} {field} must be a boolean")
        ids.add(case["id"])
        count += 1
    if count < 24:
        raise ValueError(f"evaluation corpus must contain at least 24 cases, found {count}")
    return count


def check_model_docs(root: Path, model: dict[str, Any]) -> None:
    _, factors = flatten_model(model)
    factors_text = (root / "references" / "factors.md").read_text(encoding="utf-8")
    weights_text = (root / "references" / "weights.md").read_text(encoding="utf-8")
    ordinal = 0
    for factor_id, factor in factors.items():
        ordinal += 1
        if factors_text.count(factor_id) != 1:
            raise ValueError(f"{factor_id} must appear exactly once in references/factors.md")
        if weights_text.count(factor_id) != 1:
            raise ValueError(f"{factor_id} must appear exactly once in references/weights.md")
        expected_heading = f"### {factor_id} — {ordinal}. {factor['name']}"
        if expected_heading not in factors_text:
            raise ValueError(f"{factor_id} name/order is not synchronized in factors.md")
        expected_weight = f"| {factor_id} | {factor['name']} | {float(factor['weight']):.1f} |"
        if expected_weight not in weights_text:
            raise ValueError(f"{factor_id} name/weight is not synchronized in weights.md")
    for profile_id in model.get("context_profiles", {}):
        if weights_text.count(f"| {profile_id} |") != 1:
            raise ValueError(f"context profile {profile_id} is not synchronized in weights.md")


# Fenced blocks and inline spans hold illustrative samples, not live links.
FENCED_CODE = re.compile(r"^[ \t]*(`{3,}|~{3,}).*?(?:^[ \t]*\1[ \t]*$|\Z)", re.DOTALL | re.MULTILINE)
INLINE_CODE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)", re.DOTALL)
MARKDOWN_LINK = re.compile(r"(?<!\\)\[[^\]]+\]\(([^)]+)\)")


def link_destination(target: str) -> str:
    """Strip a CommonMark link title; a bare destination cannot contain spaces."""
    target = target.strip()
    if target.startswith("<"):
        closing = target.find(">")
        if closing != -1:
            return target[1:closing]
    return target.split(maxsplit=1)[0] if target else ""


def validate_markdown_links(root: Path) -> None:
    """Check local file targets in shipped Markdown prose, relative to each document."""
    files = list(root.glob("*.md"))
    for folder in ("references", "examples", "tests"):
        files.extend((root / folder).rglob("*.md"))
    # Keep the caller's root for reporting; containment compares resolved paths.
    resolved_root = root.resolve()
    for document in files:
        content = document.read_text(encoding="utf-8")
        prose = INLINE_CODE.sub("\n", FENCED_CODE.sub("\n", content))
        for target in MARKDOWN_LINK.findall(prose):
            destination = link_destination(target)
            parsed = urlsplit(destination)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (document.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(resolved_root) or not resolved.exists():
                raise ValueError(
                    f"{document.relative_to(root)} references missing or external file: {destination}"
                )


def validate_package(root: Path) -> dict[str, Any]:
    skill_path = root / "SKILL.md"
    frontmatter = read_frontmatter(skill_path)
    if frontmatter.get("name") != root.name:
        raise ValueError("SKILL.md name must match the skill directory name")
    name = frontmatter.get("name", "")
    if (
        not re.fullmatch(r"[a-z0-9-]{1,64}", name)
        or name.startswith("-")
        or name.endswith("-")
        or "--" in name
    ):
        raise ValueError("SKILL.md name must satisfy Agent Skills naming rules")
    if frontmatter.get("version") != SKILL_VERSION:
        raise ValueError(f"SKILL.md metadata.version must be {SKILL_VERSION}")
    description = frontmatter.get("description", "")
    if not description or len(description) > 1024 or "<" in description or ">" in description:
        raise ValueError("SKILL.md description must contain 1-1024 characters")
    compatibility = frontmatter.get("compatibility", "")
    if compatibility and len(compatibility) > 500:
        raise ValueError("SKILL.md compatibility must contain at most 500 characters")

    skill_text = skill_path.read_text(encoding="utf-8")
    if len(skill_text.splitlines()) > 500:
        raise ValueError("SKILL.md must remain under 500 lines for progressive disclosure")
    validate_markdown_links(root)

    model_path = root / "references" / "architecture-quality-model.json"
    model = load_json(model_path)
    model_summary = validate_model(model)
    if frontmatter.get("model-version") != model.get("model_version"):
        raise ValueError("SKILL.md model-version must match the canonical model")
    if frontmatter.get("factors") != str(model_summary["factors"]):
        raise ValueError("SKILL.md factor count must match the canonical model")
    if frontmatter.get("domains") != str(model_summary["domains"]):
        raise ValueError("SKILL.md domain count must match the canonical model")
    check_model_docs(root, model)

    template = load_json(root / "examples" / "assessment-template.json")
    assessment_schema = root / "schemas" / "assessment.schema.json"
    validate_assessment(template, model, schema_path=assessment_schema)
    for example in sorted((root / "examples").glob("*.json")):
        assessment = load_json(example)
        validate_assessment(assessment, model, schema_path=assessment_schema)

    schemas = sorted((root / "schemas").glob("*.schema.json"))
    if len(schemas) != 3:
        raise ValueError("schemas/ must contain exactly three schema files")
    for schema in schemas:
        schema_data = load_json(schema)
        if schema_data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            raise ValueError(f"schema {schema.name} must use JSON Schema draft 2020-12")
        if schema_data.get("type") != "object":
            raise ValueError(f"schema {schema.name} root type must be object")

    eval_count = validate_eval_cases(root / "tests" / "evals" / "cases.jsonl")

    sources = load_json(root / "references" / "sources.json")
    if sources.get("schema_version") != "1.0":
        raise ValueError("sources.json schema_version must be 1.0")
    source_items = sources.get("sources")
    if not isinstance(source_items, list):
        raise ValueError("sources.json sources must be a list")
    source_ids: set[str] = set()
    for source in source_items:
        if not isinstance(source, dict):
            raise ValueError("each source must be an object")
        source_id = source.get("id")
        if not source_id or source_id in source_ids:
            raise ValueError(f"invalid or duplicate source id: {source_id}")
        source_ids.add(source_id)
        for field in ("title", "url", "authority", "stability", "last_verified"):
            if not source.get(field):
                raise ValueError(f"source {source_id} is missing {field}")
        if not str(source["url"]).startswith("https://"):
            raise ValueError(f"source {source_id} must use an https URL")
        if source["stability"] not in {"stable", "volatile", "draft"}:
            raise ValueError(f"source {source_id} has invalid stability")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source["last_verified"])):
            raise ValueError(f"source {source_id} has invalid last_verified date")

    openai_yaml = root / "agents" / "openai.yaml"
    if not openai_yaml.exists():
        raise ValueError("missing agents/openai.yaml")
    openai_text = openai_yaml.read_text(encoding="utf-8")
    if "$assessing-software-architecture-quality" not in openai_text:
        raise ValueError("agents/openai.yaml default_prompt must mention the skill")

    return {
        **model_summary,
        "schemas": len(schemas),
        "evals": eval_count,
        "sources": len(source_ids),
    }


def default_root() -> Path:
    return Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and score software architecture quality assessments."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    package = subparsers.add_parser("validate-package")
    package.add_argument("root", nargs="?", type=Path, default=default_root())

    assessment = subparsers.add_parser("validate-assessment")
    assessment.add_argument("assessment", type=Path)
    assessment.add_argument("--model", type=Path)

    score = subparsers.add_parser("score")
    score.add_argument("assessment", type=Path)
    score.add_argument("--model", type=Path)
    score.add_argument("--format", choices=("json", "markdown"), default="json")

    sync = subparsers.add_parser("sync-model-docs")
    sync.add_argument("root", nargs="?", type=Path, default=default_root())
    sync.add_argument("--check", action="store_true", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "validate-package":
            summary = validate_package(args.root.resolve())
            print(
                "Package validation: OK "
                f"({summary['domains']} domains, {summary['factors']} factors, "
                f"{summary['evals']} evals, {summary['sources']} sources)"
            )
            return 0

        if args.command == "sync-model-docs":
            root = args.root.resolve()
            model = load_json(root / "references" / "architecture-quality-model.json")
            validate_model(model)
            check_model_docs(root, model)
            print("Model documentation: synchronized")
            return 0

        root = default_root()
        model_path = args.model or root / "references" / "architecture-quality-model.json"
        model = load_json(model_path)
        assessment = load_json(args.assessment)
        if args.command == "validate-assessment":
            summary = validate_assessment(assessment, model)
            print(json.dumps({"status": "valid", **summary}, indent=2))
            return 0
        if args.command == "score":
            result = score_assessment(assessment, model)
            if args.format == "markdown":
                print(markdown_result(result), end="")
            else:
                print(json.dumps(result, indent=2))
            return 0
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
