# Part 2 — Where Valheim in-game text lives

Research for the Valheim Irish Mod string catalog and extraction pipeline. **No plugin code changes** in this document; implementation choices for Parts 2–3 are recommendations only.

**Status:** Research note (Oct 2026). Re-validate against your pinned Valheim build when implementing extractors.

---

## Executive summary

| Finding | Implication for this mod |
|--------|---------------------------|
| Base-game strings are **not** loose `English.csv` files under `valheim_Data/`. They live as **CSV inside Unity `TextAsset`s** bundled in `valheim_Data/resources.assets` (and related assets). | Batch extraction needs **asset unpacking** (UnityPy, UABE, or a dedicated tool), not a simple folder scan. |
| Runtime resolution uses **`Localization.instance.Localize(string)`** and an internal **`Translate(string)`** dictionary lookup — **not** `GetText`. | Harmony hooks and dump mode should target **`Localize` / `Translate`** (and language load), not a non-existent `GetText` API. |
| Tokens use a **`$` prefix** in UI strings (e.g. `$item_stoneAxe`); the dictionary key is usually **without** the leading `$`. | Catalog identity should be **localization keys** (e.g. `item_stoneAxe`), with optional metadata for composite strings and `$1` placeholders. |
| Official languages are **columns in the CSV header**; **English** is the primary fallback column when a cell is empty. | Irish can be modeled as **runtime overrides** of English values, or eventually as a new language column in assets (heavier, touches `resources.assets`). |
| **Jötunn** adds mod/community strings via **`CustomLocalization`**, JSON/YAML under `Translations/{LanguageName}/`, and **`community_translation.json`**. | Other mods add keys at runtime; a **static asset dump alone will miss mod content**. |
| Some mods **hardcode English** without `$` tokens. | Full coverage may need **UI text interception** (as in [LocalizationPatcher](https://thunderstore.io/c/valheim/p/Modnet/LocalizationPatcher/)) — out of scope for v1 base-game focus unless explicitly expanded. |

**Recommended Part 2 approach:** **Hybrid** — static baseline from shipped localization assets (or Jötunn’s generated English key list for a given game version) **plus** an optional in-mod **dump mode** that logs `(key, english)` from `Translate` / `Localize` during play to catch updates, mod keys, and edge cases.

---

## 1. Shipped data: `valheim_Data` and Unity assets

### What is on disk

- **`valheim_Data/resources.assets`** (large Unity serialized file) contains multiple localization **`TextAsset`** objects. Community tooling (e.g. [valheim-viet-hoa](https://github.com/monokaijs/valheim-viet-hoa)) reports **several** localization assets in one file (on the order of **thousands of rows** and **thousands of unique keys** per modern build).
- Classic asset names referenced in decompiled / older builds include at least:
  - `localization` — base table loaded via `Resources.Load("localization", typeof(TextAsset))`
  - `localization_extra` — additional rows (loaded through the game’s extended CSV loading path in newer versions)
- There is **no** maintained, user-editable `valheim_Data/Localization/English.json` tree for vanilla Valheim. Patching “vanilla language” by dropping files next to the exe is **not** how the base game works (contrast: some **total conversion** mods ship a replacement `resources.assets`).

### CSV format (conceptual)

Decompiled `Localization.SetupLanguage` (historical reference: [warmcat mirror of `Localization.cs`](http://git.warmcat.org/Valheim/plain/Valheim_v0.141.2_r202102/Valheim/assembly_guiutils/Localization.cs)) shows:

1. First line of the CSV is a **header**: comma-separated **language names** (`English`, `German`, …).
2. Each subsequent row: **key** in column 0, translations in matching language columns.
3. Rows starting with `//` are comments; empty rows skipped.
4. If the selected language cell is empty, the game **falls back to English** (column index 1 in early layouts).

Newer builds add more assets and `LoadCSV`-style loading; treat row counts and asset count as **version-specific** — hash `resources.assets` per Valheim patch.

### Static extraction options

| Method | Pros | Cons |
|--------|------|------|
| **UnityPy / UABE** export of `localization*` TextAssets to CSV/JSON | Complete for **that** `resources.assets` hash; auditable offline | Must re-run on every game update; must parse CSV correctly (quoting, commas) |
| **JötunnDoc English dump** ([English.html](https://valheim-modding.github.io/Jotunn/data/localization/translations/English.html)) | Fast baseline key + English text for a **documented game version** | Generated from a specific Valheim version; not a substitute for hashing your install |
| **Dedicated pipelines** (e.g. valheim-vn `extract` → `catalog.jsonl`) | Manifests, translation memory, validation | Extra tooling; learn from their model for **stable keys** and **source hashes** |

For this mod’s catalog (`key`, `english`, `source_hash`, metadata), prefer extraction that records **`resources.assets` SHA-256** (or equivalent) alongside keys so Part 3 can invalidate cache entries when English changes.

---

## 2. Runtime API: `Localization` (vanilla)

### Entry points (decompiled behavior)

- **`Localization.instance.Localize(string text)`**  
  Scans `text` for `$word` segments; each segment is passed to **`Translate(word)`**; supports placeholders `$1`, `$2`, … via `InsertWords` after token replacement.
- **`Translate(string word)`**  
  - `KEY_*` → keybinding display via `ZInput` / bound key strings.  
  - Otherwise lookup in **`m_translations`** dictionary.  
  - Missing key → returns **`[word]`** (visible bracket form in UI).
- **`SetupLanguage(string language)`**  
  Clears/reloads dictionary from CSV TextAssets for the chosen header column.
- **`GetSelectedLanguage()`** / PlayerPrefs `"language"` — player’s language name string (e.g. `"English"`).

There is **no** `Localization.instance.GetText` in the public Valheim API surfaced by decompilations and mod examples. Project docs should say **`Localize` / `Translate`**.

### UI wiring

- Components like **`Localize`** (`MonoBehaviour`) call `Localization.instance.Localize(transform)` on `Awake` to rewrite child **Unity UI `Text`** strings.
- Much of the game also uses **TextMeshPro**; mod diagnostics often log both **token** (`item.m_itemData.m_shared.m_name`) and **resolved** text via `Localization.instance.Localize(token)`.

### Harmony patch targets (for dump mode and future injection)

| Target | Typical use |
|--------|-------------|
| **`Localization.Translate`** (prefix/postfix) | Log or replace **single token** resolution; best **key identity** for catalog |
| **`Localization.Localize`** (postfix) | Observe **fully expanded** strings (multiple tokens, placeholders) |
| **`Localization.SetupLanguage`** / **`LoadCSV`** (postfix) | Run after tables load: merge Irish map, or dump all keys once |
| **`FejdStartup.Awake`** or menu load | Late enough that `Localization.instance` exists |

**LocalizationCache** (Thunderstore) patches **`LoadCSV`** to cache lookups — useful reference for **where** to hook without replacing entire tables.

**Injection (Part 3) sketch:** keep player on **English** (or selected language) for compatibility, and in a **`Translate` postfix** return Irish from cache when `word` matches a known key; learner mode appends ` [english]` using the original dictionary value. Alternative: register a **custom language column** via asset patch (valheim-vn style) — higher maintenance, not required for a BepInEx-only Thunderstore mod.

---

## 3. Jötunn and mod-added strings

Jötunn is **not required** for vanilla string replacement, but it defines how **most content mods** add text.

- **`LocalizationManager.Instance.GetLocalization()`** → per-mod **`CustomLocalization`**.
- Files: **`Translations/{LanguageName}/*.json`** (Crowdin-style flat map), YAML with YamlDotNet, or code **`AddTranslation("English", dict)`**.
- **`community_translation.json`** is loaded **first** among community files ([`CommunityTranslationFileName`](https://valheim-modding.github.io/Jotunn/api/Jotunn.Managers.LocalizationManager.CommunityTranslationFileName.html)).
- **`LocalizationManager.OnLocalizationAdded`** — fires when custom localizations are merged; resets on menu flow — use for one-shot or re-entrant setup.
- **`TryTranslate(string word)`** — mod tokens first, then vanilla `Translate`.

Example pattern from community translation mods: Harmony **postfix on `SetupLanguage`** → `GetLocalization().AddJsonFile("Russian", …)` from config folder.

**For Irish Mod v1:** base game keys from assets; optionally log **unknown** `[token]` or Jötunn keys seen at runtime. Supporting **every** third-party mod’s hardcoded English is a separate problem ([LocalizationPatcher](https://thunderstore.io/c/valheim/p/Modnet/LocalizationPatcher/) patches `Localize`/`Translate` **and** `TMP_Text.text` / `UI.Text.text`).

---

## 4. How existing translation mods approach strings

| Approach | Examples | Fits Irish Mod? |
|----------|----------|-----------------|
| **Replace `resources.assets`** with new language columns | Older [valheim-ja](https://github.com/Gedevan-Aleksizde/valheim-ja), valheim-vn **build-assets** | Possible for “official” Irish language; **not** ideal for Thunderstore + learner toggle + AI cache |
| **Jötunn `community_translation.json`** | valheim-vn **export-json**, RelicHeim-style JSON drops | Good **delivery** format for a frozen cache; still need extract + AI pipeline |
| **Runtime Harmony on `Localization`** | LocalizationPatcher, Russian patch mods | Best match for **dynamic cache** and **learner suffix** without patching game files |
| **Asset + SQLite TM** | valheim-vn | Reference architecture for **Part 3** batch translate and validation |

---

## 5. File scan vs runtime logging tool

### Static file scan (install dir)

**Required** for a complete **vanilla** baseline:

- Target: `valheim_Data/resources.assets` (and any additional bundles your build uses for localization TextAssets).
- Output: `catalog.json` / JSONL with `{ "key", "english", "asset", "row" }`.
- Run in CI or dev script when Valheim updates; compare manifest hash to published mod README.

**Insufficient alone** for:

- Keys added only when DLC/patches load extra CSVs at runtime (usually still in assets, but multiple files).
- **Mod** content (Jötunn, hardcoded strings).
- Strings that only appear as **composed** `Localize` input without a single dictionary key (rarer).

### Runtime dump mode (BepInEx config flag)

**Recommended complement:**

- Patch `Translate` with a config flag `DumpStrings=true`.
- Log `key` + resolved English (and language) to `BepInEx/config/.../string-dump.jsonl`.
- Dedupe in post-processing; merge into master catalog.
- Playthrough or scripted dev world tour for UI surfaces (inventory, map, boss UI, settings).

### Third-party baseline without unpacking

- Use Jötunn **English** dump for the **same version** you ship against as a **sanity check** (key coverage diff), not as the legal/source-of-truth extract without matching hashes.

---

## 6. String identity and catalog schema (proposal)

Align with `VALHEIM_IRISH_MOD.md` Part 2 goals:

```json
{
  "key": "item_stoneAxe",
  "english": "Stone axe",
  "source_hash": "sha256-of-english-at-extract-time",
  "categories": ["item"],
  "notes": "optional: KEY_ binding, placeholders"
}
```

Rules:

- Prefer **dictionary keys** over hashing English body text.
- Store **raw** English from the English column / `Translate` before any mod override.
- For `Localize` strings with multiple `$` tokens, catalog **each token** separately; store composite patterns only for analysis.
- **`KEY_*` tokens:** catalog as keys but mark `type: "keybinding"` — Irish may still want surrounding sentence translated.

---

## 7. Open questions to close in implementation spikes

1. **Exact TextAsset names and loader paths** on the Valheim version pinned in the mod README (post–Ashlands / Unity 6 era builds).
2. Whether **`LoadCSV`** is the stable hook name across versions (vs only `SetupLanguage`).
3. **Client-only UI** vs any server-visible localized strings (multiplayer).
4. **Performance:** size of full key set (~4k+) loaded into memory vs lazy load from cache on first `Translate`.
5. **Irish as language:** add `language_irish` token + column vs always override while language stays English.

---

## 8. Suggested next implementation steps (Part 2 build)

1. Pin Valheim build; record `resources.assets` hash.
2. Prototype extractor (Python + UnityPy or small C# one-off) → `strings/en-baseline.json`.
3. Add optional **dump mode** design doc / follow-up PR (Harmony on `Translate` only).
4. Diff baseline against [Jötunn English list](https://valheim-modding.github.io/Jotunn/data/localization/translations/English.html) for the same version.
5. Hand off stable keys to Part 3 translation cache.

---

## References

- [Jötunn — Localization tutorial](https://valheim-modding.github.io/Jotunn/tutorials/localization.html)
- [Jötunn — LocalizationManager API](https://valheim-modding.github.io/Jotunn/api/Jotunn.Managers.LocalizationManager.html)
- [Jötunn — English key dump (versioned)](https://valheim-modding.github.io/Jotunn/data/localization/translations/English.html)
- [Valheim-Modding Wiki — Key binding strings (`$KEY_`)](https://github.com/Valheim-Modding/Wiki/wiki/Key-Binding-Strings)
- Decompiled `Localization.cs` (historical): [warmcat mirror](http://git.warmcat.org/Valheim/plain/Valheim_v0.141.2_r202102/Valheim/assembly_guiutils/Localization.cs)
- [valheim-viet-hoa](https://github.com/monokaijs/valheim-viet-hoa) — asset extraction, catalog, Jötunn JSON export
- [LocalizationPatcher](https://thunderstore.io/c/valheim/p/Modnet/LocalizationPatcher/) — Harmony on `Localize`/`Translate` and UI text setters
- [blaxxun-boop/LocalizationManager](https://github.com/blaxxun-boop/LocalizationManager) — lightweight mod localization helper
