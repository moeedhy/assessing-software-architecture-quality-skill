# Assessing Software Architecture Quality

A portable Agent Skill for evidence-led architecture decisions and reviews. Version 2 makes depth proportional, scoring optional, evidence machine-checkable, and runtime guidance capability-adaptive. Version 2.1 recalibrates the composite score bands and extends the catalog to 49 factors.

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
- `schemas/` — JSON Schemas for evidence, assessments, and deterministic results.
- `scripts/architecture_quality.py` — standard-library package validation and opt-in scoring.
- `tests/unit/` and `tests/evals/` — deterministic tests and machine-readable behavioral cases.
- `examples/assessment-template.json` — empty STANDARD checkpoint to copy and extend.
- `examples/deep-assessment.json` — complete, scoreable DEEP assessment to copy from.
- `agents/openai.yaml` — optional OpenAI/Codex interface metadata.

## Design position

This skill is not a style guide or pattern enforcer. It evaluates the architecture a system actually experiences: change propagation, code and runtime dependencies, data and consistency ownership, delivery constraints, failure behavior, security boundaries, and team boundaries.

The weights, multipliers, thresholds, and score bands are authored decision heuristics—not scientific or standards-derived laws. A critical gate can override a favorable average. A score is never required for a useful review.

The composite is an ordinal scale rescaled to 0–100, **not a percentage**: uniform factor health `h` produces exactly `25h`, so a system whose every factor is Acceptable (2) scores 50 and lands in the **Adequate** band. Band labels use a vocabulary deliberately disjoint from the health-scale words, and the script reports `mean_health` (0–4) beside every composite.

## Install

Copy the whole `assessing-software-architecture-quality/` directory into a skills-compatible location. Keep the directory name identical to the `name` in `SKILL.md`. The guidance has no runtime dependency; the optional CLI needs Python 3.10 or newer and only the standard library.

## Validate

```bash
python3 scripts/architecture_quality.py validate-package .
python3 -m unittest discover -s tests/unit -p 'test_*.py' -v
```

To validate or score a structured assessment:

```bash
python3 scripts/architecture_quality.py validate-assessment examples/deep-assessment.json
python3 scripts/architecture_quality.py score examples/deep-assessment.json --format markdown
```

`score_requested: true` requires `depth: DEEP` and all 49 factor records. Scores are withheld when evidence coverage or critical-gate requirements are not met, and a computed composite is demoted to a labelled diagnostic whenever a critical gate has failed.

## Source of truth

Edit `references/architecture-quality-model.json` first when changing IDs or weights, then synchronize the prose tables and run:

```bash
python3 scripts/architecture_quality.py sync-model-docs --check
```

Behavioral release evaluation must compare fresh-context baseline and skill-enabled runs. See `tests/evals.md`; do not substitute self-review for an independent evaluator.
