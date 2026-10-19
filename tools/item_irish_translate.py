"""Best-effort Gaeilge for Valheim item_* strings (rule-based, no MT API)."""

from __future__ import annotations

import re

# Valheim / Norse proper nouns — keep as-is in output.
PROPER_NOUNS: frozenset[str] = frozenset(
    {
        "Dyrnwyn",
        "Asksvin",
        "Eitr",
        "Yagluth",
        "Bonemass",
        "Moder",
        "Eikthyr",
        "The Elder",
        "Odin",
        "Valheim",
        "Mistlands",
        "Ashlands",
        "Black Forest",
        "Deep North",
        "Draumyx",
        "Grimvarn",
        "Solryth",
        "Veydris",
        "Megingjord",
        "Dvergr",
        "Fader",
        "Bjorn",
        "Björn",
        "Lox",
        "Ymir",
        "Haldor",
        "Hildir",
        "Halstein",
        "Fenring",
        "Kvastur",
        "Kvasturr",
        "Karve",
        "Drakkar",
        "Serpent",
        "Surtrling",
        "Surtling",
        "Bonemaw",
        "Seeker",
        "Gjall",
        "Niedhogg",
        "Eldner",
        "Berzerkr",
        "Fenris",
    }
)

EXACT: dict[str, str] = {
    "Armour": "Armúr",
    "Armor": "Armúr",
    "Amber": "Ómra",
    "Amber Pearl": "Pearla Ómra",
    "Ancient Coin": "Bonn Ársa",
    "Ancient Seed": "Síol Ársa",
    "Ancient Root": "Fréamh Ársa",
    "Wood Arrow": "Saighead adhmaid",
    "Bronzehead Arrow": "Saighead chré-umha",
    "Flinthead Arrow": "Saighead chlochóige",
    "Ironhead Arrow": "Saighead iarainn",
    "Silver Arrow": "Saighead airgid",
    "Fire Arrow": "Saighead tine",
    "Frost Arrow": "Saighead sioc",
    "Poison Arrow": "Saighead nimhe",
    "Obsidian Arrow": "Saighead obsaidian",
    "Needle Arrow": "Saighead snáthaid",
    "Charred Arrow": "Saighead dóite",
    "Carapace Arrow": "Saighead bhlaoscach",
    "Bloodgold Arrow": "Saighead fola-óir",
    "<color=yellow>Valuable</color>": "<color=yellow>Luachmhar</color>",
    "The ancient root seems all dried up": "Is cosúil go bhfuil an fréamh ársa triomaithe go hiomlán",
    "The ancient root is pulsating with energy": "Tá an fréamh ársa ag pulsáil le fuinneamh",
    "The ancient root's glow is fading": "Tá lonradh an fhreamha ársa ag laigsiú",
}

# English word / token -> Irish (lowercase keys).
WORDS: dict[str, str] = {
    "a": "a",
    "an": "an",
    "the": "an",
    "of": "de",
    "and": "agus",
    "or": "nó",
    "for": "do",
    "with": "le",
    "from": "ó",
    "in": "i",
    "on": "ar",
    "to": "chun",
    "your": "do",
    "you": "tú",
    "it": "é",
    "its": "a",
    "this": "seo",
    "that": "sin",
    "one": "ceann",
    "all": "gach",
    "some": "roinnt",
    "very": "an-",
    "old": "sean",
    "ancient": "ársa",
    "wood": "adhmad",
    "wooden": "adhmaid",
    "stone": "cloch",
    "flint": "clochóir",
    "bronze": "cré-umha",
    "iron": "iarann",
    "silver": "airgead",
    "black": "dubh",
    "metal": "miotail",
    "copper": "copar",
    "tin": "stán",
    "gold": "ór",
    "bloodgold": "fola-óir",
    "crystal": "criostal",
    "bone": "cnámh",
    "skull": "cailleach",
    "ribcage": "cageán coirp",
    "rib": "easna",
    "hide": "craiceann",
    "leather": "leathar",
    "meat": "feoil",
    "cooked": "rósta",
    "raw": "amh",
    "uncooked": "amh",
    "egg": "ubh",
    "tail": "eireaball",
    "head": "ceann",
    "blade": "lann",
    "sword": "claidheamh",
    "axe": "tuagh",
    "hammer": "casúr",
    "mace": "maide",
    "knife": "scian",
    "spear": "sleá",
    "bow": "bogha",
    "arrow": "saighead",
    "shield": "sciath",
    "helmet": "clogad",
    "chest": "ucht",
    "legs": "cosa",
    "cape": "cóta",
    "armor": "armúr",
    "armour": "armúr",
    "chestplate": "briogáid",
    "pants": "brístí",
    "boots": "bróga",
    "ring": "fáinne",
    "necklace": "muince",
    "amulet": "pónaire",
    "belt": "crios",
    "cloak": "cóta",
    "seed": "síol",
    "root": "fréamh",
    "berry": "caor",
    "mushroom": "muisiriún",
    "fish": "iasc",
    "honey": "meala",
    "sap": "sú",
    "resin": "roisín",
    "tar": "tár",
    "oil": "ola",
    "coal": "guail",
    "ore": "mianach",
    "scrap": "scrios",
    "fragment": "crios",
    "shard": "smior",
    "tip": "barr",
    "hilt": "hilt",
    "handle": "lámh",
    "pole": "cuaille",
    "atgeir": "atgeir",
    "pickaxe": "piocóid",
    "hoe": "grafán",
    "rake": "ráca",
    "scythe": "speal",
    "club": "maide",
    "staff": "bata",
    "wand": "slat",
    "torch": "tóirse",
    "lantern": "laindéir",
    "candle": "coinneal",
    "fire": "tine",
    "frost": "sioc",
    "poison": "nimh",
    "obsidian": "obsaidian",
    "carapace": "blaosc",
    "needle": "snáthaid",
    "charred": "dóite",
    "vile": "gránna",
    "relic": "seoda",
    "coin": "bonn",
    "gem": "seoid",
    "pearl": "pearl",
    "valuable": "luachmhar",
    "potion": "posóid",
    "mead": "mead",
    "wine": "fíon",
    "ale": "leann",
    "bread": "arán",
    "stew": "stobhach",
    "soup": "anraith",
    "sausage": "ispín",
    "queen": "banríon",
    "king": "rí",
    "dragon": "dragún",
    "serpent": "nathair",
    "wolf": "mac tíre",
    "boar": "torc",
    "deer": "fia",
    "lox": "lox",
    "trophy": "trófaí",
    "troll": "troll",
    "goblin": "goblin",
    "dvergr": "dvergr",
    "seeker": "cuardaí",
    "soldier": "saighdiúir",
    "brute": "bruíon",
    "shaman": "seamhnóir",
    "berserker": "berserker",
    "cultist": "cultach",
    "growth": "fás",
    "vine": "féar",
    "plant": "planda",
    "tree": "crann",
    "fine": "mín",
    "core": "croí",
    "plank": "clár",
    "beam": "tráth",
    "nail": "tairne",
    "chain": "slabhra",
    "rope": "ròpa",
    "portal": "portán",
    "marble": "marmar",
    "granite": "eibhear",
    "blackmetal": "dubh-mhiotail",
    "scale": "scála",
    "feather": "cleite",
    "wing": "sciathán",
    "eye": "súil",
    "heart": "croí",
    "tusk": "starrfhiacail",
    "fang": "fiacail",
    "claw": "crúb",
    "horn": "adharc",
    "antler": "adharca",
    "pelt": "craiceann",
    "fur": "fionnadh",
    "linen": "linín",
    "wool": "olann",
    "thread": "snáth",
    "yarn": "snáth",
    "fabric": "éadach",
    "rune": "rún",
    "scroll": "scrúdú",
    "key": "eochair",
    "map": "léarscáil",
    "cart": "cairt",
    "wagon": "vaigín",
    "boat": "bád",
    "raft": "ráta",
    "longship": "long",
    "bed": "leaba",
    "chair": "cathaoir",
    "table": "bord",
    "bench": "binse",
    "stool": "stól",
    "rug": "ruga",
    "banner": "bratach",
    "sign": "comhartha",
    "box": "bosca",
    "barrel": "baraille",
    "crate": "creat",
    "sack": "sac",
    "bag": "mála",
    "tankard": "pionta",
    "tank": "tanc",
    "turret": "túr",
    "trap": "ribe",
    "bomb": "buama",
    "explosive": "pléascach",
    "ooze": "salachar",
    "slime": "slaim",
    "guck": "guck",
    "eitr": "eitr",
    "mist": "ceo",
    "fog": "ceo",
    "ash": "luaith",
    "ember": "ló",
    "saddle": "diallait",
    "harness": "harnais",
    "collar": "muince",
    "lure": "mealltóir",
    "bait": "mealladh",
    "fishing": "iascaireacht",
    "rod": "slat",
    "hook": "crúca",
    "line": "líne",
    "net": "líon",
    "medium": "meánach",
    "heavy": "trom",
    "light": "éadrom",
    "small": "beag",
    "large": "mór",
    "great": "mór",
    "lesser": "níos lú",
    "greater": "níos mó",
    "sharp": "géar",
    "hard": "crua",
    "soft": "bog",
    "wet": "fliuch",
    "dry": "tirim",
    "hot": "te",
    "cold": "fuar",
    "dark": "dorcha",
    "bright": "geal",
    "green": "glas",
    "red": "dearg",
    "blue": "gorm",
    "yellow": "buí",
    "purple": "corcra",
    "orange": "oráiste",
    "white": "bán",
    "grey": "liath",
    "gray": "liath",
    "broken": "briste",
    "crude": "amh",
    "fine": "mín",
    "quality": "cáilíocht",
    "reinforced": "neartaithe",
    "polished": "snasta",
    "forged": "cruthaithe",
    "crafted": "déanta",
    "magical": "draíochta",
    "cursed": "mallachta",
    "blessed": "beannaithe",
    "powerful": "cumhachtach",
    "deadly": "marfach",
    "sturdy": "crua",
    "fragile": "leochail",
    "perfect": "foirfe",
    "savage": "fiáin",
    "wild": "fiáin",
    "lost": "caillte",
    "forgotten": "dearmadta",
    "mysterious": "mistéireach",
    "strange": "ainnis",
    "rare": "annamh",
    "common": "coitianta",
    "unique": "uathúil",
    "legendary": "finscéalta",
    "hold": "coinnigh",
    "held": "coinnithe",
    "against": "in aghaidh",
    "ear": "cluas",
    "hear": "cloisteáil",
    "whisperings": "cogarnaíl",
    "within": "laistigh",
    "surface": "dromchla",
    "still": "fós",
    "bears": "iompraíonn",
    "trace": "rian",
    "symbols": "siombailí",
    "age": "aois",
    "world": "domhan",
    "materials": "ábhair",
    "hardest": "is cruaille",
    "perhaps": "b'fhéidir",
    "messenger": "teachtaire",
    "death": "bás",
    "sleek": "sleamhain",
    "sharper": "níos géire",
    "than": "ná",
    "flinthead": "clochóige",
    "bronzehead": "cré-umha",
    "ironhead": "iarainn",
    "pointy": "géar",
    "heavy": "trom",
    "gonna": "beidh",
    "hurt": "gortú",
    "hurt.": "gortú",
    "likely": "is dócha",
    "could": "d'fhéadfadh",
    "might": "d'fhéadfadh",
    "would": "d'fhéadfadh",
    "if": "má",
    "had": "ag",
    "have": "ag",
    "has": "ag",
    "seems": "is cosúil",
    "pulsating": "ag pulsáil",
    "energy": "fuinneamh",
    "glow": "lonradh",
    "fading": "ag laigsiú",
    "dried": "triomaithe",
    "up": "suas",
    "parts": "páirteanna",
    "pieces": "píosaí",
    "piece": "píosa",
    "reassembled": "athchóirithe",
    "reforged": "athchruthaithe",
    "reforge": "athchruthú",
    "long": "fada",
    "forgotten": "dearmadta",
    "sword": "claidheamh",
    "shard": "smior",
    "looks": "breathnaíonn",
    "like": "cosúil",
    "able": "ábalta",
    "made": "déanta",
    "mad": "déanta",
    "armour": "armúr",
    "armor": "armúr",
    "forging": "cruthú",
    "bears": "iompraíonn",
    "fur": "fionnadh",
    "strength": "neart",
    "relic": "seoda",
    "smooth": "mín",
    "opaque": "doiléir",
    "gem": "seoid",
    "striking": "suntasach",
    "colour": "dath",
    "reminiscent": "cosúil",
    "deep": "domhain",
    "forests": "coillte",
    "vibrant": "beoga",
    "summer": "samhradh",
    "sunset": "luí na gréine",
    "rich": "saibhir",
    "suitable": "oiriúnach",
    "royalty": "ríoga",
    "tiny": "beagán",
    "pelvis": "pelvis",
    "neck": "muineál",
    "bladder": "málas",
    "carrion": "marbhthithe",
    "lingering": "fann",
    "pickable": "piocadh",
    "mold": "múnla",
    "crossbow": "crosbogha",
    "bolt": "bolta",
    "sledge": "slacán",
    "battleaxe": "tuagh chatha",
    "fistweapon": "arm lámha",
    "fishingbait": "mealladh iascaireachta",
    "flametal": "miotail lasrach",
    "lightning": "tintreach",
    "frostfire": "tine sioc",
    "bloodlightning": "tintreach fola",
    "mage": "draoi",
    "deepnorth": "an Domhan Domhain Thuaidh",
    "ashlands": "Tír na Luaith",
    "hardrock": "cloch chrua",
    "axe2h": "tuadh dhá-láimhe",
    "mace2h": "maide dhá-láimhe",
    "sword2h": "claidheamh dhá-láimhe",
    "bombblob": "buama blob",
    "blob": "blob",
    "tower": "túr",
    "upgrader": "uasghrádóir",
    "fireworkrocket": "roicéad tine ealaíne",
    "splitner": "splitner",
    "slayer": "slayer",
    "ripper": "ripper",
    "drop": "titim",
    "hp": "hp",
    "chicken": "sicín",
    "nature": "dúlra",
    "blood": "fola",
    "berzerkr": "berzerkr",
    "fenris": "fenris",
    "hildir": "hildir",
    "undead": "mairbh",
    "bjorn": "bjorn",
    "asks": "asks",
    "asksvin": "asksvin",
    "uncooked": "amh",
    "trophy": "trófaí",
}

_TAG_RE = re.compile(r"(<[^>]+>)")
_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ0-9]+(?:'[a-z]+)?|[^A-Za-z0-9\s]+|\s+")


def _protect_tags(text: str) -> tuple[str, list[str]]:
    tags: list[str] = []

    def repl(m: re.Match[str]) -> str:
        tags.append(m.group(0))
        return f"⟦T{len(tags) - 1}⟧"

    return _TAG_RE.sub(repl, text), tags


def _restore_tags(text: str, tags: list[str]) -> str:
    for i, tag in enumerate(tags):
        text = text.replace(f"⟦T{i}⟧", tag)
    return text


def _preserve_proper_nouns(text: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}
    for i, noun in enumerate(sorted(PROPER_NOUNS, key=len, reverse=True)):
        if noun in text:
            ph = f"⟦P{i}⟧"
            placeholders[ph] = noun
            text = text.replace(noun, ph)
    return text, placeholders


def _restore_placeholders(text: str, placeholders: dict[str, str]) -> str:
    for ph, val in placeholders.items():
        text = text.replace(ph, val)
    return text


def _split_words(text: str) -> list[str]:
    """Split English label into tokens (words + punctuation)."""
    parts: list[str] = []
    for m in re.finditer(r"[A-Za-zÀ-ÿ0-9]+(?:'[a-z]+)?|[^A-Za-z0-9]+", text):
        parts.append(m.group(0))
    return parts


def _translate_token(token: str) -> str:
    if not token.isalpha() and not any(c.isalpha() for c in token):
        return token
    low = token.lower()
    if low in WORDS:
        ir = WORDS[low]
        if token[0].isupper() and ir and ir[0].islower():
            return ir[0].upper() + ir[1:]
        return ir
    # CamelCase interior split: BlackMetal -> black + metal already handled via lower
    return token


def translate_phrase(english: str) -> str:
    english = english.strip()
    if not english:
        return english
    if english in EXACT:
        return EXACT[english]

    protected, tags = _protect_tags(english)
    protected, pn = _preserve_proper_nouns(protected)

    parts = _split_words(protected)
    out: list[str] = []
    for p in parts:
        if p.isspace() or (not any(c.isalpha() for c in p)):
            out.append(p)
            continue
        out.append(_translate_token(p))

    result = "".join(out)
    # Fix spacing: insert space between adjacent words when original had spaces
    if " " in english and " " not in result and len(out) > 1:
        spaced = []
        for p in out:
            if p in (" ", "\t"):
                spaced.append(" ")
            elif spaced and spaced[-1] not in (" ", ""):
                spaced.append(" ")
            spaced.append(p)
        result = "".join(spaced).strip()

    # Re-split with spaces for multi-word labels
    if " " in english:
        words = re.findall(r"[A-Za-zÀ-ÿ0-9']+", protected)
        ir_words = [_translate_token(w) for w in words]
        # Irish often puts adjective after noun for items; keep English order for clarity
        result = " ".join(ir_words)

    return _restore_placeholders(_restore_tags(result, tags), pn)


def translate_item(key: str, english: str) -> str:
    return translate_phrase(english)
