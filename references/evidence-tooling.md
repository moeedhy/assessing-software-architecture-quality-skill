# Evidence tooling

Use this menu when a decision needs a measurement. Commands are starting points, not verdicts. Record the tool, version, scope, and time window on the evidence record. Do not install a tool unless the decision value justifies the cost and authorization allows it. If a command cannot be run, mark the factor UNKNOWN.

Interpretation rules stay in [evidence and metrics](evidence-and-metrics.md). The composite is never computed from these commands. From the skill root, use `python3 scripts/architecture_quality.py score`.

## History and hotspots

From the repository root, after confirming the history window with the user or the decision frame:

```sh
git log --since="6 months ago" --name-only --pretty=format: | sed '/^$/d' | sort | uniq -c | sort -nr | head -40
```

That ranks paths by commit touches. It is a hotspot candidate list, not architecture health. Exclude generated and vendored paths before interpreting it.

Co-change for one path, useful for AQ-C02:

```sh
git log --since="6 months ago" --name-only --pretty=format: -- path/to/module | sed '/^$/d' | sort | uniq -c | sort -nr | head -20
```

Change amplification for one work item is the set of paths in that change, grouped by module, schema, deployable, and owning team. Prefer `git show --stat <range>` or the work-item diff over repository-wide churn.

Filter mechanical commits (formatting, lockfile-only, generated code) before treating co-change as a boundary smell. Implementation-plus-test co-change is expected.

## Static structure

Pick the tool that matches the language actually in the repository. A missing tool is UNKNOWN, not a zero.

| Need | Examples to prefer when already present |
|---|---|
| Import cycles and dependency direction | dependency-cruiser, madge, import-linter, go-arch-lint, ArchUnit, Nx or eslint boundaries, cargo-depgraph |
| Package or project boundaries | the build tool's own project graph, not a hand-drawn folder tree |
| Declared versus enforced rules | architecture fitness tests already in the suite; agent instruction files are claims until a check fails on violation |

Read the rule files the repository already uses (for example `AGENTS.md`, `CLAUDE.md`, `.cursor/rules`, ArchUnit tests, import-linter contracts) as evidence of intended boundaries. Compare them with the graph. A prose rule that generated code ignores is a conformance gap, not compliance.

## Runtime, delivery, and cost

Prefer the system's existing telemetry over a new agent. Record population, units, aggregation, and time window.

- Latency and errors: service-level distributions and tails, not a single host average.
- Recovery: restore or failover exercise results, including RTO/RPO actually observed.
- Delivery: lead time, deployment frequency, change-failure rate, and recovery time for the application, never per-developer productivity.
- Cost: cost per request, tenant, or workflow when it could change the choice. An SLO met only at an unsustainable unit cost is a tradeoff to report.

## Contracts, supply chain, data lifecycle

- Contracts: published compatibility policy, deprecation window, and a consumer-driven contract test that fails on a breaking change. Repository count is not this measurement.
- Supply chain: who can write to the build and release path, whether artifacts are signed, and whether deploy verifies provenance. A vulnerability-scanner count is supporting evidence, not the gate.
- Data lifecycle: trace one deletion or residency requirement through derived stores, caches, search indexes, analytics copies, and backups, and record the step where it stops.

## Stop

Stop when the measurement can support or change the scoped recommendation. Do not inventory every metric the tools can emit.
