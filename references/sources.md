# Authoritative Sources and Provenance

Last reviewed: 2026-09-07. `sources.json` is the machine-readable provenance ledger.

The sources below ground terminology and operating guidance. The skill's 49-factor selection, weights, multipliers, thresholds, profiles, and score bands are authored heuristics, not claims from these sources.

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

Re-check volatile sources before making “current/latest” claims. As reviewed on 2026-09-07, ISO/IEC 25010:2023 is the published edition shown by ISO, DORA documents five delivery metrics, OpenTelemetry lists profiles as an Alpha signal, NIST SSDF 1.2 Rev.1 is still an Initial Public Draft, and SLSA v1.2 is current with v1.0 retired. Do not silently promote draft or alpha material to stable guidance.
