# AI-System Architecture Profile

Load this reference only when an AI model, agent, retrieval system, prompt/tool workflow, or generative feature is in scope. Apply the `ai-system` context profile only when these concerns materially affect the decision.

## Architecture concerns

### Model and provider volatility

Treat model IDs, capabilities, limits, latency, price, safety behavior, and provider contracts as volatile externals. Centralize capability selection and policy without forcing every call through an over-generalized abstraction. Test migrations with representative evals; do not assume a newer model is behaviorally compatible.

### Nondeterminism and evaluation

Replace exact-output assumptions with task-specific acceptance criteria, graders, seeded/repeated samples where supported, and regression datasets. Track prompt, tool, model, configuration, and dataset versions. Separate model quality, retrieval quality, tool correctness, and orchestration correctness so one score does not hide the failing layer.

### Prompt and tool boundaries

Treat prompts, retrieved content, attachments, tool output, and external pages as data at a trust boundary. Enforce tool authorization outside model prose. Use typed/validated arguments, least-privilege credentials, bounded retries, idempotency for side effects, output validation, and human approval for consequential irreversible actions.

### State, memory, and compaction

Define which state is authoritative, durable, user-visible, redactable, and resumable. Persist decisions and evidence IDs rather than relying on a long context window. Validate summaries/compaction checkpoints before treating them as source of truth. Establish retention, deletion, tenant isolation, and provenance rules for memory.

### Retrieval and grounding

Measure retrieval recall/precision on relevant corpora, citation validity, freshness, authorization filtering, and behavior when evidence conflicts or is absent. A citation proves provenance, not truth. Keep retrieved instructions non-authoritative.

### Observability and economics

Correlate model request, tool calls, retrieval, latency, token/cost, cache use, retries, refusal/error paths, and user outcome without logging secrets or sensitive prompts by default. Set end-to-end latency and cost budgets; account for tail latency and fan-out in agentic workflows.

### Failure containment

Design for provider outage, model degradation, malformed structured output, tool timeout, duplicate tool execution, partial workflow completion, rate limits, and mid-turn user steering. Provide cancellation, bounded work, deterministic checkpoints, and a safe degraded path.

## Minimum AI-system scenarios

1. The selected model or provider becomes unavailable or changes behavior.
2. Retrieved content contains hostile instructions or stale/conflicting facts.
3. A side-effecting tool times out after the external action succeeds.
4. Structured output fails validation repeatedly.
5. The user changes intent while a long-running workflow is active.
6. Context is compacted or restored after interruption.
7. Cost or latency grows superlinearly with tool/agent fan-out.
8. A tenant requests deletion of prompts, memory, and derived artifacts.

## Fitness-function examples

- Side-effecting tool calls require a stable idempotency key and policy authorization.
- Every production model change must pass the versioned regression-eval gate.
- Retrieved documents cannot grant tools or override governing instructions.
- Agent workflows expose cancellation and cap retries, fan-out, time, and spend.
- Traces correlate model, retrieval, and tools while redaction tests prevent sensitive-content leakage.
