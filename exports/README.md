# Translation exports

Full export of Irish (`ga`) strings from `plugins/irish-mod/Translations/*.ga.json`.

| Artifact | Description |
|----------|-------------|
| `translations-full.json` | All entries as a JSON array, sorted by `key` |
| `translations-full.csv` | Same fields for Excel/Google Sheets (UTF-8 with BOM) |

## Snapshot

- **Rows (unique keys):** 6,058
- **Source files:** 21 `*.ga.json` translation bundles
- **Generated (UTC):** 2026-10-19 19:43:19 UTC

## Regenerate

From the repository root:

```bash
python tools/export_all_translations.py
```

Optional paths:

```bash
python tools/export_all_translations.py --trans-dir plugins/irish-mod/Translations --export-dir exports
```

Each row includes `key`, `english`, `irish`, `sourceFile`, file-level metadata (`pendingApiKey`, `machineAssisted`, `screen_id`, …), and per-entry `translationMethod`. Keys are deduplicated across files (first file in sorted filename order wins).
