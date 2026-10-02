# Authoritative Sources and Provenance

Ledger updated: 2026-09-12. `sources.json` is the machine-readable provenance ledger; each entry's `last_verified` records its own verification date. This update does not reverify every older source.

The sources below ground terminology and operating guidance. The skill's 49-factor selection, weights, multipliers, thresholds, profiles, and score bands are authored heuristics, not claims from these sources. The framework-use lens and method crosswalks are also authored guidance: they add no factors or scores and do not establish standards compliance or certification.

## Skill and agent engineering

- Agent Skills Specification — https://agentskills.io/specification
- OpenAI, Build Skills — https://learn.chatgpt.com/docs/build-skills
- OpenAI, Latest Model guide — https://developers.openai.com/api/docs/guides/latest-model
- OpenAI, Evaluation best practices — https://platform.openai.com/docs/guides/evaluation-best-practices
- Anthropic, Equipping agents with Agent Skills — https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic, Building effective agents — https://www.anthropic.com/engineering/building-effective-agents

## Architecture and software quality

- ISO/IEC 25010:2023 Product Quality Model — https://www.iso.org/standard/78176.html
- SonarSource, Cognitive Complexity — https://www.sonarsource.com/resources/cognitive-complexity/
- DORA software delivery performance metrics — https://dora.dev/guides/dora-metrics/
- OpenTelemetry Signals — https://opentelemetry.io/docs/concepts/signals/
- AWS Well-Architected Reliability, fault isolation — https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/use-fault-isolation-to-protect-your-workload.html
- Microsoft Azure Architecture Center, microservices — https://learn.microsoft.com/en-us/azure/architecture/microservices/
- OWASP Threat Modeling — https://owasp.org/www-community/Threat_Modeling
- NIST SP 800-218 Rev.1 Initial Public Draft, SSDF 1.2 — https://csrc.nist.gov/pubs/sp/800/218/r1/ipd
- SLSA, Supply-chain Levels for Software Artifacts — https://slsa.dev/spec/

## Recency policy

Re-check volatile sources before making “current/latest” claims. The earlier 2026-09-07 review recorded DORA's five delivery metrics, OpenTelemetry profiles as Alpha, NIST SSDF 1.2 Rev.1 as an Initial Public Draft, and SLSA v1.2 as current with v1.0 retired. These are dated observations, not newly verified claims. Do not silently promote draft or alpha material to stable guidance.

On 2026-09-12, ISO's public page again showed ISO/IEC 25010:2023, edition 2, as published; its public abstract supports scope and edition, not a complete clause-level crosswalk. AWS fault-isolation guidance was also reopened. Other existing entries retain their prior verification dates.

## Conditional assessment methods

- [SEI, ATAM: Method for Architecture Evaluation](https://www.sei.cmu.edu/library/atam-method-for-architecture-evaluation/) — CMU/SEI-2000-TR-004 (2000). The skill uses a lightweight ATAM-inspired adaptation, not the complete formal method.
- [C4 model, Diagrams](https://c4model.com/diagrams) and [Container abstraction](https://c4model.com/abstractions/container) — living official guidance retrieved 2026-09-12; only decision-relevant views are selected.
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) — page publication date 2024-11-06, retrieved 2026-09-12. This is AWS-specific guidance; the [fault-isolation example](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/use-fault-isolation-to-protect-your-workload.html) uses REL10. Other providers require their own sources.

## NestJS profile

These official sources were retrieved on 2026-09-12. The migration guide describes v11 to v12, and the profile references current v12-era documentation. Resolve actual repository and integration-package versions before applying it; documentation on a moving URL or default branch is not a pinned API contract.

- [Migration guide](https://docs.nestjs.com/migration-guide)
- [Custom providers](https://docs.nestjs.com/fundamentals/custom-providers) and [modules](https://docs.nestjs.com/modules)
- [Lifecycle events](https://docs.nestjs.com/fundamentals/lifecycle-events)
- [Injection scopes](https://docs.nestjs.com/fundamentals/injection-scopes)
- [Request lifecycle](https://docs.nestjs.com/faq/request-lifecycle)
- [Circular dependency](https://docs.nestjs.com/fundamentals/circular-dependency)
- [Testing, official documentation source](https://raw.githubusercontent.com/nestjs/docs.nestjs.com/master/content/fundamentals/unit-testing.md)
- [Configuration, official documentation source](https://raw.githubusercontent.com/nestjs/docs.nestjs.com/master/content/techniques/configuration.md)

The testing and configuration rendered pages failed retrieval; their official documentation source files were successfully read instead. New ledger entries record `applicable_version`; source verification means the page was inspected, not that every API was executed or compatibility with a target project was proven.
