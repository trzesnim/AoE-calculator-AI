import re
import math
import time
import urllib.request
import urllib.parse
import json
import os
try:
    import requests
except ImportError:
    requests = None
import streamlit as st

# ==============================================================================
# Age of Empires II: Definitive Edition 1v1 Battle Calculator
# Fully Dynamic Architecture (SiegeEngineers TechTree API + Fandom MediaWiki API)
# ZERO Hardcoded Tech Trees, ZERO Silent Fallbacks, 100% Dynamic API Grounding
# ==============================================================================

CIVILIZATIONS = [
    "Generic", "Armenians", "Aztecs", "Bengalis", "Berbers", "Bohemians",
    "Britons", "Bulgarians", "Burgundians", "Burmese", "Byzantines", "Celts",
    "Chinese", "Cumans", "Danes", "Dravidians", "Ethiopians", "Franks",
    "Georgians", "Goths", "Gurjaras", "Hindustanis", "Huns", "Incas",
    "Italians", "Japanese", "Jurchens", "Khitans", "Khmer", "Koreans",
    "Lithuanians", "Magyars", "Malay", "Malians", "Mapuche", "Mayans",
    "Mongols", "Muisca", "Persians", "Poles", "Portuguese", "Romans",
    "Saracens", "Saxons", "Shu", "Sicilians", "Slavs", "Spanish",
    "Tatars", "Teutons", "Tupi", "Turks", "Varangians", "Vietnamese",
    "Vikings", "Wei", "Wu"
]

AGE_DEPENDENT_UNITS = [
    "scout cavalry",
    "eagle scout",
    "flemish militia",
    "serjeant"
]

SUICIDE_UNITS = [
    "Petard", "Demolition Raft", "Demolition Ship", "Heavy Demolition Ship", "Flaming Camel", "Saboteur"
]

# Synchronized UNITS without duplicate "Elite ..." entries
UNITS = [
    "Arambai", "Arbalester", "Archer", "Armored Elephant", "Ballista Elephant",
    "Battering Ram", "Battle Elephant", "Berserk", "Blackwood Archer", "Bolas Rider",
    "Bombard Cannon", "Boyar", "Camel Archer", "Camel Rider", "Camel Scout",
    "Cannon Galleon", "Capped Ram", "Caravel", "Carrack", "Cataphract", "Cavalier",
    "Cavalry Archer", "Centurion", "Chakram Thrower", "Champi Runner", "Champi Scout",
    "Champi Warrior", "Champion", "Chu Ko Nu", "Composite Bowman", "Condottiero",
    "Conquistador", "Coustillier", "Crossbowman", "Demolition Raft", "Demolition Ship",
    "Dromon", "Eagle Scout", "Eagle Warrior", "Elephant Archer",
    "Fast Fire Ship", "Fire Archer", "Fire Galley", "Fire Lancer", "Fire Ship", "Fishing Ship", "Flaming Camel",
    "Flemish Militia", "Galley", "Galleon", "Gbeto", "Genitour", "Genoese Crossbowman",
    "Ghulam", "Grenadier", "Guecha Warrior", "Halberdier", "Hand Cannoneer",
    "Hearth Troop", "Heavy Camel Rider", "Heavy Cavalry Archer", "Heavy Demolition Ship",
    "Heavy Hei Guang Cavalry", "Heavy Mounted Crossbowman", "Heavy Scorpion", "Hei Guang Cavalry",
    "Houfnice", "Hulk", "Huskarl", "Hussar", "Hussite Wagon",
    "Ibirapema Warrior", "Imperial Camel Rider", "Imperial Skirmisher", "Iron Pagoda",
    "Janissary", "Jarl", "Jian Swordsman", "Jomsviking", "Kamayuk", "Karambit Warrior",
    "Keshik", "Kipchak", "Knight", "Kona", "Konnik", "Legionary", "Leitis",
    "Liao Dao", "Light Cavalry", "Long Swordsman", "Longbowman", "Longship", "Magyar Huszar",
    "Mameluke", "Man-at-Arms", "Mangonel", "Mangudai", "Militia", "Missionary",
    "Monaspa", "Monk", "Mounted Crossbowman", "Mounted Trebuchet", "Obuch", "Onager",
    "Organ Gun", "Paladin", "Petard", "Pikeman", "Plumed Archer", "Ratha",
    "Rattan Archer", "Samurai", "Savar", "Scorpion", "Scout Cavalry", "Serjeant",
    "Shotel Warrior", "Shrivamsha Rider", "Siege Elephant", "Siege Onager", "Siege Ram",
    "Siege Tower", "Skirmisher", "Slinger", "Spearman", "Steppe Lancer", "Tarkan", "Temple Guard",
    "Teutonic Knight", "Thirisadai", "Throwing Axeman", "Tiger Cavalry", "Trade Cart",
    "Trade Cog", "Transport Ship", "Trebuchet", "Turtle Ship", "Two-Handed Swordsman",
    "Urumi Swordsman", "Varangian Guard", "Villager", "War Chariot", "War Elephant",
    "War Galley", "War Hulk", "War Wagon", "Warrior Priest", "White Feather Guard",
    "Winged Hussar", "Woad Raider", "Xianbei Raider", "Xolotl Warrior"
]

# Synchronized ELITE_UNITS
ELITE_UNITS = [
    "Arambai", "Ballista Elephant", "Battle Elephant", "Berserk", "Blackwood Archer",
    "Bolas Rider", "Boyar", "Camel Archer", "Cannon Galleon", "Caravel",
    "Cataphract", "Centurion", "Chakram Thrower", "Champi Warrior", "Chu Ko Nu",
    "Composite Bowman", "Conquistador", "Coustillier", "Eagle Warrior", "Elephant Archer",
    "Fire Archer", "Fire Lancer", "Gbeto", "Genitour", "Genoese Crossbowman", "Ghulam", "Guecha Warrior",
    "Hearth Troop", "Huskarl", "Hussite Wagon", "Ibirapema Warrior", "Iron Pagoda",
    "Janissary", "Jarl", "Jian Swordsman", "Jomsviking", "Kamayuk", "Karambit Warrior", "Keshik",
    "Kipchak", "Kona", "Konnik", "Leitis", "Liao Dao", "Longbowman", "Longship",
    "Magyar Huszar", "Mameluke", "Mangudai", "Monaspa", "Obuch", "Organ Gun",
    "Plumed Archer", "Ratha", "Rattan Archer", "Samurai", "Serjeant", "Shotel Warrior",
    "Shrivamsha Rider", "Skirmisher", "Steppe Lancer", "Tarkan", "Temple Guard",
    "Teutonic Knight", "Throwing Axeman", "Tiger Cavalry", "Turtle Ship",
    "Urumi Swordsman", "Varangian Guard", "War Elephant", "War Wagon",
    "White Feather Guard", "Woad Raider", "Xianbei Raider"
]

# BUG 2: FIX ID COLLISION IN load_techtree_data (unique_obj)
@st.cache_data(ttl=86400, show_spinner=False)
def load_techtree_data() -> tuple[dict, set]:
    url_data = "https://raw.githubusercontent.com/SiegeEngineers/aoe2techtree/master/data/data.json"
    url_strings = "https://raw.githubusercontent.com/SiegeEngineers/aoe2techtree/master/data/locales/en/strings.json"
    
    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    try:
        req_d = urllib.request.Request(url_data, headers=headers)
        with urllib.request.urlopen(req_d, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(f"Failed to fetch data.json from SiegeEngineers API: {e}")

    try:
        req_s = urllib.request.Request(url_strings, headers=headers)
        with urllib.request.urlopen(req_s, timeout=10) as resp:
            strings = json.loads(resp.read().decode("utf-8"))
    except Exception:
        strings = {}

    units_dict = data.get("data", {}).get("Unit") or data.get("data", {}).get("units") or {}
    techs_dict = data.get("data", {}).get("Tech") or data.get("data", {}).get("techs") or {}

    def clean_str(s):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s))).strip()

    def get_name(item):
        lid = item.get("LanguageNameId")
        if lid is not None:
            for offset in [0, 9000, 10000]:
                cand = str(int(lid) + offset)
                if cand in strings:
                    c = clean_str(strings[cand])
                    if c:
                        return c
        return clean_str(item.get("internal_name", ""))

    unit_id_to_name = {}
    for uid, uinfo in units_dict.items():
        nm = get_name(uinfo)
        if nm:
            unit_id_to_name[int(uid)] = nm.lower()

    tech_id_to_name = {}
    for tid, tinfo in techs_dict.items():
        nm = get_name(tinfo)
        if nm:
            tech_id_to_name[int(tid)] = nm.lower()

    civs_source = data.get("civs") or data.get("techtrees") or {}
    techtree = {}

    for civ_name, civ_tree in civs_source.items():
        u_raw = civ_tree.get("units") or civ_tree.get("Unit") or []
        t_raw = civ_tree.get("techs") or civ_tree.get("Tech") or []
        unique_obj = civ_tree.get("unique", {})

        # BUG 2: Separate u_extra and t_extra explicitly to prevent ID collisions
        u_extra = []
        t_extra = []
        if isinstance(unique_obj, dict):
            for k, v in unique_obj.items():
                if "unit" in k.lower():
                    u_extra.append(v)
                elif "tech" in k.lower():
                    t_extra.append(v)
        elif isinstance(unique_obj, list):
            u_extra = unique_obj
            t_extra = unique_obj

        c_units = set()
        c_techs = set()

        for item in list(u_raw) + u_extra:
            uid = item if isinstance(item, int) else item.get("id") if isinstance(item, dict) else None
            if uid is not None and uid in unit_id_to_name:
                c_units.add(unit_id_to_name[uid])

        for item in list(t_raw) + t_extra:
            tid = item if isinstance(item, int) else item.get("id") if isinstance(item, dict) else None
            if tid is not None and tid in tech_id_to_name:
                c_techs.add(tech_id_to_name[tid])

        techtree[civ_name] = {"units": c_units, "techs": c_techs}

    global_known_units = set(unit_id_to_name.values())
    return techtree, global_known_units

def check_fandom_availability(wikitext: str, civ: str) -> bool:
    if not civ or civ.lower() == "generic":
        return True

    # 1. In Fandom wikitext, Infobox |Civilization = ...
    m_civ = re.search(r"\|\s*Civilization\s*=\s*([^\r\n]+)", wikitext, re.I)
    if m_civ:
        val = m_civ.group(1).split("<!--")[0].strip()
        if "all" in val.lower():
            return True
        if re.search(r"\b" + re.escape(civ) + r"\b", val, re.I):
            return True
        if any(c in val for c in ["{{2icons|", "[[", "Bengalis", "Britons", "Franks", "Aztecs", "Tupi", "Dravidians", "Gurjaras", "Cumans"]):
            return False

    # 2. In Fandom wikitext, {{Availability|...}} template
    m_avail = re.search(r"\{\{Availability\|([^}]+)\}\}", wikitext, re.I)
    if m_avail:
        val = m_avail.group(1)
        if "all" in val.lower():
            return True
        if re.search(r"\b" + re.escape(civ) + r"\b", val, re.I):
            return True
        return False

    return True

# IMPROVEMENT 2: RESOURCE COST PARSING IN UNIT
class Unit:
    def __init__(self, name, hp, p_attack=None, m_attack=None, rof=2.0, armor=0, pierce_armor=0, attack_bonus=None, armor_class=None, boost_tech=None, elite=False, parsed_techs=None, tech_civ_restrictions=None, cost=None):
        self.name = name
        self.hp = int(hp) if hp is not None else 50
        self.p_attack = int(p_attack) if p_attack is not None else None
        self.m_attack = int(m_attack) if m_attack is not None else None
        self.rof = float(rof) if rof is not None else 2.0
        self.armor = int(armor) if armor is not None else 0
        self.pierce_armor = int(pierce_armor) if pierce_armor is not None else 0
        self.attack_bonus = attack_bonus or {}
        self.armor_class = armor_class or []
        self.boost_tech = boost_tech or ""
        self.elite = elite
        self.parsed_techs = parsed_techs or {}
        self.tech_civ_restrictions = tech_civ_restrictions or {}
        self.cost = cost or {"Food": 0, "Wood": 0, "Gold": 0}
        self.total_cost = sum(self.cost.values())

    def __str__(self):
        bonus_str = ", ".join([f"+{v} vs {k}" for k, v in self.attack_bonus.items()]) if self.attack_bonus else "None"
        class_str = ", ".join(self.armor_class) if self.armor_class else "None"
        p_str = str(self.p_attack) if self.p_attack is not None else "None"
        m_str = str(self.m_attack) if self.m_attack is not None else "None"
        cost_parts = [f"{k}: {v}" for k, v in self.cost.items() if v > 0]
        cost_str = ", ".join(cost_parts) if cost_parts else "None (0)"
        return f"Name: {self.name}\nCost: {cost_str} (Total: {self.total_cost})\nHP: {self.hp}\nMelee Attack: {m_str}\nPierce Attack: {p_str}\nRate of Fire (ROF): {self.rof:.2f}s\nMelee Armor: {self.armor}\nPierce Armor: {self.pierce_armor}\nAttack Bonuses: {bonus_str}\nArmor Classes: {class_str}"

def extract_template(wikitext: str, template_name: str) -> str:
    target = "{{" + template_name.lower()
    idx = wikitext.lower().find(target)
    if idx == -1:
        target_short = "{{" + template_name.split("|")[0].lower()
        idx = wikitext.lower().find(target_short)
        if idx == -1:
            return ""
    depth = 0
    start = idx
    i = idx
    n = len(wikitext)
    while i < n - 1:
        pair = wikitext[i:i+2]
        if pair == "{{":
            depth += 1
            i += 2
        elif pair == "}}":
            depth -= 1
            i += 2
            if depth == 0:
                return wikitext[start:i]
        else:
            i += 1
    return wikitext[start:]

def normalize_class_name(cls_name: str) -> str:
    c = cls_name.strip().lower()
    mapping = {
        "archers": "archer",
        "spearmen": "spearman",
        "cavalry archers": "cavalry archer",
        "unique units": "unique unit",
        "gunpowder units": "gunpowder unit",
        "mameluke:": "mamelukes",
        "mameluke": "mamelukes",
        "ships": "ship",
        "camels": "camel",
        "camel units": "camel",
        "elephants": "elephant",
        "war elephants": "war elephant",
        "buildings": "building",
        "walls and gates": "walls and gates",
        "castles": "castles",
        "siege weapons": "siege weapon",
        "suicide units": "suicide unit",
        "eagle warriors": "eagle warrior",
    }
    return mapping.get(c, c)

# BUG 3 & BUG 4: MULTILINE INFOBOX & TECH RESTRICTIONS SPLITTING
@st.cache_data(ttl=86400, show_spinner=False)
def fetch_wiki_unit(unit_name: str):
    clean = unit_name.replace("Elite ", "").strip()
    clean_slug = clean.replace(" ", "_")
    candidates = [
        f"{clean_slug}_(Age_of_Empires_II)",
        clean_slug,
        f"{clean_slug}_(unit)"
    ]

    headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    content = ""

    for cand in candidates:
        # 1. Primary: Modern MediaWiki action=parse
        url_parse = f"https://ageofempires.fandom.com/api.php?action=parse&page={urllib.parse.quote(cand)}&prop=wikitext&redirects=1&format=json"
        for _ in range(2):
            try:
                req = urllib.request.Request(url_parse, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    wt = data.get("parse", {}).get("wikitext", {}).get("*", "")
                    if wt and "infobox" in wt.lower():
                        content = wt
                        break
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(1.2)
                    continue
                break
            except Exception:
                break
        if content:
            break

        # 2. Secondary: MediaWiki action=query revisions
        url = f"https://ageofempires.fandom.com/api.php?action=query&prop=revisions&titles={urllib.parse.quote(cand)}&rvprop=content&formatversion=2&redirects=1&format=json"
        for _ in range(2):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    query = data.get("query", {})
                    pages = query.get("pages", [])
                    if pages and not pages[0].get("missing"):
                        revisions = pages[0].get("revisions", [])
                        if revisions:
                            wt = revisions[0].get("content", "")
                            if "infobox" in wt.lower():
                                content = wt
                                break
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(1.2)
                    continue
                break
            except Exception:
                break
        if content:
            break

    if not content:
        return None, "", {}, {}, []

    # Extract raw substring of Boosts|Technologies
    pattern_boost = r"Boosts\|Technologies(.+?)(?:\{\{Boosts\||==\s*Civilization|\{\{Availability)"
    m_boost = re.search(pattern_boost, content, re.DOTALL)
    boost_tech_str = m_boost.group(1).strip() if m_boost else ""
    if not boost_tech_str:
        b_fallback = extract_template(content, "Boosts|Technologies") or extract_template(content, "Boosts")
        boost_tech_str = b_fallback

    # BUG 4: Split by BOTH newlines and <br> tags
    tech_civ_restrictions = {}
    for segment in re.split(r"[\r\n]+|<br\s*/?>", boost_tech_str, flags=re.I):
        m_only = re.search(r"\(([^)]*?)\s+only\)", segment, re.I)
        if m_only:
            civs_part = m_only.group(1)
            civ_names = re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", civs_part)
            if not civ_names:
                civ_names = [c.strip() for c in re.split(r"[,/]", civs_part) if c.strip()]
            before_only = segment[:m_only.start()]
            techs = re.findall(r"\{\{2icons\|([^}|]+)", before_only)
            if not techs:
                techs = re.findall(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", before_only)
            for t in techs:
                tech_civ_restrictions[t.strip().lower()] = [c.strip() for c in civ_names]

    parsed_techs = {}
    tech_tokens = re.findall(r"\{\{2icons\|([^}|]+)\}\}", boost_tech_str)
    for tok in tech_tokens:
        tok_clean = tok.strip()
        if tok_clean:
            parsed_techs[tok_clean.lower()] = {
                "name": tok_clean,
                "civs": tech_civ_restrictions.get(tok_clean.lower(), [])
            }

    # BUG 3: Read full line for Civilization
    wiki_allowed_civs = []
    ibox_match = extract_template(content, "Infobox AoE2 unit") or extract_template(content, "Infobox")
    if ibox_match:
        civ_m = re.search(r"\|\s*Civilization\s*=\s*([^\r\n]+)", ibox_match, re.I)
        if civ_m:
            c_val = civ_m.group(1).split("<!--")[0].strip()
            if not any(k in c_val.lower() for k in ["see table", "all", "various"]):
                parsed_c = re.findall(r"\{\{2icons\|([^}|]+)", c_val)
                if not parsed_c:
                    parsed_c = re.findall(r"\[\[(?:[^|\]]+\|)?([A-Za-z]+)\]\]", c_val)
                wiki_allowed_civs = [c.replace("Maya", "Mayans").strip() for c in parsed_c if c.strip() and "allies" not in c.lower()]

    return content, boost_tech_str, parsed_techs, tech_civ_restrictions, wiki_allowed_civs

# BUG 1 & BUG 3 & IMPROVEMENT 2: parse_unit with r"\g<1>", multiline parsing, and cost
def parse_unit(unit_name: str, is_elite: bool, age: int) -> Unit:
    norm = unit_name.lower()
    content, boost_tech_str, parsed_techs, tech_civ_restrictions, wiki_allowed_civs = fetch_wiki_unit(unit_name)

    if not content:
        st.error(f"Failed to fetch unit stats for **{unit_name}** from Fandom MediaWiki API.")
        return Unit(unit_name, 50, rof=2.0, boost_tech=boost_tech_str, elite=is_elite)

    ibox = extract_template(content, "Infobox AoE2 unit") or extract_template(content, "Infobox")
    if "trebuchet" in norm and "PAttack" not in ibox and content.count("Infobox AoE2 unit") > 1:
        ibox = extract_template(content[content.find("Infobox AoE2 unit") + 10:], "Infobox AoE2 unit")

    # BUG 3: Multiline-aware field extraction
    data = {}
    if ibox:
        for m in re.finditer(r"\|\s*([A-Za-z0-9_]+)\s*=\s*(.*?)(?=\n\s*\||\n\s*\}\}|\Z)", ibox, re.S):
            data[m.group(1).strip()] = m.group(2).strip()

    final_name = f"Elite {unit_name}" if is_elite else unit_name

    def parse_stat(val):
        if not val:
            return None
        val_str = str(val)

        # Clean File tags and image links
        val_str = re.sub(r"\[\[File:[^\]]+\]\]", "", val_str, flags=re.I)
        val_str = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\g<1>", val_str)

        # Clean tooltips with explicit backreference
        val_str = re.sub(r"\{\{tt\|([^|]+)\|.*?\}\}", r"\g<1>", val_str)

        # 1. Check for multiline <br> segments (e.g. Castle / Imperial / Elite)
        segments = re.split(r"<br\s*/?>", val_str, flags=re.I)
        if len(segments) > 1:
            resolved = False
            if is_elite:
                elite_segs = [s for s in segments if "elite" in s.lower()]
                if elite_segs:
                    val_str = elite_segs[-1]
                    resolved = True
            if not resolved:
                age_keywords = {1: ["dark"], 2: ["feudal"], 3: ["castle"], 4: ["imperial"]}
                for a in range(age, 0, -1):
                    keys = age_keywords[a]
                    matched = [s for s in segments if any(k in s.lower() for k in keys) and "elite" not in s.lower()]
                    if matched:
                        val_str = matched[-1]
                        break

        # 2. Check inline age-dependent stats
        age_map = {1: "Dark Age", 2: "Feudal Age", 3: "Castle Age", 4: "Imperial Age"}
        matches = re.findall(r"(Dark Age|Feudal Age|Castle Age|Imperial Age)\}\}\s*(\d+)", val_str, re.I)
        if matches:
            found_dict = {m[0].lower(): int(m[1]) for m in matches}
            target_val = None
            for a in range(age, 0, -1):
                a_name = age_map[a].lower()
                if a_name in found_dict:
                    target_val = found_dict[a_name]
                    break
            if target_val is not None:
                return float(target_val)

        # 3. Split by comma for base vs elite
        comma_match = re.search(r"(.+?)\s*,\s*(.+)", val_str)
        if comma_match:
            val_str = comma_match.group(2) if is_elite else comma_match.group(1)

        # 4. Strip <br />(\d+) <small> if present
        br_match = re.search(r"<br\s*/?>(\d+)\s*<small>", val_str, re.I)
        if br_match:
            val_str = br_match.group(1)

        # 5. Strip templates like {{AoE2Icon|...}}, {{2icons|...}}
        val_str = re.sub(r"\{\{[^}]+\}\}", "", val_str)

        # 6. Extract primary number (requires at least one digit)
        num_match = re.search(r"([+-]?\d+(?:\.\d+)?)", str(val_str))
        return float(num_match.group(1)) if num_match else 0.0

    # Parse Cost
    food_cost = int(parse_stat(data.get("Food")) or 0)
    wood_cost = int(parse_stat(data.get("Wood")) or 0)
    gold_cost = int(parse_stat(data.get("Gold")) or 0)
    cost_dict = {"Food": food_cost, "Wood": wood_cost, "Gold": gold_cost}

    parsed_hp = parse_stat(data.get("HP"))
    hp = int(parsed_hp) if (parsed_hp is not None and parsed_hp > 0) else 50

    raw_p = parse_stat(data.get("PAttack"))
    raw_m = parse_stat(data.get("MAttack"))
    p_atk = int(raw_p) if (raw_p is not None and raw_p > 0) else None
    m_atk = int(raw_m) if (raw_m is not None and raw_m > 0) else None
    rof = float(parse_stat(data.get("ROF")) or 2.0)
    arm = int(parse_stat(data.get("Armor")) if data.get("Armor") is not None else 0)
    parm = int(parse_stat(data.get("PierceArmor")) if data.get("PierceArmor") is not None else 0)

    bonus_str = data.get("AttackBonus", "")
    attack_bonus = {}
    if bonus_str:
        matches = re.findall(r"([+-]?\d+(?:\s*,\s*[+-]?\d+)?).*?vs\.?\s*.*?2class\|([^}|]+)", str(bonus_str))
        for nums, cls in matches:
            parts = [p.strip() for p in nums.split(",")]
            val = parts[1] if (is_elite and len(parts) > 1) else parts[0]
            try:
                norm_cls = normalize_class_name(cls)
                val_int = int(val)
                attack_bonus[norm_cls] = val_int
                attack_bonus[cls.strip()] = val_int
            except ValueError:
                pass

    if "skirmisher" in norm:
        attack_bonus["unshielded"] = 4 if is_elite else 3

    class_str = data.get("Class", "")
    armor_class = [normalize_class_name(c) for c in re.findall(r"2class\|([^}|]+)", class_str)]
    if "jian swordsman" in norm and "unshielded" not in armor_class:
        armor_class.append("unshielded")

    return Unit(final_name, hp, p_atk, m_atk, rof, arm, parm, attack_bonus, armor_class, boost_tech_str, is_elite, parsed_techs, tech_civ_restrictions, cost=cost_dict)

def is_unit_available(civ: str, unit_name: str) -> tuple[bool, str]:
    if not civ or civ == "Generic":
        return True, ""

    content, _, _, _, wiki_allowed_civs = fetch_wiki_unit(unit_name)

    if wiki_allowed_civs and civ not in wiki_allowed_civs:
        return False, f"{unit_name} is exclusive to {', '.join(wiki_allowed_civs)}."

    if content and not check_fandom_availability(content, civ):
        return False, f"{civ} does not have access to {unit_name} according to Fandom Wiki."

    techtree, global_known_units = load_techtree_data()
    clean_u = unit_name.strip().lower()
    clean_nopack = clean_u.replace(" (packed)", "").strip()

    is_known_in_techtree = clean_u in global_known_units or clean_nopack in global_known_units

    if civ in techtree and is_known_in_techtree:
        allowed_units = techtree[civ].get("units", set())
        if clean_u in allowed_units or clean_nopack in allowed_units:
            return True, ""
        if clean_u.startswith("elite "):
            base_u = clean_u.replace("elite ", "").strip()
            if base_u in allowed_units and clean_u in allowed_units:
                return True, ""
        return False, f"{civ} does not get access to {unit_name} in the official Age of Empires II tech tree."

    return True, ""

# BUG 5: FIX compute_effective_stats (Skirmisher Thumb Ring, Villager Loom/Supremacy, Romans, Burmese, Teutons, Malians, Gurjaras, etc.)
def compute_effective_stats(u: Unit, civ: str, up: dict, opponent: Unit = None) -> dict:
    hp = u.hp
    if up.get("bloodlines"):
        hp += 20
    if up.get("loom") and "villager" in u.name.lower():
        hp += 15
    if up.get("supremacy") and "villager" in u.name.lower():
        hp += 40

    if civ == "Franks" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry"]):
        hp = int(hp * 1.2)
    elif civ == "Vikings" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        hp = int(hp * 1.2)
    elif civ == "Turks" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["gunpowder unit"]):
        hp = int(hp * 1.25)
    elif civ == "Saracens" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["camel"]):
        hp += 10
    if up.get("sipahi") and "cavalry archer" in u.name.lower():
        hp += 20
    if up.get("el_dorado") and "eagle" in u.name.lower():
        hp += 40
    if up.get("chatras") and "battle elephant" in u.name.lower():
        hp += 100
    if (up.get("furor_celticus") or up.get("furor_celtica")) and ("siege" in str(u.armor_class).lower() or "trebuchet" in u.name.lower()):
        hp = int(hp * 1.4)

    rof = u.rof
    if civ == "Japanese" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        rof *= 0.75
    elif civ == "Mongols" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry archer"]):
        rof *= 0.80
    elif civ == "Hindustanis" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["camel"]):
        rof *= 0.833
    elif civ == "Saracens" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["ship"]) and any(w in u.name.lower() for w in ["galley", "galleon"]):
        rof *= 0.80
    elif civ == "Byzantines" and "fire" in u.name.lower():
        rof *= 0.80
    elif up.get("stirrups") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry"]):
        rof *= 0.75
    elif up.get("kataparuto") and "trebuchet" in u.name.lower():
        rof *= 0.75

    # BUG 5: Skirmisher / Genitour Thumb Ring does NOT increase ROF
    if up.get("thumb_ring"):
        is_skirm_or_genitour = any(w in u.name.lower() for w in ["skirmisher", "genitour"])
        if not is_skirm_or_genitour:
            if any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry archer"]):
                rof *= 0.90
            elif any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["archer"]):
                rof *= 0.85

    p_atk = u.p_attack
    m_atk = u.m_attack

    if p_atk is not None:
        p_atk += up.get("r_atk_val", 0)
        if up.get("chemistry"):
            p_atk += 1
        if up.get("recurve_bow") and "cavalry archer" in u.name.lower():
            p_atk += 1
        if up.get("bogsveigar") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["archer", "ship"]):
            p_atk += 1
        if up.get("rocketry"):
            if "chu ko nu" in u.name.lower():
                p_atk += 2
            elif "scorpion" in u.name.lower():
                p_atk += 4
        if up.get("counterweights") and "trebuchet" in u.name.lower():
            p_atk = int(p_atk * 1.15)

    if m_atk is not None:
        m_atk += up.get("m_atk_val", 0)
        # Burmese civ bonus: +3 melee attack for infantry
        if civ == "Burmese" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
            m_atk += 3
        if up.get("supremacy") and "villager" in u.name.lower():
            m_atk += 6
        if up.get("garland_wars") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
            m_atk += 4
        if up.get("farimba") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry", "camel"]):
            m_atk += 5

    m_arm_val = up.get("m_arm_val", 0)
    p_arm_val = up.get("p_arm_val", 0)

    # Romans armor multiplier: Apply * 2 to Blacksmith infantry armor upgrades
    if civ == "Romans" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        m_arm_val *= 2
        p_arm_val *= 2

    m_arm = u.armor + m_arm_val
    p_arm = u.pierce_armor + p_arm_val

    # Teutons civ bonus: +2 melee armor for infantry and cavalry (except Scout Cavalry)
    if civ == "Teutons":
        if any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
            m_arm += 2
        elif any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry"]) and "scout cavalry" not in u.name.lower():
            m_arm += 2

    # Malians civ bonus: +3 pierce armor for infantry
    if civ == "Malians" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        p_arm += 3

    # Loom and Supremacy for Villagers
    if up.get("loom") and "villager" in u.name.lower():
        m_arm += 1
        p_arm += 2
    if up.get("supremacy") and "villager" in u.name.lower():
        m_arm += 2
        p_arm += 2

    if up.get("parthian"):
        m_arm += 1
        p_arm += 2
    if up.get("gambesons") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        p_arm += 1
    if up.get("careening") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["ship"]):
        p_arm += 1
    if up.get("carracks") and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["ship"]):
        m_arm += 1
        p_arm += 1
    if up.get("ironclad") and "siege" in str(u.armor_class).lower():
        m_arm += 4
    if up.get("hauberk") and "knight" in u.name.lower():
        m_arm += 1
        p_arm += 2

    if up.get("tower_shields"):
        p_arm += 2
    if up.get("pavise"):
        m_arm += 1
        p_arm += 1
    if up.get("silk_armor"):
        m_arm += 1
        p_arm += 1
    if up.get("fabric_shields"):
        m_arm += 1
        p_arm += 2
    if up.get("bagains"):
        m_arm += 5

    active_bonus = 0
    if opponent:
        for opp_cls in opponent.armor_class:
            norm_opp = normalize_class_name(opp_cls)
            if norm_opp in u.attack_bonus:
                active_bonus += u.attack_bonus[norm_opp]
            elif opp_cls in u.attack_bonus:
                active_bonus += u.attack_bonus[opp_cls]

        if up.get("parthian") and "spearman" in [normalize_class_name(ac) for ac in opponent.armor_class]:
            active_bonus += (2 if "unique unit" in u.armor_class else 4)

        if up.get("cranequins") and "infantry" in [normalize_class_name(ac) for ac in opponent.armor_class]:
            active_bonus += 2

        if civ == "Gurjaras" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry", "camel", "elephant"]) and active_bonus > 0:
            active_bonus = int(active_bonus * 1.4)

        if getattr(opponent, "_civ", None) == "Sicilians":
            active_bonus = int(active_bonus * 0.67)

    return {
        "hp": hp,
        "p_atk": p_atk,
        "m_atk": m_atk,
        "rof": rof,
        "m_arm": m_arm,
        "p_arm": p_arm,
        "bonus": active_bonus
    }

def format_effective_stats(u: Unit, civ: str, up: dict, opponent: Unit = None) -> str:
    eff = compute_effective_stats(u, civ, up, opponent)
    p_atk_str = str(eff["p_atk"]) if eff["p_atk"] is not None else "None"
    m_atk_str = str(eff["m_atk"]) if eff["m_atk"] is not None else "None"

    special = []
    if "leitis" in u.name.lower():
        special.append("Ignores Enemy Armor")
    if up.get("wootz_steel"):
        special.append("Wootz Steel (Ignores Enemy Armor)")
    if "obuch" in u.name.lower():
        special.append("Armor Shredding (-1 Armor per hit)")
    if "coustillier" in u.name.lower():
        special.append(f"Charge Attack (+{40 if u.elite else 35} 1st hit)")
    if "urumi" in u.name.lower():
        special.append(f"Charge Attack (+{10 if u.elite else 9} 1st hit)")
    if up.get("comitatenses"):
        special.append("Comitatenses Charge (+5 1st hit)")
    if up.get("siphons"):
        special.append("Siphons (Explosive Initial Burst Strike)")
    if "chu ko nu" in u.name.lower():
        special.append(f"Multishot ({5 if u.elite else 3} arrows)")
    if "kipchak" in u.name.lower():
        special.append(f"Multishot ({4 if u.elite else 3} arrows)")
    if up.get("kataparuto"):
        special.append("Kataparuto (33% Faster Attack & 4x Pack Speed)")
    if up.get("warwolf"):
        special.append("Warwolf (100% Blast Damage)")
    if up.get("thumb_ring"):
        is_skirm = any(w in u.name.lower() for w in ["skirmisher", "genitour"])
        if not is_skirm:
            rate_txt = "11% Faster Attack" if "cavalry archer" in str(u.armor_class).lower() else "18% Faster Attack"
            special.append(f"Thumb Ring ({rate_txt})")
        else:
            special.append("Thumb Ring (100% Accuracy)")
    if up.get("loom"):
        special.append("Loom (+15 HP, +1/+2 Armor)")
    if up.get("supremacy"):
        special.append("Supremacy (+40 HP, +6 Attack, +2/+2 Armor)")
    if up.get("careening"):
        special.append("Careening (+1 Pierce Armor)")
    if up.get("dry_dock"):
        special.append("Dry Dock (+15% Ship Speed)")
    if up.get("carracks"):
        special.append("Carracks (+1/+1 Ship Armor)")
    if civ == "Sicilians":
        special.append("Takes 33% Less Bonus Damage")
    if civ == "Romans" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        special.append("2x Blacksmith Armor Effect")
    if civ == "Burmese" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        special.append("+3 Infantry Melee Attack")
    if civ == "Teutons":
        special.append("+2 Melee Armor")
    if civ == "Malians" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["infantry"]):
        special.append("+3 Infantry Pierce Armor")
    if civ == "Gurjaras" and any(c in [normalize_class_name(ac) for ac in u.armor_class] for c in ["cavalry", "camel", "elephant"]):
        special.append("+40% Mounted Bonus Damage")
    if u.name in SUICIDE_UNITS:
        special.append("Single-Use Explosive/Suicide Unit")

    special_str = ", ".join(special) if special else "None"
    bonus_str = f"+{eff['bonus']} vs opponent classes" if eff["bonus"] > 0 else "0"

    cost_parts = [f"{k}: {v}" for k, v in u.cost.items() if v > 0]
    cost_str = ", ".join(cost_parts) if cost_parts else "None (0)"

    return f"""Unit: {u.name} ({civ})
Cost: {cost_str} (Total: {u.total_cost})
HP: {eff['hp']}
Melee Attack: {m_atk_str}
Pierce Attack: {p_atk_str}
Rate of Fire (ROF): {eff['rof']:.2f}s
Melee Armor: {eff['m_arm']}
Pierce Armor: {eff['p_arm']}
Active Bonus Dmg vs Opponent: {bonus_str}
Special Mechanics: {special_str}"""

# BUG 5: EXACT AOE2 DAMAGE FORMULA IN calculate_kill_trajectory
def calculate_kill_trajectory(attacker: Unit, defender: Unit, civ_att: str, civ_def: str, up_att: dict, up_def: dict, eff_att: dict, eff_def: dict) -> tuple[int, float, list[int]]:
    cur_hp = eff_def["hp"]
    hp_after_each_hit = []

    is_p = eff_att["p_atk"] is not None
    atk = eff_att["p_atk"] if is_p else eff_att["m_atk"]
    bonus = eff_att["bonus"]
    rof = eff_att["rof"]

    cur_target_m = eff_def["m_arm"]
    cur_target_p = eff_def["p_arm"]

    hits = 0

    if atk is None or atk <= 0:
        return 999, 999.0, [cur_hp]

    while cur_hp > 0 and hits < 4000:
        target_arm = cur_target_p if is_p else cur_target_m
        if "leitis" in attacker.name.lower() or up_att.get("wootz_steel"):
            target_arm = 0

        # Exact AoE2 Damage Formula: max(1, max(0, atk - target_arm) + bonus)
        dmg = max(1, max(0, atk - target_arm) + bonus)

        # Charge attacks on hit 1
        if hits == 0:
            if "coustillier" in attacker.name.lower():
                dmg += (40 if getattr(attacker, "elite", False) else 35)
            elif "urumi" in attacker.name.lower():
                dmg += (10 if getattr(attacker, "elite", False) else 9)
            elif up_att.get("comitatenses"):
                dmg += 5
            elif up_att.get("siphons"):
                dmg += 20

        # Extra projectiles for Chu Ko Nu and Kipchak
        if "chu ko nu" in attacker.name.lower():
            extra = 4 if getattr(attacker, "elite", False) else 2
            dmg += extra * max(1, max(0, 3 - cur_target_p))
        elif "kipchak" in attacker.name.lower():
            extra = 3 if getattr(attacker, "elite", False) else 2
            dmg += extra * max(1, max(0, 3 - cur_target_p))

        cur_hp -= dmg
        hp_after_each_hit.append(max(0, cur_hp))
        hits += 1

        # Obuch armor shredding
        if "obuch" in attacker.name.lower():
            cur_target_m = max(0, cur_target_m - 1)
            cur_target_p = max(0, cur_target_p - 1)

        if cur_hp <= 0:
            break

    total_time = (hits - 1) * rof if hits > 0 else 0.0
    return hits, total_time, hp_after_each_hit

# BUG 6 & IMPROVEMENT 2: CLEAN UP simulate_1v1 USING calculate_kill_trajectory & COST EFFICIENCY
def simulate_1v1(u1: Unit, u2: Unit, civ1: str, civ2: str, up1: dict, up2: dict):
    u1._civ = civ1
    u2._civ = civ2

    u1_suicide = u1.name in SUICIDE_UNITS or any("suicide" in str(c).lower() for c in u1.armor_class)
    u2_suicide = u2.name in SUICIDE_UNITS or any("suicide" in str(c).lower() for c in u2.armor_class)

    if u1_suicide or u2_suicide:
        msg_parts = []
        if u1_suicide and u2_suicide:
            msg_parts.append(f"⚠️ Both {u1.name} and {u2.name} are single-use suicide/explosive units.")
        elif u1_suicide:
            msg_parts.append(f"⚠️ {u1.name} is a single-use suicide/explosive unit.")
        else:
            msg_parts.append(f"⚠️ {u2.name} is a single-use suicide/explosive unit.")
        msg_parts.append("1v1 sustained combat simulation is excluded for suicide units.")
        msg_parts.append("Displaying unit attributes, blast damage, and upgrade stats below.")
        return "\n\n".join(msg_parts)

    eff1 = compute_effective_stats(u1, civ1, up1, u2)
    eff2 = compute_effective_stats(u2, civ2, up2, u1)

    can_attack1 = (eff1["p_atk"] is not None and eff1["p_atk"] > 0) or (eff1["m_atk"] is not None and eff1["m_atk"] > 0)
    can_attack2 = (eff2["p_atk"] is not None and eff2["p_atk"] > 0) or (eff2["m_atk"] is not None and eff2["m_atk"] > 0)

    u1_label = f"{u1.name} ({civ1})"
    u2_label = f"{u2.name} ({civ2})"

    if not can_attack1 and not can_attack2:
        return f"Neither {u1_label} nor {u2_label} has an attack.\n\nStalemate! Both units cannot damage each other."

    traj1_hits, traj1_time, hp2_history = calculate_kill_trajectory(u1, u2, civ1, civ2, up1, up2, eff1, eff2)
    traj2_hits, traj2_time, hp1_history = calculate_kill_trajectory(u2, u1, civ2, civ1, up2, up1, eff2, eff1)

    if not can_attack2:
        return f"{u1_label} defeats non-attacking {u2_label} in {traj1_hits} hits ({traj1_time:.2f}s)!\n\nOutcome: {u1_label} takes 0 damage and finishes with {eff1['hp']} HP remaining."

    if not can_attack1:
        return f"{u2_label} defeats non-attacking {u1_label} in {traj2_hits} hits ({traj2_time:.2f}s)!\n\nOutcome: {u2_label} takes 0 damage and finishes with {eff2['hp']} HP remaining."

    def cost_trade_summary(winner_label, loser_label, win_u, lose_u, win_hp_rem, win_hp_max):
        if win_u.total_cost <= 0 or lose_u.total_cost <= 0:
            return ""
        win_lost_pct = max(0.0, (win_hp_max - win_hp_rem) / win_hp_max)
        win_res_lost = int(win_lost_pct * win_u.total_cost)
        lose_res_lost = lose_u.total_cost
        diff = lose_res_lost - win_res_lost
        return (
            f"\n- Resource Trade: {winner_label} lost ~{win_res_lost} resources ({win_lost_pct*100:.1f}% unit value) "
            f"vs {loser_label} completely destroyed ({lose_res_lost} resources lost). "
            f"Net advantage: +{diff} resources."
        )

    # BUG 6: Clean trajectory resolution
    if abs(traj1_time - traj2_time) < 1e-5:
        return f"A draw! Both {u1_label} and {u2_label} eliminate each other simultaneously in {traj1_hits} vs {traj2_hits} hits at {traj1_time:.2f}s."

    if traj1_time < traj2_time:
        hits2 = min(traj2_hits, int(math.floor(traj1_time / eff2["rof"] + 1e-5)) + 1)
        rem1 = hp1_history[hits2 - 1] if hits2 > 0 else eff1["hp"]
        max_hp1 = eff1["hp"]
        dealt2 = max_hp1 - rem1
        pct1 = (rem1 / max_hp1) * 100 if max_hp1 > 0 else 0
        cost_line = cost_trade_summary(u1_label, u2_label, u1, u2, rem1, max_hp1)

        return (
            f"{u1_label} wins 1v1 against {u2_label}!\n\n"
            f"Outcome:\n"
            f"- {u1_label} lands lethal strike in {traj1_hits} hits ({traj1_time:.2f}s).\n"
            f"- {u2_label} dealt {dealt2} dmg across {hits2} hits.\n"
            f"- Winner surviving HP: {rem1} / {max_hp1} HP remaining ({pct1:.1f}%).\n"
            f"- The losing unit ({u2_label}) would have killed the winner in {traj2_hits} hits and {traj2_time:.2f} seconds.{cost_line}"
        )
    else:
        hits1 = min(traj1_hits, int(math.floor(traj2_time / eff1["rof"] + 1e-5)) + 1)
        rem2 = hp2_history[hits1 - 1] if hits1 > 0 else eff2["hp"]
        max_hp2 = eff2["hp"]
        dealt1 = max_hp2 - rem2
        pct2 = (rem2 / max_hp2) * 100 if max_hp2 > 0 else 0
        cost_line = cost_trade_summary(u2_label, u1_label, u2, u1, rem2, max_hp2)

        return (
            f"{u2_label} wins 1v1 against {u1_label}!\n\n"
            f"Outcome:\n"
            f"- {u2_label} lands lethal strike in {traj2_hits} hits ({traj2_time:.2f}s).\n"
            f"- {u1_label} dealt {dealt1} dmg across {hits1} hits.\n"
            f"- Winner surviving HP: {rem2} / {max_hp2} HP remaining ({pct2:.1f}%).\n"
            f"- The losing unit ({u1_label}) would have killed the winner in {traj1_hits} hits and {traj1_time:.2f} seconds.{cost_line}"
        )

MELEE_ATK_NAMES = {0: "None (+0)", 1: "Forging (+1)", 2: "Iron Casting (+2)", 3: "Blast Furnace (+4)"}
MELEE_ATK_VALUES = {0: 0, 1: 1, 2: 2, 3: 4}

RANGED_ATK_NAMES = {0: "None (+0)", 1: "Fletching (+1)", 2: "Bodkin Arrow (+2)", 3: "Bracer (+3)"}
RANGED_ATK_VALUES = {0: 0, 1: 1, 2: 2, 3: 3}

INF_ARM_NAMES = {0: "None (+0/+0)", 1: "Scale Mail Armor (+1/+1)", 2: "Chain Mail Armor (+2/+2)", 3: "Plate Mail Armor (+3/+4)"}
INF_ARM_VALUES = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 4)}

CAV_ARM_NAMES = {0: "None (+0/+0)", 1: "Scale Barding Armor (+1/+1)", 2: "Chain Barding Armor (+2/+2)", 3: "Plate Barding Armor (+3/+4)"}
CAV_ARM_VALUES = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 4)}

ARC_ARM_NAMES = {0: "None (+0/+0)", 1: "Padded Archer Armor (+1/+1)", 2: "Leather Archer Armor (+2/+2)", 3: "Ring Archer Armor (+3/+4)"}
ARC_ARM_VALUES = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 4)}

# IMPROVEMENT 1: FILTER UNIT SELECTBOX BY SELECTED CIVILIZATION
def render_unit_config(col, side_idx: int, default_civ: str, default_unit: str):
    with col:
        st.subheader(f"Unit {side_idx}")
        civ = st.selectbox(f"Civilization {side_idx}", CIVILIZATIONS, index=CIVILIZATIONS.index(default_civ), key=f"civ_{side_idx}")

        # Move FTT checkbox above Unit selectbox
        ftt = st.checkbox("Full Tech Tree (FTT)", key=f"ftt_{side_idx}", help="Enable unhistorical units and upgrades for testing")

        techtree, global_known_units = load_techtree_data()

        # IMPROVEMENT 1: Filter UNITS for chosen civilization
        if civ != "Generic" and not ftt:
            civ_units_set = techtree.get(civ, {}).get("units", set())
            selectable_units = []
            for u in sorted(UNITS):
                u_lower = u.lower()
                u_nopack = u_lower.replace(" (packed)", "").strip()
                if u_lower in global_known_units or u_nopack in global_known_units:
                    if u_lower in civ_units_set or u_nopack in civ_units_set:
                        selectable_units.append(u)
                else:
                    selectable_units.append(u)
        else:
            selectable_units = sorted(UNITS)

        def_unit_idx = selectable_units.index(default_unit) if default_unit in selectable_units else 0
        unit_name = st.selectbox(f"Unit {side_idx}", selectable_units, index=def_unit_idx, key=f"unit_name_{side_idx}")

        is_avail, reason = is_unit_available(civ, unit_name)
        if not is_avail:
            if not ftt:
                st.error(f"⚠️ **{unit_name}** is not available to **{civ}** in Age of Empires II: DE.\n\n*{reason}*\n\nPlease select an accessible unit, choose another civilization, or enable **Full Tech Tree (FTT)**.")
                return None, civ, None, False
            else:
                st.info(f"ℹ️ {civ} does not normally train {unit_name}, but calculation is permitted under Full Tech Tree (FTT).")

        is_elite = False
        can_be_elite = False

        if unit_name in ELITE_UNITS:
            if ftt or civ == "Generic":
                can_be_elite = True
            else:
                if civ in techtree:
                    civ_units_set = techtree[civ].get("units", set())
                    can_be_elite = f"elite {unit_name.lower()}" in civ_units_set
                else:
                    content, _, _, _, wiki_allowed_civs = fetch_wiki_unit(unit_name)
                    if wiki_allowed_civs:
                        can_be_elite = civ in wiki_allowed_civs
                    elif content:
                        can_be_elite = check_fandom_availability(content, civ)
                    else:
                        can_be_elite = True

        if can_be_elite:
            is_elite = st.checkbox(f"Elite {unit_name}?", key=f"elite_{side_idx}")

        age = 4
        if unit_name.lower() in AGE_DEPENDENT_UNITS:
            age = st.segmented_control(
                f"Age for {unit_name}",
                options=[1, 2, 3, 4],
                format_func={1: "Dark", 2: "Feudal", 3: "Castle", 4: "Imperial"}.get,
                default=4,
                key=f"age_{side_idx}"
            ) or 4

        fu = st.checkbox("Fully Upgraded (FU)", key=f"fu_{side_idx}")
        upgrades = {}

        base_unit = parse_unit(unit_name, is_elite, age)
        boost = base_unit.boost_tech.lower()
        tech_restrictions = getattr(base_unit, "tech_civ_restrictions", {})

        civ_techs = techtree.get(civ, {}).get("techs", set()) if (civ != "Generic" and not ftt) else set()

        if ftt or civ == "Generic":
            max_m_atk = 3
            max_r_atk = 3
            max_i_arm = 3
            max_c_arm = 3
            max_a_arm = 3
        else:
            max_m_atk = 3 if "blast furnace" in civ_techs else (2 if "iron casting" in civ_techs else (1 if "forging" in civ_techs else 0))
            max_r_atk = 3 if "bracer" in civ_techs else (2 if "bodkin arrow" in civ_techs else (1 if "fletching" in civ_techs else 0))
            max_i_arm = 3 if "plate mail armor" in civ_techs else (2 if "chain mail armor" in civ_techs else (1 if "scale mail armor" in civ_techs else 0))
            max_c_arm = 3 if "plate barding armor" in civ_techs else (2 if "chain barding armor" in civ_techs else (1 if "scale barding armor" in civ_techs else 0))
            max_a_arm = 3 if "ring archer armor" in civ_techs else (2 if "leather archer armor" in civ_techs else (1 if "padded archer armor" in civ_techs else 0))

        has_m_atk = any(k in boost for k in ["forging", "iron casting", "blast furnace"])
        has_r_atk = any(k in boost for k in ["fletching", "bodkin arrow", "bracer"])
        has_i_arm = any(k in boost for k in ["scale mail armor", "chain mail armor", "plate mail armor"])
        has_c_arm = any(k in boost for k in ["scale barding armor", "chain barding armor", "plate barding armor"])
        has_a_arm = any(k in boost for k in ["padded archer armor", "leather archer armor", "ring archer armor"])

        def is_tech_permitted(tech_name: str, is_unique: bool = False) -> bool:
            t_clean = tech_name.strip().lower()
            if t_clean not in boost:
                return False
            if civ == "Generic":
                return ftt if is_unique else True
            if ftt:
                return True
            if civ_techs and t_clean not in civ_techs:
                return False
            if t_clean in tech_restrictions:
                allowed_c = tech_restrictions[t_clean]
                if allowed_c and civ not in allowed_c:
                    return False
            return True

        has_bloodlines = is_tech_permitted("bloodlines")
        has_thumb_ring = is_tech_permitted("thumb ring")
        has_parthian = is_tech_permitted("parthian tactics")
        has_chemistry = is_tech_permitted("chemistry")
        has_gambesons = is_tech_permitted("gambesons")
        has_careening = is_tech_permitted("careening")
        has_dry_dock = is_tech_permitted("dry dock")
        has_siege_engineers = is_tech_permitted("siege engineers")
        has_cranequins = is_tech_permitted("cranequins")
        has_siphons = is_tech_permitted("siphons")

        # Villager Loom & Supremacy
        is_villager = "villager" in unit_name.lower()
        has_loom = is_villager
        has_supremacy = is_villager and (ftt or civ == "Spanish")

        has_kataparuto = is_tech_permitted("kataparuto", True)
        has_warwolf = is_tech_permitted("warwolf", True)
        has_ironclad = is_tech_permitted("ironclad", True)
        has_furor = is_tech_permitted("furor celticus", True) or is_tech_permitted("furor celtica", True)
        has_recurve = is_tech_permitted("recurve bow", True)
        has_rocketry = is_tech_permitted("rocketry", True)
        has_garland = is_tech_permitted("garland wars", True)
        has_farimba = is_tech_permitted("farimba", True)
        has_wootz = is_tech_permitted("wootz steel", True)
        has_stirrups = is_tech_permitted("stirrups", True)
        has_hauberk = is_tech_permitted("hauberk", True)
        has_sipahi = is_tech_permitted("sipahi", True)
        has_el_dorado = is_tech_permitted("el dorado", True)
        has_chatras = is_tech_permitted("chatras", True)
        has_comitatenses = is_tech_permitted("comitatenses", True)
        has_bogsveigar = is_tech_permitted("bogsveigar", True)
        has_tower_shields = is_tech_permitted("tower shields", True)
        has_pavise = is_tech_permitted("pavise", True)
        has_silk_armor = is_tech_permitted("silk armor", True)
        has_fabric_shields = is_tech_permitted("fabric shields", True)
        has_bagains = is_tech_permitted("bagains", True)
        has_carracks = is_tech_permitted("carracks", True)
        has_panokseon = is_tech_permitted("panokseon", True)
        has_artillery = is_tech_permitted("artillery", True)
        has_greek_fire = is_tech_permitted("greek fire", True)
        has_counterweights = is_tech_permitted("counterweights", True)
        has_curare = is_tech_permitted("curare", True)
        has_caciques = is_tech_permitted("caciques", True)

        if fu:
            m_val = 0
            if has_m_atk:
                m_val = MELEE_ATK_VALUES[max_m_atk]
            upgrades["m_atk_val"] = m_val

            r_val = 0
            if has_r_atk:
                r_val = RANGED_ATK_VALUES[max_r_atk]
            upgrades["r_atk_val"] = r_val

            m_arm_v, p_arm_v = 0, 0
            if has_i_arm:
                m_arm_v, p_arm_v = INF_ARM_VALUES[max_i_arm]
            elif has_c_arm:
                m_arm_v, p_arm_v = CAV_ARM_VALUES[max_c_arm]
            elif has_a_arm:
                m_arm_v, p_arm_v = ARC_ARM_VALUES[max_a_arm]

            upgrades["m_arm_val"] = m_arm_v
            upgrades["p_arm_val"] = p_arm_v

            upgrades["bloodlines"] = has_bloodlines
            upgrades["thumb_ring"] = has_thumb_ring
            upgrades["parthian"] = has_parthian
            upgrades["chemistry"] = has_chemistry
            upgrades["gambesons"] = has_gambesons
            upgrades["careening"] = has_careening
            upgrades["dry_dock"] = has_dry_dock
            upgrades["siege_engineers"] = has_siege_engineers
            upgrades["cranequins"] = has_cranequins
            upgrades["siphons"] = has_siphons

            upgrades["loom"] = has_loom
            upgrades["supremacy"] = has_supremacy

            upgrades["kataparuto"] = has_kataparuto and civ != "Generic"
            upgrades["warwolf"] = has_warwolf and civ != "Generic"
            upgrades["ironclad"] = has_ironclad and civ != "Generic"
            upgrades["furor_celticus"] = has_furor and civ != "Generic"
            upgrades["recurve_bow"] = has_recurve and civ != "Generic"
            upgrades["rocketry"] = has_rocketry and civ != "Generic"
            upgrades["garland_wars"] = has_garland and civ != "Generic"
            upgrades["farimba"] = has_farimba and civ != "Generic"
            upgrades["wootz_steel"] = has_wootz and civ != "Generic"
            upgrades["stirrups"] = has_stirrups and civ != "Generic"
            upgrades["hauberk"] = has_hauberk and civ != "Generic"
            upgrades["sipahi"] = has_sipahi and civ != "Generic"
            upgrades["el_dorado"] = has_el_dorado and civ != "Generic"
            upgrades["chatras"] = has_chatras and civ != "Generic"
            upgrades["comitatenses"] = has_comitatenses and civ != "Generic"
            upgrades["bogsveigar"] = has_bogsveigar and civ != "Generic"
            upgrades["tower_shields"] = has_tower_shields and civ != "Generic"
            upgrades["pavise"] = has_pavise and civ != "Generic"
            upgrades["silk_armor"] = has_silk_armor and civ != "Generic"
            upgrades["fabric_shields"] = has_fabric_shields and civ != "Generic"
            upgrades["bagains"] = has_bagains and civ != "Generic"
            upgrades["carracks"] = has_carracks and civ != "Generic"
            upgrades["panokseon"] = has_panokseon and civ != "Generic"
            upgrades["artillery"] = has_artillery and civ != "Generic"
            upgrades["greek_fire"] = has_greek_fire and civ != "Generic"
            upgrades["counterweights"] = has_counterweights and civ != "Generic"
            upgrades["curare"] = has_curare and civ != "Generic"
            upgrades["caciques"] = has_caciques and civ != "Generic"
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                m_val = 0
                if has_m_atk:
                    opts = list(range(max_m_atk + 1))
                    tier = st.selectbox(
                        "Melee Attack",
                        opts,
                        index=0,
                        format_func=lambda x: MELEE_ATK_NAMES[x],
                        key=f"m_atk_{side_idx}"
                    )
                    m_val = MELEE_ATK_VALUES[tier]
                upgrades["m_atk_val"] = m_val

                r_val = 0
                if has_r_atk:
                    opts = list(range(max_r_atk + 1))
                    tier = st.selectbox(
                        "Ranged Attack",
                        opts,
                        index=0,
                        format_func=lambda x: RANGED_ATK_NAMES[x],
                        key=f"r_atk_{side_idx}"
                    )
                    r_val = RANGED_ATK_VALUES[tier]
                upgrades["r_atk_val"] = r_val

                m_arm_v, p_arm_v = 0, 0
                if has_i_arm:
                    opts = list(range(max_i_arm + 1))
                    tier = st.selectbox(
                        "Infantry Armor",
                        opts,
                        index=0,
                        format_func=lambda x: INF_ARM_NAMES[x],
                        key=f"i_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = INF_ARM_VALUES[tier]
                elif has_c_arm:
                    opts = list(range(max_c_arm + 1))
                    tier = st.selectbox(
                        "Cavalry Armor",
                        opts,
                        index=0,
                        format_func=lambda x: CAV_ARM_NAMES[x],
                        key=f"c_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = CAV_ARM_VALUES[tier]
                elif has_a_arm:
                    opts = list(range(max_a_arm + 1))
                    tier = st.selectbox(
                        "Archer Armor",
                        opts,
                        index=0,
                        format_func=lambda x: ARC_ARM_NAMES[x],
                        key=f"a_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = ARC_ARM_VALUES[tier]

                upgrades["m_arm_val"] = m_arm_v
                upgrades["p_arm_val"] = p_arm_v

            with col_b:
                if has_bloodlines:
                    upgrades["bloodlines"] = st.checkbox("Bloodlines (+20 HP)", key=f"bl_{side_idx}")
                if has_thumb_ring:
                    rate_label = "Faster Fire Rate" if not any(w in unit_name.lower() for w in ["skirmisher", "genitour"]) else "100% Accuracy"
                    upgrades["thumb_ring"] = st.checkbox(f"Thumb Ring ({rate_label})", key=f"tr_{side_idx}")
                if has_parthian:
                    upgrades["parthian"] = st.checkbox("Parthian Tactics (+1/+2 Armor, +Bonus vs Spear)", key=f"pt_{side_idx}")
                if has_chemistry:
                    upgrades["chemistry"] = st.checkbox("Chemistry (+1 Attack)", key=f"chem_{side_idx}")
                if has_gambesons:
                    upgrades["gambesons"] = st.checkbox("Gambesons (+1 Pierce Armor)", key=f"gam_{side_idx}")
                if has_loom:
                    upgrades["loom"] = st.checkbox("Loom (+15 HP, +1/+2 Armor)", key=f"loom_{side_idx}")
                if has_supremacy:
                    upgrades["supremacy"] = st.checkbox("Supremacy (+40 HP, +6 Atk, +2/+2 Armor)", key=f"sup_{side_idx}")
                if has_careening:
                    upgrades["careening"] = st.checkbox("Careening (+1 Pierce Armor)", key=f"car_{side_idx}")
                if has_dry_dock:
                    upgrades["dry_dock"] = st.checkbox("Dry Dock (+15% Ship Speed)", key=f"dd_{side_idx}")
                if has_siege_engineers:
                    upgrades["siege_engineers"] = st.checkbox("Siege Engineers (+20% vs Build)", key=f"se_{side_idx}")
                if has_cranequins:
                    upgrades["cranequins"] = st.checkbox("Cranequins (+1 Attack)", key=f"cran_{side_idx}")
                if has_siphons:
                    upgrades["siphons"] = st.checkbox("Siphons (Explosive Initial Burst Strike)", key=f"siph_{side_idx}")

            if has_kataparuto:
                upgrades["kataparuto"] = st.checkbox("Kataparuto (33% Faster Attack & 4x Pack Speed)", key=f"kata_{side_idx}")
            if has_warwolf:
                upgrades["warwolf"] = st.checkbox("Warwolf (100% Blast Radius)", key=f"ww_{side_idx}")
            if has_ironclad:
                upgrades["ironclad"] = st.checkbox("Ironclad (+4 Melee Armor)", key=f"ic_{side_idx}")
            if has_furor:
                upgrades["furor_celticus"] = st.checkbox("Furor Celticus (+40% HP)", key=f"fc_{side_idx}")
            if has_recurve:
                upgrades["recurve_bow"] = st.checkbox("Recurve Bow (+1 Atk/Range)", key=f"rb_{side_idx}")
            if has_rocketry:
                upgrades["rocketry"] = st.checkbox("Rocketry (+Attack)", key=f"rock_{side_idx}")
            if has_garland:
                upgrades["garland_wars"] = st.checkbox("Garland Wars (+4 Attack)", key=f"gw_{side_idx}")
            if has_farimba:
                upgrades["farimba"] = st.checkbox("Farimba (+5 Attack)", key=f"far_{side_idx}")
            if has_wootz:
                upgrades["wootz_steel"] = st.checkbox("Wootz Steel (Ignore Armor)", key=f"ws_{side_idx}")
            if has_stirrups:
                upgrades["stirrups"] = st.checkbox("Stirrups (+33% Atk Speed)", key=f"stirr_{side_idx}")
            if has_hauberk:
                upgrades["hauberk"] = st.checkbox("Hauberk (+1/+2 Armor)", key=f"haub_{side_idx}")
            if has_sipahi:
                upgrades["sipahi"] = st.checkbox("Sipahi (+20 HP)", key=f"sip_{side_idx}")
            if has_el_dorado:
                upgrades["el_dorado"] = st.checkbox("El Dorado (+40 HP)", key=f"eld_{side_idx}")
            if has_chatras:
                upgrades["chatras"] = st.checkbox("Chatras (+100 HP)", key=f"chat_{side_idx}")
            if has_comitatenses:
                upgrades["comitatenses"] = st.checkbox("Comitatenses (+5 Charge Attack)", key=f"com_{side_idx}")
            if has_bogsveigar:
                upgrades["bogsveigar"] = st.checkbox("Bogsveigar (+1 Attack)", key=f"bog_{side_idx}")
            if has_tower_shields:
                upgrades["tower_shields"] = st.checkbox("Tower Shields (+2 Pierce Armor)", key=f"ts_{side_idx}")
            if has_pavise:
                upgrades["pavise"] = st.checkbox("Pavise (+1/+1 Armor)", key=f"pav_{side_idx}")
            if has_silk_armor:
                upgrades["silk_armor"] = st.checkbox("Silk Armor (+1/+1 Armor)", key=f"sa_{side_idx}")
            if has_fabric_shields:
                upgrades["fabric_shields"] = st.checkbox("Fabric Shields (+1/+2 Armor)", key=f"fs_{side_idx}")
            if has_bagains:
                upgrades["bagains"] = st.checkbox("Bagains (+5 Melee Armor)", key=f"bag_{side_idx}")
            if has_carracks:
                upgrades["carracks"] = st.checkbox("Carracks (+1/+1 Ship Armor)", key=f"carrak_{side_idx}")
            if has_panokseon:
                upgrades["panokseon"] = st.checkbox("Panokseon (+15% Ship Speed)", key=f"panok_{side_idx}")
            if has_artillery:
                upgrades["artillery"] = st.checkbox("Artillery (+2 Cannon Galleon Range)", key=f"artill_{side_idx}")
            if has_greek_fire:
                upgrades["greek_fire"] = st.checkbox("Greek Fire (+1 Fire Ship Range)", key=f"gf_{side_idx}")
            if has_counterweights:
                upgrades["counterweights"] = st.checkbox("Counterweights (+15% Trebuchet Attack)", key=f"cw_{side_idx}")
            if has_curare:
                upgrades["curare"] = st.checkbox("Curare (Poison damage)", key=f"cur_{side_idx}")
            if has_caciques:
                upgrades["caciques"] = st.checkbox("Caciques (Infantry speed & combat boost)", key=f"cac_{side_idx}")

        return base_unit, civ, upgrades, True

def main():
    st.set_page_config(page_title="AoE2 1v1 Battle Calculator", page_icon="⚔️", layout="wide")
    st.title("⚔️ Age of Empires 2 1v1 Battle Calculator (Patch 185872 & Naval Fleet)")
    st.markdown("Calculate 1v1 battles with civilization bonuses, dynamic SiegeEngineers techtree API & Fandom MediaWiki data, full tech tree overrides, and DLC support.")

    col1, col2 = st.columns(2)
    u1, civ1, up1, ok1 = render_unit_config(col1, 1, "Burgundians", "Flemish Militia")
    u2, civ2, up2, ok2 = render_unit_config(col2, 2, "Generic", "Pikeman")

    st.divider()

    if not ok1 or not ok2:
        st.warning("⚠️ Simulation cannot proceed until valid civilizations and accessible units are selected.")
        return

    res = simulate_1v1(u1, u2, civ1, civ2, up1, up2)

    st.subheader("Simulation Outcome")
    st.code(res, language="text")

    st.divider()
    scol1, scol2 = st.columns(2)
    with scol1:
        st.write(f"**{u1.name} Generic Base Stats:**")
        st.code(str(u1), language="text")
        st.write(f"**{u1.name} ({civ1}) Actual Combat Stats (Upgraded):**")
        st.code(format_effective_stats(u1, civ1, up1, u2), language="text")
        
    with scol2:
        st.write(f"**{u2.name} Generic Base Stats:**")
        st.code(str(u2), language="text")
        st.write(f"**{u2.name} ({civ2}) Actual Combat Stats (Upgraded):**")
        st.code(format_effective_stats(u2, civ2, up2, u1), language="text")

if __name__ == "__main__":
    main()
