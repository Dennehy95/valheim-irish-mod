# Translations to fix (QA queue)

Use this folder during development to track **dodgy, missing, or deferred** Irish strings. We fix accuracy in focused passes after coverage is high—not while keys are still landing.

## Workflow

1. **While building coverage** — When you spot a bad string in-game (learner mode helps), add an entry under [`issues.md`](issues.md) or a new `issue-*.md` file here. Do not block feature work on polish.
2. **Near ~100% key coverage** — Export the full translation set for external Irish review (native speaker / editor).
3. **Fix passes** — Pull open items from this queue into batch fixes (word order, MT cleanup, missing keys). Close or update `status` when merged.
4. **Accuracy is deferred until QA** — Entries here are triage notes, not the source of truth; canonical strings live in `plugins/irish-mod/Translations/*.ga.json`.

## Common issue types

| Category | Meaning |
|----------|---------|
| `missing-translation` | Irish missing or identical to English (fallback). |
| `partial-mt` | Mixed English/Irish or obvious machine output. |
| `word-order` | Irish wants **noun + modifier** (or natural compound order), not English **modifier + noun**. Tool names are a frequent example: *tuagh cloch* (stone axe), not *Cloch Tuagh* or *Axe Cloch*. Expect **systematic** word-order fixes across item/tool keys after MT passes. |

## Source files

- Item names & descriptions: `plugins/irish-mod/Translations/item-names.ga.json`
- Extracted English keys: `plugins/irish-mod/extracted/item-names.json`

## Index

- [issues.md](issues.md) — logged issues (newest at top)
