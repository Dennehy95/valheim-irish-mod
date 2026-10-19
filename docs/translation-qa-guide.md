# Translation QA guide (~6k Irish strings)

Coverage for vanilla Valheim keys is complete; the next phase is **quality**: fluency, register, game terminology, and Irish-specific grammar (especially compound nouns and tool names). This guide describes practical ways to **rank, filter, and review** the full set without changing canonical JSON until a human approves fixes.

**Canonical source:** `plugins/irish-mod/Translations/*.ga.json`  
**Full export for review:** [`exports/`](../exports/README.md) (`translations-full.json` / `.csv`)  
**Issue queue:** [`translations-to-fix/`](../translations-to-fix/README.md) (log problems; fix in focused passes)

---

## 1. Start with heuristic filters (scripts)

Run cheap automated flags on the export (or on `*.ga.json` directly) to **prioritize** rows, not to auto-fix copy.

| Heuristic | What it catches | Suggested action |
|-----------|-----------------|------------------|
| `irish == english` (after trim) | Untranslated fallback or proper nouns left in English | Review; keep only intentional proper nouns |
| Empty or whitespace-only `irish` | Missing translation | Fix or log in `translations-to-fix/` |
| Length ratio | Irish much shorter/longer than English (e.g. &lt; 0.4× or &gt; 2.5×) | Often MT truncation, wrong key, or pasted UI junk |
| Word-count mismatch | Large delta in token count (ignore `{0}` / `<color=` tags) | Dialogue vs label confusion |
| Mixed EN + GA | Latin letters with Irish diacritics, or obvious English function words in Irish field | `partial-mt` cleanup |
| Residual English tokens | Whole-word matches: `the`, `and`, `your`, `forge`, `blade` in `irish` | High-priority MT sweep |
| Duplicate `irish` across many keys | Same wrong string wired to unrelated keys | Data bug (see queue examples) |
| `translationMethod` / file flags | `machineAssisted`, `pendingApiKey` | Extra scrutiny on those bundles |

Implement filters as a small Python script over `exports/translations-full.json` and write flagged keys to `translations-to-fix/issue-*.md` or a `qa-flags.csv` with a `flag` column.

**Key-prefix priority** (high player visibility first):

- `menu_`, `settings`, HUD / inventory screens → menus and tutorials  
- `item_`, `piece_` → names players see constantly  
- `tutorial_`, achievement / lore strings → onboarding and tone  
- Long `description` / dialogue keys → fluency and register  

---

## 2. Spreadsheet workflow

1. Open `exports/translations-full.csv` in Excel or Google Sheets (UTF-8 BOM opens cleanly in Excel).
2. **Sort** by `key` or filter by prefix (`item_`, `piece_`, `menu_`).
3. Add columns: `qa_flag`, `priority` (1–3), `reviewer`, `notes`, `fixed_in_pr`.
4. Use **conditional formatting**: `irish` equals `english`, or `LEN(irish)=0`.
5. Share a **subset sheet** with a reviewer (e.g. all `menu_*` + top 200 items) before tackling lore blocks.

Do not treat the sheet as source of truth—merge approved edits back into the matching `*.ga.json` entry.

---

## 3. AI batch review (assist only)

Export **chunks** (200–400 rows) with a fixed rubric in the prompt:

- **Fluency:** natural Caighdeán Oifigiúl, not literal calque  
- **Register:** terse UI labels vs fuller tutorial prose  
- **Game terms:** consistent choices (e.g. stamina, biome, boss names)  
- **Grammar:** Irish **noun + modifier** order for compounds and tools (see below)  
- **Preserve:** `{0}`, `<color=…>`, `\\n`, and proper nouns where English is intentional  

Ask the model for: `key`, `issue_type`, `suggested_irish`, `confidence`, `note`.  
**Never auto-merge** model output—spot-check every suggestion, especially items and menus.

---

## 4. Back-translation (confidence flag)

For suspicious rows:

1. Take `irish` → translate to English with Argos Translate (offline) or DeepL (API).  
2. Compare back-translation to original `english` (semantic similarity or manual read).  
3. Large divergence → mark `low-confidence` and queue for human review.

Useful after MT-heavy passes; less useful for very short labels.

---

## 5. Human review (highest value)

A fluent **Gaeilge** reviewer should start with:

1. Main menu, settings, and HUD  
2. Item and piece **names** (not every description on day one)  
3. Tutorial and achievement text  
4. Lore and long dialogue in later passes  

Pair reviewer notes with [`translations-to-fix/issues.md`](../translations-to-fix/issues.md) so fixes stay traceable.

---

## 6. Irish-specific checklist

- **Caighdeán Oifigiúil:** standard spelling and grammar unless the project explicitly chooses a dialect register for flavor.  
- **Proper nouns:** bosses, biomes, and trademarked names (e.g. *Dyrnwyn*) may stay English or use an agreed Irish form—document the choice once and apply consistently.  
- **Tool and material compounds:** Irish prefers **material + tool** (*tuagh cloch*, stone axe), not English **modifier + noun** (*Cloch Tuagh*, *Axe Stone*). Expect **systematic** fixes across `item_*` / `piece_*` after machine-assisted passes.  
- **UI junk:** unrelated Irish phrases copied into item keys (wrong screen scrape) show up as nonsense vs English—heuristic length and back-translation help catch these quickly.  
- **Tags and placeholders:** reviewers must leave game markup untouched.

---

## 7. Regenerating the export

After JSON edits:

```bash
python tools/export_all_translations.py
```

See [`exports/README.md`](../exports/README.md) for row counts and timestamps.

---

## Related docs

- Short pointer: [`docs/translations-qa.md`](translations-qa.md)  
- Queue workflow: [`translations-to-fix/README.md`](../translations-to-fix/README.md)
