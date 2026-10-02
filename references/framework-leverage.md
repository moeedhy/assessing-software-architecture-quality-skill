# Framework-use lens

Use this unscored lens when framework integration materially affects the decision. It asks whether the project uses its framework effectively for its actual requirements. It is not a feature-adoption checklist or a 50th factor. Unused framework capabilities are not defects, and custom code is not inherently duplication.

## Establish applicability

1. Detect the framework and resolved version from manifests, lockfiles, installed packages when available, and bootstrap code. Record conflicts; a version range alone does not establish the running version.
2. Identify each relevant host: HTTP, messaging, scheduled worker, CLI, serverless function, or multiple application contexts. Trace which capabilities are actually registered and invoked in that host.
3. State the concrete requirement, quality constraint, and current behavior. Read local architectural constraints before assuming framework independence, one composition root, or one dependency-injection container is required.
4. Check version-matched official documentation or implementation for the capability being compared. Record source version, verification date, and limitations. If unavailable, record UNKNOWN; do not recommend APIs from an unverified newer release.

For NestJS, continue with the [NestJS profile](nestjs.md). For other frameworks, apply the same comparison and obtain their official sources only for relevant capabilities.

## Compare semantics before recommending replacement

Consider the current implementation, a native capability, a supported extension point, and retained custom behavior where viable. A short record is enough:

| Field | Required reasoning |
|---|---|
| Requirement | Observable behavior and acceptance condition; applicable hosts and version |
| Evidence | Current registration, callers, configuration, runtime or test evidence, and source references |
| Alternatives | How current/native/extension/custom options meet or fail the requirement; mark nonviable options and why |
| Semantic differences | Lifecycle, scope, error behavior, transactions, concurrency, idempotency, authorization, recovery, and host support as relevant |
| Consequence | Change cost, hidden coupling, operating cost, or lost guarantees; map to existing AQ factor IDs |
| Recommendation | Keep, simplify, reconfigure, wrap, or replace; smallest change, migration risk, and before/after proof |

A similar name or smaller line count does not establish equivalence. In particular, a transport interceptor does not by itself establish durable idempotency or atomic persistence; a scheduler does not by itself establish a durable job claim. Verify the specific extension's guarantees instead of assuming either presence or absence.

In a structured assessment, attach `framework_assessment` to the relevant `review_context.findings[]` entry: framework, version (or null), requirement, capability, capability evidence IDs, fit/gap, classification, and migration cost. Keep factor IDs, recommendation, verification, and the finding's evidence links on the finding. Reuse source-backed evidence records; a URL alone does not prove runtime activation.

## Classify the observation

- **EFFECTIVE_USE**: the implementation uses an appropriate framework capability with evidence that its semantics fit. Keep it; do not manufacture a finding.
- **AVOIDABLE_DUPLICATION**: bespoke plumbing reproduces a supported capability's required semantics, and replacing it has an evidenced net benefit. State equivalence and migration proof.
- **MISUSE**: registration, lifetime, ordering, or another framework assumption violates a required behavior. Identify the actual failure path, not just an unconventional pattern.
- **JUSTIFIED_CUSTOMIZATION**: custom behavior or a wrapper protects a requirement the viable native alternative does not satisfy, or has lower total cost under the constraints. State what it adds and why it remains necessary.
- **UNKNOWN**: version, runtime activation, equivalence, or required behavior is not established. Name the evidence that would resolve it.

Use one causal finding even when several factors are affected: unnecessary registries can affect AQ-A01/AQ-A03/C01/F01; broad exports or cycles AQ-B07/B08/B12; worker lifetime defects AQ-E03/E04/E05; unsafe authorization AQ-H02/H03. The finding participates only through the existing factor assessments and gates. Do not add framework scores, bonuses for feature count, penalties for unused features, or duplicate weights.

## Stop condition

Stop after the framework question can change or support the scoped recommendation. A focused lifecycle review does not require inspecting every pipe, guard, or optional package. Record source uncertainty explicitly and preserve REVIEW's read-only boundary.
