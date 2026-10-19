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

## Batch 3 scopes

| File | Prefix | Keys |
|------|--------|------|
| `settings-ui.keys.txt` | `settings_*` | ~222 — full settings menus |
| `gameplay-messages.keys.txt` | `msg_*` | ~134 — gameplay toasts / feedback |

Regenerate:

```powershell
python tools/discover_scope_keys.py --prefix settings_ `
  --exclude-file tools/scopes/fejd-root-main-menu.keys.txt `
  --exclude-file tools/scopes/inventory-panel.keys.txt `
  --exclude-file tools/scopes/hud-gameplay.keys.txt `
  --exclude-file tools/scopes/character-ui.keys.txt `
  --exclude-file tools/scopes/building-ui.keys.txt `
  --out tools/scopes/settings-ui.keys.txt

python tools/discover_scope_keys.py --prefix msg_ `
  --exclude-file tools/scopes/fejd-root-main-menu.keys.txt `
  --exclude-file tools/scopes/inventory-panel.keys.txt `
  --exclude-file tools/scopes/hud-gameplay.keys.txt `
  --exclude-file tools/scopes/character-ui.keys.txt `
  --exclude-file tools/scopes/building-ui.keys.txt `
  --out tools/scopes/gameplay-messages.keys.txt
```

## Batch 4 — item names (`item_*`)

| File | Prefix | Keys |
|------|--------|------|
| `item-names.keys.txt` | `item_` | ~1959 — all item display names, descriptions, and lore (no UI-length filter) |

Regenerate scope + extract + translations:

```powershell
python tools/generate_item_names_scope.py

python tools/extract_screen_strings.py `
  --scope tools/scopes/item-names.keys.txt `
  --screen-id item-names `
  --screen-title "Item names and descriptions" `
  --out plugins/irish-mod/extracted/item-names.json

pip install argostranslate
python tools/build_item_mt_cache.py
python tools/generate_item_names_irish_map.py
python tools/build_ga_from_extract.py `
  --extract plugins/irish-mod/extracted/item-names.json `
  --irish-map tools/item-names_irish_map.json `
  --out plugins/irish-mod/Translations/item-names.ga.json `
  --screen-id item-names
```

## Batch 5 — piece names, NPC dialogue, menus (`piece_*`, `npc_*`, `menu_*`)

| File | Prefix | Keys |
|------|--------|------|
| `piece-names.keys.txt` | `piece_` | ~786 — remaining after `building-ui.ga.json` |
| `npc-dialogue.keys.txt` | `npc_` | ~350 |
| `menus-rest.keys.txt` | `menu_` | ~226 — excludes `fejd-root-main-menu` |

Regenerate scopes + full pipeline per batch:

```powershell
python tools/generate_prefix_scope.py --prefix piece_ --out tools/scopes/piece-names.keys.txt
python tools/run_coverage_batch.py --scope tools/scopes/piece-names.keys.txt --screen-id piece-names --screen-title "Building piece names" --extract plugins/irish-mod/extracted/piece-names.json --irish-map tools/piece-names_irish_map.json --ga-out plugins/irish-mod/Translations/piece-names.ga.json
```

(Same pattern for `npc-dialogue` and `menus-rest`.)

## Batch 6 — status effects, fallen warrior, tutorial (`se_*`, `fallenwarrior_*`, `tutorial_*`)

| File | Prefix | Keys |
|------|--------|------|
| `status-effects.keys.txt` | `se_` | 223 |
| `fallen-warrior.keys.txt` | `fallenwarrior_` | 202 |
| `tutorial.keys.txt` | `tutorial_` | 165 |

```powershell
python tools/generate_prefix_scope.py --prefix se_ --out tools/scopes/status-effects.keys.txt
python tools/run_coverage_batch.py --scope tools/scopes/status-effects.keys.txt --screen-id status-effects --screen-title "Status effects" --extract plugins/irish-mod/extracted/status-effects.json --irish-map tools/status-effects_irish_map.json --ga-out plugins/irish-mod/Translations/status-effects.ga.json
```

(Same pattern for `fallen-warrior` and `tutorial`.)

## Batch 7 — lore, enemy names, captions (`lore_*`, `enemy_*`, `caption_*`)

| File | Prefix | Keys |
|------|--------|------|
| `lore.keys.txt` | `lore_` | 144 |
| `enemy-names.keys.txt` | `enemy_` | 138 |
| `captions.keys.txt` | `caption_` | 132 |

```powershell
python tools/generate_prefix_scope.py --prefix lore_ --out tools/scopes/lore.keys.txt
python tools/run_coverage_batch.py --scope tools/scopes/lore.keys.txt --screen-id lore --screen-title "Lore text" --extract plugins/irish-mod/extracted/lore.json --irish-map tools/lore_irish_map.json --ga-out plugins/irish-mod/Translations/lore.ga.json
```

(Same pattern for `enemy-names` and `captions`.)

Vanilla key census: `python tools/count_vanilla_keys.py`.
