---
name: experience-reuse
description: >-
  Capture a newly created skill's first verified successful task; also trigger before repeating prior work: previously handled / re-read / continue / same issue / 之前处理过 / 重新读取 / 上次 / 续办, including read-only requests to inspect a named skill, file, tool or site. Apply catalog-first path checks or scoped experience reuse; unrelated one-off reads do not trigger it.
---

# Experience Reuse

Apply relevant experience before the next action. Keep the coordination method at user level, experience with its owning project, and stable procedures in their existing skills or tools. Native memory supplies historical pointers. Successful reuse is the goal; token reduction is a secondary, separately measured possibility.

## Trigger and load

- When the user refers to earlier work and asks to re-read, repeat, resume, or continue an operation involving a named skill, file, tool, site, or workflow, load this skill once before the first relevant operation. Read-only summaries also qualify.
- A request not to run the target skill's production workflow does not disable this read-only preflight. Do not wait for another failure or replace this preflight with generic memory search.
- Also intervene for user corrections, retries/method changes after failure, and newly verified reusable discoveries. Unrelated one-off reads do not require this skill.
- After a newly created skill first completes a real task and passes outcome checks, load this skill once before closing the task and follow [first-success capture](references/workflow.md#first-verified-success). No previous failure, second use, repeat-work cue, or user reminder is required. Installation, syntax checks, and process exit alone do not establish task success.

## Exact-catalog short path

Once this skill is loaded, if the task supplies exact root mappings and a skill reference, resolve and read that target directly. Do not add this skill's own memory/index search, run the target's production workflow, or create experience records for this read. If a higher-priority host memory protocol requires a quick pass, follow it and reuse the result without a duplicate search; no memory match is needed to use an explicit catalog.

Run this skill's `scripts/read_skill.py`, copying the mappings and reference from the current task:

```text
python -X utf8 <installed-skill>/scripts/read_skill.py --root "r0=<actual-project-skill-root>" --root "r1=<actual-user-skill-root>" --reference r0/<target-skill>/SKILL.md
```

The reader only uses supplied roots. Unknown aliases, path escapes, and missing files fail without guessing another location. Success returns `ok: true`, `activation: experience-reuse.catalog-first`, the actual `resolved_path`, and the target's full `content`. Inspect the real output, complete the original read-only task, and stop if there is no new experience to capture.

## Other experience tasks

Read [the experience workflow](references/workflow.md) for scoped retrieval, condition checks, adoption, outcome verification, maintenance, and consolidation. Use `scripts/praxis.py` only when a structured index is useful; read [the integration contract](references/integration.md) before changing records. Prefer pointers to existing authorities. A single lookup does not require creating an index.

## Boundaries and verification

Both helpers require Python 3.10+, use the standard library, run offline, and make no model calls. The catalog reader writes nothing; the index writes only inside the explicit project. Current instructions and authoritative sources govern recalled history. Never edit generated native memories, copy private chats, or propagate project methods globally without authorization. Existing access, credential, spend, professional-role, and review gates remain effective. Do not implicitly install hooks/background tasks or change models.

This is model-side routing, not a universal tool interceptor. Verify actual skill loading before the target action, method adoption, the first target path, and the requested result in fresh sessions. Installation or helper tests alone do not prove automatic selection. Report measured costs separately; do not claim token savings from successful reuse.
