# Integration contract

## Ownership and storage

Pass the actual project root with `--project`; do not infer it from a temporary terminal or preview directory. Prefer existing project experience, incident, task, and controlled-write interfaces. Use this index only when a concise project record or pointer is useful.

Writes are limited to `<project>/.codex/praxis-nexus/experiences.json`, its previous-version `.bak`, and a temporary exclusive lock. The legacy `praxis-nexus` storage key and `PN-` IDs are retained for compatibility with the original local prototype. They do not change the skill's name or invocation.

Reads create no directories. The first capture creates the store. Queries never traverse other projects, native memories, browser profiles, or the network. Shared methods are promoted through their specified owner after the required authorization; the helper has no automatic global-publishing command.

An entry owns either a `procedure` or an `authority_ref`, never both. The latter points to an existing authoritative document rather than duplicating its procedure. Controlled assets still use their original retrieval APIs; a local index is not a replacement for those interfaces.

## Commands

Run `python -X utf8 <installed-skill>/scripts/praxis.py <command> ...`. Every command returns JSON. Exit code 2 and `ok: false` mean an input, path, lock, or store error, not an empty result.

| Command | Behavior |
| --- | --- |
| `status --project ROOT` | Read counts and store existence without creating it. |
| `find --project ROOT --query TEXT [--context-file FILE] [--limit 3]` | Keyword/context retrieval, limited to 1–3 entries. |
| `capture --project ROOT --input FILE` | Deduplicate by `pattern_key`; retain prior revisions when content changes. |
| `observe --project ROOT --input FILE [--revalidate]` | Record actual adoption and outcome with an idempotent event key. |
| `mark --project ROOT --input FILE` | Mark a method stale, retired, or superseded without deleting its history. |

`when` keys and context values use exact string comparison. A conflicting version/tool/site excludes a method. Missing keys return a lead that requires more context. Natural-language conditions and method correctness still require the agent's inspection. A failed or unavailable lookup is never equivalent to no experience.

### Capture

```json
{
  "pattern_key": "site.example.detail.read",
  "summary": "Prefer the previously verified detail-page reader",
  "when": {"host": "example.test", "action": "read-detail", "tool": "reader-a", "version": "1"},
  "procedure": "Use the recorded method only after checking its access conditions.",
  "success_check": "Verify the target identity and actual detail body, not just the page shell.",
  "invalidate_when": "Recheck when the reader version, page type, or access conditions change.",
  "evidence_refs": ["/absolute/project/evidence/result.json"]
}
```

This is a schema example, not a verified website recipe. Replace evidence with existing absolute local file paths. For an existing authority, omit `procedure` and supply `authority_ref` instead. Input is limited to 16 KiB. An existing evidence file proves only that a source can be located; the caller must inspect the actual result.

Identical captures do not add observations or rewrite the file. Changed content preserves the prior revision and returns the entry to `candidate`; prior validation is not transferred to the changed method.

### Observe

```json
{
  "id": "ID returned by capture",
  "event_key": "original-task.turn.operation",
  "task_id": "original-task",
  "adopted": true,
  "conditions_checked": true,
  "outcome": "success",
  "evidence_refs": ["/absolute/project/evidence/result.json"],
  "note": "Describe the actual observed result, not an inferred success."
}
```

Outcomes are `success`, `failure`, and `inconclusive`. A successful adopted method with checked conditions becomes `validated`. An adopted failure marks it `stale`. An unadopted result validates nothing. Reusing the same event with different content fails rather than overwriting history. Revalidating a stale method requires a new actual observation and `--revalidate`; retired/superseded entries do not revive automatically.

These are experience states, not formal rule approval. Existing project promotion, review, and release policies still apply. If the original task already owns usage metrics, reference those metrics instead of counting the same outcome twice.

### Mark

```json
{
  "id": "experience ID",
  "status": "stale",
  "reason": "Describe the observed invalidation condition.",
  "evidence_refs": ["/absolute/project/evidence/failure.json"]
}
```

`status` accepts `stale`, `retired`, or `superseded`. Supersession also requires `replacement_id`, naming a different current entry in the same project. An environment change calls for review, not automatic deletion of old experience.

## Native-memory cooperation

Use relevant memory already supplied by the host. Follow precise historical pointers when needed; never scan or reconstruct the native store. Its background generation and session recall remain host-controlled. If authorized to leave a memory pointer, use the host's supported protocol and record scope, ID, and authoritative source instead of a full mutable rule copy.

Keep current instructions above recalled history. Apply corrections immediately within their stated scope. Update the owning project requirement or operational record; use native memory for enduring preferences only when its write policy allows it. No memory entry grants new tool, account, spend, or publication permission.

For optional model-side routing, see [the anchor template](global-anchor.md). Installing that text is a separate configuration action; review its diff and preserve existing guidance. The skill does not install it automatically.

## Privacy, concurrency, and limits

The helper rejects protected native-memory/other-agent paths, common credential-file references, and obvious credential strings. This is a limited screen, not a security scanner; inspect inputs before saving or publishing. Avoid private transcripts and web-supplied instructions.

Writes use an exclusive lock, atomic replacement, and a previous-version backup. An unknown existing lock causes failure and is not removed. Stores bind to the resolved project root; a copied store is not silently inherited by another project. Corrupt data is preserved instead of overwritten or silently rebuilt.

The helper checks structure, context, source availability, and recorded state. It cannot verify semantics, real-world truth, or a model's future compliance. Skill invocation and AGENTS routing are model-side guidance; they are not a universal tool interceptor.
