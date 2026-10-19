# AI review workflow (slim export)

Use **slim** exports when asking an AI to review Irish copy: each row is only `key`, `english`, and `irish`. Full metadata stays in `plugins/irish-mod/Translations/*.ga.json` until you merge approved `irish` values back.

| Step | Tool | Output |
|------|------|--------|
| Spreadsheet / full QA | `tools/export_all_translations.py` | `exports/translations-full.json`, `.csv` |
| AI review | `tools/export_slim_translations.py` | `exports/translations-slim.json` (optional `.jsonl`) |
| Large batches | `tools/split_slim_chunks.py` | `exports/chunks/chunk-001.json`, … |
| Apply fixes | `tools/merge_slim_translations.py` | Updates `*.ga.json` in place |
| Refresh snapshot | `tools/export_all_translations.py` | Regenerate full export after merge |

See also [translation-qa-guide.md](translation-qa-guide.md) for heuristics and human QA; this doc is the **slim round-trip** only.

---

## 1. Export slim

From the repository root:

```bash
python tools/export_slim_translations.py
python tools/export_slim_translations.py --jsonl
```

Artifacts:

- `exports/translations-slim.json` — JSON array, sorted by `key`
- `exports/translations-slim.jsonl` — same rows, one JSON object per line (handy for streaming)

Schema per entry:

```json
{ "key": "item_amber", "english": "Amber", "irish": "ómra" }
```

---

## 2. Split into chunks (optional)

```bash
python tools/split_slim_chunks.py
python tools/split_slim_chunks.py --size 150 --out-dir exports/chunks/menu-pass
```

Default input is `exports/translations-slim.json`; default output is `exports/chunks/chunk-001.json`, `chunk-002.json`, … with **200** entries each. Each chunk file uses the same slim schema only.

**After AI edits each chunk**, either:

1. **Merge chunks one at a time** (safe if chunk keys do not overlap):

   ```bash
   python tools/merge_slim_translations.py exports/chunks/chunk-001.json
   python tools/merge_slim_translations.py exports/chunks/chunk-002.json
   # ...
   ```

2. **Recombine into one slim file**, then merge once. From the repo root (PowerShell):

   ```powershell
   python -c "import json,glob; paths=sorted(glob.glob('exports/chunks/chunk-*.json')); rows=[e for p in paths for e in json.load(open(p,encoding='utf-8'))]; json.dump(rows, open('exports/translations-slim-reviewed.json','w',encoding='utf-8'), ensure_ascii=False, indent=2); print(len(rows),'entries')"
   ```

   ```bash
   python tools/merge_slim_translations.py exports/translations-slim-reviewed.json
   ```

---

## 3. Prompt template (per chunk)

Attach one chunk file (or paste its JSON array). Use a rubric like this:

```text
You are reviewing Irish (Gaeilge) game UI strings for a Valheim mod.

Input: JSON array of objects with fields key, english, irish.

For each entry:
1. Rate quality 1–5 (5 = fluent, correct register, game-appropriate).
2. If irish needs work, rewrite irish only. Do not change key or english.
3. Preserve placeholders and markup exactly: {0}, {1}, <color=...>, \n, proper nouns where English is intentional.

Output: the same JSON array shape (key, english, irish only). Keep the same keys in the same order. Only change irish where you improve it.

Register: short labels stay terse; descriptions and dialogue can be fuller. Prefer natural Caighdeán Oifigiúl over literal English calques.
```

Spot-check high-impact keys (`menu_`, `item_`, `piece_`, tutorials) before merging.

---

## 4. Merge back into canonical JSON

```bash
python tools/merge_slim_translations.py exports/translations-slim-reviewed.json
python tools/merge_slim_translations.py exports/translations-slim-reviewed.json --dry-run
python tools/merge_slim_translations.py exports/translations-slim-reviewed.json --mark-reviewed
```

Behavior:

- Locates each `key` across all `plugins/irish-mod/Translations/*.ga.json` files.
- Updates **only** `irish` when the slim value differs.
- Leaves `english`, `sourceFile` metadata, `pendingApiKey`, `machineAssisted`, `translationMethod`, etc. unchanged unless you pass `--mark-reviewed` (sets `translationMethod` to `ai-reviewed` on changed entries and `machineAssisted` to `true` on touched bundle files).
- Prints counts: keys updated, unchanged, not found.

Accepts a **JSON array** (`.json`) or **JSONL** (`.jsonl` or line-delimited objects).

---

## 5. Regenerate full export

```bash
python tools/export_all_translations.py
```

Commit changes to `*.ga.json` when you are satisfied; keep slim exports local or regenerate them—they are disposable working copies.
