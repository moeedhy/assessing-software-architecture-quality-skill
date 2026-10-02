# Assessment Modes and Depth

Intent answers **why the skill is being used**. Depth answers **how much evidence and output are justified**. Select both explicitly; do not treat them as synonyms.

## Intent modes

| Mode | Decision being supported | Evidence emphasis | Key boundary |
|---|---|---|---|
| DESIGN | Choose or test a proposed architecture | requirements, scenarios, prototypes, constraints, ADRs | operational behavior is unknown until observed |
| REVIEW | Assess an existing system | source, data, tests, delivery, runtime, incidents, ownership | read-only unless implementation is requested |
| CHANGE | Make a bounded architectural change | acceptance contract, affected paths, before/after behavior | do not expand scope opportunistically |
| MODERNIZATION | Evolve legacy structure or platform | change pressure, seams, migration risk, compatibility, reversibility | prefer staged migration over rewrite by default |
| INCIDENT | Explain and contain an architecture-related failure | timeline, telemetry, state transitions, recovery, blast radius | immediate containment and evidence preservation lead |

## Depth modes

### TRIAGE

Use for a single decision, urgent incident question, or a narrow architectural risk. Inspect the critical gates and only factors capable of changing the decision. Output the decision, decisive evidence, unknowns, next check, and immediate action. Do not calculate a composite.

### STANDARD

Default for architecture reviews and design choices. Map the relevant boundaries, corroborate material findings, compare real alternatives, and provide phased recommendations plus fitness functions. Assess only relevant factors; do not calculate a composite.

### DEEP

Use when the user explicitly asks for a full assessment, benchmark, due-diligence packet, or numerical score. Record all 49 factors as ASSESSED, UNKNOWN, or NOT_APPLICABLE; assess every applicable critical gate; calculate coverage; and use the deterministic scoring contract if a score was requested.

## Escalation rules

- A critical-gate signal deepens that risk lane immediately, regardless of chosen depth.
- Conflicting evidence requires corroboration or an explicit unresolved contradiction.
- Broad scope alone does not require DEEP; decision consequence and requested assurance do.
- A score request implies DEEP, but DEEP does not imply a score.
- Missing evidence produces a partial assessment, not invented facts or automatic task expansion.

## Selection examples

Worked routes are listed in `SKILL.md`, which is already loaded when this file is read. Do not invent a third intent or a fourth depth.
