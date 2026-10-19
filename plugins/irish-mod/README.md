# Irish Mod (BepInEx plugin)

Minimal Valheim BepInEx plugin for the Irish language learning mod (slice 1: load + log only).

- **GUID:** `com.dennehy95.valheim.irishmod`
- **Version:** `0.1.0`

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
2. Copy `bin/Debug/net472/IrishMod.dll` (or `bin/Release/net472/`) to your Valheim folder:

   `BepInEx/plugins/IrishMod/IrishMod.dll` (Thunderstore profile or Steam overlay)

3. Repeat on the **dedicated server** Valheim install if you mirror client plugins there.

4. Launch Valheim; check `BepInEx/LogOutput.log` for:

   `Valheim Irish Mod 0.1.0 loaded.`

## Thunderstore (later)

Packaging (`manifest.json`, dependencies on `denikson-BepInExPack_Valheim`, etc.) is planned after hooks and translations exist.
