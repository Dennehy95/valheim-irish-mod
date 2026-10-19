# Valheim Irish Mod

BepInEx plugin for [Valheim](https://store.steampowered.com/app/892970/Valheim/) that will replace in-game **text** with Irish (Gaeilge) translations, with an optional learner mode showing the original English in brackets (e.g. `Dia dhuit [Hello]`). Audio is out of scope.

**Status:** Slice 1 — minimal plugin that loads and logs to the BepInEx console. String extraction, AI translation, and keybind toggles come in later slices.

## Stack

- Steam Valheim + [BepInEx](https://thunderstore.io/c/valheim/p/denikson/BepInExPack_Valheim/) (Thunderstore / mod manager workflow)
- Client and dedicated server: install the built DLL under `BepInEx/plugins/`

## Project layout

| Path | Purpose |
|------|---------|
| `VALHEIM_IRISH_MOD.md` | Full project overview and roadmap |
| `plugins/irish-mod/` | C# BepInEx plugin (`IrishMod.dll`) |

## Build

From `plugins/irish-mod/`:

```powershell
dotnet build `
  -p:GamePath="A:\Steam\steamapps\common\Valheim" `
  -p:BepInExPath="$env:APPDATA\Thunderstore Mod Manager\DataFolder\Valheim\profiles\WonPoyuntO_NetworkMods"
```

- `GamePath` — Steam Valheim folder (`valheim.exe`, `valheim_Data\Managed\`).
- `BepInExPath` — folder that contains a full **BepInEx core** (`BepInEx\core\BepInEx.dll`). With Thunderstore Mod Manager, that is usually the active **profile** directory, not the bare Steam install (which may only have leftover `BepInEx\plugins` from launches).

If both live in one folder, omit `BepInExPath` (it defaults to `GamePath`).

## Install (manual)

Copy `plugins/irish-mod/bin/Debug/net472/IrishMod.dll` (or Release) to:

- `%Valheim%\BepInEx\plugins\IrishMod.dll`

Use the same layout on a dedicated server if you run server-side plugins.

## License

TBD.
