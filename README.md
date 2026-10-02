# Assessing Software Architecture Quality

A portable Agent Skill for evidence-led architecture decisions and reviews. Version 2.2 adds unscored framework-use guidance, a NestJS profile, conditional assessment methods, and resumable review context. The numerical model remains version 2.1 with 49 factors and unchanged scoring.

## What is included

- `SKILL.md` — activation boundary and compact operating contract.
- `references/architecture-quality-model.json` — canonical IDs, weights, profiles, gates, and scoring thresholds.
- `references/assessment-modes.md` — intent and TRIAGE/STANDARD/DEEP routing.
- `references/evidence-contract.md` — traceable evidence, claim, and confidence rules.
- `references/factors.md` — 49-factor interpretation catalog.
- `references/weights.md` — optional scoring semantics and safeguards.
- `references/review-protocol.md` — evidence-driven workflow.
- `references/ai-systems.md` — architecture concerns specific to AI-enabled systems.
- `references/runtime-guidance.md` — capability-adaptive agent behavior.
- `references/report-contract.md` — proportional output contracts.
- `references/framework-leverage.md` and `references/nestjs.md` — native capability fit, duplication, misuse, and justified customization.
- `references/assessment-methods.md` — conditional ATAM-inspired, ISO 25010, C4, and provider-specific Well-Architected lenses.
- `references/release.md` — validation, evaluation, package digest, and separate installation procedure.
- `schemas/` — JSON Schemas for evidence, assessments, and deterministic results.
- `scripts/architecture_quality.py` — standard-library package validation and opt-in scoring.
- `tests/unit/` and `tests/evals/` — deterministic tests and machine-readable behavioral cases.
- `examples/assessment-template.json` — empty STANDARD checkpoint to copy and extend.
- `examples/deep-assessment.json` — complete, scoreable DEEP assessment to copy from.
- `examples/framework-review.json` — synthetic schema-2.1 checkpoint retaining unresolved version and architecture evidence.
- `agents/openai.yaml` — optional OpenAI/Codex interface metadata.

## Design position

This skill is not a style guide or pattern enforcer. It evaluates the architecture a system actually experiences: change propagation, code and runtime dependencies, data and consistency ownership, delivery constraints, failure behavior, security boundaries, and team boundaries.

The weights, multipliers, thresholds, and score bands are authored decision heuristics—not scientific or standards-derived laws. A critical gate can override a favorable average. A score is never required for a useful review.

The composite is an ordinal scale rescaled to 0–100, **not a percentage**: uniform factor health `h` produces exactly `25h`, so a system whose every factor is Acceptable (2) scores 50 and lands in the **Adequate** band. Band labels use a vocabulary deliberately disjoint from the health-scale words, and the script reports `mean_health` (0–4) beside every composite.

Framework leverage asks whether native features or custom behavior satisfy the actual requirements at lower total cost. It adds no factor or score, and unused capabilities are not defects. Assessment methods feed the same evidence and findings; mappings are authored interpretations, not compliance claims.

## Install

Copy the whole `assessing-software-architecture-quality/` directory into a skills-compatible location. Keep the directory name identical to the `name` in `SKILL.md`. The guidance has no runtime dependency; the optional CLI needs Python 3.10 or newer and only the standard library.

## Validate

```bash
python3 scripts/architecture_quality.py validate-package .
python3 -m unittest discover -s tests/unit -p 'test_*.py' -v
```

For development and release checks, install `requirements-dev.txt` into a virtual environment and run the same tests there, plus:

```bash
python3 scripts/validate_schemas.py
python3 scripts/package_digest.py .
```

The JSON Schema checks validate the schemas themselves, all example assessments, evidence records, and scoring outputs using draft 2020-12. The CLI additionally validates cross-record references, factor membership, and scoring prerequisites. Dependency-free unit runs explicitly skip development schema tests when `jsonschema` is unavailable; a release check must run them. The runtime CLI still uses only the standard library.

To validate or score a structured assessment:

```bash
python3 scripts/architecture_quality.py validate-assessment examples/deep-assessment.json
python3 scripts/architecture_quality.py score examples/deep-assessment.json --format markdown
```

`score_requested: true` requires `depth: DEEP` and all 49 factor records. Scores are withheld when evidence coverage or critical-gate requirements are not met, and a computed composite is demoted to a labelled diagnostic whenever a critical gate has failed.

Assessment schema `2.1` supports optional `review_context` for scope, scenarios, findings, alternatives, contradictions, and pending work. Schema `2.0` inputs remain supported, and missing context means it was not captured. Evidence `summary` is optional, including on legacy inputs. Scoring-result schema `2.0` and model `2.1.0` are unchanged.

## Source of truth

Edit `references/architecture-quality-model.json` first when changing IDs or weights, then synchronize the prose tables and run:

```bash
python3 scripts/architecture_quality.py sync-model-docs --check
```

Behavioral release evaluation compares fresh-context no-skill, previous-v2.1, and candidate-v2.2 runs using independent grading. See [the evaluation protocol](tests/evals.md). The matrix remains **UNEXECUTED**; deterministic checks and code review are not behavioral release evidence. Installation is a separate action after reviewing [the release procedure](references/release.md).
