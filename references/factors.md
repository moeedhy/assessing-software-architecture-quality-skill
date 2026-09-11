# Architecture Factor Reference — 49 Factors

Use this as a concise interpretation guide. `weights.md` contains default weights.

## A. Understandability

### AQ-A01 — 1. Cognitive Load
**Meaning:** total context required to make a safe change.  
**Inspect:** concepts, repos, services, technologies, teams, hidden rules, dependency depth.  
**Healthy:** normal changes can be reasoned about locally.  
**Smell:** small changes require broad system knowledge.

### AQ-A02 — 2. Cognitive Complexity
**Meaning:** human reasoning difficulty caused by control flow.  
**Inspect:** nesting, branching, boolean complexity, recursion, interrupted flow.  
**Healthy:** important logic is readable and decisions are explicit.  
**Rule:** thresholds trigger review; they do not prove bad architecture.

### AQ-A03 — 3. Obscurity / Unknown Unknowns
**Meaning:** important effects/constraints are difficult to discover.  
**Inspect:** hidden side effects, globals, reflection, implicit conventions, undocumented coupling.  
**Healthy:** affected areas are discoverable before change.

### AQ-A04 — 4. Conceptual Clarity
**Meaning:** architecture expresses a coherent, limited vocabulary and model.  
**Inspect:** naming, abstraction count, overloaded terms, generic manager/helper/service concepts.  
**Healthy:** concepts have stable meaning within their boundary.

## B. Modularity & Dependencies

### AQ-B01 — 5. Cohesion
Responsibilities inside a module belong together and change for related business reasons.

### AQ-B02 — 6. LCOM
Diagnostic estimate of method/state cohesion. Record the variant. Never redesign solely from LCOM.

### AQ-B03 — 7. Coupling
Strength/breadth of dependencies. Inspect static, runtime, temporal, data, consistency, deployment, and organizational forms.

### AQ-B04 — 8. Afferent Coupling (Ca)
Incoming dependencies. High Ca means contracts deserve stability and compatibility care; it is not inherently bad.

### AQ-B05 — 9. Efferent Coupling (Ce)
Outgoing dependencies. High Ce may indicate excessive knowledge/responsibility.

### AQ-B06 — 10. Instability
`I = Ce / (Ca + Ce)`. Use with volatility and abstraction analysis. Stable != good; unstable != bad.

### AQ-B07 — 11. Dependency Cycles
Mutual dependencies. Prioritize large or cross-domain/team strongly connected components.

### AQ-B08 — 12. Dependency Direction
Dependencies should protect stable business policy from volatile implementation details where that isolation pays for itself.

### AQ-B09 — 13. Separation of Concerns
Separate unrelated reasons for change: domain policy, transport, persistence, presentation, security, integration, operations.

### AQ-B10 — 14. Information Hiding
A module should hide meaningful volatile decisions. Ask: what knowledge does this boundary prevent consumers from needing?

### AQ-B11 — 15. Encapsulation
State and invariants are controlled by the abstraction responsible for them; external callers do not reproduce validity rules.

### AQ-B12 — 16. API Surface Area
Public classes, methods, endpoints, events, schemas, configuration, permissions, and extension points create maintenance obligations. Keep exposure intentional.

## C. Changeability & Evolvability

### AQ-C01 — 17. Change Amplification
How widely a conceptual change propagates. Healthy architecture localizes business changes near the owning capability.

### AQ-C02 — 18. Change Coupling
Elements repeatedly modified together over time. Healthy co-change matches intended boundaries; unexpected distant co-change is a boundary hypothesis.

### AQ-C03 — 19. Volatility Alignment
Separate concerns that change at materially different rates or for different reasons.

### AQ-C04 — 20. Replaceability
Cost of changing technology/provider/implementation. Isolate volatile externals when realistic replacement/testability benefit exceeds abstraction cost.

### AQ-C05 — 21. Evolvability
Ability to accommodate unforeseen requirements incrementally without repeated architectural surgery.

### AQ-C06 — 22. Reversibility
Cost of undoing a decision. Keep uncertain decisions reversible until evidence justifies commitment.

### AQ-C07 — 23. Hotspot Risk
Frequently changing areas with structural weakness and high business importance deserve priority.

### AQ-C08 — 24. Technical Debt Pressure
Accumulated design compromises that materially increase future change/operational cost. Prioritize economically, not aesthetically.

### AQ-C09 — 25. Contract & Schema Evolution
Whether consumers can upgrade independently: interface/message versioning, backward and forward compatibility, deprecation policy, consumer-driven contract tests, and expand-contract data migration. Independent deployability is a claim about contract evolution, not about repository or service count. Ask whether a breaking change can reach a consumer without a compatible transition window.

## D. Distributed Coupling & Failure Containment

### AQ-D01 — 26. Temporal Coupling
Components must be simultaneously available or execute in strict sequence. Use sync/async according to business semantics, not ideology.

### AQ-D02 — 27. Data Coupling
Multiple components depend directly on the same representation/storage. Independently deployed services writing the same critical tables is a strong smell.

### AQ-D03 — 28. Consistency Coupling
Multiple components must synchronously agree for one operation. Strong consistency should follow real business invariants.

### AQ-D04 — 29. Coordination Cost
Human/system coordination required for a change: teams, approvals, repos, handoffs, synchronized releases.

### AQ-D05 — 30. Blast Radius
Users, tenants, regions, services, data, or capabilities affected by a failure/bad change. Healthy systems contain non-critical failures.

## E. Runtime Quality

### AQ-E01 — 31. Scalability
Ability to absorb relevant growth without disproportionate degradation/cost. Consider request, data, write/read, tenant, geographic, and organizational scale.

### AQ-E02 — 32. Performance Efficiency
Efficient resource use while meeting performance requirements. Optimize measured bottlenecks, including tail latency and cost/operation.

### AQ-E03 — 33. Availability
Required capability is usable when expected. Assess user-relevant SLIs/SLOs and hard dependency chains.

### AQ-E04 — 34. Resilience
Ability to withstand/recover from dependency and infrastructure failures. Inspect timeouts, bounded retries, jitter, circuit breaking, isolation, idempotency, degradation, failover.

### AQ-E05 — 35. Recovery Architecture
Ability to restore service/data after disruption. Inspect RTO/RPO, backup, restore verification, failover, and exercises.

## F. Engineering Capability

### AQ-F01 — 36. Testability
Important behavior can be verified deterministically with appropriate isolation and manageable setup/time.

### AQ-F02 — 37. Observability
Operators can explain novel runtime behavior using correlated traces, metrics, logs, and meaningful context.

### AQ-F03 — 38. Deployability
Changes can be released and recovered with acceptable independence, batch size, coordination, and risk.

### AQ-F04 — 39. Architecture Conformance
Actual implementation matches declared architectural boundaries/constraints. Trust implementation evidence over stale diagrams.

### AQ-F05 — 40. Architecture Fitness Functions
Machine-verifiable checks continuously protect important architectural characteristics where practical.

## G. Domain & Organization

### AQ-G01 — 41. Domain Alignment
Architecture boundaries align with meaningful business capabilities/models, enabling change locality and coherent ownership.

### AQ-G02 — 42. Ownership Clarity
Critical code, services, datasets, contracts, alerts, and operations have accountable owners.

### AQ-G03 — 43. Team Cognitive Load
A team owns a comprehensible domain and can deliver without excessive cross-team knowledge/coordination.

## H. Governance & Security

### AQ-H01 — 44. Architecture Risk
Likelihood and impact of architecture failing business objectives. Consider reach, detectability, reversibility, and recovery difficulty.

### AQ-H02 — 45. Attack Surface
Reachable capabilities available to attackers: entry points, privileged APIs, trust boundaries, identities, external integrations, secrets, data exposure.

### AQ-H03 — 46. Security Coupling
Extent to which compromise of one component/identity grants reach into others. Prefer least privilege, isolated credentials, and containment.

### AQ-H04 — 47. Continuous Architecture Governance
Architecture decisions remain visible, owned, reviewed, threat-modeled when relevant, and continuously enforced/updated rather than periodically rediscovered.

### AQ-H05 — 48. Supply Chain & Build Integrity
Trust in what actually reaches production: direct and transitive dependency risk, update latency for known-vulnerable dependencies, the build/release pipeline as a trust boundary, artifact provenance and signing, and who can inject code or configuration into a release. A compromised build path has system-wide blast radius regardless of application-level design.

### AQ-H06 — 49. Data Lifecycle & Privacy Architecture
Whether the architecture can satisfy the obligations attached to the data it holds: classification, retention, deletion and erasure propagation into derived stores and backups, residency, tenant isolation, and lineage. Ask whether a deletion or residency requirement is architecturally reachable, not merely documented in policy.
