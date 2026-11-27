# Experience Reuse casebook

Four development cases below are factual observations from the work that produced this skill, including a catalog-path reuse trial and a two-session discovery-to-reuse chain. Local usernames, project names, absolute machine paths, and private transcripts are omitted. The other cases illustrate practical use; they are not customer results or claims of measured savings.

## 1. An explicit path was available, but the assistant guessed another

**Status: observed execution omission.**

The supplied skill catalog located `ai-capability-amplifier` in the project's `.codex/skills` directory. The assistant first tried a user-level skills path, got a file-not-found error, and later read the correct project-local file.

```text
Available before acting:
  <project>/.codex/skills/ai-capability-amplifier/SKILL.md

Initially attempted:
  <codex-user-skills>/ai-capability-amplifier/SKILL.md

Result:
  File not found; another lookup was needed.
```

The failure occurred before the read: the assistant did not use the path already supplied. There was no need to recover a forgotten fact first. Another memory plugin alone would not necessarily have prevented the mistake.

**Expected intervention:** consult the task's exact catalog entry, resolve its stated root, and read that file. Fall back to a scoped search only if the supplied path is actually unavailable. A particular skill's project-local location does not imply that every skill is project-local.

**What could be recorded:** a concise operational lesson, such as "resolve the current catalog entry before guessing a conventional skill path," plus a pointer to the original task's evidence. Do not store machine-specific usernames as a universal recipe or copy the full conversation.

**Verification:** a fresh task with a supplied catalog should use the given path on its first read. If the same wrong read occurs, classify it as execution failure even if the lesson was retrieved.

**Follow-up:** the next case documents one successful fresh-session application after the routing repair. The original omission by itself did not prove prevention, and one later success does not establish a general reliability rate.

## 2. Fresh-session automatic reuse after trigger repair

**Status: observed automatic application in one fresh Codex CLI session, 2026-11-27.**

The reusable lesson from case 1 was: **resolve the current task's exact catalog before guessing a conventional skill location**. It was promoted into a persistent conditional routing rule, a short skill preflight, and a generic read-only catalog adapter. The target skill's particular location was not hardcoded into the adapter.

### Request and setup

The same read-only request was reused: revisit earlier `ai-capability-amplifier` work, read its `SKILL.md`, and summarize its purpose, use cases, and verification requirements in three short Chinese points. The request prohibited production work, file modifications, network access, and other agents. It supplied:

```text
r0 = <project>/.codex/skills
r1 = <codex-user-skills>
ai-capability-amplifier: file: r0/ai-capability-amplifier/SKILL.md
```

The actual task prompt did not name Experience Reuse or invoke `$experience-reuse`. The installed skill metadata and persistent AGENTS routing were available normally. A fresh CLI session used the existing ChatGPT subscription; no API billing, hooks, native-memory setting changes, or additional agents were introduced. Native memory remained enabled with the same supplied summary as the earlier enabled trial.

### What failed before the repair

In the earlier fresh-session trial, the catalog already led to the correct target path, but the agent did not load Experience Reuse. Correct output alone therefore did not establish automatic skill application. The observed gap was between discovery/routing and loading the preflight; the test does not establish the model's internal reason for skipping it.

The repair made repeated-work cues and named operations explicit in the discovery description and AGENTS anchor, included read-only summaries, and clarified that excluding target production work does not exclude the preflight. A compact entry routes exact catalogs to `read_skill.py`; advanced record management stays in a separate reference.

### What the fresh session actually did

1. Loaded the installed Experience Reuse `SKILL.md` before the target read.
2. Performed the host-required native-memory quick pass; it returned no matching entry.
3. Called `read_skill.py` with the supplied `r0` and `r1` mappings and the exact `r0/.../SKILL.md` reference.
4. Received `ok: true`, the real project-local path, the target's actual full content, and `fallback_attempted: false`.
5. Returned the requested three-point summary without running the target production workflow.

The offline audit checked actual tool events and compared the returned body with the target file. It did not infer adoption from the final answer or the assistant's claim that it had used a skill.

| Acceptance check | Observed result |
| --- | --- |
| Task prompt does not name the experience skill | Passed |
| Fresh session loads the preflight before the target | Passed |
| Catalog adapter actually runs | Passed |
| First target read uses the supplied project root | Passed |
| Returned body equals the real target file | Passed |
| A guessed user-level fallback is attempted | No |

This is the useful result: **the operational lesson affected the next action without an explicit skill invocation in the request**. No experience-index entry was needed because the current catalog was already authoritative. The lesson was reused through the maintained routing/instruction/tool layers, rather than copied into another memory database.

### Evidence, reproducibility, and limits

The [sanitized validation summary](../examples/fresh-session-validation.json) records the observed checks and secondary usage metrics. Raw transcripts, native-memory content, usernames, and machine-specific paths remain private; this is a maintainer-audited case, not a public independent reproduction of those logs.

The package includes seven portable catalog-reader tests alongside the existing 17 index tests. They exercise root selection even when a user-level copy exists, no fallback on a missing project target, alias/path rejection, actual returned content, and no writes. These tests validate deterministic behavior; they do not simulate automatic model selection.

Only one post-repair fresh CLI trial was run for this catalog-path case. It establishes neither a reliability percentage nor Desktop new-chat behavior, all-host coverage, or elimination of repeated errors. The earlier enabled trial also read the target correctly, so this comparison demonstrates newly observed preflight adoption, not a measured reduction in wrong-path reads. The public instructions are an English adaptation of the tested local instructions; a later clarification explicitly defers to higher-priority host memory quick passes. No extra model trial was run for that documentation clarification or translation. The generic catalog adapter is the same implementation used in the trial.

Experience reuse is the acceptance goal. Token use is a secondary diagnostic: the earlier enabled-but-unloaded trial used 64,999 total tokens across two model calls; the post-repair trial used 99,086 across three. This case provides **no token-saving claim**. Costs exclude preparation/audit work in the parent conversation and are not an API charge calculation.

## 3. A new lesson saved automatically, then reused in a fresh session

**Status: one complete two-session chain observed on 2026-11-27, using a synthetic offline order-export fixture and the existing ChatGPT subscription. Actual route: project task receipt.**

This case tested a different question from case 2: could an agent discover a new operational method, save it without a reminder, and have a separate fresh session find and apply it? No experience record was seeded by the test harness. Neither task prompt named Experience Reuse or asked the agent to save a lesson.

### Session A: discover, verify, and persist

The isolated project initially contained an ordinary README, local scope instructions, the `order_export` tool, and batch A. There was no experience store or prior task receipt. The tool and inputs were protected from modification. The task asked for fulfilled-order count, units, and amount using the README's command, allowing necessary local result files.

The README's default report call returned the real executable error `E_LAYOUT_MISMATCH`. Inspection and help established that the input schema `orders.archive/2` required the supported `archive-v2` layout. The agent automatically loaded Experience Reuse and its full workflow during recovery, then ran:

```text
python -X utf8 tools/order_export.py report --file inbox/batch_a.wex --layout archive-v2
```

The actual result was **3 fulfilled orders, 9 units, CNY 114.80**, excluding one cancelled row. The agent saved the actual JSON output to `results/batch_a.report.json` and, without a save-experience instruction, created `results/batch_a.verification.md` with the lesson, conditions, and result evidence.

The following is an English rendering of the agent-written receipt's operational lesson; the original local receipt was in Chinese:

```text
Method: after E_LAYOUT_MISMATCH, inspect the input and check report help;
use the layout they confirm, without changing the tool or source export.
Verified conditions: order_export 1.0.0; orders.archive/2; archive-v2.
Evidence: results/batch_a.report.json and the actual successful report output.
Before later use: recheck tool version and input schema.
```

This was a project-owned task receipt carrying reusable experience. The agent did not create `experiences.json`, call `praxis.py capture`, or rewrite the user-level skill. That distinction is part of the result, not an implementation detail to hide.

### Session B: automatic loading and actual reuse

After A ended, the observer retained A's project files and added a different batch B. A separate `codex exec` launch created a fresh model session, without resume/fork, chat-history handoff, or copied answers. The task said, in substance:

> We handled this project's order_export export before. Continue with the new batch, inbox/batch_b.wex, and summarize fulfilled orders, units, and amount.

This is an English paraphrase of the Chinese task prompt. It contained no skill name, learned parameter, or experience-file path. The reference to previous work was intentional: it exercised the installed repeated-work trigger.

The new session:

1. Automatically loaded Experience Reuse before the order-export operation.
2. Discovered the project result files and read the complete A verification receipt and its actual result.
3. Inspected batch B and checked the current tool version, schema, and supported parameters.
4. Used `--layout archive-v2` on its **first report call**, with no repeated default-layout error.
5. Saved the new result and verified it by reading it back and independently recalculating fulfilled rows with `Decimal`.

Batch B produced **3 fulfilled orders, 8 units, CNY 252.50**. Its fulfilled amounts were `36.00 + 116.60 + 99.90`; a cancelled row was excluded. Different inputs and totals distinguish reuse of the method from reuse of A's answer.

### What the audit established

| Check | Actual evidence |
| --- | --- |
| New lesson was saved by the agent | A's completed tool command created the receipt after a successful real report. |
| Observer did not supply the lesson | No seeded record or manual intermediate experience write; the A receipt was frozen before B. |
| New session did not receive a direct invocation | Neither task prompt named the skill; B received no recipe or receipt path. |
| Skill and lesson were used before the report | B loaded the skill, then read the full A receipt, then called the report tool. |
| Conditions were checked | B's actual inspect result confirmed version 1.0.0 and schema orders.archive/2 before reporting. |
| Known failure was avoided | Exactly one B report call used archive-v2; no E_LAYOUT_MISMATCH occurred in B. |
| Requested result was correct | Actual output, source identity, excluded rows, saved JSON, and independent decimal arithmetic agreed. |

The audit used completed tool events and actual returned content, not just the assistant's final claim. The A receipt remained unchanged between the frozen handoff and the end of B. The [sanitized closed-loop validation summary](../examples/closed-loop-validation.json) records these checks, event order, and secondary usage diagnostics. Raw chats, native-memory bodies, usernames, and absolute machine paths are not published; this is maintainer-audited evidence.

### Why the project receipt path matters

The skill permits experience to remain with its owning task/project source. Here, A's verification receipt already held the method and evidence, and B found that source through normal project inspection. No second experience database was required. The observed chain is:

```text
New local failure -> working method verified -> project receipt written
                    -> independent fresh session
                    -> skill loaded -> receipt read -> conditions checked
                    -> method applied -> new result verified
```

Native memory stayed enabled, with the same injected summary in both sessions. New memory generation was disabled only for these CLI invocations, so the newly discovered method was not learned through this test's background memory generation. User-level routing supplied the entry point; the project receipt owned the new lesson; the fresh session applied it. No generated native-memory file was edited.

### Validation boundary

- One chain, two fresh CLI contexts, and an intentionally constructed local compatibility fixture. This is a real execution test of that fixture, not production-site evidence or a reliability percentage.
- Automatic loading operated with the installed skill and an authorized persistent AGENTS route. B was explicitly told there was earlier work on this project/tool; unrelated or unprompted future tasks were not tested.
- This validates **project-receipt persistence and reuse**. It does not validate `praxis.py capture/find` end to end, embedding retrieval, automatic global skill rewriting, or formal promotion of a project lesson.
- Desktop new-chat behavior, cross-host operation, and reuse without any previous-work cue remain untested. The public English narrative describes the installed local runtime trial; publication is not an additional behavior test.
- Both sessions used the existing ChatGPT login, with chatgpt-only login forced and API environment credentials removed. No new model/reasoning selection, hooks, extra agents, or API billing route was used.
- The CLI host added only a trust entry for the isolated writable test project. Exact hash reconstruction verified that sole configuration change; the entry was removed after testing and the original configuration restored. Protected project inputs and existing skill/instructions retained their original content.

The acceptance goal was experience actually saved and reused. The two CLI sessions used 511,044 total tokens across 14 model calls; this includes cached input and excludes parent-conversation preparation/audit. There was no matched efficiency baseline and **no token-saving claim**.

## 4. A naming change affected several connected entry points

**Status: observed configuration change and isolated helper tests.**

During development, the user rejected the original name, Praxis Nexus, and chose Experience Reuse. The runtime directory, skill metadata, invocation example, user-level routing block, documentation, and test entry point were updated together. Prior files were archived outside the active skill root. The legacy storage directory and observation IDs were retained for compatibility.

**Expected intervention:** identify the current authoritative runtime and all affected references before renaming. Preserve historical receipts; do not rewrite old results to imply they were produced under the new name. Keep stable data identities unless a separately verified migration is needed.

**Observed check:** all 17 isolated CLI behavior tests passed at the renamed runtime path. The renamed routing block was also present in subsequent instructions in the current conversation.

**What is not established:** this proves those local checks, not that a fresh model session automatically selects the renamed skill or that tokens have been saved.

## 5. Reader A returns the body; reader B returns only a page shell

**Status: illustrative website-access scenario.**

Before: each task starts by trying B, sees a title or shell, then rediscovers A.

After: the owning project records the page type, reader/version, access conditions, target identity, and actual body check. Before the next related read, the agent retrieves the method and checks those conditions. Under matching conditions it prefers A; if the environment changed, it performs a narrow recheck.

**Native-memory role:** point to the established method and prior task. **Skill role:** check that the current action fits. **Tool role:** fetch and verify the requested body.

**Evidence:** inspect the actual body for the correct target; HTTP success, a title, or an empty shell is insufficient. No recipe authorizes bypassing login, CAPTCHA, rate limits, or access restrictions.

**Test coverage:** exact-context matching, candidate/validated states, and stale-method exclusion are helper-tested. No live website behavior is asserted here.

## 6. A tool upgrade invalidates a previously working command

**Status: illustrative environment-drift scenario.**

Before: a remembered command is retried unchanged because it worked in an older tool version.

After: the recorded recipe includes the relevant version. The observed current version conflicts, so `find` reports `context_mismatch` instead of presenting the old recipe as a preferred method. The agent consults current authoritative documentation and tests a minimal corrected operation.

**Evidence:** actual current version plus the corrected operation's requested result. The revised method is a new candidate; an earlier success does not validate its changed content.

**Test coverage:** version exclusion and revision-reset behavior. Unknown context is a request to check, not a guessed match.

## 7. A task-specific correction must retain its scope

**Status: illustrative user-instruction scenario.**

The user says, "Keep the original script for this video." The agent applies that requirement immediately to the current task and updates its owning task record where authorized.

It does not infer "never rewrite any script in any project." If the user explicitly establishes an enduring preference, the host's supported native-memory protocol handles that preference. The execution record points to the current requirement rather than maintaining a competing copy.

**Verification:** later edits preserve this task's original script; unrelated tasks retain their own permissions. A helper record cannot establish that the user's preference was actually saved by the host.

## 8. A method succeeds once and later fails

**Status: illustrative lifecycle scenario.**

Capture records a candidate with evidence. An actual adopted success with checked conditions yields `validated`. A later adopted failure marks it `stale` and preserves the observations. It no longer appears as a recommended search result.

The agent diagnoses the changed conditions. A fresh success can revalidate it through explicit `--revalidate`; retirement or supersession cannot be undone just by replaying a success observation.

**Verification:** query results distinguish stale exclusion from no match. Use a new event key for the new operation; replaying the same event does not manufacture another success.

**Test coverage:** failure exclusion, revalidation, event idempotency/conflicts, and supersession.

## 9. Similar tasks in different projects need different methods

**Status: illustrative project-isolation scenario.**

Project A uses one approved reader; Project B uses another. A global memory summary may mention that A has a successful method. The helper searches only the explicit project's store, and a copied store is rejected because its bound project root differs.

If a common method is genuinely useful, authorized sharing promotes a conditional rule to its designated shared skill/configuration. It does not silently expose another project's private evidence or overwrite B's current policy.

**Test coverage:** no cross-project lookup and copied-store rejection. This is not a claim that the host's own memories are automatically project-isolated by this helper.

## 10. A clean process exit hides a wrong result

**Status: illustrative outcome-verification scenario.**

A command exits with code zero but returns data for the wrong product, an empty page, or a media file missing the requested content.

The experience record defines the requested success condition. The agent inspects the actual result and records its real outcome. Merely setting `outcome: success` would be a caller error; the helper checks structure and source availability, not truth.

**Verification:** inspect the target identity, content coverage, or rendered artifact using the original workflow's checks. Neither the index nor native memory replaces those checks.

## Evaluate improvement, not record volume

Use comparable fresh tasks with native memory alone and with native memory plus this skill. Track whether relevant experience arrived before the first action, whether it was adopted, whether it worked, and why a repetition occurred. Include capture, retrieval, and review overhead in total tokens and latency.

More saved lessons, a larger SKILL.md, or a successful demo is not proof of better task performance. Keep ineffective changes out of the owning workflow and preserve a way to revert them.
