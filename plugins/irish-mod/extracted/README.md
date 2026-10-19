# Extracted English strings (Part 2 spike)

Static dumps of **scoped** UI strings for translation pipeline work. These files are **English-only catalogs** — no Irish text, no runtime replacement.

## Screens

| File | Screen | Keys |
|------|--------|------|
| [`fejd-root-main-menu.json`](fejd-root-main-menu.json) | FejdStartup **root main menu** (Start / Join / Settings / Credits / Quit plus same-view footer links) | See `key_count` in file |
| [`inventory-panel.json`](inventory-panel.json) | In-game **inventory / player panel** (Tab): tabs, crafting UI, damage types, station level, actions | 61 (`inventory_*` prefix) |

### Scope rationale (`fejd-root-main-menu`)

- **Included:** Dictionary keys for the primary title-screen navigation row and auxiliary labels on that same view (`menu_startgame`, `menu_joingame`, `menu_mod_notice`, etc.).
- **Excluded:** Character select, world select, settings sub-panels, join-server UI, and loading/seizure-warning overlays (separate panels).
- **Identity:** Keys match `Localization.Translate` ids (no `$` prefix), sourced from the `localization*` **TextAsset** CSV tables inside `valheim_Data/resources.assets`.

### Scope rationale (`inventory-panel`)

- **Chosen over `hud_*`:** The `inventory_*` prefix maps cleanly to the Tab inventory/crafting/stats panel (61 keys) without pulling in the much larger hotbar, build menu, emote, and map-pin HUD surface (~200+ `hud_*` keys).
- **Included:** Panel chrome — tab labels, craft/repair/upgrade buttons, damage and resistance types, station level strings, inventory actions (split, transfer, drop), achievements/compendium tab titles.
- **Excluded:** Per-item display names (`$item_*`), hotbar/build HUD (`hud_*`), and container-specific UI outside the player panel.
- **Scope list:** [`tools/scopes/inventory-panel.keys.txt`](../../../tools/scopes/inventory-panel.keys.txt)

## Regenerate

From repo root (Python 3.10+):

```powershell
pip install -r tools/requirements.txt
python tools/extract_screen_strings.py `
  --game-path "A:\Steam\steamapps\common\Valheim" `
  --scope tools/scopes/fejd-root-main-menu.keys.txt `
  --screen-id fejd-root-main-menu `
  --screen-title "FejdStartup root main menu" `
  --scope-notes "Primary title-screen navigation and same-view footer links; excludes character/world select and settings sub-panels." `
  --out plugins/irish-mod/extracted/fejd-root-main-menu.json

python tools/extract_screen_strings.py `
  --game-path "A:\Steam\steamapps\common\Valheim" `
  --scope tools/scopes/inventory-panel.keys.txt `
  --screen-id inventory-panel `
  --screen-title "In-game inventory and player panel" `
  --scope-notes "All inventory_* keys for Tab inventory/crafting/stats; excludes hud_* and item names." `
  --out plugins/irish-mod/extracted/inventory-panel.json
```

Each JSON file records `resources_assets_sha256` for the install used at extract time. Re-run after Valheim patches and diff keys or English text before refreshing translation cache.

## Static vs runtime

This spike uses **static extraction only** (UnityPy + CSV parse). A future optional BepInEx dump mode on `Localization.Translate` can validate scope against a live main-menu session; it was not required here because all scoped keys resolve from shipped assets.
