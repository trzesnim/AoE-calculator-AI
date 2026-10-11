import re
import math
import requests
import streamlit as st

# ==============================================================================
# Age of Empires II: Definitive Edition 1v1 Battle Calculator
# Updated for Patch 185872 & All Multiplayer DLCs:
# - The Viking Sagas (Danes, Saxons, Varangians, and Vikings rework)
# - The Last Chieftains (Mapuche, Muisca, Tupi)
# - The Mountain Royals (Armenians, Georgians)
# - Return of Rome (Romans)
# - Dynasties of India (Bengalis, Dravidians, Gurjaras, Hindustanis)
# - Dawn of the Dukes (Bohemians, Poles)
# - Lords of the West (Burgundians, Sicilians)
# ==============================================================================

CIVILIZATIONS = [
    "Generic", "Armenians", "Aztecs", "Bengalis", "Berbers", "Bohemians",
    "Britons", "Bulgarians", "Burgundians", "Burmese", "Byzantines", "Celts",
    "Chinese", "Cumans", "Danes", "Dravidians", "Ethiopians", "Franks",
    "Georgians", "Goths", "Gurjaras", "Hindustanis", "Huns", "Incas",
    "Italians", "Japanese", "Khmer", "Koreans", "Lithuanians", "Magyars",
    "Malay", "Malians", "Mapuche", "Mayans", "Mongols", "Muisca",
    "Persians", "Poles", "Portuguese", "Romans", "Saracens", "Saxons",
    "Sicilians", "Slavs", "Spanish", "Tatars", "Teutons", "Tupi",
    "Turks", "Varangians", "Vietnamese", "Vikings"
]

ALL_CIV_TEAM_UNITS = [
    "Condottiero",
    "Genitour",
    "Elite Genitour",
    "Imperial Skirmisher",
    "Kipchak",
    "Elite Kipchak"
]

AGE_DEPENDENT_UNITS = [
    "scout cavalry",
    "eagle scout",
    "flemish militia",
    "serjeant"
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
    "Gbeto", "Genitour", "Genoese Crossbowman", "Ghulam", "Guecha Warrior",
    "Halberdier", "Hand Cannoneer", "Hearth Troop", "Heavy Camel Rider",
    "Heavy Cavalry Archer", "Heavy Scorpion", "Houfnice", "Huskarl", "Hussar",
    "Hussite Wagon", "Ibirapema Warrior", "Imperial Camel Rider",
    "Imperial Skirmisher", "Janissary", "Jian Swordsman", "Jomsviking",
    "Kamayuk", "Karambit Warrior", "Keshik", "Kipchak", "Knight", "Kona",
    "Konnik", "Legionary", "Leitis", "Light Cavalry", "Long Swordsman",
    "Longbowman", "Magyar Huszar", "Mameluke", "Man-at-Arms", "Mangonel",
    "Mangudai", "Militia", "Missionary", "Monaspa", "Monk", "Mounted Crossbowman",
    "Obuch", "Onager", "Organ Gun", "Paladin", "Pikeman", "Plumed Archer",
    "Ratha", "Rattan Archer", "Samurai", "Savar", "Scorpion", "Scout Cavalry",
    "Serjeant", "Shotel Warrior", "Shrivamsha Rider", "Siege Elephant",
    "Siege Onager", "Siege Ram", "Siege Tower", "Skirmisher", "Slinger",
    "Spearman", "Steppe Lancer", "Teutonic Knight", "Throwing Axeman",
    "Trade Cart", "Trebuchet", "Two-Handed Swordsman", "Urumi Swordsman",
    "Varangian Guard", "Villager", "War Elephant", "War Wagon", "Warrior Priest",
    "Winged Hussar", "Woad Raider", "Xianbei Raider"
]

ELITE_UNITS = [
    "Arambai", "Ballista Elephant", "Berserk", "Bolas Rider", "Boyar", "Camel Archer",
    "Cataphract", "Centurion", "Chakram Thrower", "Chu Ko Nu", "Composite Bowman",
    "Conquistador", "Coustillier", "Gbeto", "Genitour", "Genoese Crossbowman",
    "Ghulam", "Guecha Warrior", "Hearth Troop", "Huskarl", "Hussite Wagon",
    "Ibirapema Warrior", "Janissary", "Jomsviking", "Kamayuk", "Karambit Warrior",
    "Keshik", "Kipchak", "Kona", "Konnik", "Leitis", "Longbowman", "Magyar Huszar",
    "Mameluke", "Mangudai", "Monaspa", "Obuch", "Organ Gun", "Plumed Archer",
    "Ratha", "Rattan Archer", "Samurai", "Serjeant", "Shotel Warrior",
    "Shrivamsha Rider", "Teutonic Knight", "Throwing Axeman", "Urumi Swordsman",
    "Varangian Guard", "War Elephant", "War Wagon", "Woad Raider", "Xianbei Raider"
]

# Tech tree limits and features per civilization
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
    "Cumans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": False, "gambesons": True},
    "Danes": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
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
    "Mapuche": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Mayans": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Mongols": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Muisca": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Persians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Poles": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Portuguese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Romans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": False, "gambesons": True},
    "Saracens": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Saxons": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Sicilians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Slavs": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Spanish": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Tatars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False},
    "Teutons": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Tupi": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 0, "max_i_arm": 2, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Turks": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Varangians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Vietnamese": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Vikings": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
}

# Unique units dedicated exclusively to particular civilizations
EXCLUSIVE_UNIQUE_UNITS = {
    "Arambai": ["Burmese"],
    "Ballista Elephant": ["Khmer"],
    "Berserk": ["Vikings"],
    "Bolas Rider": ["Mapuche"],
    "Boyar": ["Slavs"],
    "Camel Archer": ["Berbers"],
    "Cataphract": ["Byzantines"],
    "Centurion": ["Romans"],
    "Chakram Thrower": ["Gurjaras"],
    "Chu Ko Nu": ["Chinese"],
    "Composite Bowman": ["Armenians"],
    "Conquistador": ["Spanish"],
    "Coustillier": ["Burgundians"],
    "Flemish Militia": ["Burgundians"],
    "Gbeto": ["Malians"],
    "Genoese Crossbowman": ["Italians"],
    "Ghulam": ["Hindustanis"],
    "Guecha Warrior": ["Muisca"],
    "Hearth Troop": ["Saxons"],
    "Houfnice": ["Bohemians"],
    "Huskarl": ["Goths"],
    "Hussite Wagon": ["Bohemians"],
    "Ibirapema Warrior": ["Tupi"],
    "Janissary": ["Turks"],
    "Jomsviking": ["Danes"],
    "Kamayuk": ["Incas"],
    "Karambit Warrior": ["Malay"],
    "Keshik": ["Tatars"],
    "Kona": ["Mapuche"],
    "Konnik": ["Bulgarians"],
    "Legionary": ["Romans"],
    "Leitis": ["Lithuanians"],
    "Longbowman": ["Britons"],
    "Magyar Huszar": ["Magyars"],
    "Mameluke": ["Saracens"],
    "Mangudai": ["Mongols"],
    "Missionary": ["Spanish"],
    "Monaspa": ["Georgians"],
    "Obuch": ["Poles"],
    "Organ Gun": ["Portuguese"],
    "Plumed Archer": ["Mayans"],
    "Ratha": ["Bengalis"],
    "Rattan Archer": ["Vietnamese"],
    "Samurai": ["Japanese"],
    "Savar": ["Persians"],
    "Serjeant": ["Sicilians"],
    "Shotel Warrior": ["Ethiopians"],
    "Shrivamsha Rider": ["Gurjaras"],
    "Slinger": ["Incas"],
    "Teutonic Knight": ["Teutons"],
    "Throwing Axeman": ["Franks"],
    "Urumi Swordsman": ["Dravidians"],
    "Varangian Guard": ["Varangians", "Byzantines"],
    "War Elephant": ["Persians"],
    "War Wagon": ["Koreans"],
    "Warrior Priest": ["Armenians"],
    "Winged Hussar": ["Poles", "Lithuanians"],
    "Woad Raider": ["Celts"]
}

# Civilizations without standard stable cavalry
NO_STABLE_CIVS = ["Aztecs", "Incas", "Mayans", "Muisca", "Tupi"]

# Specific unit availability restrictions
UNIT_RESTRICTIONS = {
    "Halberdier": {
        "banned": ["Turks", "Aztecs", "Berbers", "Chinese", "Italians", "Malians", "Mongols", "Portuguese", "Saracens"]
    },
    "Paladin": {
        "allowed": ["Burgundians", "Byzantines", "Celts", "Cumans", "Franks", "Huns", "Lithuanians", "Magyars", "Spanish", "Teutons"]
    },
    "Arbalester": {
        "banned": ["Bulgarians", "Burmese", "Celts", "Cumans", "Franks", "Goths", "Huns", "Persians", "Slavs", "Spanish", "Teutons", "Turks"]
    },
    "Champion": {
        "banned": ["Bulgarians", "Ethiopians", "Huns", "Khmer", "Malay", "Mayans", "Persians", "Tatars"]
    },
    "Hand Cannoneer": {
        "banned": ["Britons", "Celts", "Chinese", "Huns", "Mayans", "Mongols", "Aztecs", "Incas", "Muisca", "Tupi", "Mapuche"]
    },
    "Camel Rider": {
        "allowed": ["Berbers", "Byzantines", "Chinese", "Cumans", "Ethiopians", "Gurjaras", "Hindustanis", "Malians", "Mongols", "Persians", "Saracens", "Tatars", "Turks"]
    },
    "Heavy Camel Rider": {
        "allowed": ["Berbers", "Byzantines", "Chinese", "Ethiopians", "Gurjaras", "Hindustanis", "Malians", "Mongols", "Persians", "Saracens", "Tatars", "Turks"]
    },
    "Imperial Camel Rider": {
        "allowed": ["Hindustanis"]
    },
    "Steppe Lancer": {
        "allowed": ["Mongols", "Tatars", "Cumans", "Chinese"]
    },
    "Elite Steppe Lancer": {
        "allowed": ["Mongols", "Tatars", "Cumans", "Chinese"]
    },
    "Battle Elephant": {
        "allowed": ["Bengalis", "Burmese", "Khmer", "Malay", "Vietnamese"]
    },
    "Elite Battle Elephant": {
        "allowed": ["Bengalis", "Burmese", "Khmer", "Malay", "Vietnamese"]
    },
    "Armored Elephant": {
        "allowed": ["Bengalis", "Dravidians", "Gurjaras", "Hindustanis"]
    },
    "Siege Elephant": {
        "allowed": ["Bengalis", "Dravidians", "Gurjaras", "Hindustanis"]
    },
    "Mounted Crossbowman": {
        "allowed": ["Bohemians", "Britons", "Burgundians", "Franks", "Lithuanians", "Magyars", "Poles", "Portuguese", "Romans", "Saxons", "Sicilians", "Slavs"]
    }
}

def is_unit_available(civ: str, unit_name: str) -> tuple[bool, str]:
    if civ == "Generic":
        return True, ""

    # Alliance shared units available to all civs
    if unit_name in ALL_CIV_TEAM_UNITS:
        return True, ""

    base_name = unit_name.replace("Elite ", "")

    # Check exclusive unique units
    if base_name in EXCLUSIVE_UNIQUE_UNITS:
        allowed = EXCLUSIVE_UNIQUE_UNITS[base_name]
        if civ not in allowed:
            return False, f"{civ} does not get access to {unit_name}."

    # Check Meso / Native American stable restrictions
    if civ in NO_STABLE_CIVS:
        cavalry_units = ["Knight", "Cavalier", "Paladin", "Scout Cavalry", "Light Cavalry", "Hussar", "Camel Rider", "Heavy Camel Rider", "Steppe Lancer", "Battle Elephant"]
        if base_name in cavalry_units:
            return False, f"{civ} does not have access to Stables ({unit_name})."

    # Non-American civilizations do not get Eagle units
    if base_name in ["Eagle Scout", "Eagle Warrior", "Elite Eagle Warrior"]:
        if civ not in ["Aztecs", "Incas", "Mayans", "Mapuche", "Muisca", "Tupi"]:
            return False, f"{civ} does not get access to {unit_name}."

    # Check specific ban/allow lists
    if base_name in UNIT_RESTRICTIONS:
        rule = UNIT_RESTRICTIONS[base_name]
        if "banned" in rule and civ in rule["banned"]:
            return False, f"{civ} does not get access to {unit_name}."
        if "allowed" in rule and civ not in rule["allowed"]:
            return False, f"{civ} does not get access to {unit_name}."

    return True, ""

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
def fetch_wiki_unit(unit_name: str):
    title = unit_name.replace(" ", "_")
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

# Curated unit baseline fallbacks for modern Patch 185872
CURATED_UNITS = {
    "Knight": (100, None, 10, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Cavalier": (120, None, 12, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Paladin": (160, None, 14, 1.9, 2, 3, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Scout Cavalry": (45, None, 3, 2.04, 0, 2, {"Monk": 6}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Light Cavalry": (60, None, 7, 2.0, 0, 2, {"Monk": 10}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Hussar": (75, None, 7, 1.9, 0, 2, {"Monk": 12}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Pikeman": (55, None, 4, 3.05, 1, 0, {"Cavalry": 22, "Camel": 18, "War elephant": 25}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Halberdier": (60, None, 6, 3.05, 1, 0, {"Cavalry": 32, "Camel": 26, "War elephant": 28}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Arbalester": (40, 6, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Crossbowman": (35, 5, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Champion": (70, None, 13, 2.0, 1, 1, {"Eagle Warrior": 8, "Standard building": 4}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons"),
    "Jian Swordsman": (65, None, 12, 2.0, 1, 1, {"Eagle Warrior": 6}, ["Infantry", "Unshielded"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons"),
    "Chu Ko Nu": (45, 8, None, 3.0, 0, 0, {"Spearman": 2}, ["Archer", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry"),
    "Kipchak": (40, 4, None, 2.2, 0, 0, {"Spearman": 2}, ["Archer", "Cavalry archer", "Cavalry", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Bloodlines, Thumb Ring"),
    "Coustillier": (115, None, 8, 1.9, 2, 2, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor"),
    "Obuch": (80, None, 8, 1.9, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Leitis": (100, None, 12, 1.9, 1, 1, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Urumi Swordsman": (55, None, 8, 2.0, 1, 0, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Varangian Guard": (75, None, 12, 1.9, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Jomsviking": (70, None, 11, 2.0, 1, 1, {"Building": 4}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Hearth Troop": (70, 7, 10, 2.0, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Bolas Rider": (60, 6, None, 2.0, 0, 1, {}, ["Cavalry", "Cavalry archer", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Bloodlines"),
    "Kona": (80, None, 9, 1.9, 1, 1, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Bloodlines"),
    "Guecha Warrior": (65, None, 9, 2.0, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Ibirapema Warrior": (60, None, 10, 1.9, 1, 1, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Mounted Crossbowman": (50, 6, None, 2.1, 0, 1, {}, ["Cavalry", "Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines"),
    "Monk": (30, None, None, 5.5, 0, 0, {}, ["Monk"], ""),
    "Villager": (25, None, 3, 2.03, 0, 0, {}, [], ""),
    "Trade Cart": (70, None, None, 2.0, 0, 0, {}, [], "")
}

def parse_unit(unit_name: str, is_elite: bool, age: int) -> Unit:
    norm = unit_name.lower()

    # Dynamic scaling for age-dependent units
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

    if "scout cavalry" in norm:
        atk = 3 if age <= 1 else (5 if age == 2 else 5)
        return Unit("Scout Cavalry", 45, m_attack=atk, rof=2.04, armor=0, pierce_armor=2, attack_bonus={"Monk": 6}, armor_class=["Cavalry"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines", elite=is_elite)

    if "eagle scout" in norm:
        atk = 4 if age <= 2 else 7
        return Unit("Eagle Scout", 50 if age <= 2 else 55, m_attack=atk, rof=2.0, armor=0, pierce_armor=2 if age <= 2 else 3, attack_bonus={"Cavalry": 3, "Camel": 1}, armor_class=["Infantry", "Eagle Warrior"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor", elite=is_elite)

    content, boost_tech = fetch_wiki_unit(unit_name)

    if not content and unit_name in CURATED_UNITS:
        c = CURATED_UNITS[unit_name]
        return Unit(f"Elite {unit_name}" if (is_elite and not unit_name.startswith("Elite")) else unit_name, c[0], c[1], c[2], c[3], c[4], c[5], dict(c[6]), list(c[7]), c[8], is_elite)

    if not content:
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

    if "skirmisher" in norm:
        attack_bonus["Unshielded"] = 4 if is_elite else 3

    class_str = data.get("Class", "")
    armor_class = [c.strip().title() for c in re.findall(r"2class\|([^}|]+)", class_str)]
    if "jian swordsman" in norm and "Unshielded" not in armor_class:
        armor_class.append("Unshielded")

    return Unit(final_name, hp, p_atk, m_atk, rof, arm, parm, attack_bonus, armor_class, boost_tech, is_elite)

def simulate_1v1(u1: Unit, u2: Unit, civ1: str, civ2: str, up1: dict, up2: dict):
    can_attack1 = (u1.p_attack is not None and u1.p_attack > 0) or (u1.m_attack is not None and u1.m_attack > 0)
    can_attack2 = (u2.p_attack is not None and u2.p_attack > 0) or (u2.m_attack is not None and u2.m_attack > 0)

    if not can_attack1 and not can_attack2:
        return f"Neither {u1.name} nor {u2.name} has an attack.\n\nStalemate! Both units cannot damage each other."

    # Compute effective stats for Unit 1
    u1_hp = u1.hp + (20 if up1.get("bloodlines") else 0)
    if civ1 == "Franks" and any(c in u1.armor_class for c in ["Cavalry"]):
        u1_hp = int(u1_hp * 1.2)
    elif civ1 == "Vikings" and any(c in u1.armor_class for c in ["Infantry"]):
        u1_hp = int(u1_hp * 1.2)
    elif civ1 == "Turks" and any(c in u1.armor_class for c in ["Gunpowder unit"]):
        u1_hp = int(u1_hp * 1.25)
    elif civ1 == "Saracens" and any(c in u1.armor_class for c in ["Camel"]):
        u1_hp += 10
    if up1.get("sipahi") and "cavalry archer" in u1.name.lower():
        u1_hp += 20
    if up1.get("el_dorado") and "eagle" in u1.name.lower():
        u1_hp += 40
    if up1.get("chatras") and "battle elephant" in u1.name.lower():
        u1_hp += 100

    # Compute effective stats for Unit 2
    u2_hp = u2.hp + (20 if up2.get("bloodlines") else 0)
    if civ2 == "Franks" and any(c in u2.armor_class for c in ["Cavalry"]):
        u2_hp = int(u2_hp * 1.2)
    elif civ2 == "Vikings" and any(c in u2.armor_class for c in ["Infantry"]):
        u2_hp = int(u2_hp * 1.2)
    elif civ2 == "Turks" and any(c in u2.armor_class for c in ["Gunpowder unit"]):
        u2_hp = int(u2_hp * 1.25)
    elif civ2 == "Saracens" and any(c in u2.armor_class for c in ["Camel"]):
        u2_hp += 10
    if up2.get("sipahi") and "cavalry archer" in u2.name.lower():
        u2_hp += 20
    if up2.get("el_dorado") and "eagle" in u2.name.lower():
        u2_hp += 40
    if up2.get("chatras") and "battle elephant" in u2.name.lower():
        u2_hp += 100

    # Rate of fire adjustments
    rof1 = u1.rof
    if civ1 == "Japanese" and any(c in u1.armor_class for c in ["Infantry"]):
        rof1 *= 0.75
    elif civ1 == "Mongols" and any(c in u1.armor_class for c in ["Cavalry archer"]):
        rof1 *= 0.80
    elif civ1 == "Hindustanis" and any(c in u1.armor_class for c in ["Camel"]):
        rof1 *= 0.833
    elif up1.get("stirrups") and any(c in u1.armor_class for c in ["Cavalry"]):
        rof1 *= 0.75

    rof2 = u2.rof
    if civ2 == "Japanese" and any(c in u2.armor_class for c in ["Infantry"]):
        rof2 *= 0.75
    elif civ2 == "Mongols" and any(c in u2.armor_class for c in ["Cavalry archer"]):
        rof2 *= 0.80
    elif civ2 == "Hindustanis" and any(c in u2.armor_class for c in ["Camel"]):
        rof2 *= 0.833
    elif up2.get("stirrups") and any(c in u2.armor_class for c in ["Cavalry"]):
        rof2 *= 0.75

    # Base attacks
    is_p1 = u1.p_attack is not None
    base_atk1 = (u1.p_attack if is_p1 else u1.m_attack) or 0
    base_atk1 += (up1.get("r_atk", 0) if is_p1 else up1.get("m_atk", 0))
    if civ1 == "Burmese" and any(c in u1.armor_class for c in ["Infantry"]):
        base_atk1 += 3
    if up1.get("chemistry") and is_p1:
        base_atk1 += 1
    if up1.get("recurve_bow") and "cavalry archer" in u1.name.lower():
        base_atk1 += 1
    if up1.get("rocketry") and "chu ko nu" in u1.name.lower():
        base_atk1 += 2
    if up1.get("garland_wars") and any(c in u1.armor_class for c in ["Infantry"]):
        base_atk1 += 4
    if up1.get("farimba") and any(c in u1.armor_class for c in ["Cavalry"]):
        base_atk1 += 5

    is_p2 = u2.p_attack is not None
    base_atk2 = (u2.p_attack if is_p2 else u2.m_attack) or 0
    base_atk2 += (up2.get("r_atk", 0) if is_p2 else up2.get("m_atk", 0))
    if civ2 == "Burmese" and any(c in u2.armor_class for c in ["Infantry"]):
        base_atk2 += 3
    if up2.get("chemistry") and is_p2:
        base_atk2 += 1
    if up2.get("recurve_bow") and "cavalry archer" in u2.name.lower():
        base_atk2 += 1
    if up2.get("rocketry") and "chu ko nu" in u2.name.lower():
        base_atk2 += 2
    if up2.get("garland_wars") and any(c in u2.armor_class for c in ["Infantry"]):
        base_atk2 += 4
    if up2.get("farimba") and any(c in u2.armor_class for c in ["Cavalry"]):
        base_atk2 += 5

    # Armors
    armor_mult1 = 2 if civ1 == "Romans" else 1
    u1_m_armor = u1.armor + (up1.get("i_arm", 0) if "Infantry" in u1.armor_class else up1.get("c_arm", 0)) * armor_mult1
    u1_p_armor = u1.pierce_armor + (up1.get("a_arm", 0) if "Archer" in u1.armor_class else (up1.get("i_arm", 0) if "Infantry" in u1.armor_class else up1.get("c_arm", 0))) * armor_mult1
    if civ1 == "Teutons" and any(c in u1.armor_class for c in ["Infantry", "Cavalry"]):
        u1_m_armor += 2
    if civ1 == "Malians" and "Infantry" in u1.armor_class:
        u1_p_armor += 3
    if up1.get("gambesons") and "Infantry" in u1.armor_class:
        u1_p_armor += 1
    if up1.get("parthian") and "Cavalry archer" in u1.armor_class:
        u1_m_armor += 1
        u1_p_armor += 2
    if up1.get("hauberk") and "Knight" in u1.name:
        u1_m_armor += 1
        u1_p_armor += 2

    armor_mult2 = 2 if civ2 == "Romans" else 1
    u2_m_armor = u2.armor + (up2.get("i_arm", 0) if "Infantry" in u2.armor_class else up2.get("c_arm", 0)) * armor_mult2
    u2_p_armor = u2.pierce_armor + (up2.get("a_arm", 0) if "Archer" in u2.armor_class else (up2.get("i_arm", 0) if "Infantry" in u2.armor_class else up2.get("c_arm", 0))) * armor_mult2
    if civ2 == "Teutons" and any(c in u2.armor_class for c in ["Infantry", "Cavalry"]):
        u2_m_armor += 2
    if civ2 == "Malians" and "Infantry" in u2.armor_class:
        u2_p_armor += 3
    if up2.get("gambesons") and "Infantry" in u2.armor_class:
        u2_p_armor += 1
    if up2.get("parthian") and "Cavalry archer" in u2.armor_class:
        u2_m_armor += 1
        u2_p_armor += 2
    if up2.get("hauberk") and "Knight" in u2.name:
        u2_m_armor += 1
        u2_p_armor += 2

    # Bonus damages
    bonus1 = sum([u1.attack_bonus.get(cls, 0) for cls in u2.armor_class])
    if civ1 == "Gurjaras" and "Cavalry" in u1.armor_class:
        bonus1 = int(bonus1 * 1.4)
    if civ2 == "Sicilians":
        bonus1 = int(bonus1 * 0.67)

    bonus2 = sum([u2.attack_bonus.get(cls, 0) for cls in u1.armor_class])
    if civ2 == "Gurjaras" and "Cavalry" in u2.armor_class:
        bonus2 = int(bonus2 * 1.4)
    if civ1 == "Sicilians":
        bonus2 = int(bonus2 * 0.67)

    # Simulation Unit 1 attacks Unit 2
    hits1 = 0
    time1 = 0.0
    if can_attack1:
        cur_u2_hp = u2_hp
        cur_u2_m_arm = u2_m_armor
        cur_u2_p_arm = u2_p_armor
        while cur_u2_hp > 0 and hits1 < 1000:
            target_arm = (cur_u2_p_arm if is_p1 else cur_u2_m_arm)
            if "leitis" in u1.name.lower() or up1.get("wootz_steel"):
                target_arm = 0
            dmg = max(1, base_atk1 - target_arm) + bonus1

            # Charge attack
            if hits1 == 0:
                if "coustillier" in u1.name.lower():
                    dmg += (40 if u1.elite else 35)
                elif "urumi" in u1.name.lower():
                    dmg += (10 if u1.elite else 9)
                elif up1.get("comitatenses"):
                    dmg += 5

            # Multishot extra projectiles
            if "chu ko nu" in u1.name.lower():
                extra = 4 if u1.elite else 2
                dmg += extra * max(1, 3 - cur_u2_p_arm)
            elif "kipchak" in u1.name.lower():
                extra = 3 if u1.elite else 2
                dmg += extra * max(1, 3 - cur_u2_p_arm)

            cur_u2_hp -= dmg
            hits1 += 1

            # Obuch armor shred
            if "obuch" in u1.name.lower():
                cur_u2_m_arm = max(0, cur_u2_m_arm - 1)
                cur_u2_p_arm = max(0, cur_u2_p_arm - 1)

        time1 = max(0.0, (hits1 - 1) * rof1)

    # Simulation Unit 2 attacks Unit 1
    hits2 = 0
    time2 = 0.0
    if can_attack2:
        cur_u1_hp = u1_hp
        cur_u1_m_arm = u1_m_armor
        cur_u1_p_arm = u1_p_armor
        while cur_u1_hp > 0 and hits2 < 1000:
            target_arm = (cur_u1_p_arm if is_p2 else cur_u1_m_arm)
            if "leitis" in u2.name.lower() or up2.get("wootz_steel"):
                target_arm = 0
            dmg = max(1, base_atk2 - target_arm) + bonus2

            if hits2 == 0:
                if "coustillier" in u2.name.lower():
                    dmg += (40 if u2.elite else 35)
                elif "urumi" in u2.name.lower():
                    dmg += (10 if u2.elite else 9)
                elif up2.get("comitatenses"):
                    dmg += 5

            if "chu ko nu" in u2.name.lower():
                extra = 4 if u2.elite else 2
                dmg += extra * max(1, 3 - cur_u1_p_arm)
            elif "kipchak" in u2.name.lower():
                extra = 3 if u2.elite else 2
                dmg += extra * max(1, 3 - cur_u1_p_arm)

            cur_u1_hp -= dmg
            hits2 += 1

            if "obuch" in u2.name.lower():
                cur_u1_m_arm = max(0, cur_u1_m_arm - 1)
                cur_u1_p_arm = max(0, cur_u1_p_arm - 1)

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

def render_unit_config(col, side_idx: int, default_civ: str, default_unit: str):
    with col:
        st.subheader(f"Unit {side_idx}")
        civ = st.selectbox(f"Civilization {side_idx}", CIVILIZATIONS, index=CIVILIZATIONS.index(default_civ), key=f"civ_{side_idx}")

        def_unit_idx = sorted(UNITS).index(default_unit) if default_unit in UNITS else 0
        unit_name = st.selectbox(f"Unit {side_idx}", sorted(UNITS), index=def_unit_idx, key=f"unit_name_{side_idx}")

        is_avail, reason = is_unit_available(civ, unit_name)
        if not is_avail:
            st.error(f"⚠️ {reason}")
            return None, civ, None, False

        is_elite = False
        if unit_name in ELITE_UNITS:
            is_elite = st.checkbox(f"Elite {unit_name}?", key=f"elite_{side_idx}")

        # Age selector shown ONLY if age influences base unit stats
        age = 4
        if unit_name.lower() in AGE_DEPENDENT_UNITS:
            age = st.segmented_control(
                f"Age for {unit_name}",
                options=[1, 2, 3, 4],
                format_func={1: "Dark", 2: "Feudal", 3: "Castle", 4: "Imperial"}.get,
                default=4,
                key=f"age_{side_idx}"
            ) or 4

        c_info = CIV_DATA.get(civ, CIV_DATA["Generic"])
        fu = st.checkbox("Fully Upgraded (FU)", key=f"fu_{side_idx}")
        ftt = st.checkbox("Full Tech Tree (FTT)", key=f"ftt_{side_idx}")

        upgrades = {}
        max_m_atk = 3 if ftt else c_info["max_m_atk"]
        max_r_atk = 3 if ftt else c_info["max_r_atk"]
        max_i_arm = 3 if ftt else c_info["max_i_arm"]
        max_c_arm = 3 if ftt else c_info["max_c_arm"]
        max_a_arm = 3 if ftt else c_info["max_a_arm"]

        # Parse unit baseline to know what upgrades are relevant
        base_unit = parse_unit(unit_name, is_elite, age)
        is_melee = base_unit.m_attack is not None
        is_ranged = base_unit.p_attack is not None
        classes = base_unit.armor_class

        if fu:
            upgrades["m_atk"] = max_m_atk
            upgrades["r_atk"] = max_r_atk
            upgrades["i_arm"] = max_i_arm
            upgrades["c_arm"] = max_c_arm
            upgrades["a_arm"] = max_a_arm
            upgrades["bloodlines"] = True if (ftt or c_info["bloodlines"]) else False
            upgrades["thumb_ring"] = True if (ftt or c_info["thumb_ring"]) else False
            upgrades["parthian"] = True if (ftt or c_info["parthian"]) else False
            upgrades["chemistry"] = True if (ftt or c_info["chemistry"]) else False
            upgrades["gambesons"] = True if (ftt or c_info["gambesons"]) else False
            # Unique techs when FU is enabled
            upgrades["recurve_bow"] = (civ == "Magyars")
            upgrades["rocketry"] = (civ == "Chinese")
            upgrades["garland_wars"] = (civ == "Aztecs")
            upgrades["farimba"] = (civ == "Malians")
            upgrades["wootz_steel"] = (civ == "Dravidians")
            upgrades["stirrups"] = (civ == "Bulgarians")
            upgrades["hauberk"] = (civ == "Sicilians")
            upgrades["sipahi"] = (civ == "Turks")
            upgrades["el_dorado"] = (civ == "Mayans")
            upgrades["chatras"] = (civ == "Vietnamese")
            upgrades["comitatenses"] = (civ == "Romans")
        else:
            # Granular upgrade pickers
            st.markdown("**Upgrades & Technologies:**")
            col_a, col_b = st.columns(2)
            with col_a:
                if is_melee:
                    upgrades["m_atk"] = st.selectbox(f"Melee Attack (+0 to +{max_m_atk})", list(range(max_m_atk + 1)), index=max_m_atk, key=f"m_atk_{side_idx}")
                if is_ranged:
                    upgrades["r_atk"] = st.selectbox(f"Ranged Attack (+0 to +{max_r_atk})", list(range(max_r_atk + 1)), index=max_r_atk, key=f"r_atk_{side_idx}")
                if "Infantry" in classes:
                    upgrades["i_arm"] = st.selectbox(f"Infantry Armor (+0 to +{max_i_arm})", list(range(max_i_arm + 1)), index=max_i_arm, key=f"i_arm_{side_idx}")
                if "Cavalry" in classes:
                    upgrades["c_arm"] = st.selectbox(f"Cavalry Armor (+0 to +{max_c_arm})", list(range(max_c_arm + 1)), index=max_c_arm, key=f"c_arm_{side_idx}")
                if "Archer" in classes:
                    upgrades["a_arm"] = st.selectbox(f"Archer Armor (+0 to +{max_a_arm})", list(range(max_a_arm + 1)), index=max_a_arm, key=f"a_arm_{side_idx}")

            with col_b:
                if "Cavalry" in classes and (ftt or c_info["bloodlines"]):
                    upgrades["bloodlines"] = st.checkbox("Bloodlines (+20 HP)", key=f"bl_{side_idx}")
                if "Archer" in classes and (ftt or c_info["thumb_ring"]):
                    upgrades["thumb_ring"] = st.checkbox("Thumb Ring (100% Acc)", key=f"tr_{side_idx}")
                if "Cavalry archer" in classes and (ftt or c_info["parthian"]):
                    upgrades["parthian"] = st.checkbox("Parthian Tactics (+1/+2)", key=f"pt_{side_idx}")
                if is_ranged and (ftt or c_info["chemistry"]):
                    upgrades["chemistry"] = st.checkbox("Chemistry (+1 Attack)", key=f"chem_{side_idx}")
                if "Infantry" in classes and (ftt or c_info["gambesons"]):
                    upgrades["gambesons"] = st.checkbox("Gambesons (+1 Pierce Armor)", key=f"gam_{side_idx}")

            # Civ Unique Techs if relevant
            if civ == "Magyars" and "cavalry archer" in unit_name.lower():
                upgrades["recurve_bow"] = st.checkbox("Recurve Bow (+1 Atk/Range)", key=f"rb_{side_idx}")
            if civ == "Chinese" and "chu ko nu" in unit_name.lower():
                upgrades["rocketry"] = st.checkbox("Rocketry (+2 Attack)", key=f"rock_{side_idx}")
            if civ == "Aztecs" and "Infantry" in classes:
                upgrades["garland_wars"] = st.checkbox("Garland Wars (+4 Attack)", key=f"gw_{side_idx}")
            if civ == "Malians" and "Cavalry" in classes:
                upgrades["farimba"] = st.checkbox("Farimba (+5 Attack)", key=f"far_{side_idx}")
            if civ == "Dravidians" and ("Infantry" in classes or "Cavalry" in classes):
                upgrades["wootz_steel"] = st.checkbox("Wootz Steel (Ignore Armor)", key=f"ws_{side_idx}")
            if civ == "Bulgarians" and "Cavalry" in classes:
                upgrades["stirrups"] = st.checkbox("Stirrups (+33% Atk Speed)", key=f"stirr_{side_idx}")
            if civ == "Sicilians" and "Knight" in unit_name:
                upgrades["hauberk"] = st.checkbox("Hauberk (+1/+2 Armor)", key=f"haub_{side_idx}")
            if civ == "Turks" and "cavalry archer" in unit_name.lower():
                upgrades["sipahi"] = st.checkbox("Sipahi (+20 HP)", key=f"sip_{side_idx}")
            if civ == "Mayans" and "eagle" in unit_name.lower():
                upgrades["el_dorado"] = st.checkbox("El Dorado (+40 HP)", key=f"eld_{side_idx}")
            if civ == "Vietnamese" and "battle elephant" in unit_name.lower():
                upgrades["chatras"] = st.checkbox("Chatras (+100 HP)", key=f"chat_{side_idx}")
            if civ == "Romans" and ("legionary" in unit_name.lower() or "centurion" in unit_name.lower() or "knight" in unit_name.lower()):
                upgrades["comitatenses"] = st.checkbox("Comitatenses (+5 Charge Attack)", key=f"com_{side_idx}")

        return base_unit, civ, upgrades, True

def main():
    st.set_page_config(page_title="AoE2 1v1 Battle Calculator", page_icon="⚔️", layout="wide")
    st.title("⚔️ Age of Empires 2 1v1 Battle Calculator (Patch 185872)")
    st.markdown("Calculate 1v1 battles with civilization bonuses, full tech tree overrides, unique unit mechanics, and Patch 185872 DLCs.")

    col1, col2 = st.columns(2)
    u1, civ1, up1, ok1 = render_unit_config(col1, 1, "Franks", "Knight")
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
        st.write(f"**{u1.name} ({civ1}) Baseline Stats:**")
        st.code(str(u1))
    with scol2:
        st.write(f"**{u2.name} ({civ2}) Baseline Stats:**")
        st.code(str(u2))

if __name__ == "__main__":
    main()
