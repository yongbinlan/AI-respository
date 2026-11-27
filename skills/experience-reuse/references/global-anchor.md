# Optional model-side routing

Install the skill first. Persistent routing is a separate authorized configuration change; installation does not apply this template automatically. Resolve the actual installed `SKILL.md` path, replace `<absolute-installed-SKILL.md>` below, and append only this marked block to the appropriate existing user-level or project-level `AGENTS.md`. Preserve unrelated text. Never edit generated native memories or another agent's skill directory.

```markdown
<!-- experience-reuse:start -->
## Experience Reuse - repeated-work preflight

When the user refers to earlier work and asks to re-read, repeat, resume, or
continue an operation involving a named skill, file, tool, site, or workflow,
load `<absolute-installed-SKILL.md>` once before the first relevant operation.
This applies to read-only summaries too. A request not to run the target
skill's production workflow does not disable this read-only preflight.
Do not replace the preflight with a generic memory search. Follow its short
path when an exact catalog is already supplied.

Also use it for a user correction, a resolved failure, or a newly verified
reusable method. Unrelated one-off reads do not require it. Keep experience
with its owning project/source, retain current authority and approval gates,
and do not edit generated native memories or propagate project methods globally.
This is model-side routing, not a universal tool interceptor.
After a newly created skill's first real task succeeds and its outcome has
been verified, load the same Experience Reuse skill once before closing the
task and preserve the successful method, applicability conditions, and evidence
with its owning project/task record. No prior failure, repeat request, or user
reminder is required. Installation, syntax checks, and process exit alone do
not establish task success. Preserve existing formal promotion/review gates.
<!-- experience-reuse:end -->
```

Verify the effective file, instruction precedence, and discovery in the actual host. A new session or host restart may be needed. Higher-priority host memory rules still apply; the skill cannot disable them. See the [fresh-session case](casebook.md#2-fresh-session-automatic-reuse-after-trigger-repair) for one observed successful application with this routing design. That observation is not a reliability guarantee for other hosts or tasks.

To remove this routing, delete only the marked block, preserving later unrelated edits. Setting `allow_implicit_invocation: false` disables implicit skill selection, but a separate AGENTS instruction can still direct a model to read the installed file. Review both sources when disabling automatic routing; do not blindly restore an old whole-file backup.
