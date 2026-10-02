# Assessing Software Architecture Quality

Evidence-led architecture reviews for coding agents. It judges a system from corroborated evidence, withholds a score unless a full assessment can support one, and recommends the smallest reversible change.

The agent-facing description lives in `SKILL.md` frontmatter. This file is for installing and releasing the package. Version 2.3 is the package. The numerical model remains version 2.1 with 49 factors and unchanged scoring.

## Install

This repository is one skill. The [skills CLI](https://github.com/vercel-labs/skills) installs it as `assessing-software-architecture-quality`, the `name` in `SKILL.md`, whatever the GitHub repository is called.

```bash
npx skills add moeedhy/assessing-software-architecture-quality-skill
```

Use `--global` to install for every project. The guidance has no runtime dependency. Validation and scoring need Python 3.10 or newer and only the standard library.

A raw clone uses the repository folder name. Package validation requires the folder name to equal `name`, so rename that clone to `assessing-software-architecture-quality` before running the checks below.

## Release

There is no registry submission. A public GitHub repository is the release, and skills.sh lists the skill from install telemetry.

1. Add a license file and set `license` in `SKILL.md`. This repository does not have one yet; do not publish it as reusable without one.
2. Let GitHub Actions pass on the commit you intend to ship.
3. Tag that commit `v2.3.0`, matching `metadata.version`, and attach the `package_digest.py` output to the GitHub release.
4. Install once from a clean project and confirm the skill directory name.

The evaluation matrix in `tests/evals.md` has not been run. Do not describe the package as behaviorally validated.

## What is included

- `SKILL.md` — activation boundary and compact operating contract.
- `references/architecture-quality-model.json` — canonical IDs, weights, profiles, gates, and scoring thresholds.
- `references/assessment-modes.md` — intent and TRIAGE/STANDARD/DEEP routing.
- `references/evidence-contract.md` — traceable evidence, claim, and confidence rules.
- `references/evidence-tooling.md` — commands and ecosystem tools for obtaining measurements.
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
- `tests/unit/` and `tests/evals/` — deterministic tests, behavioral cases, and near-miss activation probes.
- `examples/assessment-template.json` — empty STANDARD checkpoint to copy and extend.
- `examples/deep-assessment.json` — complete, scoreable DEEP assessment to copy from.
- `examples/framework-review.json` — synthetic schema-2.1 checkpoint retaining unresolved version and architecture evidence.
- `agents/openai.yaml` — optional OpenAI/Codex interface metadata.

## Design position

This skill is not a style guide or pattern enforcer. It evaluates the architecture a system actually experiences: change propagation, code and runtime dependencies, data and consistency ownership, delivery constraints, failure behavior, security boundaries, and team boundaries.

The weights, multipliers, thresholds, and score bands are authored decision heuristics—not scientific or standards-derived laws. A critical gate can override a favorable average. A score is never required for a useful review.

The composite is an ordinal scale rescaled to 0–100, **not a percentage**: uniform factor health `h` produces exactly `25h`, so a system whose every factor is Acceptable (2) scores 50 and lands in the **Adequate** band. Band labels use a vocabulary deliberately disjoint from the health-scale words, and the script reports `mean_health` (0–4) beside every composite.

Framework leverage asks whether native features or custom behavior satisfy the actual requirements at lower total cost. It adds no factor or score, and unused capabilities are not defects. Assessment methods feed the same evidence and findings; mappings are authored interpretations, not compliance claims.

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

Behavioral release evaluation compares fresh-context no-skill, previous-v2.1, and candidate-v2.3 runs using independent grading. See [the evaluation protocol](tests/evals.md). The matrix remains **UNEXECUTED**; deterministic checks and code review are not behavioral release evidence. Installation is a separate action after reviewing [the release procedure](references/release.md).
