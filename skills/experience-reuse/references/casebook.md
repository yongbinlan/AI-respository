# Experience Reuse casebook

Two development incidents are factual observations from the conversation that produced this skill. Local usernames, project names, absolute machine paths, and private transcripts are omitted. The other cases illustrate practical use; they are not customer results or claims of measured savings.

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

**What is not established:** this case motivated the workflow; it is not evidence that the skill has already eliminated the error in future sessions.

## 2. A naming change affected several connected entry points

**Status: observed configuration change and isolated helper tests.**

During development, the user rejected the original name, Praxis Nexus, and chose Experience Reuse. The runtime directory, skill metadata, invocation example, user-level routing block, documentation, and test entry point were updated together. Prior files were archived outside the active skill root. The legacy storage directory and observation IDs were retained for compatibility.

**Expected intervention:** identify the current authoritative runtime and all affected references before renaming. Preserve historical receipts; do not rewrite old results to imply they were produced under the new name. Keep stable data identities unless a separately verified migration is needed.

**Observed check:** all 17 isolated CLI behavior tests passed at the renamed runtime path. The renamed routing block was also present in subsequent instructions in the current conversation.

**What is not established:** this proves those local checks, not that a fresh model session automatically selects the renamed skill or that tokens have been saved.

## 3. Reader A returns the body; reader B returns only a page shell

**Status: illustrative website-access scenario.**

Before: each task starts by trying B, sees a title or shell, then rediscovers A.

After: the owning project records the page type, reader/version, access conditions, target identity, and actual body check. Before the next related read, the agent retrieves the method and checks those conditions. Under matching conditions it prefers A; if the environment changed, it performs a narrow recheck.

**Native-memory role:** point to the established method and prior task. **Skill role:** check that the current action fits. **Tool role:** fetch and verify the requested body.

**Evidence:** inspect the actual body for the correct target; HTTP success, a title, or an empty shell is insufficient. No recipe authorizes bypassing login, CAPTCHA, rate limits, or access restrictions.

**Test coverage:** exact-context matching, candidate/validated states, and stale-method exclusion are helper-tested. No live website behavior is asserted here.

## 4. A tool upgrade invalidates a previously working command

**Status: illustrative environment-drift scenario.**

Before: a remembered command is retried unchanged because it worked in an older tool version.

After: the recorded recipe includes the relevant version. The observed current version conflicts, so `find` reports `context_mismatch` instead of presenting the old recipe as a preferred method. The agent consults current authoritative documentation and tests a minimal corrected operation.

**Evidence:** actual current version plus the corrected operation's requested result. The revised method is a new candidate; an earlier success does not validate its changed content.

**Test coverage:** version exclusion and revision-reset behavior. Unknown context is a request to check, not a guessed match.

## 5. A task-specific correction must retain its scope

**Status: illustrative user-instruction scenario.**

The user says, "Keep the original script for this video." The agent applies that requirement immediately to the current task and updates its owning task record where authorized.

It does not infer "never rewrite any script in any project." If the user explicitly establishes an enduring preference, the host's supported native-memory protocol handles that preference. The execution record points to the current requirement rather than maintaining a competing copy.

**Verification:** later edits preserve this task's original script; unrelated tasks retain their own permissions. A helper record cannot establish that the user's preference was actually saved by the host.

## 6. A method succeeds once and later fails

**Status: illustrative lifecycle scenario.**

Capture records a candidate with evidence. An actual adopted success with checked conditions yields `validated`. A later adopted failure marks it `stale` and preserves the observations. It no longer appears as a recommended search result.

The agent diagnoses the changed conditions. A fresh success can revalidate it through explicit `--revalidate`; retirement or supersession cannot be undone just by replaying a success observation.

**Verification:** query results distinguish stale exclusion from no match. Use a new event key for the new operation; replaying the same event does not manufacture another success.

**Test coverage:** failure exclusion, revalidation, event idempotency/conflicts, and supersession.

## 7. Similar tasks in different projects need different methods

**Status: illustrative project-isolation scenario.**

Project A uses one approved reader; Project B uses another. A global memory summary may mention that A has a successful method. The helper searches only the explicit project's store, and a copied store is rejected because its bound project root differs.

If a common method is genuinely useful, authorized sharing promotes a conditional rule to its designated shared skill/configuration. It does not silently expose another project's private evidence or overwrite B's current policy.

**Test coverage:** no cross-project lookup and copied-store rejection. This is not a claim that the host's own memories are automatically project-isolated by this helper.

## 8. A clean process exit hides a wrong result

**Status: illustrative outcome-verification scenario.**

A command exits with code zero but returns data for the wrong product, an empty page, or a media file missing the requested content.

The experience record defines the requested success condition. The agent inspects the actual result and records its real outcome. Merely setting `outcome: success` would be a caller error; the helper checks structure and source availability, not truth.

**Verification:** inspect the target identity, content coverage, or rendered artifact using the original workflow's checks. Neither the index nor native memory replaces those checks.

## Evaluate improvement, not record volume

Use comparable fresh tasks with native memory alone and with native memory plus this skill. Track whether relevant experience arrived before the first action, whether it was adopted, whether it worked, and why a repetition occurred. Include capture, retrieval, and review overhead in total tokens and latency.

More saved lessons, a larger SKILL.md, or a successful demo is not proof of better task performance. Keep ineffective changes out of the owning workflow and preserve a way to revert them.
