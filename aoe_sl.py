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

# Civilization tech tree maximums and tech allowances
CIV_DATA = {
    "Generic": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Armenians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Aztecs": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "siege_engineers": True},
    "Bengalis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Berbers": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "siege_engineers": True},
    "Bohemians": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Britons": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Bulgarians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Burgundians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Burmese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 1, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Byzantines": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Celts": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Chinese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Cumans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": False, "gambesons": True, "siege_engineers": True},
    "Danes": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Dravidians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 1, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Ethiopians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Franks": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Georgians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Goths": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Gurjaras": {"max_m_atk": 2, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Hindustanis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Huns": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "siege_engineers": True},
    "Incas": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Italians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Japanese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Khmer": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": False, "siege_engineers": True},
    "Koreans": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Lithuanians": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Magyars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "siege_engineers": True},
    "Malay": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 1, "max_i_arm": 2, "bloodlines": False, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Malians": {"max_m_atk": 2, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Mapuche": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Mayans": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Mongols": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Muisca": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Persians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Poles": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Portuguese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Romans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": False, "gambesons": True, "siege_engineers": True},
    "Saracens": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Saxons": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Sicilians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Slavs": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Spanish": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Tatars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "siege_engineers": True},
    "Teutons": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Tupi": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 0, "max_i_arm": 2, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Turks": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Varangians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Vietnamese": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
    "Vikings": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "siege_engineers": True},
}

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

NO_STABLE_CIVS = ["Aztecs", "Incas", "Mayans", "Muisca", "Tupi"]

# Strict unit availability restrictions across all 52 civilizations
# Note: Lithuanians & Poles get Winged Hussar, NOT standard Hussar!
UNIT_RESTRICTIONS = {
    "Cavalry Archer": {
        "banned": ["Aztecs", "Britons", "Burgundians", "Celts", "Franks", "Incas", "Mayans", "Muisca", "Teutons", "Tupi", "Vikings", "Armenians", "Bohemians"]
    },
    "Heavy Cavalry Archer": {
        "banned": ["Aztecs", "Britons", "Burgundians", "Celts", "Franks", "Incas", "Mayans", "Muisca", "Teutons", "Tupi", "Vikings", "Armenians", "Bohemians", "Bulgarians", "Burmese", "Goths", "Italians", "Malay", "Malians", "Poles", "Portuguese", "Romans", "Sicilians", "Slavs", "Spanish"]
    },
    "Hussar": {
        "banned": ["Aztecs", "Britons", "Chinese", "Franks", "Incas", "Japanese", "Lithuanians", "Malay", "Mayans", "Muisca", "Poles", "Portuguese", "Teutons", "Tupi", "Vikings"]
    },
    "Winged Hussar": {
        "allowed": ["Lithuanians", "Poles"]
    },
    "Halberdier": {
        "banned": ["Turks", "Aztecs", "Berbers", "Chinese", "Italians", "Malians", "Mongols", "Portuguese", "Saracens"]
    },
    "Paladin": {
        "allowed": ["Burgundians", "Byzantines", "Celts", "Cumans", "Franks", "Huns", "Lithuanians", "Magyars", "Spanish", "Teutons"]
    },
    "Savar": {
        "allowed": ["Persians"]
    },
    "Cavalier": {
        "banned": ["Aztecs", "Bengalis", "Dravidians", "Gurjaras", "Hindustanis", "Incas", "Mayans", "Muisca", "Saracens", "Tupi"]
    },
    "Knight": {
        "banned": ["Aztecs", "Bengalis", "Dravidians", "Gurjaras", "Hindustanis", "Incas", "Mayans", "Muisca", "Tupi"]
    },
    "Arbalester": {
        "banned": ["Bulgarians", "Burmese", "Celts", "Cumans", "Franks", "Goths", "Huns", "Persians", "Slavs", "Spanish", "Teutons", "Turks"]
    },
    "Crossbowman": {
        "banned": ["Bulgarians", "Spanish"]
    },
    "Champion": {
        "banned": ["Bulgarians", "Ethiopians", "Huns", "Khmer", "Malay", "Mayans", "Persians", "Tatars", "Romans"]
    },
    "Two-Handed Swordsman": {
        "banned": ["Persians", "Romans"]
    },
    "Legionary": {
        "allowed": ["Romans"]
    },
    "Hand Cannoneer": {
        "banned": ["Aztecs", "Britons", "Bulgarians", "Burmese", "Celts", "Chinese", "Cumans", "Huns", "Incas", "Magyars", "Malay", "Mayans", "Mongols", "Muisca", "Slavs", "Teutons", "Tupi", "Vikings", "Mapuche"]
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
    },
    "Siege Onager": {
        "allowed": ["Aztecs", "Celts", "Ethiopians", "Koreans", "Malians", "Mongols", "Saracens", "Slavs", "Teutons"]
    },
    "Siege Ram": {
        "banned": ["Britons", "Burmese", "Franks", "Goths", "Japanese", "Koreans", "Lithuanians", "Malians", "Portuguese", "Teutons", "Turks", "Vietnamese", "Vikings"]
    },
    "Houfnice": {
        "allowed": ["Bohemians"]
    }
}

def is_unit_available(civ: str, unit_name: str) -> tuple[bool, str]:
    if civ == "Generic":
        return True, ""

    if unit_name in ALL_CIV_TEAM_UNITS:
        return True, ""

    base_name = unit_name.replace("Elite ", "")

    if base_name in EXCLUSIVE_UNIQUE_UNITS:
        allowed = EXCLUSIVE_UNIQUE_UNITS[base_name]
        if civ not in allowed:
            return False, f"{civ} does not get access to {unit_name}."

    if civ in NO_STABLE_CIVS:
        cavalry_units = ["Knight", "Cavalier", "Paladin", "Scout Cavalry", "Light Cavalry", "Hussar", "Camel Rider", "Heavy Camel Rider", "Steppe Lancer", "Battle Elephant", "Cavalry Archer", "Heavy Cavalry Archer"]
        if base_name in cavalry_units:
            return False, f"{civ} does not have access to Stables ({unit_name})."

    if base_name in ["Eagle Scout", "Eagle Warrior", "Elite Eagle Warrior"]:
        if civ not in ["Aztecs", "Incas", "Mayans", "Mapuche", "Muisca", "Tupi"]:
            return False, f"{civ} does not get access to {unit_name}."

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
        p_str = str(self.p_attack) if self.p_attack is not None else "None"
        m_str = str(self.m_attack) if self.m_attack is not None else "None"
        return f"Name: {self.name}\nHP: {self.hp}\nMelee Attack: {m_str}\nPierce Attack: {p_str}\nRate of Fire (ROF): {self.rof:.2f}s\nMelee Armor: {self.armor}\nPierce Armor: {self.pierce_armor}\nAttack Bonuses: {bonus_str}\nArmor Classes: {class_str}"

@st.cache_data
def fetch_wiki_unit(unit_name: str):
    title = unit_name.replace(" ", "_")
    if title == "Villager":
        title = "Villager_(Age_of_Empires_II)"
    elif title == "Trebuchet":
        title = "Trebuchet_(Age_of_Empires_II)"
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

# Curated unit baseline fallbacks for Patch 185872 with exact historical boost technologies
CURATED_UNITS = {
    "Trebuchet": (150, 200, None, 10.0, 2, 8, {"Building": 250}, ["Siege weapon"], "Kataparuto, Warwolf, Ironclad, Furor Celticus, Siege Engineers"),
    "Knight": (100, None, 10, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Hauberk, Stirrups, Farimba, Wootz Steel, Comitatenses"),
    "Cavalier": (120, None, 12, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Hauberk, Stirrups, Farimba, Wootz Steel, Comitatenses"),
    "Paladin": (160, None, 14, 1.9, 2, 3, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Hauberk, Stirrups, Farimba"),
    "Scout Cavalry": (45, None, 3, 2.04, 0, 2, {"Monk": 6}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Silk Armor, Stirrups, Farimba"),
    "Light Cavalry": (60, None, 7, 2.0, 0, 2, {"Monk": 10}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Silk Armor, Stirrups, Farimba"),
    "Hussar": (75, None, 7, 1.9, 0, 2, {"Monk": 12}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Silk Armor, Stirrups, Farimba"),
    "Winged Hussar": (80, None, 9, 1.9, 1, 2, {"Monk": 12}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Lechitic Legacy"),
    "Pikeman": (55, None, 4, 3.05, 1, 0, {"Cavalry": 22, "Camel": 18, "War elephant": 25}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Garland Wars, Wootz Steel, Tower Shields"),
    "Halberdier": (60, None, 6, 3.05, 1, 0, {"Cavalry": 32, "Camel": 26, "War elephant": 28}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Garland Wars, Wootz Steel, Tower Shields"),
    "Archer": (30, 4, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bogsveigar"),
    "Crossbowman": (35, 5, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bogsveigar, Cranequins"),
    "Arbalester": (40, 6, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bogsveigar, Cranequins"),
    "Skirmisher": (30, 2, None, 3.0, 0, 3, {"Archer": 3, "Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Tower Shields, Hul'che Javelineers"),
    "Elite Skirmisher": (35, 3, None, 3.0, 0, 4, {"Archer": 4, "Spearman": 3, "Cavalry archer": 2}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Tower Shields, Hul'che Javelineers"),
    "Imperial Skirmisher": (35, 4, None, 3.0, 0, 4, {"Archer": 5, "Spearman": 3, "Cavalry archer": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Tower Shields, Hul'che Javelineers"),
    "Cavalry Archer": (50, 6, None, 2.0, 0, 0, {"Spearman": 2}, ["Archer", "Cavalry archer", "Cavalry"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines, Thumb Ring, Parthian Tactics, Chemistry, Recurve Bow, Sipahi, Silk Armor"),
    "Heavy Cavalry Archer": (60, 7, None, 2.0, 1, 0, {"Spearman": 4}, ["Archer", "Cavalry archer", "Cavalry"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines, Thumb Ring, Parthian Tactics, Chemistry, Recurve Bow, Sipahi, Silk Armor"),
    "Champion": (70, None, 13, 2.0, 1, 1, {"Eagle Warrior": 8, "Standard building": 4}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons, Garland Wars, Wootz Steel, Druzhina"),
    "Jian Swordsman": (65, None, 12, 2.0, 1, 1, {"Eagle Warrior": 6}, ["Infantry", "Unshielded"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons"),
    "Chu Ko Nu": (45, 8, None, 3.0, 0, 0, {"Spearman": 2}, ["Archer", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Rocketry"),
    "Kipchak": (40, 4, None, 2.2, 0, 0, {"Spearman": 2}, ["Archer", "Cavalry archer", "Cavalry", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Bloodlines, Thumb Ring"),
    "Coustillier": (115, None, 8, 1.9, 2, 2, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor"),
    "Obuch": (80, None, 8, 1.9, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Leitis": (100, None, 12, 1.9, 1, 1, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Urumi Swordsman": (55, None, 8, 2.0, 1, 0, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Wootz Steel"),
    "Varangian Guard": (75, None, 12, 1.9, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Jomsviking": (70, None, 11, 2.0, 1, 1, {"Building": 4}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Hearth Troop": (70, 7, 10, 2.0, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Bolas Rider": (60, 6, None, 2.0, 0, 1, {}, ["Cavalry", "Cavalry archer", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Bloodlines"),
    "Kona": (80, None, 9, 1.9, 1, 1, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Bloodlines"),
    "Guecha Warrior": (65, None, 9, 2.0, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Ibirapema Warrior": (60, None, 10, 1.9, 1, 1, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Mounted Crossbowman": (50, 6, None, 2.1, 0, 1, {}, ["Cavalry", "Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines"),
    "Monk": (30, None, None, 5.5, 0, 0, {}, ["Monk"], ""),
    "Villager": (25, None, 3, 2.03, 0, 0, {}, [], "Supremacy, Loom, Wheelbarrow, Hand Cart"),
    "Trade Cart": (70, None, None, 2.0, 0, 0, {}, [], "")
}

def parse_unit(unit_name: str, is_elite: bool, age: int) -> Unit:
    norm = unit_name.lower()

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
        return Unit("Eagle Scout", 50 if age <= 2 else 55, m_attack=atk, rof=2.0, armor=0, pierce_armor=2 if age <= 2 else 3, attack_bonus={"Cavalry": 3, "Camel": 1}, armor_class=["Infantry", "Eagle Warrior"], boost_tech="Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, El Dorado", elite=is_elite)

    content, boost_tech = fetch_wiki_unit(unit_name)

    # Combine wiki boost_tech with curated list for comprehensive coverage
    curated_boost = CURATED_UNITS.get(unit_name, ("", "", "", "", "", "", "", "", ""))[8]
    if curated_boost:
        boost_tech = f"{boost_tech}, {curated_boost}"

    if not content and unit_name in CURATED_UNITS:
        c = CURATED_UNITS[unit_name]
        return Unit(f"Elite {unit_name}" if (is_elite and not unit_name.startswith("Elite")) else unit_name, c[0], c[1], c[2], c[3], c[4], c[5], dict(c[6]), list(c[7]), boost_tech, is_elite)

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

    if unit_name in CURATED_UNITS:
        for c in CURATED_UNITS[unit_name][7]:
            if c not in armor_class:
                armor_class.append(c)

    return Unit(final_name, hp, p_atk, m_atk, rof, arm, parm, attack_bonus, armor_class, boost_tech, is_elite)

def compute_effective_stats(u: Unit, civ: str, up: dict, opponent: Unit = None) -> dict:
    hp = u.hp
    if up.get("bloodlines"):
        hp += 20
    if civ == "Franks" and any(c in u.armor_class for c in ["Cavalry"]):
        hp = int(hp * 1.2)
    elif civ == "Vikings" and any(c in u.armor_class for c in ["Infantry"]):
        hp = int(hp * 1.2)
    elif civ == "Turks" and any(c in u.armor_class for c in ["Gunpowder unit"]):
        hp = int(hp * 1.25)
    elif civ == "Saracens" and any(c in u.armor_class for c in ["Camel"]):
        hp += 10
    if up.get("sipahi") and "cavalry archer" in u.name.lower():
        hp += 20
    if up.get("el_dorado") and "eagle" in u.name.lower():
        hp += 40
    if up.get("chatras") and "battle elephant" in u.name.lower():
        hp += 100
    if up.get("furor_celticus") and ("siege" in str(u.armor_class).lower() or "trebuchet" in u.name.lower()):
        hp = int(hp * 1.4)

    rof = u.rof
    # Civ attack speed bonuses
    if civ == "Japanese" and any(c in u.armor_class for c in ["Infantry"]):
        rof *= 0.75
    elif civ == "Mongols" and any(c in u.armor_class for c in ["Cavalry archer"]):
        rof *= 0.80
    elif civ == "Hindustanis" and any(c in u.armor_class for c in ["Camel"]):
        rof *= 0.833
    elif up.get("stirrups") and any(c in u.armor_class for c in ["Cavalry"]):
        rof *= 0.75
    elif up.get("kataparuto") and "trebuchet" in u.name.lower():
        rof *= 0.75

    # Thumb Ring increases fire rate: Foot archers ~18% faster (0.85x), Cav Archers ~11% faster (0.90x)
    if up.get("thumb_ring"):
        if any(c in u.armor_class for c in ["Cavalry archer"]):
            rof *= 0.90
        elif any(c in u.armor_class for c in ["Archer"]):
            rof *= 0.85

    m_atk = u.m_attack
    if m_atk is not None:
        m_atk += up.get("m_atk_val", 0)
        if civ == "Burmese" and any(c in u.armor_class for c in ["Infantry"]):
            m_atk += 3
        if up.get("garland_wars") and any(c in u.armor_class for c in ["Infantry"]):
            m_atk += 4
        if up.get("farimba") and any(c in u.armor_class for c in ["Cavalry"]):
            m_atk += 5

    p_atk = u.p_attack
    if p_atk is not None:
        p_atk += up.get("r_atk_val", 0)
        if up.get("chemistry"):
            p_atk += 1
        if up.get("recurve_bow") and "cavalry archer" in u.name.lower():
            p_atk += 1
        if up.get("rocketry") and "chu ko nu" in u.name.lower():
            p_atk += 2
        if up.get("rocketry") and "scorpion" in u.name.lower():
            p_atk += 4
        if up.get("bogsveigar") and any(c in u.armor_class for c in ["Archer"]):
            p_atk += 1
        if up.get("cranequins") and any(c in u.name.lower() for c in ["crossbowman", "arbalester"]):
            p_atk += 1

    armor_mult = 2 if civ == "Romans" else 1
    m_arm = u.armor + up.get("m_arm_val", 0) * armor_mult
    p_arm = u.pierce_armor + up.get("p_arm_val", 0) * armor_mult

    if civ == "Teutons" and any(c in u.armor_class for c in ["Infantry", "Cavalry"]):
        m_arm += 2
    if civ == "Malians" and any(c in u.armor_class for c in ["Infantry"]):
        p_arm += 3
    if up.get("gambesons") and any(c in u.armor_class for c in ["Infantry"]):
        p_arm += 1
    if up.get("parthian") and any(c in u.armor_class for c in ["Cavalry archer"]):
        m_arm += 1
        p_arm += 2
    if up.get("hauberk") and "knight" in u.name.lower():
        m_arm += 1
        p_arm += 2
    if up.get("ironclad") and ("siege" in str(u.armor_class).lower() or "trebuchet" in u.name.lower()):
        m_arm += 4
    if up.get("bagains") and "two-handed" in u.name.lower():
        m_arm += 5
    if up.get("tower_shields") and any(c in u.name.lower() for c in ["spearman", "pikeman", "halberdier", "skirmisher"]):
        p_arm += 2
    if up.get("pavise") and any(c in u.name.lower() for c in ["genoese", "condottiero"]):
        m_arm += 1
        p_arm += 1
    if up.get("silk_armor") and any(c in u.name.lower() for c in ["scout", "light cavalry", "hussar", "lancer", "cavalry archer"]):
        m_arm += 1
        p_arm += 1
    if up.get("fabric_shields") and any(c in u.name.lower() for c in ["kamayuk", "slinger", "eagle"]):
        m_arm += 1
        p_arm += 2

    bonus = 0
    if opponent and opponent.armor_class:
        bonus = sum([u.attack_bonus.get(cls, 0) for cls in opponent.armor_class])
        if civ == "Gurjaras" and any(c in u.armor_class for c in ["Cavalry"]):
            bonus = int(bonus * 1.4)
        if hasattr(opponent, 'civ') and getattr(opponent, 'civ', '') == "Sicilians":
            bonus = int(bonus * 0.67)

    return {
        "hp": hp,
        "m_atk": m_atk,
        "p_atk": p_atk,
        "rof": rof,
        "m_arm": m_arm,
        "p_arm": p_arm,
        "bonus": bonus
    }

def format_effective_stats(u: Unit, civ: str, up: dict, opponent: Unit = None) -> str:
    eff = compute_effective_stats(u, civ, up, opponent)
    m_atk_str = str(eff["m_atk"]) if eff["m_atk"] is not None else "None"
    p_atk_str = str(eff["p_atk"]) if eff["p_atk"] is not None else "None"
    
    special = []
    if up.get("wootz_steel") or "leitis" in u.name.lower():
        special.append("Ignores Enemy Armor")
    if "obuch" in u.name.lower():
        special.append("Shreds Enemy Armor (-1/-1 per hit)")
    if "coustillier" in u.name.lower():
        special.append(f"Charge Attack (+{40 if u.elite else 35} 1st hit)")
    if "urumi" in u.name.lower():
        special.append(f"Charge Attack (+{10 if u.elite else 9} 1st hit)")
    if up.get("comitatenses"):
        special.append("Comitatenses Charge (+5 1st hit)")
    if "chu ko nu" in u.name.lower():
        special.append(f"Multishot ({5 if u.elite else 3} arrows)")
    if "kipchak" in u.name.lower():
        special.append(f"Multishot ({4 if u.elite else 3} arrows)")
    if up.get("kataparuto"):
        special.append("Kataparuto (33% Faster Attack & 4x Pack Speed)")
    if up.get("warwolf"):
        special.append("Warwolf (100% Blast Damage)")
    if up.get("thumb_ring"):
        rate_txt = "11% Faster Attack" if "cavalry archer" in str(u.armor_class).lower() else "18% Faster Attack"
        special.append(f"Thumb Ring ({rate_txt})")
    if civ == "Sicilians":
        special.append("Takes 33% Less Bonus Damage")
    if civ == "Romans" and any(c in u.armor_class for c in ["Infantry"]):
        special.append("2x Blacksmith Armor Effect")

    special_str = ", ".join(special) if special else "None"
    bonus_str = f"+{eff['bonus']} vs opponent classes" if eff["bonus"] > 0 else "0"

    return f"""Unit: {u.name} ({civ})
HP: {eff['hp']}
Melee Attack: {m_atk_str}
Pierce Attack: {p_atk_str}
Rate of Fire (ROF): {eff['rof']:.2f}s
Melee Armor: {eff['m_arm']}
Pierce Armor: {eff['p_arm']}
Active Bonus Dmg vs Opponent: {bonus_str}
Special Mechanics: {special_str}"""

def simulate_1v1(u1: Unit, u2: Unit, civ1: str, civ2: str, up1: dict, up2: dict):
    can_attack1 = (u1.p_attack is not None and u1.p_attack > 0) or (u1.m_attack is not None and u1.m_attack > 0)
    can_attack2 = (u2.p_attack is not None and u2.p_attack > 0) or (u2.m_attack is not None and u2.m_attack > 0)

    if not can_attack1 and not can_attack2:
        return f"Neither {u1.name} nor {u2.name} has an attack.\n\nStalemate! Both units cannot damage each other."

    eff1 = compute_effective_stats(u1, civ1, up1, u2)
    eff2 = compute_effective_stats(u2, civ2, up2, u1)

    hits1 = 0
    time1 = 0.0
    if can_attack1:
        is_p1 = eff1["p_atk"] is not None
        atk1 = eff1["p_atk"] if is_p1 else eff1["m_atk"]
        bonus1 = eff1["bonus"]
        cur_u2_hp = eff2["hp"]
        cur_u2_m_arm = eff2["m_arm"]
        cur_u2_p_arm = eff2["p_arm"]

        while cur_u2_hp > 0 and hits1 < 1000:
            target_arm = (cur_u2_p_arm if is_p1 else cur_u2_m_arm)
            if "leitis" in u1.name.lower() or up1.get("wootz_steel"):
                target_arm = 0
            dmg = max(1, atk1 - target_arm) + bonus1

            if hits1 == 0:
                if "coustillier" in u1.name.lower():
                    dmg += (40 if u1.elite else 35)
                elif "urumi" in u1.name.lower():
                    dmg += (10 if u1.elite else 9)
                elif up1.get("comitatenses"):
                    dmg += 5

            if "chu ko nu" in u1.name.lower():
                extra = 4 if u1.elite else 2
                dmg += extra * max(1, 3 - cur_u2_p_arm)
            elif "kipchak" in u1.name.lower():
                extra = 3 if u1.elite else 2
                dmg += extra * max(1, 3 - cur_u2_p_arm)

            cur_u2_hp -= dmg
            hits1 += 1

            if "obuch" in u1.name.lower():
                cur_u2_m_arm = max(0, cur_u2_m_arm - 1)
                cur_u2_p_arm = max(0, cur_u2_p_arm - 1)

        time1 = max(0.0, (hits1 - 1) * eff1["rof"])

    hits2 = 0
    time2 = 0.0
    if can_attack2:
        is_p2 = eff2["p_atk"] is not None
        atk2 = eff2["p_atk"] if is_p2 else eff2["m_atk"]
        bonus2 = eff2["bonus"]
        cur_u1_hp = eff1["hp"]
        cur_u1_m_arm = eff1["m_arm"]
        cur_u1_p_arm = eff1["p_arm"]

        while cur_u1_hp > 0 and hits2 < 1000:
            target_arm = (cur_u1_p_arm if is_p2 else cur_u1_m_arm)
            if "leitis" in u2.name.lower() or up2.get("wootz_steel"):
                target_arm = 0
            dmg = max(1, atk2 - target_arm) + bonus2

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

        time2 = max(0.0, (hits2 - 1) * eff2["rof"])

    if not can_attack1 and can_attack2:
        return f"{u1.name} ({civ1}) does not attack.\n\n{u2.name} ({civ2}) takes {hits2} hits and {time2:.2f} seconds to kill {u1.name} ({civ1})\n\n{u2.name} ({civ2}) wins 1v1 (uncontested)"

    if can_attack1 and not can_attack2:
        return f"{u2.name} ({civ2}) does not attack.\n\n{u1.name} ({civ1}) takes {hits1} hits and {time1:.2f} seconds to kill {u2.name} ({civ2})\n\n{u1.name} ({civ1}) wins 1v1 (uncontested)"

    winner_str = ""
    if time1 < time2:
        winner_str = f"{u1.name} ({civ1}) wins 1v1"
    elif time2 < time1:
        winner_str = f"{u2.name} ({civ2}) wins 1v1"
    else:
        winner_str = f"Both units take the same time to kill each other (Tie)"

    summary = (
        f"{u1.name} ({civ1}) takes {hits1} hits and {time1:.2f} seconds to kill {u2.name} ({civ2})\n\n"
        f"{u2.name} ({civ2}) takes {hits2} hits and {time2:.2f} seconds to kill {u1.name} ({civ1})\n\n"
        f"{winner_str}"
    )
    return summary

MELEE_ATK_NAMES = {0: "None (+0)", 1: "Forging (+1)", 2: "Iron Casting (+2)", 3: "Blast Furnace (+4)"}
MELEE_ATK_VALUES = {0: 0, 1: 1, 2: 2, 3: 4}

RANGED_ATK_NAMES = {0: "None (+0)", 1: "Fletching (+1)", 2: "Bodkin Arrow (+2)", 3: "Bracer (+3)"}
RANGED_ATK_VALUES = {0: 0, 1: 1, 2: 2, 3: 3}

INF_ARM_NAMES = {0: "None (+0/+0)", 1: "Scale Mail Armor (+1/+1)", 2: "Chain Mail Armor (+2/+2)", 3: "Plate Mail Armor (+3/+3)"}
INF_ARM_VALUES = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 3)}

CAV_ARM_NAMES = {0: "None (+0/+0)", 1: "Scale Barding Armor (+1/+1)", 2: "Chain Barding Armor (+2/+2)", 3: "Plate Barding Armor (+3/+4)"}
CAV_ARM_VALUES = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 4)}

ARC_ARM_NAMES = {0: "None (+0/+0)", 1: "Padded Archer Armor (+1/+1)", 2: "Leather Archer Armor (+2/+2)", 3: "Ring Archer Armor (+3/+4)"}
ARC_ARM_VALUES = {0: (0, 0), 1: (1, 1), 2: (2, 2), 3: (3, 4)}

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

        base_unit = parse_unit(unit_name, is_elite, age)
        boost = base_unit.boost_tech.lower()

        # Dynamic check: which upgrade lines apply to THIS unit based on wiki {{Boosts|Technologies}}
        has_m_atk = any(k in boost for k in ["forging", "iron casting", "blast furnace"])
        has_r_atk = any(k in boost for k in ["fletching", "bodkin arrow", "bracer"])
        has_i_arm = any(k in boost for k in ["scale mail armor", "chain mail armor", "plate mail armor"])
        has_c_arm = any(k in boost for k in ["scale barding armor", "chain barding armor", "plate barding armor"])
        has_a_arm = any(k in boost for k in ["padded archer armor", "leather archer armor", "ring archer armor"])

        has_bloodlines = "bloodlines" in boost
        has_thumb_ring = "thumb ring" in boost
        has_parthian = "parthian tactics" in boost
        has_chemistry = "chemistry" in boost
        has_gambesons = "gambesons" in boost
        has_siege_engineers = "siege engineers" in boost
        has_cranequins = "cranequins" in boost

        # Unique techs affecting this unit
        has_kataparuto = "kataparuto" in boost
        has_warwolf = "warwolf" in boost
        has_ironclad = "ironclad" in boost
        has_furor = "furor celticus" in boost
        has_recurve = "recurve bow" in boost
        has_rocketry = "rocketry" in boost
        has_garland = "garland wars" in boost
        has_farimba = "farimba" in boost
        has_wootz = "wootz steel" in boost
        has_stirrups = "stirrups" in boost
        has_hauberk = "hauberk" in boost
        has_sipahi = "sipahi" in boost
        has_el_dorado = "el dorado" in boost
        has_chatras = "chatras" in boost
        has_comitatenses = "comitatenses" in boost
        has_bogsveigar = "bogsveigar" in boost
        has_tower_shields = "tower shields" in boost
        has_pavise = "pavise" in boost
        has_silk_armor = "silk armor" in boost
        has_fabric_shields = "fabric shields" in boost
        has_bagains = "bagains" in boost

        if fu:
            upgrades["m_atk_val"] = MELEE_ATK_VALUES[max_m_atk] if has_m_atk else 0
            upgrades["r_atk_val"] = RANGED_ATK_VALUES[max_r_atk] if has_r_atk else 0
            
            m_arm_v, p_arm_v = 0, 0
            if has_i_arm:
                m_arm_v, p_arm_v = INF_ARM_VALUES[max_i_arm]
            elif has_c_arm:
                m_arm_v, p_arm_v = CAV_ARM_VALUES[max_c_arm]
            elif has_a_arm:
                m_arm_v, p_arm_v = ARC_ARM_VALUES[max_a_arm]
                
            upgrades["m_arm_val"] = m_arm_v
            upgrades["p_arm_val"] = p_arm_v
            upgrades["bloodlines"] = has_bloodlines and (ftt or c_info["bloodlines"])
            upgrades["thumb_ring"] = has_thumb_ring and (ftt or c_info["thumb_ring"])
            upgrades["parthian"] = has_parthian and (ftt or c_info["parthian"])
            upgrades["chemistry"] = has_chemistry and (ftt or c_info["chemistry"])
            upgrades["gambesons"] = has_gambesons and (ftt or c_info["gambesons"])
            upgrades["siege_engineers"] = has_siege_engineers and (ftt or c_info.get("siege_engineers", True))
            upgrades["cranequins"] = has_cranequins and (ftt or civ == "Burgundians")
            
            # Civ Unique techs under FU
            upgrades["kataparuto"] = has_kataparuto and (ftt or civ == "Japanese")
            upgrades["warwolf"] = has_warwolf and (ftt or civ == "Britons")
            upgrades["ironclad"] = has_ironclad and (ftt or civ == "Teutons")
            upgrades["furor_celticus"] = has_furor and (ftt or civ == "Celts")
            upgrades["recurve_bow"] = has_recurve and (ftt or civ == "Magyars")
            upgrades["rocketry"] = has_rocketry and (ftt or civ == "Chinese")
            upgrades["garland_wars"] = has_garland and (ftt or civ == "Aztecs")
            upgrades["farimba"] = has_farimba and (ftt or civ == "Malians")
            upgrades["wootz_steel"] = has_wootz and (ftt or civ == "Dravidians")
            upgrades["stirrups"] = has_stirrups and (ftt or civ == "Bulgarians")
            upgrades["hauberk"] = has_hauberk and (ftt or civ == "Sicilians")
            upgrades["sipahi"] = has_sipahi and (ftt or civ == "Turks")
            upgrades["el_dorado"] = has_el_dorado and (ftt or civ == "Mayans")
            upgrades["chatras"] = has_chatras and (ftt or civ == "Vietnamese")
            upgrades["comitatenses"] = has_comitatenses and (ftt or civ == "Romans")
            upgrades["bogsveigar"] = has_bogsveigar and (ftt or civ == "Vikings")
            upgrades["tower_shields"] = has_tower_shields and (ftt or civ == "Lithuanians")
            upgrades["pavise"] = has_pavise and (ftt or civ == "Italians")
            upgrades["silk_armor"] = has_silk_armor and (ftt or civ == "Tatars")
            upgrades["fabric_shields"] = has_fabric_shields and (ftt or civ == "Incas")
            upgrades["bagains"] = has_bagains and (ftt or civ == "Bulgarians")
        else:
            st.markdown("**Upgrades & Technologies:**")
            col_a, col_b = st.columns(2)
            with col_a:
                if has_m_atk:
                    opts = list(range(max_m_atk + 1))
                    tier = st.selectbox(
                        "Melee Attack",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: MELEE_ATK_NAMES[x],
                        key=f"m_atk_{side_idx}"
                    )
                    upgrades["m_atk_val"] = MELEE_ATK_VALUES[tier]
                else:
                    upgrades["m_atk_val"] = 0

                if has_r_atk:
                    opts = list(range(max_r_atk + 1))
                    tier = st.selectbox(
                        "Ranged Attack",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: RANGED_ATK_NAMES[x],
                        key=f"r_atk_{side_idx}"
                    )
                    upgrades["r_atk_val"] = RANGED_ATK_VALUES[tier]
                else:
                    upgrades["r_atk_val"] = 0

                m_arm_v, p_arm_v = 0, 0
                if has_i_arm:
                    opts = list(range(max_i_arm + 1))
                    tier = st.selectbox(
                        "Infantry Armor",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: INF_ARM_NAMES[x],
                        key=f"i_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = INF_ARM_VALUES[tier]
                elif has_c_arm:
                    opts = list(range(max_c_arm + 1))
                    tier = st.selectbox(
                        "Cavalry Armor",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: CAV_ARM_NAMES[x],
                        key=f"c_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = CAV_ARM_VALUES[tier]
                elif has_a_arm:
                    opts = list(range(max_a_arm + 1))
                    tier = st.selectbox(
                        "Archer Armor",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: ARC_ARM_NAMES[x],
                        key=f"a_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = ARC_ARM_VALUES[tier]

                upgrades["m_arm_val"] = m_arm_v
                upgrades["p_arm_val"] = p_arm_v

            with col_b:
                if has_bloodlines and (ftt or c_info["bloodlines"]):
                    upgrades["bloodlines"] = st.checkbox("Bloodlines (+20 HP)", key=f"bl_{side_idx}")
                if has_thumb_ring and (ftt or c_info["thumb_ring"]):
                    upgrades["thumb_ring"] = st.checkbox("Thumb Ring (Faster Fire Rate)", key=f"tr_{side_idx}")
                if has_parthian and (ftt or c_info["parthian"]):
                    upgrades["parthian"] = st.checkbox("Parthian Tactics (+1/+2)", key=f"pt_{side_idx}")
                if has_chemistry and (ftt or c_info["chemistry"]):
                    upgrades["chemistry"] = st.checkbox("Chemistry (+1 Attack)", key=f"chem_{side_idx}")
                if has_gambesons and (ftt or c_info["gambesons"]):
                    upgrades["gambesons"] = st.checkbox("Gambesons (+1 Pierce Armor)", key=f"gam_{side_idx}")
                if has_siege_engineers and (ftt or c_info.get("siege_engineers", True)):
                    upgrades["siege_engineers"] = st.checkbox("Siege Engineers (+20% vs Build)", key=f"se_{side_idx}")
                if has_cranequins and (ftt or civ == "Burgundians"):
                    upgrades["cranequins"] = st.checkbox("Cranequins (+1 Attack)", key=f"cran_{side_idx}")

            # Specific unique techs dynamically checked against unit's boost_tech
            if has_kataparuto and (ftt or civ == "Japanese"):
                upgrades["kataparuto"] = st.checkbox("Kataparuto (Fires & Packs 33% Faster)", key=f"kata_{side_idx}")
            if has_warwolf and (ftt or civ == "Britons"):
                upgrades["warwolf"] = st.checkbox("Warwolf (100% Blast Radius)", key=f"ww_{side_idx}")
            if has_ironclad and (ftt or civ == "Teutons"):
                upgrades["ironclad"] = st.checkbox("Ironclad (+4 Melee Armor)", key=f"ic_{side_idx}")
            if has_furor and (ftt or civ == "Celts"):
                upgrades["furor_celticus"] = st.checkbox("Furor Celticus (+40% HP)", key=f"fc_{side_idx}")
            if has_recurve and (ftt or civ == "Magyars"):
                upgrades["recurve_bow"] = st.checkbox("Recurve Bow (+1 Atk/Range)", key=f"rb_{side_idx}")
            if has_rocketry and (ftt or civ == "Chinese"):
                upgrades["rocketry"] = st.checkbox("Rocketry (+Attack)", key=f"rock_{side_idx}")
            if has_garland and (ftt or civ == "Aztecs"):
                upgrades["garland_wars"] = st.checkbox("Garland Wars (+4 Attack)", key=f"gw_{side_idx}")
            if has_farimba and (ftt or civ == "Malians"):
                upgrades["farimba"] = st.checkbox("Farimba (+5 Attack)", key=f"far_{side_idx}")
            if has_wootz and (ftt or civ == "Dravidians"):
                upgrades["wootz_steel"] = st.checkbox("Wootz Steel (Ignore Armor)", key=f"ws_{side_idx}")
            if has_stirrups and (ftt or civ == "Bulgarians"):
                upgrades["stirrups"] = st.checkbox("Stirrups (+33% Atk Speed)", key=f"stirr_{side_idx}")
            if has_hauberk and (ftt or civ == "Sicilians"):
                upgrades["hauberk"] = st.checkbox("Hauberk (+1/+2 Armor)", key=f"haub_{side_idx}")
            if has_sipahi and (ftt or civ == "Turks"):
                upgrades["sipahi"] = st.checkbox("Sipahi (+20 HP)", key=f"sip_{side_idx}")
            if has_el_dorado and (ftt or civ == "Mayans"):
                upgrades["el_dorado"] = st.checkbox("El Dorado (+40 HP)", key=f"eld_{side_idx}")
            if has_chatras and (ftt or civ == "Vietnamese"):
                upgrades["chatras"] = st.checkbox("Chatras (+100 HP)", key=f"chat_{side_idx}")
            if has_comitatenses and (ftt or civ == "Romans"):
                upgrades["comitatenses"] = st.checkbox("Comitatenses (+5 Charge Attack)", key=f"com_{side_idx}")
            if has_bogsveigar and (ftt or civ == "Vikings"):
                upgrades["bogsveigar"] = st.checkbox("Bogsveigar (+1 Attack)", key=f"bog_{side_idx}")
            if has_tower_shields and (ftt or civ == "Lithuanians"):
                upgrades["tower_shields"] = st.checkbox("Tower Shields (+2 Pierce Armor)", key=f"ts_{side_idx}")
            if has_pavise and (ftt or civ == "Italians"):
                upgrades["pavise"] = st.checkbox("Pavise (+1/+1 Armor)", key=f"pav_{side_idx}")
            if has_silk_armor and (ftt or civ == "Tatars"):
                upgrades["silk_armor"] = st.checkbox("Silk Armor (+1/+1 Armor)", key=f"sa_{side_idx}")
            if has_fabric_shields and (ftt or civ == "Incas"):
                upgrades["fabric_shields"] = st.checkbox("Fabric Shields (+1/+2 Armor)", key=f"fs_{side_idx}")
            if has_bagains and (ftt or civ == "Bulgarians"):
                upgrades["bagains"] = st.checkbox("Bagains (+5 Melee Armor)", key=f"bag_{side_idx}")

        return base_unit, civ, upgrades, True

def main():
    st.set_page_config(page_title="AoE2 1v1 Battle Calculator", page_icon="⚔️", layout="wide")
    st.title("⚔️ Age of Empires 2 1v1 Battle Calculator (Patch 185872)")
    st.markdown("Calculate 1v1 battles with civilization bonuses, full tech tree overrides, unique unit mechanics, and Patch 185872 DLCs.")

    col1, col2 = st.columns(2)
    u1, civ1, up1, ok1 = render_unit_config(col1, 1, "Japanese", "Trebuchet")
    u2, civ2, up2, ok2 = render_unit_config(col2, 2, "Britons", "Trebuchet")

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
