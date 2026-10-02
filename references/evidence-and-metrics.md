# Evidence and Metric Rules

Metrics generate questions; they do not automatically generate architecture conclusions. Follow `evidence-contract.md` and attach measurements to stable factor IDs from `factors.md`.

## Metric classes

### M1 — Direct or formal metrics

Examples: Cognitive Complexity, a specified LCOM variant, Ca, Ce, Instability, cycle count. Calculate only when definitions and inputs are known. Record the tool, version, scope, and variant.

### M2 — Operational metrics

Examples: availability, p95/p99 latency, throughput, error rate, RTO/RPO, delivery metrics, AI request latency/cost. Record population, source, units, aggregation, and time window. Prefer user-relevant service-level signals to component vanity metrics.

### M3 — Historical or behavioral metrics

Examples: change coupling, hotspots, churn, change amplification, contributors. Filter generated/vendor files and mechanical commits. Use feature/work-item scope when possible; implementation-plus-test co-change is not automatically harmful.

### M4 — Composite architecture indicators

Examples: Cognitive Load, Blast Radius, Replaceability, Coordination Cost, Volatility Alignment. No universal formula exists. Use structured evidence or an organization-defined metric; do not invent arbitrary precision.

### M5 — Qualitative architecture judgment

Examples: Domain Alignment, Conceptual Clarity, Information Hiding. State observations, interpretation, competing explanations, and confidence.

## Interpretation rules

### Complexity and cohesion

- Cognitive Complexity is a review trigger, not an architecture verdict.
- System Cognitive Load includes concepts, services, repositories, technologies, teams, setup, dependency depth, and implicit rules.
- Record the LCOM variant. Test the hypothesis of unrelated responsibility clusters using semantics and change history before splitting.

### Coupling and boundaries

Assess static, runtime-availability, temporal, data/schema, consistency, deployment, and organizational coupling separately. Low imports do not prove loose coupling. For Ca/Ce, define component scope and use `I = Ce / (Ca + Ce)`; stable does not mean good.

For dependency cycles, record the nodes, largest strongly connected component, and whether cycles cross business, deployment, or team boundaries. A local implementation cycle is not equivalent to a cross-context cycle.

### Change and hotspots

Change Amplification counts the files, modules, repositories, services, schemas, deployment units, and teams touched by a representative conceptual change. Hotspot priority combines active change, structural weakness, and business importance. Gate-level risks remain urgent even in low-churn code.

### Runtime and delivery

- Availability: inspect end-to-end hard dependency chains and user SLIs/SLOs.
- Performance: use distributions and tails; require measure → hypothesis → experiment → re-measure.
- Resilience: test timeouts, bounded retries, jitter, idempotency, isolation, degradation, and failover under realistic faults.
- Recovery: backups alone are insufficient; verify restore, RTO/RPO, ordering, and exercises.
- Observability: operators should explain what failed, where, for whom, why, in which version, and along which path.
- Delivery metrics: assess a service/application delivery system and trends, never individual developer productivity.
- Cost: record cost per request, tenant, or workflow when it could change the choice. Meeting an SLO only at an unsustainable unit cost is not yet acceptable.

### Testability and AI evaluation

Coverage alone is insufficient. Inspect determinism, isolation, duration, flaky behavior, critical-path scenarios, and contract/integration boundaries. For AI systems, separate model, retrieval, tool, orchestration, safety, latency, and cost evaluations; record model/prompt/tool/dataset versions and repeated-run variance.

### Contracts and supply chain

Independent deployability is a property of contract evolution, not of repository count: check for a published compatibility policy, a deprecation window longer than consumer upgrade latency, and contract tests that fail on a breaking change. For the supply chain, prefer evidence about the build path itself — who can write to it, whether artifacts are signed, whether provenance is verified at deploy — over a dependency-scanner count alone.

### Data lifecycle

Test the obligation, not the policy document. Trace one deletion or residency requirement through derived stores, caches, search indexes, analytics copies, and backups, and record where it stops.

### Security

Use threat and reachability evidence. Never average a demonstrated critical reachable vulnerability, authorization bypass, data-integrity failure, or mandatory-control failure into a favorable maintainability score.

## Anti-double-counting

The canonical model marks factors as primary, supporting, or diagnostic and assigns overlap groups. When several signals describe one causal mechanism, report one root-cause finding with supporting factor IDs. Do not create several remediation programs merely to mirror several metrics.
