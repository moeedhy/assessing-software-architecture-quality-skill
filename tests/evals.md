# Behavioral Evaluation Protocol

Status: **UNEXECUTED**. This package contains a corpus and an execution protocol, not observed behavioral results. Package validation and unit tests are deterministic checks; neither establishes agent quality or improvement over v2.1.

`tests/evals/cases.jsonl` is the canonical corpus. E01–E36 retain their IDs; E26 now names the 49-factor model. E37–E50 cover framework fit, justified custom guarantees, independent domains, unknown versions, irrelevant native features, proportional methods, unsupported compliance claims, checkpoint contradictions and scope, activation, and causal deduplication. Each case's prompt is its inline synthetic fixture. These facts are test data, not assertions about a real framework or repository.

## Cheap tier

Run this before spending a full matrix, and store transcripts outside the package so they do not change the digest. It does not satisfy the release gates below.

For E03, E13, E20, E27, and E36, run at least five fresh-context repetitions with the candidate skill and five with no skill. Read every output. A no-skill control that already avoids the failure means there is nothing for the skill to fix on that case. Variance across the five candidate reps means the wording is not binding yet.

Activation probes live in `tests/evals/triggers.json` (near misses included). They are not a substitute for observing real discovery: a harness that cannot isolate skill discovery must report the activation lane as unavailable.

## Freeze the experiment

1. Freeze the candidate package and record its digest using `scripts/package_digest.py`. Keep transcripts, result records and generated run artifacts **outside** the package: tests are distributable inputs, so putting run outputs in `tests/` changes the digest.
2. Freeze the v2.1 baseline from Git revision `566ec56` (confirm `git show 566ec56:SKILL.md` contains package/model version `2.1.0` and 49 factors). Resolve and record the full revision, never just a mutable branch name. Archive that revision into a distinct temporary directory. Run the candidate digest tool against that directory; the baseline need not contain the new tool.
3. Freeze the candidate corpus independently of the package variants. Use the **same candidate corpus**, including new cases, in all conditions. Record its SHA-256, each prompt's exact UTF-8 SHA-256, and hashes of any attached fixture files. The corpus prompt itself supplies the inline fixture; do not silently supply different repository files to each condition.
4. Define model IDs, tool/runtime versions, sampling settings, budgets, seeds when supported, grader identity/version, and execution date before generating responses. Use at least the most capable intended model and the least expensive intended supported model for each supported runtime. Do not claim support for combinations that were not run.
5. Pre-register at least three repetitions **for every case and condition**, even apparently deterministic cases. For the current 50 cases this is 450 subject responses per model/runtime pair. Randomize condition order within each case/repetition using a recorded seed. Freeze acceptance criteria before seeing responses.

Archive example (writes only new temporary directories, does not change the checkout):

```sh
baseline_dir=$(mktemp -d)
git rev-parse '566ec56^{commit}'
git show 566ec56:SKILL.md
git archive 566ec56 | tar -x -C "$baseline_dir"
python3 scripts/package_digest.py "$baseline_dir"
python3 scripts/package_digest.py .
```

## Three conditions, fresh context each time

| Condition | Subject instructions and package access |
| --- | --- |
| `NO_SKILL` | Neutral task instructions and fixture only; architecture skill absent from discovery and inaccessible through tools. |
| `BASELINE_V2_1` | Same neutral instructions and fixture; only the frozen v2.1 architecture skill is discoverable. |
| `CANDIDATE_V2_3` | Same neutral instructions and fixture; only the frozen v2.3 candidate is discoverable. |

For every subject response, create a fresh conversation and isolated workspace with no preceding conversation, memory, prior response, grading criteria, or other condition's package. Use the same discovery/loading mechanism, model, runtime, fixture, tools and budgets for baseline and candidate. Keep unrelated skills absent or identical. Do not force full architecture skill loading in activation cases: let the runtime's normal discovery and routing operate, and record actual activation. Loading the skill's instructions or emitting its architecture workflow counts as activation; merely exposing skill discovery metadata does not. If the runtime cannot isolate discovery or observe activation, report that lane as unavailable and do not claim activation validation.

Synthetic cases require reasoning from provided facts. Framework Q is fictitious; do not substitute undocumented claims about a real framework. If a run uses a real repository or live documentation, freeze exact snapshots and expose the same files and recorded tool responses to all conditions. Do not grant extra network access or extra tools to a candidate. Record refused or unavailable tools; a harness failure is `ERROR`, not a subject pass or an excluded inconvenient result. Fix the harness, preserve the failed record and rerun the affected matched triplet with a new run ID.

An execution adapter can be implemented in any capable evaluation environment. This repository does **not** ship or assume an external runner. Its adapter must implement this interface:

```text
for model_runtime in preregistered_matrix:
  for case in frozen_candidate_corpus:
    for repetition in [1, 2, 3]:
      for condition in seeded_permutation(three_conditions):
        session = fresh_isolated_session(model_runtime, condition_package)
        response, tool_trace, activation = session.run(case.prompt, fixed_fixture)
        save_subject_record_outside_package(response, tool_trace, activation)
blind_records = assign_random_ids_and_remove_condition_metadata(subject_records)
judgments = independent_grader.grade(blind_records, frozen_rubric, fixed_fixture)
join_conditions_only_after_all_judgments_are_frozen()
compute_gates_for_each_model_runtime_and_paired_condition_deltas()
```

## Independent, blind grading

Use an evaluator separate from the subject and skill author, with a fresh context for each response. The evaluator receives the exact prompt/fixture, case pass/fail rubric, response and relevant tool evidence, but no condition labels, package versions/digests, generation order, author preference, or hidden reasoning. Random IDs replace revealing artifact paths. Keep response text intact; subjects may reveal their own condition in prose, so report any loss of blinding instead of claiming perfect blindness. Grade each response individually before comparing conditions. A subject grading its own output or an author manually declaring success is not independent evidence.

For each case, pass requires the substantive `pass` contract and no behavior matching `fail`. Do not require specific wording, factor IDs or named methods if equivalent reasoning meets the contract, except where the case explicitly tests their meaning. Report activation separately from content. A disagreement about a critical verdict requires a second independent blinded reviewer; freeze both judgments and the adjudication rationale. Never hide a critical failure in an average. Retain all failed outputs and counterexamples; any repair starts a new candidate digest and a new evaluation run. Add frozen paraphrases/adversarial variants before rerunning, and keep original cases.

## Gates and comparison

For **each** candidate model/runtime combination across all registered repetitions:

- Critical case pass rate must be **100%**; overall case pass rate must be **at least 90%**. Pending or unresolved errors prevent completion, and missing records cannot reduce the denominator.
- No critical case/repetition that passes with `BASELINE_V2_1` may fail with `CANDIDATE_V2_3`. Report any baseline-to-candidate regression in safety, authorization, gates, evidence honesty and false precision explicitly.
- Require correct activation on all negative cases (E10, E25, E46) and on explicit architecture recall cases (including E49). Report false positives and false negatives over **all** cases using `activation_expected`. Report precision `TP/(TP+FP)` and recall `TP/(TP+FN)` as separate values, with undefined denominators reported as unknown. Corpus-based precision is not an estimate of real-world traffic prevalence.
- Report matched pass-rate deltas from `NO_SKILL` to baseline, `NO_SKILL` to candidate, and baseline to candidate, overall and by category, alongside raw counts and repetition variance. Passing thresholds alone is not evidence of improvement; do not claim improvement without measured comparative results.
- Deterministic package, schema and unit checks must pass independently. Until this matrix is executed and independently graded, the release remains **behaviorally unvalidated**, even if every deterministic check passes.

## Result contract

Store a run manifest and one record per case/condition/repetition outside the package, then a separately frozen blind judgment file and a joined results file. Never publish skill versions as the experiment condition inside grader inputs. The manifest must contain `run_id`, `status` (`UNEXECUTED`, `RUNNING`, `COMPLETED`, `INVALID`), timestamps, full baseline revision, condition/package digests (null for no skill), frozen corpus and fixture hashes, model/runtime/tool matrix, sampling/budget settings, repetition count, randomization seed, grader versions, blinding limitations, and registration/subject/judgment artifact locators. `COMPLETED` requires all registered records and independent judgments; it does not mean gates passed.

Each joined result must contain the fields below. This is an **illustrative schema instance, not a performed run or a PASS claim**. Replace placeholders only from recorded evidence. Before execution, timestamps, response/judgment locators and verdict remain null or `NOT_RUN`.

```json
{
  "record_schema_version": "1.0",
  "run_id": "EXAMPLE-NOT-EXECUTED",
  "status": "UNEXECUTED",
  "case_id": "E39",
  "condition": "CANDIDATE_V2_3",
  "critical": true,
  "model_id": "TO_BE_RECORDED",
  "runtime_id": "TO_BE_RECORDED",
  "tools_manifest_sha256": null,
  "sampling": {"temperature": null, "seed": null, "max_output_tokens": null},
  "package_digest": null,
  "corpus_sha256": null,
  "prompt_sha256": null,
  "fixture_sha256": null,
  "repetition": 1,
  "order_seed": null,
  "started_at": null,
  "response_locator": null,
  "tool_trace_locator": null,
  "activation_expected": true,
  "activation_observed": null,
  "blind_id": null,
  "grader_id": null,
  "grader_version": null,
  "blinding_compromised": null,
  "verdict": "NOT_RUN",
  "rationale": null,
  "evidence": [],
  "adjudication_locator": null
}
```

Allowed verdicts are `NOT_RUN`, `PASS`, `FAIL`, `ERROR`; only independently judged subject responses receive `PASS` or `FAIL`. In executed records, hash fields use `sha256:<64 lowercase hex digits>`, timestamps use UTC ISO 8601, tool traces/response artifacts must exist, and rationale must cite evidence locators or excerpts. For inline fixtures, `fixture_sha256` equals `prompt_sha256`. Keep grader identity and version required for judged records. The joined record's unique key is `(run_id, model_id, runtime_id, case_id, condition, repetition)`; retain a distinct attempt ID for harness retries. Include per-condition gate summaries, activation confusion matrices, paired deltas, critical regressions, missing/error counts and final independent review in the run report.
