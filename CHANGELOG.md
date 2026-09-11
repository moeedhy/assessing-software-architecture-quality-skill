# Changelog

## 2.1.0 — 2026-09-07

- **Fixed a score-band calibration defect.** The composite (`25 * mean health`) was banded with percentage-style thresholds, so a system whose every factor was rated *Acceptable* reported as **Critical**, and a uniformly *Strong* system reported as **Acceptable**. Band thresholds now sit at the midpoints between uniform-health anchors.
- Gave score bands a vocabulary (Exemplary / Healthy / Adequate / Fragile / Failing) deliberately disjoint from the health-scale words, so a band can never be misread as a factor health level. Added a unit test asserting the two vocabularies stay disjoint.
- Added `mean_health` (0–4) to scoring results and rendered output, making the ordinal basis of the composite explicit.
- A computed composite is now demoted to `Diagnostic composite (NOT the verdict)` and accompanied by the failed gate names whenever a critical gate has failed, matching the contract already stated in `weights.md`.
- Added three factors, extending the catalog to 49: `AQ-C09` Contract & Schema Evolution, `AQ-H05` Supply Chain & Build Integrity, `AQ-H06` Data Lifecycle & Privacy Architecture.
- Rebalanced domain weights (B 16→13, H 10→13) and documented the anti-double-counting rationale for domains B and G, including an explicit warning that G's low weight means "already counted", never "low priority".
- Extended the security gate to cover the path artifacts take to production, and the safety/compliance gate to cover unsatisfiable erasure, retention, residency, and tenant-isolation obligations.
- Added evidence channels and factor-interaction patterns for contracts, supply chain, and data lifecycle.
- Added `examples/deep-assessment.json`, the first complete scoreable DEEP payload in the package.
- Added four behavioral eval cases (E33–E36) covering the new factors and composite misreading.
- Added SLSA to the provenance ledger; re-verified volatile sources on 2026-09-07 (SLSA v1.2 current, v1.0 retired).
- Replaced hardcoded factor-count and version literals in the script with named constants.

## 2.0.0 — 2026-09-04

Architecture-quality skill v2.

- Added intent modes plus proportional TRIAGE, STANDARD, and DEEP assessment depths.
- Preserved the 46-factor/8-domain catalog and assigned stable `AQ-*` factor IDs.
- Made the JSON model the canonical source for weights, profiles, gates, metric classes, and overlap roles.
- Made scoring explicitly opt-in and deterministic; DEEP, coverage, domain-unknown, and critical-gate safeguards prevent false precision.
- Added JSON Schemas for evidence, assessment state, and scoring results.
- Added a pure-standard-library validation/scoring CLI and executable unit tests.
- Added a machine-readable behavioral evaluation corpus covering activation, safety, evidence discipline, AI systems, and scoring traps.
- Added instruction/data-boundary rules, capability-adaptive runtime guidance, resumable structured state, and current-agent features such as tool discovery, structured outputs, asynchronous evidence lanes, and mid-turn steering.
- Added an AI-system context profile covering model/provider volatility, evaluation quality, nondeterminism, prompt/tool boundaries, observability, and cost/latency.
- Added machine-readable source provenance and optional OpenAI/Codex interface metadata.

## 1.0.0 — 2026-09-04

- Established the 46-factor model across 8 domains.
- Added evidence coverage, critical gates, context profiles, a review protocol, provenance, and an initial prose evaluation suite.
