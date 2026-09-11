# Worked Example — Checkout Architecture Hotspot

## Scenario

An existing commerce application has:

- checkout logic in one service,
- pricing rules duplicated in checkout, invoice, and promotion handlers,
- 42 pricing-related commits in the last quarter,
- representative pricing changes touching 18 files across 5 modules,
- weekly regressions in promotion behavior,
- core pricing tests requiring database + queue infrastructure,
- p99 checkout latency is acceptable,
- no critical security or recovery issue found in the assessed scope.

## Correct reasoning shape

**Route:** REVIEW + STANDARD  
**Score:** not requested

### Evidence ledger excerpt

| ID | Kind | Locator | Supports |
|---|---|---|---|
| EV-GIT-001 | MEASUREMENT | pricing-related commits, previous quarter | AQ-C02, AQ-C07 |
| EV-CHANGE-001 | MEASUREMENT | representative promotion work item diff | AQ-C01, AQ-G01 |
| EV-CODE-001 | OBSERVATION | checkout, invoice, and promotion handlers | AQ-B01, AQ-G01 |
| EV-TEST-001 | OBSERVATION | pricing test setup | AQ-F01, AQ-A01 |
| EV-RUNTIME-001 | MEASUREMENT | checkout latency dashboard, previous quarter | AQ-E02 |

The locators above identify evidence classes for the example. A real report must provide repository paths/lines, commit or work-item ranges, and dashboard IDs/time windows.

### Executive decision

The highest architecture risk is not runtime performance; it is poor locality of change around pricing policy. Pricing is an active hotspot with high Change Amplification, repeated Change Coupling, low cohesion of responsibility, and weak testability. The recommended first move is to create one explicit pricing-policy boundary inside the existing deployment unit, not split a new microservice. Runtime architecture should remain unchanged until the localized boundary demonstrates value and an independent deployment/scaling need emerges.

### Finding F-001 — Pricing policy is distributed

**Priority:** P1  
**Factor IDs:** AQ-C01, AQ-C02, AQ-B01, AQ-G01, AQ-F01, AQ-A01  
**Evidence IDs:** EV-GIT-001, EV-CHANGE-001, EV-CODE-001, EV-TEST-001  
**Interpretation:** one business policy has multiple implementation owners and cannot be changed locally.  
**Root cause:** pricing is represented as cross-cutting technical logic instead of an owned domain policy boundary.  
**Impact:** regression risk, larger review surface, slower changes, harder testing.  
**Change pressure:** HIGH  
**Reach:** COMPONENT  
**Confidence:** HIGH

**Critical gates:** no failure is demonstrated by this example; security and recovery remain UNKNOWN outside the assessed scope. No composite is calculated.

**Recommendation:** Introduce an internal `PricingPolicy`/pricing module owning pricing decisions and move callers toward that boundary incrementally. Keep it in the current process/deployment unit.

**Alternative:** Extract a pricing service now.

**Why not yet:** a service adds network availability, deployment, observability, contract, and data/consistency concerns without current evidence of independent scaling/deployment/team ownership need.

**Fitness functions:** prevent pricing-rule implementations outside the pricing boundary; keep pricing domain tests infrastructure-free where possible.

**Verification:** next representative pricing change should touch fewer modules; pricing rule tests should run without queue/database infrastructure; regression rate and change-coupling trend should improve over subsequent changes.

## What this example demonstrates

The skill should not optimize the highest raw metric or recommend the most fashionable architecture. It should combine structural evidence with change history, identify a root cause, choose the smallest effective boundary improvement, expose unknown gates, and define how later evidence will prove or disprove the recommendation.
