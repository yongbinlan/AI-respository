# Experience Reuse

Use relevant execution experience **before the next action**, with project boundaries, source evidence, and stale-method checks.

Experience Reuse is a lightweight Codex skill with an offline Python helper. It connects remembered history to a concrete operational decision: find the original method, check whether it still applies, use it, verify the result, and update the owning record.

## Why this project exists

An agent can remember an earlier solution and still repeat the same mistake. The useful detail may never have been saved, a relevant memory may not be recalled, the summary may omit a critical condition, or the agent may ignore information already in the current context.

The last case helped motivate this project. In a real development conversation, the skill catalog already placed `ai-capability-amplifier` in the project's `.codex/skills` directory. The assistant nevertheless tried the user-level skills directory, received a file-not-found error, and only then used the supplied project path.

**The information was already available before the read. The missing step was applying it to the action.** Adding another memory database alone would not necessarily prevent that omission.

This skill introduces a focused pre-action check and a small, project-scoped experience loop. It does not promise that a language model will obey every instruction or that all tool calls are intercepted.

## Problems it helps address

- Repeating an unchanged failed command or access method after it was already diagnosed.
- Guessing a file location despite an exact path or catalog entry in the current task.
- Reusing a successful method without its tool version, page type, or environment conditions.
- Saving lessons that are never consulted before the relevant operation.
- Copying mutable rules into memory, task notes, and skills until they disagree.
- Promoting a one-off preference into a global instruction.
- Calling an operation successful because a process exited cleanly rather than checking the requested result.

## How it works with native memory

Native memory and procedural experience overlap. Both can contain corrections, decisions, and successful methods. This skill adds explicit ownership and action-time checks rather than trying to replace memory.

| Component | Responsibility |
| --- | --- |
| Native memory | Recall relevant history, preferences, decisions, and pointers to prior work. |
| Experience Reuse | Locate the authority, check conditions before acting, and capture useful new observations. |
| Project record | Own the scoped method and its evidence, revisions, observations, and invalidation reasons. |
| Existing professional skill/tool | Own stable procedures, deterministic checks, and formal promotion or approval gates. |

```text
Relevant history or current instruction
                |
        Locate the authority
                |
   Check scope, conditions, evidence
                |
       Apply -> verify outcome
                |
    Update the owning project record
                |
  Consolidate stable methods selectively
```

A memory summary might say, "There is an established detail-page access method." The agent then reads that method, checks the current page/tool/environment and permissions, and adopts it only if applicable. If the summary is stale, the current authoritative source governs the action.

Keep one authoritative source per effective rule. Memory can retain a short pointer; existing project records can be indexed without copying their procedures. This skill never edits generated native-memory files, changes native-memory settings, or grants itself permission to write long-term personal memory.

[OpenAI's memory guidance](https://learn.chatgpt.com/docs/customization/memories) likewise recommends keeping required guidance in `AGENTS.md` or checked-in documentation, with memories as a recall layer. This skill does not depend on a particular undocumented memory implementation.

## Practical cases

The first two cases below were observed during development. The remaining cases are realistic usage examples, not measured production outcomes.

| Case | What changes with the workflow | Evidence label |
| --- | --- | --- |
| **Wrong skill directory despite an explicit catalog path** | Inspect the catalog and use the project path before guessing a user-level location. | Observed execution omission; future prevention is not yet measured. |
| **Renaming the skill without breaking its entry points** | Update the invocation, folder, metadata, guidance, and tests together; retain the old storage key. | Observed configuration change; 17 isolated CLI tests passed afterward. |
| A link works through reader A but reader B returns a page shell | Record page type, tool/version, access conditions, and a body/identity success check; prefer A only under matching conditions. | Illustrative; no live website claim. |
| A previously valid command fails after a tool upgrade | Version mismatch excludes the old recipe and calls for a narrow recheck. | Illustrative scenario; exact-context exclusion is covered by helper tests. |
| A user says "keep the original script for this video" | Apply the instruction immediately and keep its scope with that task/project. | Illustrative; not a new global preference. |
| A method succeeds once, then fails in a later task | Preserve both observations, mark it stale, and require explicit revalidation before recommending it again. | Illustrative scenario; lifecycle behavior is tested. |
| Two projects use different tools for a similar operation | Keep project stores isolated; share only a deliberately scoped common method. | Illustrative scenario; isolation is tested. |
| An operation exits successfully but returns the wrong entity | Use an outcome check and record the actual failure instead of treating exit code zero as validation. | Illustrative; semantic judgment remains the caller's responsibility. |

Read the [full casebook](references/casebook.md) for the observed sequence, expected intervention, evidence requirements, and limits of each case.

## Install

Requires a Codex host that supports skills and **Python 3.10+** for the helper. The helper uses only the standard library, runs offline, and does not call a model or execute saved procedures. Normal agent work still uses the host's tools and model budget.

Give Codex this instruction:

```text
Install skills/experience-reuse from
https://github.com/yongbinlan/AI-respository
into my Codex-owned user-level skills directory.
Inspect the files, resolve the actual directory, preserve any existing version,
and keep the folder structure. Do not modify native-memory settings or install
hooks. Show the installed SKILL.md path and run the helper tests.
```

For manual installation, clone this repository and copy the complete `skills/experience-reuse` folder to the skill root supported by your host. A Codex-owned user root such as `~/.codex/skills` or an approved project `.codex/skills` keeps this package separate from other agents. Resolve `CODEX_HOME` and local policy rather than assuming a username or copying into every agent directory. Back up an existing same-name version before replacing it.

Check the host's skill list. Start a new session or restart the host if needed. Implicit selection is enabled in the metadata, but host discovery and automatic selection still require actual verification. The [optional AGENTS anchor](references/global-anchor.md) provides persistent model-side routing after the user authorizes that configuration change; it is not installed automatically.

## Use it

```text
Use $experience-reuse to find this project's previous solution before trying
the same operation again. Check its conditions and capture useful new findings.
```

From this skill directory, inspect an existing project's index:

```text
python -X utf8 scripts/praxis.py status --project /absolute/path/to/project
python -X utf8 scripts/praxis.py find --project /absolute/path/to/project --query "detail reader"
```

On Windows, replace the example project root with its actual absolute Windows path. Add `--context-file` with observed string values to distinguish the current tool, action, host, version, or other conditions.

Use the project's existing incident/experience interface first. If there is no suitable owner, the first `capture` creates `.codex/praxis-nexus/experiences.json` inside the chosen project. The legacy directory name is retained for data compatibility; it is not a second skill. Read-only lookups create nothing. Stores and evidence should remain local unless explicitly reviewed for publication. Exclude `.codex/praxis-nexus/` from each owning project's Git tracking (for example through its local `.git/info/exclude`) before capturing private experience; the helper does not edit Git configuration.

The [integration contract](references/integration.md) documents capture, observation, supersession, deduplication, and error behavior.

## Run a reproducible example

```text
python -X utf8 examples/demo.py
```

The demo uses temporary synthetic projects and evidence. It checks that a candidate requires review, an observed success can be retrieved, a changed version is excluded, a failure marks the method stale, and another project does not inherit it. Temporary records are removed afterward. It does not visit websites or demonstrate automatic agent compliance.

## Validation and limits

```text
python -X utf8 tests/test_experience_reuse.py
```

The 17 isolated CLI tests cover read-only empty queries, deduplication, event conflicts, version/context checks, revisions, authority pointers, missing evidence, failure/revalidation, supersession, project isolation, copied-store rejection, locks, corrupt files, credential screening, bounded retrieval, and directory-link protection. Platform-dependent symlink tests report a skip when the OS does not permit them.

The development helper and this portable package each passed all 17 tests on Windows. This establishes helper behavior, not new-session model selection, website compatibility, semantic correctness, or token savings. Cross-platform runtime coverage remains unestablished.

Retrieval uses keywords and exact context, not embeddings. File existence is not proof of a real-world result. Privacy screening is limited. Text instructions and optional routing do not universally intercept tool calls. Existing professional and human-review gates still apply.

Measure the effect on fresh comparable tasks: first-action adoption, repeated errors, delivery quality, calls, latency, and total tokens including capture/retrieval costs. Until such a comparison exists, savings remain **unverified**.

## Files

- [SKILL.md](SKILL.md): compact agent instructions.
- [Integration contract](references/integration.md): storage, commands, evidence, and memory boundaries.
- [Casebook](references/casebook.md): observed incidents and practical examples.
- [Optional routing anchor](references/global-anchor.md): a reviewed AGENTS addition.
- [Helper](scripts/praxis.py), [demo](examples/demo.py), and [tests](tests/test_experience_reuse.py).
