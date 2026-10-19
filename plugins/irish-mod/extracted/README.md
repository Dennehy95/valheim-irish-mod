# Extracted English strings (Part 2 spike)

Static dumps of **scoped** UI strings for translation pipeline work. These files are **English-only catalogs** — no Irish text, no runtime replacement.

## Screens

| File | Screen | Keys |
|------|--------|------|
| [`fejd-root-main-menu.json`](fejd-root-main-menu.json) | FejdStartup **root main menu** (Start / Join / Settings / Credits / Quit plus same-view footer links) | See `key_count` in file |

### Scope rationale (`fejd-root-main-menu`)

- **Included:** Dictionary keys for the primary title-screen navigation row and auxiliary labels on that same view (`menu_startgame`, `menu_joingame`, `menu_mod_notice`, etc.).
- **Excluded:** Character select, world select, settings sub-panels, join-server UI, and loading/seizure-warning overlays (separate panels).
- **Identity:** Keys match `Localization.Translate` ids (no `$` prefix), sourced from the `localization*` **TextAsset** CSV tables inside `valheim_Data/resources.assets`.

## Regenerate

From repo root (Python 3.10+):

```powershell
pip install -r tools/requirements.txt
python tools/extract_screen_strings.py `
  --game-path "A:\Steam\steamapps\common\Valheim" `
  --scope tools/scopes/fejd-root-main-menu.keys.txt `
  --screen-id fejd-root-main-menu `
  --out plugins/irish-mod/extracted/fejd-root-main-menu.json
```

Each JSON file records `resources_assets_sha256` for the install used at extract time. Re-run after Valheim patches and diff keys or English text before refreshing translation cache.

## Static vs runtime

This spike uses **static extraction only** (UnityPy + CSV parse). A future optional BepInEx dump mode on `Localization.Translate` can validate scope against a live main-menu session; it was not required here because all scoped keys resolve from shipped assets.
