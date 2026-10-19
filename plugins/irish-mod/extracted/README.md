# Extracted English strings (Part 2 spike)

Static dumps of **scoped** UI strings for translation pipeline work. These files are **English-only catalogs** — no Irish text, no runtime replacement.

## Screens

| File | Screen | Keys |
|------|--------|------|
| [`fejd-root-main-menu.json`](fejd-root-main-menu.json) | FejdStartup **root main menu** (Start / Join / Settings / Credits / Quit plus same-view footer links) | 14 |
| [`inventory-panel.json`](inventory-panel.json) | In-game **inventory / player panel** (Tab): tabs, crafting UI, damage types, station level, actions | 61 |
| [`hud-gameplay.json`](hud-gameplay.json) | In-game **HUD**: hotbar, build menu chrome, map pins, taming, emotes, snap points | 127 (`hud_*`) |
| [`character-ui.json`](character-ui.json) | **Skills**, **stats**, and **character customization** labels | 150 (`skill_*`, `stat_*`, `customization_*`) |
| [`building-ui.json`](building-ui.json) | Common **hammer / build menu** piece names (curated `piece_*`) | 100 |

| [`item-names.json`](item-names.json) | **Item** display names, descriptions, lore (`item_*`) | 1959 |
| [`piece-names.json`](piece-names.json) | Remaining **building piece** names (`piece_*` after `building-ui`) | 786 |
| [`npc-dialogue.json`](npc-dialogue.json) | **NPC** dialogue (`npc_*`) | 350 |
| [`menus-rest.json`](menus-rest.json) | **Menus** outside Fejd root (`menu_*` except main menu) | 226 |

**Total scoped keys in extracts:** 3773 (4129 wired via matching `Translations/*.ga.json` as of v0.5.0).

### Scope rationale (`fejd-root-main-menu`)

- **Included:** Dictionary keys for the primary title-screen navigation row and auxiliary labels on that same view (`menu_startgame`, `menu_joingame`, `menu_mod_notice`, etc.).
- **Excluded:** Character select, world select, settings sub-panels, join-server UI, and loading/seizure-warning overlays (separate panels).
- **Identity:** Keys match `Localization.Translate` ids (no `$` prefix), sourced from the `localization*` **TextAsset** CSV tables inside `valheim_Data/resources.assets`.

### Scope rationale (`inventory-panel`)

- **Included:** Panel chrome — tab labels, craft/repair/upgrade buttons, damage and resistance types, station level strings, inventory actions (split, transfer, drop), achievements/compendium tab titles.
- **Excluded:** Per-item display names (`$item_*`), hotbar/build HUD (`hud_*`), and container-specific UI outside the player panel.
- **Scope list:** [`tools/scopes/inventory-panel.keys.txt`](../../../tools/scopes/inventory-panel.keys.txt)

### Scope rationale (`hud-gameplay`)

- **Included:** Full `hud_*` prefix from shipped localization (~127 keys): build menu, categories, placement/snap hints, map pins, taming status, emote names, pocket upgrades.
- **Excluded:** Keys already in main menu or inventory scopes; English strings over 80 chars or with embedded newlines (see [`tools/scopes/README.md`](../../../tools/scopes/README.md)).
- **Scope list:** [`tools/scopes/hud-gameplay.keys.txt`](../../../tools/scopes/hud-gameplay.keys.txt)

### Scope rationale (`character-ui`)

- **Included:** All `skill_*`, `stat_*`, and `customization_*` keys passing length filters (skills list, death/exploration stats, beard/hair style names).
- **Excluded:** Lore descriptions, inventory/main menu overlap.
- **Scope list:** [`tools/scopes/character-ui.keys.txt`](../../../tools/scopes/character-ui.keys.txt)

### Scope rationale (`building-ui`)

- **Included:** Curated high-visibility `piece_*` names (stations, structural wood/stone/iron pieces, storage, furniture stacks).
- **Excluded:** Full ~890 `piece_*` surface, description/lore keys, English over 50 chars.
- **Scope list:** [`tools/scopes/building-ui.keys.txt`](../../../tools/scopes/building-ui.keys.txt)

## Regenerate

From repo root (Python 3.10+):

```powershell
pip install -r tools/requirements.txt

python tools/discover_scope_keys.py --prefix hud_ `
  --exclude-file tools/scopes/fejd-root-main-menu.keys.txt `
  --exclude-file tools/scopes/inventory-panel.keys.txt `
  --out tools/scopes/hud-gameplay.keys.txt

python tools/discover_scope_keys.py --prefix skill_ --prefix stat_ --prefix customization_ `
  --exclude-file tools/scopes/fejd-root-main-menu.keys.txt `
  --exclude-file tools/scopes/inventory-panel.keys.txt `
  --out tools/scopes/character-ui.keys.txt

python tools/extract_screen_strings.py `
  --game-path "A:\Steam\steamapps\common\Valheim" `
  --scope tools/scopes/hud-gameplay.keys.txt `
  --screen-id hud-gameplay `
  --screen-title "In-game HUD (hotbar, prompts, build hints)" `
  --scope-notes "All hud_* keys; excludes inventory panel and main menu scopes." `
  --out plugins/irish-mod/extracted/hud-gameplay.json

python tools/extract_screen_strings.py `
  --game-path "A:\Steam\steamapps\common\Valheim" `
  --scope tools/scopes/character-ui.keys.txt `
  --screen-id character-ui `
  --screen-title "Character stats, skills, and customization" `
  --scope-notes "skill_*, stat_*, and customization_* UI strings." `
  --out plugins/irish-mod/extracted/character-ui.json

python tools/extract_screen_strings.py `
  --game-path "A:\Steam\steamapps\common\Valheim" `
  --scope tools/scopes/building-ui.keys.txt `
  --screen-id building-ui `
  --screen-title "Common building pieces (hammer menu)" `
  --scope-notes "Curated piece_* names; see tools/scopes/building-ui.keys.txt." `
  --out plugins/irish-mod/extracted/building-ui.json
```

Each JSON file records `resources_assets_sha256` for the install used at extract time. Re-run after Valheim patches and diff keys or English text before refreshing translation cache.

## Static vs runtime

This spike uses **static extraction only** (UnityPy + CSV parse). A future optional BepInEx dump mode on `Localization.Translate` can validate scope against a live main-menu session; it was not required here because all scoped keys resolve from shipped assets.
