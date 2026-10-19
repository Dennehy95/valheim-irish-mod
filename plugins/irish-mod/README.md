# Irish Mod (BepInEx plugin)

Valheim BepInEx plugin for Irish (Gaeilge) on scoped localization keys (menus, HUD, settings, and item names).

- **GUID:** `com.dennehy95.valheim.irishmod`
- **Version:** `1.0.0`

## Part 3 — scoped Irish (F8 display cycle)

- Harmony postfix on `Localization.Translate` for keys loaded from `Translations/*.ga.json` (main menu + inventory panel).
- **Default on start:** vanilla English for those wired keys (mode 0).
- **Toggle key (default F8)** cycles three modes, then repeats:
  1. **English only** (vanilla)
  2. **Irish + `[English]`** learner brackets, e.g. `Socruithe [Settings]`
  3. **Irish only** (no brackets)
- Default **F8** avoids **F7**, which **ValheimPerformanceOverhaul** often binds on the same profile.
- Config (`BepInEx/config/com.dennehy95.valheim.irishmod.cfg`): `Display.ToggleIrishKey`, `Display.IrishDisplayModeOnStart` (`0`–`2` matching the list above).
- Pressing the toggle key calls `ReLocalizeAll` on the main menu (`FejdStartup`) and inventory UI (`InventoryGui`) when present so visible text updates immediately.
- Translations ship as manual Gaeilge (`translationMethod: manual`, `pendingApiKey: true`, `machineAssisted: false` in JSON) until an API batch pass is run.
- **Item names batch (`item-names.ga.json`):** ~1959 `item_*` keys. Initial Irish strings were produced with offline Argos `en→ga` plus glossary overrides; treat long descriptions as **placeholder-quality** until a human or API review pass.
- **v0.5.0 coverage batches:** `piece-names.ga.json` (~786), `npc-dialogue.ga.json` (~350), `menus-rest.ga.json` (~226) — same Argos + rule fallback pipeline; QA pass deferred.
- **v0.6.0 coverage batches:** `status-effects.ga.json` (223), `fallen-warrior.ga.json` (202), `tutorial.ga.json` (165) — same pipeline; QA pass deferred.
- **v0.7.0 coverage batches:** `lore.ga.json` (144), `enemy-names.ga.json` (138), `captions.ga.json` (132) — same pipeline; QA pass deferred.
- **v0.8.0 coverage batches:** `achievements.ga.json` (110), `fallen.ga.json` (80), `events.ga.json` (54) — same pipeline; QA pass deferred.
- **v1.0.0 final sweep:** `remainder.ga.json` (681) — all remaining vanilla keys (platform UI, load screens, skills gap, `#piece_sapcollector_check`, etc.); **100%** of 6,058 unique `resources.assets` keys wired. Same Argos + rule pipeline; QA pass deferred.

## Prerequisites

- [.NET SDK](https://dotnet.microsoft.com/download) (build targets **net472**)
- Valheim with **BepInEx Pack for Valheim** installed (`BepInEx\core\BepInEx.dll` must exist)

## Build

```powershell
cd plugins/irish-mod
dotnet build `
  -p:GamePath="A:\Steam\steamapps\common\Valheim" `
  -p:BepInExPath="$env:APPDATA\Thunderstore Mod Manager\DataFolder\Valheim\profiles\Irish Mod Testing"
```

`GamePath` is the Steam game folder; `BepInExPath` is the Thunderstore profile that holds BepInEx core on Dennehy-Desktop.

## Install

1. Build Release or Debug.
2. Copy `bin/Debug/net472/IrishMod.dll` and the `Translations` folder to your Valheim folder:

   `BepInEx/plugins/Dennehy95-Valheim_Irish_Mod/IrishMod.dll`  
   `BepInEx/plugins/Dennehy95-Valheim_Irish_Mod/Translations/*.ga.json`

3. Repeat on the **dedicated server** Valheim install if you mirror client plugins there.

4. Launch Valheim; check `BepInEx/LogOutput.log` for:

   `Valheim Irish Mod 0.1.0 loaded.`

## Thunderstore (later)

Packaging (`manifest.json`, dependencies on `denikson-BepInExPack_Valheim`, etc.) is planned after hooks and translations exist.
