# Translation issues log

Add new entries at the top. Keep `status` as `open` | `fixed` | `wontfix`.

---

## Stone axe — tool name word order

| Field | Value |
|-------|--------|
| **Keys** | `item_axe_stone` |
| **English** | Stone Axe |
| **Current Irish** (`item-names.ga.json`) | `Axe Cloch` |
| **Symptom** | Tool name reads like English compound order (English *Axe* + Irish *Cloch*). In-game / review may also show variants such as **Cloch Tuagh**; target natural Irish tool naming, e.g. **Tuagh cloch** (noun + modifier), not modifier-first English order. |
| **Category** | `word-order` |
| **Status** | `open` |
| **Source** | `plugins/irish-mod/Translations/item-names.ga.json` |

Related (description, separate pass): `item_axe_stone_description` — English: *A crude axe for tree-felling.* — Irish: `A tua amh do crainn - leagan.`

---

## Raspberries — missing / partial Irish in learner tooltip

| Field | Value |
|-------|--------|
| **Keys** | `item_raspberries`, `item_raspberries_description` |
| **English** | Raspberries / Sweet and delicious. |
| **Current Irish** (`item-names.ga.json`) | `Sútha craobh` / `Sweet agus delicious.` |
| **Symptom** | Inventory tooltip in **learner mode**: display `Raspberries [Raspberries]` (no real Irish in the primary slot—reads as English fallback). Description: `Sweet agus delicious [Sweet and delicious.]` — obvious partial MT on the description key. |
| **Category** | `missing-translation` (display name in-game) · `partial-mt` (description) |
| **Status** | `open` |
| **Source** | `plugins/irish-mod/Translations/item-names.ga.json` |

**Note:** If the repo already has `Sútha craobh` for `item_raspberries` but the game still shows English, verify the built plugin ships the latest `item-names.ga.json` and that runtime lookup uses `item_raspberries` (not an alias key).
