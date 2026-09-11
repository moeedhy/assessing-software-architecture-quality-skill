# Architecture Assessment Output Contract

Lead with the decision. Scale the output to the selected depth and user request; do not emit empty ceremonial sections.

## TRIAGE

Return:

1. decision or immediate risk;
2. decisive evidence with locators;
3. critical-gate status relevant to scope;
4. important unknowns or contradiction;
5. smallest next action and verification.

No composite score.

## STANDARD

Return:

1. executive decision and selected intent/depth;
2. scope, constraints, assumptions, and unavailable evidence;
3. concise architecture map when relationships are not clear in prose;
4. prioritized, non-duplicative findings;
5. material alternatives and tradeoffs;
6. NOW / NEXT / LATER / DO NOT DO recommendations as useful;
7. fitness functions and verification;
8. KEEP / CHANGE / WATCH / AVOID summary;
9. evidence limitations.

No composite unless the user explicitly changes the request to DEEP scoring.

## DEEP

Include the STANDARD contract plus:

- all 49 stable factor states;
- adjusted domain weights when profiles/custom weights apply;
- domain health, confidence, trend if evidence exists, and coverage;
- all four critical gates;
- score status and withholding reasons;
- **Architecture Health** composite only for observed systems when valid;
- **Design Readiness** composite for DESIGN mode when valid.

Use `schemas/assessment.schema.json` for state and `schemas/assessment-result.schema.json` for deterministic results.

## Finding contract

```text
Finding ID:
Title:
Priority: P0/P1/P2/P3/P4
Factor IDs:
Evidence IDs and locators:
Observation:
Interpretation / root cause:
Impact:
Change pressure: LOW/MEDIUM/HIGH
Architectural reach: LOCAL/COMPONENT/SYSTEM/MULTI-SYSTEM
Confidence: LOW/MEDIUM/HIGH
Recommendation:
Alternative and tradeoff:
Fitness function:
Verification:
Owner: if known
```

Use **P0** for a critical gate or immediate unacceptable systemic risk; **P1** for high-impact/high-pressure broad risk; **P2** for material but contained or moderate-pressure risk; **P3** for localized improvement; **P4** for optional/cosmetic work with weak economic value.

## Evidence language

Write “observed,” “inferred,” “assumed,” “unknown,” and “not applicable” deliberately. Never equate no evidence of a problem with evidence that no problem exists. Never present skill-authored weights or thresholds as standards-derived scientific truth.
