# Architecture Quality Weight Model

## Contents

- Status of these weights
- Base domain weights
- Factor weights
- Why some weights are deliberately small
- Health scale
- Confidence scale
- Applicability states
- Evidence coverage
- Weighted composite
- Context profiles
- Critical gates
- Priority model

## Status of these weights

These weights are **heuristic defaults authored for this skill**. They are not ISO, DORA, NIST, Sonar, AWS, Microsoft, or academic standard weights. Project-specific quality attributes and mandatory requirements take precedence.

Use weights to structure attention and prioritization, not to manufacture certainty.

The canonical machine-readable source is `architecture-quality-model.json`. Update it first, keep every stable factor ID below synchronized, and verify with `python3 scripts/architecture_quality.py sync-model-docs --check` from the skill root.

Scoring is available only when the user explicitly requests it. A qualitative TRIAGE or STANDARD assessment is complete without a number.

## Base domain weights

| Domain | Weight |
|---|---:|
| A. Understandability | 10 |
| B. Modularity & Dependencies | 13 |
| C. Changeability & Evolvability | 18 |
| D. Distributed Coupling & Failure Containment | 12 |
| E. Runtime Quality | 14 |
| F. Engineering Capability | 12 |
| G. Domain & Organization | 8 |
| H. Governance & Security | 13 |
| **Total** | **100** |

## Factor weights

### A. Understandability — 10

| ID | Factor | Weight |
|---|---|---:|
| AQ-A01 | Cognitive Load | 4.0 |
| AQ-A02 | Cognitive Complexity | 2.5 |
| AQ-A03 | Obscurity / Unknown Unknowns | 2.0 |
| AQ-A04 | Conceptual Clarity | 1.5 |

### B. Modularity & Dependencies — 13

| ID | Factor | Weight |
|---|---|---:|
| AQ-B01 | Cohesion | 2.0 |
| AQ-B02 | LCOM | 0.5 |
| AQ-B03 | Coupling | 2.0 |
| AQ-B04 | Afferent Coupling (Ca) | 0.5 |
| AQ-B05 | Efferent Coupling (Ce) | 0.5 |
| AQ-B06 | Instability | 0.5 |
| AQ-B07 | Dependency Cycles | 1.5 |
| AQ-B08 | Dependency Direction | 1.5 |
| AQ-B09 | Separation of Concerns | 1.0 |
| AQ-B10 | Information Hiding | 1.5 |
| AQ-B11 | Encapsulation | 0.5 |
| AQ-B12 | API Surface Area | 1.0 |

### C. Changeability & Evolvability — 18

| ID | Factor | Weight |
|---|---|---:|
| AQ-C01 | Change Amplification | 4.0 |
| AQ-C02 | Change Coupling | 1.5 |
| AQ-C03 | Volatility Alignment | 2.0 |
| AQ-C04 | Replaceability | 1.0 |
| AQ-C05 | Evolvability | 2.5 |
| AQ-C06 | Reversibility | 1.0 |
| AQ-C07 | Hotspot Risk | 2.5 |
| AQ-C08 | Technical Debt Pressure | 1.5 |
| AQ-C09 | Contract & Schema Evolution | 2.0 |

### D. Distributed Coupling & Failure Containment — 12

| ID | Factor | Weight |
|---|---|---:|
| AQ-D01 | Temporal Coupling | 2.0 |
| AQ-D02 | Data Coupling | 2.5 |
| AQ-D03 | Consistency Coupling | 2.0 |
| AQ-D04 | Coordination Cost | 2.0 |
| AQ-D05 | Blast Radius | 3.5 |

### E. Runtime Quality — 14

| ID | Factor | Weight |
|---|---|---:|
| AQ-E01 | Scalability | 2.5 |
| AQ-E02 | Performance Efficiency | 2.5 |
| AQ-E03 | Availability | 2.5 |
| AQ-E04 | Resilience | 3.5 |
| AQ-E05 | Recovery Architecture | 3.0 |

### F. Engineering Capability — 12

| ID | Factor | Weight |
|---|---|---:|
| AQ-F01 | Testability | 3.0 |
| AQ-F02 | Observability | 2.5 |
| AQ-F03 | Deployability | 2.5 |
| AQ-F04 | Architecture Conformance | 2.0 |
| AQ-F05 | Architecture Fitness Functions | 2.0 |

### G. Domain & Organization — 8

| ID | Factor | Weight |
|---|---|---:|
| AQ-G01 | Domain Alignment | 4.0 |
| AQ-G02 | Ownership Clarity | 2.0 |
| AQ-G03 | Team Cognitive Load | 2.0 |

### H. Governance & Security — 13

| ID | Factor | Weight |
|---|---|---:|
| AQ-H01 | Architecture Risk | 2.0 |
| AQ-H02 | Attack Surface | 3.0 |
| AQ-H03 | Security Coupling | 2.0 |
| AQ-H04 | Continuous Architecture Governance | 2.0 |
| AQ-H05 | Supply Chain & Build Integrity | 2.5 |
| AQ-H06 | Data Lifecycle & Privacy Architecture | 1.5 |

## Why some weights are deliberately small

The same anti-double-counting rule is applied at three levels.

**Derivative metrics.** LCOM, Ca, Ce, and Instability overlap broader properties such as cohesion, coupling, change amplification, and dependency stability. Their direct weights stay small.

**Domain B (Modularity & Dependencies).** Boundary properties are largely *causes* whose consequences are already priced in C (change amplification, change coupling, hotspots) and D (coordination cost, blast radius). B is weighted below C for that reason, not because structure matters less.

**Domain G (Domain & Organization).** G carries the lowest domain weight even though Domain Alignment is the root cause behind much of B, C, and D. This is intentional and follows the same rule: G's consequences are already counted elsewhere. **Report G findings as root causes even when their weight is small** — a low weight means "already counted", never "low priority". Remediation that treats only the C and D symptoms while leaving G unaddressed is a misuse of this model.

## Health scale

| Score | Meaning |
|---:|---|
| 0 | Critical: unacceptable systemic risk, violated essential invariant, or architecture actively blocks safe operation/change |
| 1 | Weak: repeated harmful pattern with substantial cost or risk |
| 2 | Acceptable: works with manageable weaknesses |
| 3 | Strong: intentional, maintainable, and supported by evidence |
| 4 | Excellent: intentional, measured, enforced, and validated by outcomes |

Do not infer "Excellent" from tidy source code alone.

## Confidence scale

Report confidence separately from health:

- **HIGH** — multiple independent evidence channels or strong direct evidence plus corroboration.
- **MEDIUM** — credible direct evidence but incomplete corroboration.
- **LOW** — mostly inference, incomplete artifacts, or hypothetical design.
- **UNKNOWN** — insufficient evidence for a factor or gate judgment. Evidence records cannot use this value; see [the evidence contract](evidence-contract.md).

Never mathematically blend confidence into health.

## Applicability states

Every factor is one of:

- **ASSESSED**
- **UNKNOWN**
- **NOT_APPLICABLE**

Do not award points for NOT_APPLICABLE factors. Renormalize applicable weights.

## Evidence coverage

```text
coverage = assessed_applicable_weight / total_applicable_weight
```

Do not publish an authoritative composite when any of these is true:

- evidence coverage < 70%,
- a critical gate has not been assessed,
- more than 50% of an applicable domain's weight is UNKNOWN,
- the user asked for a qualitative review only.

For DESIGN mode, call any composite a **Design Readiness Score**, not observed architecture health. Never score unavailable production/delivery behavior as though measured.

## Weighted composite

For assessed applicable factors only:

```text
quality = 100 * Σ(adjusted_weight * health/4) / Σ(adjusted_weight)
```

The composite is an ordinal scale rescaled to 0–100, **not a percentage**. Uniform health `h` produces exactly `25h`, so a system whose every factor is Acceptable (2) scores 50. Report `mean_health` (0–4) alongside the composite; the deterministic script emits both.

Band labels use a vocabulary deliberately disjoint from the health-scale words so that a band can never be misread as a factor health level, and thresholds sit at the midpoints between uniform-health anchors. A band label therefore names the *average factor health* of the assessment.

Default heuristic bands:

| Score | Label | Corresponds to mean factor health |
|---:|---|---|
| 88–100 | Exemplary | ≈3.5–4.0 (Strong→Excellent) |
| 63–87 | Healthy | ≈2.5–3.5 (Acceptable→Strong) |
| 38–62 | Adequate | ≈1.5–2.5 (Weak→Acceptable) |
| 13–37 | Fragile | ≈0.5–1.5 (Critical→Weak) |
| 0–12 | Failing | ≈0.0–0.5 (Critical) |

Always show domain/factor evidence beside a composite. A score is a summary, never the conclusion by itself.

## Context profiles

Project/user-defined quality weights override these profiles. Otherwise apply relevant multipliers, cap any combined domain multiplier at 2.0, then renormalize to 100.

| ID | Profile | A | B | C | D | E | F | G | H |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| security-critical-regulated | Security-critical / regulated | 1.0 | 1.0 | 1.0 | 1.15 | 1.25 | 1.15 | 1.0 | 1.60 |
| high-scale-distributed | High-scale distributed | 1.0 | 1.10 | 1.10 | 1.50 | 1.50 | 1.20 | 1.0 | 1.10 |
| fast-changing-product | Fast-changing product | 1.20 | 1.10 | 1.35 | 1.0 | 1.0 | 1.20 | 1.10 | 1.0 |
| legacy-modernization | Legacy modernization | 1.20 | 1.25 | 1.50 | 1.10 | 1.0 | 1.20 | 1.10 | 1.0 |
| public-platform-api | Public platform / API | 1.0 | 1.25 | 1.20 | 1.10 | 1.10 | 1.10 | 1.20 | 1.20 |
| data-intensive | Data-intensive | 1.0 | 1.10 | 1.10 | 1.40 | 1.30 | 1.10 | 1.10 | 1.20 |
| ai-system | AI system | 1.10 | 1.10 | 1.20 | 1.25 | 1.25 | 1.40 | 1.0 | 1.50 |

Do not select a profile merely because a technology buzzword appears in the stack.

## Critical gates

A favorable weighted average cannot override a demonstrated gate failure.

### Security gate

Examples: unauthenticated privileged capability, reachable critical vulnerability, exposed secret enabling compromise, severe trust-boundary failure, or an unverifiable or broadly writable path by which build artifacts reach production.

### Data-integrity gate

Architecture can violate a critical business invariant or irrecoverably corrupt required data.

### Recovery gate

Critical persistent data has required recovery objectives but no credible verified recovery mechanism.

### Safety / compliance gate

A mandatory in-scope architectural control is clearly absent in a safety-critical or regulated system, including an erasure, retention, residency, or tenant-isolation obligation the architecture cannot actually satisfy.

When triggered:

```text
OVERALL STATUS = CRITICAL GATE FAILURE
```

A diagnostic numerical score may be shown only as secondary information.

## Priority model

Keep health and priority distinct. Prioritize using impact, change pressure, architectural reach, business criticality, and confidence.

Priority labels P0–P4 are defined once, in the [report contract](report-contract.md).
