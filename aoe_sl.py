import re
import requests
import streamlit as st

# ---------------------------------------------------------
# Age of Empires 2 1v1 Battle Calculator (Streamlit Version)
# ---------------------------------------------------------

CIVILIZATIONS = [
    "Generic", "Armenians", "Aztecs", "Bengalis", "Berbers", "Bohemians",
    "Britons", "Bulgarians", "Burgundians", "Burmese", "Byzantines", "Celts",
    "Chinese", "Cumans", "Dravidians", "Ethiopians", "Franks", "Georgians",
    "Goths", "Gurjaras", "Hindustanis", "Huns", "Incas", "Italians",
    "Japanese", "Khmer", "Koreans", "Lithuanians", "Magyars", "Malay",
    "Malians", "Mayans", "Mongols", "Persians", "Poles", "Portuguese",
    "Romans", "Saracens", "Sicilians", "Slavs", "Spanish", "Tatars",
    "Teutons", "Turks", "Vietnamese", "Vikings"
]

ALL_CIV_TEAM_UNITS = [
    "Condottiero",
    "Genitour",
    "Elite Genitour",
    "Imperial Skirmisher",
    "Kipchak",
    "Elite Kipchak"
]

UNITS = [
    "Arambai", "Arbalester", "Archer", "Armored Elephant", "Ballista Elephant",
    "Battering Ram", "Battle Elephant", "Berserk", "Blackwood Archer", "Bolas Rider",
    "Bombard Cannon", "Boyar", "Camel Archer", "Camel Rider", "Camel Scout",
    "Capped Ram", "Cataphract", "Cavalier", "Cavalry Archer", "Centurion",
    "Chakram Thrower", "Champion", "Chu Ko Nu", "Composite Bowman", "Condottiero",
    "Conquistador", "Coustillier", "Crossbowman", "Eagle Scout", "Eagle Warrior",
    "Elephant Archer", "Elite Battle Elephant", "Elite Eagle Warrior",
    "Elite Elephant Archer", "Elite Skirmisher", "Elite Steppe Lancer", "Flemish Militia",
    "Gbeto", "Genitour", "Genoese Crossbowman", "Ghulam", "Halberdier",
    "Hand Cannoneer", "Heavy Camel Rider", "Heavy Cavalry Archer", "Heavy Scorpion",
    "Houfnice", "Huskarl", "Hussar", "Hussite Wagon", "Imperial Camel Rider",
    "Imperial Skirmisher", "Janissary", "Jian Swordsman", "Kamayuk",
    "Karambit Warrior", "Keshik", "Kipchak", "Knight", "Konnik", "Legionary",
    "Leitis", "Light Cavalry", "Long Swordsman", "Longbowman", "Magyar Huszar",
    "Mameluke", "Man-at-Arms", "Mangonel", "Mangudai", "Militia", "Missionary",
    "Monaspa", "Monk", "Obuch", "Onager", "Organ Gun", "Paladin", "Pikeman",
    "Plumed Archer", "Ratha", "Rattan Archer", "Samurai", "Savar", "Scorpion",
    "Scout Cavalry", "Serjeant", "Shotel Warrior", "Shrivamsha Rider",
    "Siege Elephant", "Siege Onager", "Siege Ram", "Siege Tower", "Skirmisher",
    "Slinger", "Spearman", "Steppe Lancer", "Teutonic Knight", "Throwing Axeman",
    "Trade Cart", "Trebuchet", "Two-Handed Swordsman", "Urumi Swordsman",
    "Villager", "War Elephant", "War Wagon", "Winged Hussar", "Woad Raider",
    "Xianbei Raider"
]

ELITE_UNITS = [
    "Arambai", "Ballista Elephant", "Berserk", "Boyar", "Camel Archer",
    "Cataphract", "Centurion", "Chakram Thrower", "Chu Ko Nu", "Composite Bowman",
    "Conquistador", "Coustillier", "Gbeto", "Genitour", "Genoese Crossbowman",
    "Ghulam", "Huskarl", "Hussite Wagon", "Janissary", "Kamayuk", "Karambit Warrior",
    "Keshik", "Kipchak", "Konnik", "Leitis", "Longbowman", "Magyar Huszar",
    "Mameluke", "Mangudai", "Monaspa", "Obuch", "Organ Gun", "Plumed Archer",
    "Ratha", "Rattan Archer", "Samurai", "Serjeant", "Shotel Warrior",
    "Shrivamsha Rider", "Teutonic Knight", "Throwing Axeman", "Urumi Swordsman",
    "War Elephant", "War Wagon", "Woad Raider", "Xianbei Raider"
]

CIV_DATA = {
    "Generic": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Armenians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True},
    "Aztecs": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False},
    "Bengalis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Berbers": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False},
    "Bohemians": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Britons": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Bulgarians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Burgundians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Burmese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 1, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True},
    "Byzantines": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Celts": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Chinese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Cumans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Dravidians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Ethiopians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Franks": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Georgians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Goths": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Gurjaras": {"max_m_atk": 2, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Hindustanis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Huns": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False},
    "Incas": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Italians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Japanese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Khmer": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": False},
    "Koreans": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Lithuanians": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Magyars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False},
    "Malay": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 2, "bloodlines": False, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Malians": {"max_m_atk": 2, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Mayans": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Mongols": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Persians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Poles": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Portuguese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Romans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": False, "gambesons": True},
    "Saracens": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Sicilians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Slavs": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Spanish": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Tatars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False},
    "Teutons": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Turks": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Vietnamese": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Vikings": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
}

class Unit:
    def __init__(self, name, hp, p_attack=None, m_attack=None, rof=2.0, armor=0, pierce_armor=0, attack_bonus=None, armor_class=None, boost_tech=None, elite=False):
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

    def __str__(self):
        bonus_str = ", ".join([f"+{v} vs {k}" for k, v in self.attack_bonus.items()]) if self.attack_bonus else "None"
        class_str = ", ".join(self.armor_class) if self.armor_class else "None"
        return f"Name: {self.name}\nHP: {self.hp}\nPAttack: {self.p_attack}\nMAttack: {self.m_attack}\nROF: {self.rof}\nArmor: {self.armor}\nPierceArmor: {self.pierce_armor}\nAttack Bonus: {bonus_str}\nArmor Class: {class_str}"

@st.cache_data
def fetch_wiki_unit(unit_name):
    title = unit_name
    if title == "Villager":
        title = "Villager_(Age_of_Empires_II)"
    url = f"https://ageofempires.fandom.com/api.php?action=query&prop=revisions&titles={title}&rvprop=content&formatversion=2&format=json"
    try:
        r = requests.get(url, timeout=5).json()
        query = r.get("query", {})
        pages = query.get("pages", [])
        if not pages or pages[0].get("missing"):
            return None, ""
        content = pages[0]["revisions"][0]["content"]
        if ("Disambig" in content or "disambig" in content) and "Bombard Cannon" not in content:
            r2 = requests.get(f"https://ageofempires.fandom.com/api.php?action=query&prop=revisions&titles={title}_(Age_of_Empires_II)&rvprop=content&formatversion=2&format=json", timeout=5).json()
            content = r2["query"]["pages"][0]["revisions"][0]["content"]
        tech_match = re.search(r".+?Boosts\|Technologies(.+?)\{\{Boosts\|.+", content, flags=re.DOTALL)
        boost_tech = tech_match.group(1) if tech_match else ""
        content = re.sub(r"(<tabber>.+$)|(escription.+$)", "", content, flags=re.DOTALL)
        return content, boost_tech
    except Exception:
        return None, ""

def parse_unit(unit_name, is_elite, age):
    content, boost_tech = fetch_wiki_unit(unit_name)
    norm = unit_name.lower()

    # Accurate scaling for Serjeant and Flemish Militia across ages
    if "serjeant" in norm:
        if age <= 2:
            return Unit("Serjeant", 45, m_attack=5, rof=2.0, armor=1, pierce_armor=1, armor_class=["Infantry", "Unique unit"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite)
        elif age == 3:
            return Unit("Serjeant", 60, m_attack=8, rof=2.0, armor=2, pierce_armor=2, armor_class=["Infantry", "Unique unit"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite)
        else:
            return Unit("Elite Serjeant" if is_elite else "Serjeant", 75 if is_elite else 60, m_attack=11 if is_elite else 8, rof=2.0, armor=3 if is_elite else 2, pierce_armor=3 if is_elite else 2, armor_class=["Infantry", "Unique unit"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite)

    if "flemish militia" in norm:
        stats = {1: (40, 4, 0, 0), 2: (50, 6, 0, 1), 3: (65, 9, 1, 1), 4: (75, 12, 1, 1)}
        hp, atk, arm, parm = stats.get(age, (75, 12, 1, 1))
        return Unit("Flemish Militia", hp, m_attack=atk, rof=2.0, armor=arm, pierce_armor=parm, attack_bonus={"Cavalry": 8, "Camel": 6}, armor_class=["Infantry"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite)

    if not content:
        # Fallback stats
        return Unit(unit_name, 60, m_attack=10, rof=2.0, armor=1, pierce_armor=1, armor_class=["Infantry"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor", elite=is_elite)

    pattern = r"(Name|HP|PAttack|MAttack|ROF|Armor|PierceArmor|AttackBonus|Class) = (.+)\n"
    data = dict(re.findall(pattern, content))

    final_name = data.get("Name", unit_name)
    if is_elite and not final_name.startswith("Elite "):
        final_name = f"Elite {final_name}"

    def parse_stat(val):
        if not val:
            return None
        val = re.sub(r"\{\{tt\|([^|]+)\|.*?\}\}", r"\1", str(val))
        comma_match = re.search(r"(.+?)\s*,\s*(.+)", val)
        if comma_match:
            val = comma_match.group(2) if is_elite else comma_match.group(1)
        br_match = re.search(r"<br />(\d+) <small>", val)
        if br_match:
            val = br_match.group(1)
        num_match = re.search(r"([+-]?[\d.]+)", str(val))
        return float(num_match.group(1)) if num_match else 0

    hp = int(parse_stat(data.get("HP")) or 50)
    p_atk = int(parse_stat(data.get("PAttack"))) if data.get("PAttack") else None
    m_atk = int(parse_stat(data.get("MAttack"))) if data.get("MAttack") else None
    rof = float(parse_stat(data.get("ROF")) or 2.0)
    arm = int(parse_stat(data.get("Armor")) or 0)
    parm = int(parse_stat(data.get("PierceArmor")) or 0)

    # Bonuses
    bonus_str = data.get("AttackBonus", "")
    attack_bonus = {}
    if bonus_str:
        matches = re.findall(r"([+-]?\d+(?:\s*,\s*[+-]?\d+)?).*?vs\.?\s*.*?2class\|([^}|]+)", str(bonus_str))
        for nums, cls in matches:
            parts = [p.strip() for p in nums.split(",")]
            val = parts[1] if (is_elite and len(parts) > 1) else parts[0]
            try:
                attack_bonus[cls.strip().title()] = int(val)
            except ValueError:
                pass

    # Skirmishers get anti-unshielded bonus
    if "skirmisher" in norm:
        attack_bonus["Unshielded"] = 4 if is_elite else 3

    # Classes
    class_str = data.get("Class", "")
    armor_class = [c.strip().title() for c in re.findall(r"2class\|([^}|]+)", class_str)]
    if "jian swordsman" in norm and "Unshielded" not in armor_class:
        armor_class.append("Unshielded")

    return Unit(final_name, hp, p_atk, m_atk, rof, arm, parm, attack_bonus, armor_class, boost_tech, is_elite)

def simulate(u1, u2, civ1, civ2, fu1, fu2, ftt1, ftt2, age1, age2):
    # Check attack capabilities
    can_attack1 = (u1.p_attack is not None and u1.p_attack > 0) or (u1.m_attack is not None and u1.m_attack > 0)
    can_attack2 = (u2.p_attack is not None and u2.p_attack > 0) or (u2.m_attack is not None and u2.m_attack > 0)

    if not can_attack1 and not can_attack2:
        return f"Neither {u1.name} nor {u2.name} has an attack.\n\nStalemate! Both units cannot damage each other."

    # Compute upgrades
    c1 = CIV_DATA.get(civ1, CIV_DATA["Generic"])
    c2 = CIV_DATA.get(civ2, CIV_DATA["Generic"])

    # Unit 1 attack calculation against Unit 2
    hits1 = 0
    time1 = 0.0
    if can_attack1:
        is_pierce1 = u1.p_attack is not None
        base_atk1 = (u1.p_attack if is_pierce1 else u1.m_attack) + (3 if (fu1 or ftt1) else 0)
        if "chu ko nu" in u1.name.lower() and civ1 == "Chinese":
            base_atk1 += 2 # Rocketry
        target_arm2 = (u2.pierce_armor if is_pierce1 else u2.armor) + (4 if (fu2 or ftt2) else 0)

        # Unique mechanics
        ignores_armor = "leitis" in u1.name.lower() or (civ1 == "Dravidians" and fu1)
        if ignores_armor:
            target_arm2 = 0

        # Class bonuses
        bonus1 = sum([u1.attack_bonus.get(cls, 0) for cls in u2.armor_class])
        if civ2 == "Sicilians":
            bonus1 = int(bonus1 * 0.67) # -33% bonus damage

        dmg1 = max(1, base_atk1 - target_arm2) + bonus1

        # Multishot extra arrows
        if "chu ko nu" in u1.name.lower():
            extra = 4 if u1.elite else 2
            dmg1 += extra * max(1, 3 - target_arm2)
        elif "kipchak" in u1.name.lower():
            extra = 3 if u1.elite else 2
            dmg1 += extra * max(1, 3 - target_arm2)

        target_hp2 = u2.hp + (20 if (fu2 and c2.get("bloodlines")) else 0)
        # Civ HP bonuses
        if civ2 == "Franks" and "knight" in u2.name.lower():
            target_hp2 = int(target_hp2 * 1.2)
        elif civ2 == "Vikings" and "infantry" in str(u2.armor_class).lower():
            target_hp2 = int(target_hp2 * 1.2)

        # Simulation loop
        rof1 = u1.rof * (0.8 if (civ1 == "Mongols" and "cavalry archer" in u1.name.lower()) else 1.0)
        t_hp = target_hp2
        while t_hp > 0 and hits1 < 1000:
            charge = 40 if ("coustillier" in u1.name.lower() and hits1 == 0) else 0
            t_hp -= (dmg1 + charge)
            hits1 += 1
        time1 = max(0.0, (hits1 - 1) * rof1)

    # Unit 2 attack calculation against Unit 1
    hits2 = 0
    time2 = 0.0
    if can_attack2:
        is_pierce2 = u2.p_attack is not None
        base_atk2 = (u2.p_attack if is_pierce2 else u2.m_attack) + (3 if (fu2 or ftt2) else 0)
        if "chu ko nu" in u2.name.lower() and civ2 == "Chinese":
            base_atk2 += 2
        target_arm1 = (u1.pierce_armor if is_pierce2 else u1.armor) + (4 if (fu1 or ftt1) else 0)

        ignores_armor = "leitis" in u2.name.lower() or (civ2 == "Dravidians" and fu2)
        if ignores_armor:
            target_arm1 = 0

        bonus2 = sum([u2.attack_bonus.get(cls, 0) for cls in u1.armor_class])
        if civ1 == "Sicilians":
            bonus2 = int(bonus2 * 0.67)

        dmg2 = max(1, base_atk2 - target_arm1) + bonus2
        if "chu ko nu" in u2.name.lower():
            extra = 4 if u2.elite else 2
            dmg2 += extra * max(1, 3 - target_arm1)
        elif "kipchak" in u2.name.lower():
            extra = 3 if u2.elite else 2
            dmg2 += extra * max(1, 3 - target_arm1)

        target_hp1 = u1.hp + (20 if (fu1 and c1.get("bloodlines")) else 0)
        if civ1 == "Franks" and "knight" in u1.name.lower():
            target_hp1 = int(target_hp1 * 1.2)
        elif civ1 == "Vikings" and "infantry" in str(u1.armor_class).lower():
            target_hp1 = int(target_hp1 * 1.2)

        rof2 = u2.rof * (0.8 if (civ2 == "Mongols" and "cavalry archer" in u2.name.lower()) else 1.0)
        t_hp = target_hp1
        while t_hp > 0 and hits2 < 1000:
            charge = 40 if ("coustillier" in u2.name.lower() and hits2 == 0) else 0
            t_hp -= (dmg2 + charge)
            hits2 += 1
        time2 = max(0.0, (hits2 - 1) * rof2)

    if not can_attack1 and can_attack2:
        return f"{u1.name} does not attack.\n\n{u2.name} takes {hits2} hits and {time2:.2f} seconds to kill {u1.name}\n\n{u2.name} ({civ2}) wins 1v1 (uncontested)"

    if can_attack1 and not can_attack2:
        return f"{u2.name} does not attack.\n\n{u1.name} takes {hits1} hits and {time1:.2f} seconds to kill {u2.name}\n\n{u1.name} ({civ1}) wins 1v1 (uncontested)"

    summary = f"{u1.name} ({civ1}) takes {hits1} hits and {time1:.2f} seconds to kill {u2.name} ({civ2})\n\n{u2.name} ({civ2}) takes {hits2} hits and {time2:.2f} seconds to kill {u1.name} ({civ1})"
    if time1 < time2:
        return f"{summary}\n\n{u1.name} wins 1v1"
    elif time2 < time1:
        return f"{summary}\n\n{u2.name} wins 1v1"
    else:
        return f"{summary}\n\nBoth units take the same time to kill each other"

def main():
    st.set_page_config(page_title="AoE2 1v1 Battle Calculator", page_icon="⚔️", layout="wide")
    st.title("⚔️ Age of Empires 2 1v1 Battle Calculator")
    st.markdown("Calculate 1v1 battles with civilization bonuses, full tech tree overrides, and unique unit mechanics.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Unit 1")
        civ1 = st.selectbox("Civilization 1", CIVILIZATIONS, key="civ1")
        u1_name = st.selectbox("Unit 1", sorted(UNITS), key="u1_name")
        u1_elite = False
        if u1_name in ELITE_UNITS:
            u1_elite = st.checkbox(f"Elite {u1_name}?", key="u1_elite")
        age1 = st.segmented_control("Age for Unit 1", options=[1, 2, 3, 4], format_func={1: "Dark", 2: "Feudal", 3: "Castle", 4: "Imperial"}.get, default=4, key="age1")
        fu1 = st.checkbox("Fully Upgraded (FU)", key="fu1")
        ftt1 = st.checkbox("Full Tech Tree (All Techs)", key="ftt1")

    with col2:
        st.subheader("Unit 2")
        civ2 = st.selectbox("Civilization 2", CIVILIZATIONS, key="civ2")
        def_idx = sorted(UNITS).index("Pikeman") if "Pikeman" in UNITS else 0
        u2_name = st.selectbox("Unit 2", sorted(UNITS), index=def_idx, key="u2_name")
        u2_elite = False
        if u2_name in ELITE_UNITS:
            u2_elite = st.checkbox(f"Elite {u2_name}?", key="u2_elite")
        age2 = st.segmented_control("Age for Unit 2", options=[1, 2, 3, 4], format_func={1: "Dark", 2: "Feudal", 3: "Castle", 4: "Imperial"}.get, default=4, key="age2")
        fu2 = st.checkbox("Fully Upgraded (FU)", key="fu2")
        ftt2 = st.checkbox("Full Tech Tree (All Techs)", key="ftt2")

    unit1 = parse_unit(u1_name, u1_elite, age1)
    unit2 = parse_unit(u2_name, u2_elite, age2)

    st.divider()
    res = simulate(unit1, unit2, civ1, civ2, fu1, fu2, ftt1, ftt2, age1, age2)
    st.subheader("Simulation Outcome")
    st.code(res, language="text")

    st.divider()
    scol1, scol2 = st.columns(2)
    with scol1:
        st.write(f"**{unit1.name} Properties:**")
        st.code(str(unit1))
    with scol2:
        st.write(f"**{unit2.name} Properties:**")
        st.code(str(unit2))

if __name__ == "__main__":
    main()
