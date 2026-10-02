# Conditional assessment methods

Use a method only when it supplies missing decision evidence. These lenses feed the existing evidence ledger, findings, factors, gates, and options; they add no score or weights and do not require an all-method audit. A focused review can use none. Record the selected method, why it helps, its source edition, and its limitations.

Structured checkpoints can list the selected method IDs in `review_context.methods`: `ATAM_INSPIRED`, `ISO_25010_2023`, `C4`, and `WELL_ARCHITECTED`. Choosing a method neither unlocks scoring nor satisfies an evidence gate by itself.

| Decision need | Select | Minimum useful output |
|---|---|---|
| Conflicting quality priorities or uncertain architectural options | ATAM-inspired scenario and tradeoff analysis | One decisive scenario, options, sensitivities, risks, and verification |
| Check whether quality requirements omit a material concern | ISO/IEC 25010:2023-informed coverage check | Partial crosswalk and explicit gaps |
| Unclear system/runtime/ownership boundary | Selective C4 views | The view that answers the boundary question, tied to evidence |
| Cloud deployment or operational design risk | The actual provider's Well-Architected guidance | Relevant provider questions, evidence, gaps, and smallest remedy |

## ATAM-inspired scenarios and tradeoffs

SEI's ATAM analyzes architecture decisions against quality attributes and their tradeoffs. This skill uses a lightweight authored adaptation, not a claim that a full ATAM evaluation or stakeholder workshop occurred. [SEI report, CMU/SEI-2000-TR-004](https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/).

Choose a critical scenario and state: stimulus source, stimulus, environment, affected artifact, expected response, and measurable response condition. Mark assumed thresholds; do not invent stakeholder priorities or observed results. Compare at least two viable options, including keeping the current design when credible. Identify a sensitivity point where changing one decision materially changes a quality outcome, and a tradeoff point where it affects competing outcomes. Record risk, uncertainty, and the evidence that could change the choice.

Illustrative scenario: a payment provider times out during peak load after accepting a request; the workflow must recover without an unintended duplicate payment and within the agreed recovery objective. Compare bounded synchronous waiting with durable asynchronous reconciliation. Retry duration is a sensitivity; waiting longer trades response latency against fewer immediate reconciliations. Inspect durable intent, provider keys, timeout traces, and crash/retry tests. This is authored scenario analysis feeding AQ-D01/E04/E05, not evidence of production performance.

## ISO/IEC 25010:2023-informed coverage

ISO identifies the 2023 edition as a product quality model with nine characteristics. This skill's architecture factors are a different authored model. The following is a partial crosswalk for eliciting questions, not an ISO mapping endorsed by ISO, a complete evaluation, compliance, or certification. The public abstract supports edition and scope; detailed standard requirements require the actual standard. [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html).

| Selected quality concern | Related AQ factors | Coverage limit to expose |
|---|---|---|
| Functional suitability | AQ-B11, AQ-G01 | Architecture alignment does not prove product completeness or correct outcomes |
| Performance efficiency | AQ-E01, AQ-E02 | Requires representative load and resource evidence |
| Compatibility | AQ-C09, AQ-D02 | Contract evolution does not exhaust interoperability and coexistence |
| Reliability | AQ-E03, AQ-E04, AQ-E05 | Declared recovery design does not prove operational reliability |
| Security | AQ-H02, AQ-H03, AQ-H05, AQ-H06 | Architecture evidence does not replace security evaluation |
| Maintainability | AQ-A01, AQ-B01, AQ-C01, AQ-F01 | Structural evidence alone does not prove real change effort |

Explicit gaps include user interaction, accessibility, safety-specific assurance, and product-level adaptability/installation concerns beyond the inspected architecture. Name relevant missing evidence and owners; the safety/compliance gate remains applicable where required. Do not substitute the 2011 edition silently or imply that unlisted characteristics are unimportant. No AQ score should be relabeled an ISO score.

## Selective C4 views

The C4 model offers context, container, component, and code views plus supporting dynamic and deployment views; its guidance explicitly allows choosing only useful views. [C4 diagrams](https://c4model.com/diagrams).

Use context for users, external systems, and scope; container for applications, stores, and communication; component for an internal responsibility/cycle question; dynamic for a critical runtime interaction; deployment for placement and failure boundaries. A [C4 container](https://c4model.com/abstractions/container) is an application or data store abstraction, not necessarily an operating-system container. Do not generate all views or equate a directory tree with deployed architecture. Label observed versus intended elements, relevant protocols, data owners, and trust/failure boundaries; resolve contradictions against source/runtime evidence. Omit code-level views unless the decision needs them.

## Provider-specific Well-Architected review

First establish provider, actual services, deployment topology, workload requirements, and available operational evidence. Select that provider's current official framework and only relevant pillars/questions. AWS is the initial worked example here; do not treat its question IDs, service assumptions, or prescriptions as Azure/GCP guidance. For another provider, obtain its sources or mark the provider-specific lane UNKNOWN. Shared principles can still inform existing factors if labeled as general reasoning.

AWS describes its framework as guidance for architectural decisions on AWS, including operational and quality tradeoffs, rather than an audit mechanism. [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html).

**Illustrative AWS example.** A required workload must survive loss of one Availability Zone. Relevant reliability guidance is REL10 fault isolation, especially deployment across locations and bulkheads. [AWS fault isolation](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/use-fault-isolation-to-protect-your-workload.html). Inspect deployment configuration, application and data placement, shared dependencies, routing, spare capacity, and a failure exercise against the agreed recovery objective. A “multi-AZ” diagram alone is insufficient. If an application runs across zones but an indispensable dependency has no demonstrated recovery path, record that gap under AQ-D05/E03/E05; compare dependency recovery or placement changes with their cost and operational burden. Do not prescribe multi-region deployment without a requirement it uniquely satisfies. If cloud runtime is outside scope, omit this lens.
