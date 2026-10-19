# Irish Mod (BepInEx plugin)

Valheim BepInEx plugin for Irish (Gaeilge) on scoped UI keys (main menu + in-game inventory panel).

- **GUID:** `com.dennehy95.valheim.irishmod`
- **Version:** `0.3.0`

## Part 3 — scoped Irish (F7 learner mode)

- Harmony postfix on `Localization.Translate` for keys loaded from `Translations/*.ga.json` (main menu + inventory panel).
- **Default:** vanilla English for those keys.
- **Toggle key (default F7):** Irish plus original English in brackets, e.g. `Socruithe [Settings]`.
- Config (`BepInEx/config/com.dennehy95.valheim.irishmod.cfg`): `Display.ToggleIrishKey`, `Display.IrishLearnerModeOnStart`.
- Translations ship as manual Gaeilge (`translationMethod: manual`, `pendingApiKey: true` in JSON) until an API batch pass is run.

## Prerequisites

- [.NET SDK](https://dotnet.microsoft.com/download) (build targets **net472**)
- Valheim with **BepInEx Pack for Valheim** installed (`BepInEx\core\BepInEx.dll` must exist)

## Build

```powershell
cd plugins/irish-mod
dotnet build `
  -p:GamePath="A:\Steam\steamapps\common\Valheim" `
  -p:BepInExPath="$env:APPDATA\Thunderstore Mod Manager\DataFolder\Valheim\profiles\WonPoyuntO_NetworkMods"
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
