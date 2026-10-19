# Localization scope lists

Each `*.keys.txt` file is a newline-separated list of Valheim `Localization.Translate` ids (no `$` prefix). Comment lines start with `#`.

## Filters (batch 2 scopes)

Applied when generating or curating new scopes:

| Filter | Rationale |
|--------|-----------|
| Skip keys already wired in earlier scopes (`fejd-root-main-menu`, `inventory-panel`) | Avoid duplicates in translation cache |
| Max English length **80** chars (building pieces **50**) | Skip lore walls and multi-paragraph tooltips |
| No embedded newlines in English | UI labels only |
| Exclude `*_description`, `*_lore`, `*_tooltip_long`, `*_flavor` | Long-form text low value for first HUD/build pass |
| `hud_*` | Full prefix (~127 keys): hotbar, prompts, map pins, build mode chrome |
| `skill_*`, `stat_*`, `customization_*` | Character / stats / appearance UI |
| `piece_*` | Curated hammer menu names (`building-ui.keys.txt`); not the full ~890 `piece_*` surface |

Regenerate discovery lists:

```powershell
python tools/discover_scope_keys.py --prefix hud_ `
  --exclude-file tools/scopes/fejd-root-main-menu.keys.txt `
  --exclude-file tools/scopes/inventory-panel.keys.txt `
  --out tools/scopes/hud-gameplay.keys.txt

python tools/discover_scope_keys.py --prefix skill_ --prefix stat_ --prefix customization_ `
  --exclude-file tools/scopes/fejd-root-main-menu.keys.txt `
  --exclude-file tools/scopes/inventory-panel.keys.txt `
  --out tools/scopes/character-ui.keys.txt
```

`building-ui.keys.txt` is hand-curated from `piece_*` (stations, structural pieces, doors, storage, common furniture).
