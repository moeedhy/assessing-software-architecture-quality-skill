# Behavioral Evaluation Protocol

`tests/evals/cases.jsonl` is the canonical behavioral corpus. Deterministic unit tests validate package mechanics; behavioral evals validate whether an agent applies the skill correctly.

## Experimental design

For every candidate release:

1. Run each prompt in a fresh context without this skill (baseline/RED).
2. Run the same prompt, model, runtime, tools, and fixture with this skill enabled (GREEN).
3. Use a separate evaluator that has the prompt, response, pass/fail contract, and cited evidence—but not the candidate's hidden reasoning.
4. Repeat nondeterministic cases at least three times; randomize baseline/GREEN order.
5. Record model ID, runtime version, skill commit/package digest, tool availability, date, case ID, repetition, grader version, verdict, and rationale.
6. Store failures and counterexamples; improve the smallest instruction/resource that addresses the failure.

Do not fabricate a baseline, declare improvement from author self-review, or tune only to memorized wording. Add paraphrases and adversarial variants for any repaired case.

## Model/runtime matrix

At minimum, test the strongest generally available model and the lowest-cost model expected to use the skill successfully in each supported runtime. Re-run when a material model/runtime/tool change occurs. Capability claims are versioned observations, not permanent properties.

## Release gates

- 100% pass on critical cases.
- At least 90% pass overall across repetitions.
- No regression from the previous released package on any safety, authorization, gate, or false-precision case.
- Activation precision: routine style or isolated coding questions should not trigger a full architecture workflow.
- Activation recall: explicit architecture review/design/modernization/incident requests should trigger.
- Deterministic package/unit validation must pass.
- Independent evaluation evidence must exist before labeling the release behaviorally validated.

## Result record

```json
{
  "case_id": "E03",
  "condition": "GREEN",
  "model": "provider/model-version",
  "runtime": "runtime-version",
  "skill_digest": "sha256:...",
  "repetition": 1,
  "grader": "grader-version",
  "verdict": "PASS",
  "rationale": "Critical security gate overrides composite.",
  "evidence": ["response excerpt or artifact locator"]
}
```

This repository intentionally ships no claimed behavioral results until such a matrix is executed by an independent evaluator.
