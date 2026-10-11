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

# Accurate Tech Tree limits per civilization
# max_c_arm for Malay is 1 (Scale Barding Armor in Feudal, lacks Chain and Plate Barding)
CIV_DATA = {
    "Generic": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Armenians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True},
    "Aztecs": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False},
    "Bengalis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Berbers": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False},
    "Bohemians": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Britons": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Bulgarians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
    "Burgundians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Burmese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 1, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True},
    "Byzantines": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Celts": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Chinese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
    "Cumans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": False, "gambesons": True},
    "Danes": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
    "Dravidians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 1, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True},
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
    "Malay": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 1, "max_i_arm": 2, "bloodlines": False, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True},
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
    "Spanish": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True},
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

NO_STABLE_CIVS = ["Aztecs", "Incas", "Mayans", "Muisca", "Tupi"]

# Specific unit availability restrictions across all 52 civilizations
UNIT_RESTRICTIONS = {
    "Cavalry Archer": {
        "banned": ["Aztecs", "Britons", "Burgundians", "Celts", "Franks", "Incas", "Mayans", "Muisca", "Teutons", "Tupi", "Vikings", "Armenians", "Bohemians"]
    },
    "Heavy Cavalry Archer": {
        "banned": ["Aztecs", "Britons", "Burgundians", "Celts", "Franks", "Incas", "Mayans", "Muisca", "Teutons", "Tupi", "Vikings", "Armenians", "Bohemians", "Bulgarians", "Burmese", "Goths", "Italians", "Malay", "Malians", "Poles", "Portuguese", "Romans", "Sicilians", "Slavs", "Spanish"]
    },
    "Halberdier": {
        "banned": ["Turks", "Aztecs", "Berbers", "Chinese", "Italians", "Malians", "Mongols", "Portuguese", "Saracens"]
    },
    "Paladin": {
        "allowed": ["Burgundians", "Byzantines", "Celts", "Cumans", "Franks", "Huns", "Lithuanians", "Magyars", "Spanish", "Teutons"]
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
        "banned": ["Bulgarians", "Ethiopians", "Huns", "Khmer", "Malay", "Mayans", "Persians", "Tatars"]
    },
    "Two-Handed Swordsman": {
        "banned": ["Persians"]
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
    "Hussar": {
        "banned": ["Aztecs", "Britons", "Chinese", "Franks", "Incas", "Japanese", "Malay", "Mayans", "Muisca", "Portuguese", "Teutons", "Tupi", "Vikings"]
    },
    "Siege Onager": {
        "allowed": ["Aztecs", "Celts", "Ethiopians", "Koreans", "Malians", "Mongols", "Saracens", "Slavs", "Teutons"]
    },
    "Siege Ram": {
        "banned": ["Britons", "Burmese", "Franks", "Goths", "Japanese", "Koreans", "Lithuanians", "Malians", "Portuguese", "Teutons", "Turks", "Vietnamese", "Vikings"]
    },
    "Houfnice": {
        "allowed": ["Bohemians"]
    },
    "Savar": {
        "allowed": ["Persians"]
    },
    "Legionary": {
        "allowed": ["Romans"]
    },
    "Winged Hussar": {
        "allowed": ["Lithuanians", "Poles"]
    }
}

def is_unit_available(civ: str, unit_name: str) -> tuple[bool, str]:
    if civ == "Generic":
        return True, ""

    # Shared alliance units available to all civs
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
        cavalry_units = ["Knight", "Cavalier", "Paladin", "Scout Cavalry", "Light Cavalry", "Hussar", "Camel Rider", "Heavy Camel Rider", "Steppe Lancer", "Battle Elephant", "Cavalry Archer", "Heavy Cavalry Archer"]
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
        p_str = str(self.p_attack) if self.p_attack is not None else "None"
        m_str = str(self.m_attack) if self.m_attack is not None else "None"
        return f"Name: {self.name}\nHP: {self.hp}\nMelee Attack: {m_str}\nPierce Attack: {p_str}\nRate of Fire (ROF): {self.rof:.2f}s\nMelee Armor: {self.armor}\nPierce Armor: {self.pierce_armor}\nAttack Bonuses: {bonus_str}\nArmor Classes: {class_str}"

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

# Curated unit baseline fallbacks for Patch 185872
CURATED_UNITS = {
    "Knight": (100, None, 10, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Cavalier": (120, None, 12, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Paladin": (160, None, 14, 1.9, 2, 3, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Scout Cavalry": (45, None, 3, 2.04, 0, 2, {"Monk": 6}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Light Cavalry": (60, None, 7, 2.0, 0, 2, {"Monk": 10}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Hussar": (75, None, 7, 1.9, 0, 2, {"Monk": 12}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Pikeman": (55, None, 4, 3.05, 1, 0, {"Cavalry": 22, "Camel": 18, "War elephant": 25}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Halberdier": (60, None, 6, 3.05, 1, 0, {"Cavalry": 32, "Camel": 26, "War elephant": 28}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Archer": (30, 4, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Crossbowman": (35, 5, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Arbalester": (40, 6, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Skirmisher": (30, 2, None, 3.0, 0, 3, {"Archer": 3, "Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Elite Skirmisher": (35, 3, None, 3.0, 0, 4, {"Archer": 4, "Spearman": 3, "Cavalry archer": 2}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Imperial Skirmisher": (35, 4, None, 3.0, 0, 4, {"Archer": 5, "Spearman": 3, "Cavalry archer": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring"),
    "Cavalry Archer": (50, 6, None, 2.0, 0, 0, {"Spearman": 2}, ["Archer", "Cavalry archer", "Cavalry"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines, Thumb Ring, Parthian Tactics, Chemistry"),
    "Heavy Cavalry Archer": (60, 7, None, 2.0, 1, 0, {"Spearman": 4}, ["Archer", "Cavalry archer", "Cavalry"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines, Thumb Ring, Parthian Tactics, Chemistry"),
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

def get_unit_archetypes(unit_name: str, base_classes: list[str]):
    norm = unit_name.lower()
    classes = [c.lower() for c in base_classes]
    
    is_inf = ("infantry" in classes) or any(u in norm for u in [
        "swordsman", "militia", "spearman", "pikeman", "halberdier", "eagle", 
        "woad", "axeman", "huskarl", "samurai", "teutonic knight", "berserk",
        "jaguar", "kamayuk", "condottiero", "shotel", "gbeto", "karambit",
        "serjeant", "obuch", "urumi", "ghulam", "chakram", "legionary",
        "varangian", "jomsviking", "hearth troop", "guecha", "ibirapema", "warrior priest"
    ])
    
    is_cav = ("cavalry" in classes) or any(u in norm for u in [
        "scout", "light cavalry", "hussar", "knight", "cavalier", "paladin",
        "savar", "centurion", "camel", "elephant", "lancer", "cataphract",
        "tarkan", "boyar", "konnik", "keshik", "coustillier", "leitis",
        "monaspa", "shrivamsha", "kona", "bolas", "ratha", "genitour", "mounted crossbowman"
    ])
    
    is_arch = ("archer" in classes) or any(u in norm for u in [
        "archer", "crossbowman", "arbalester", "skirmisher", "longbowman",
        "chu ko nu", "plumed", "rattan", "composite bowman", "genoese",
        "slinger", "mounted crossbowman", "cavalry archer", "kipchak", "mangudai", "ratha"
    ])
    
    is_cav_arch = ("cavalry archer" in classes) or any(u in norm for u in [
        "cavalry archer", "camel archer", "mangudai", "kipchak", "elephant archer",
        "genitour", "bolas rider", "ratha"
    ])
    
    is_gun = ("gunpowder unit" in classes or "gunpowder" in classes) or any(u in norm for u in [
        "hand cannoneer", "janissary", "conquistador", "organ gun", "bombard cannon", "houfnice"
    ])
    
    return is_inf, is_cav, is_arch, is_cav_arch, is_gun

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

    # If wiki omitted essential class, augment from curated archetypes
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

    rof = u.rof
    if civ == "Japanese" and any(c in u.armor_class for c in ["Infantry"]):
        rof *= 0.75
    elif civ == "Mongols" and any(c in u.armor_class for c in ["Cavalry archer"]):
        rof *= 0.80
    elif civ == "Hindustanis" and any(c in u.armor_class for c in ["Camel"]):
        rof *= 0.833
    elif up.get("stirrups") and any(c in u.armor_class for c in ["Cavalry"]):
        rof *= 0.75

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
    if up.get("thumb_ring"):
        special.append("Thumb Ring (100% Accuracy)")
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

    # Unit 1 attack simulation against Unit 2
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

    # Unit 2 attack simulation against Unit 1
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

    # When both can attack, formulate complete breakdown with civilization in ()
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

# Upgrade option dictionaries with descriptive display names
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

        base_unit = parse_unit(unit_name, is_elite, age)
        is_inf, is_cav, is_arch, is_cav_arch, is_gun = get_unit_archetypes(unit_name, base_unit.armor_class)
        is_melee = base_unit.m_attack is not None
        is_ranged = base_unit.p_attack is not None

        if fu:
            upgrades["m_atk_tier"] = max_m_atk
            upgrades["m_atk_val"] = MELEE_ATK_VALUES[max_m_atk]
            upgrades["r_atk_tier"] = max_r_atk
            upgrades["r_atk_val"] = RANGED_ATK_VALUES[max_r_atk]
            
            # Select relevant armor values
            m_arm_v, p_arm_v = 0, 0
            if is_inf:
                m_arm_v, p_arm_v = INF_ARM_VALUES[max_i_arm]
            elif is_cav:
                m_arm_v, p_arm_v = CAV_ARM_VALUES[max_c_arm]
            elif is_arch:
                m_arm_v, p_arm_v = ARC_ARM_VALUES[max_a_arm]
                
            upgrades["m_arm_val"] = m_arm_v
            upgrades["p_arm_val"] = p_arm_v
            upgrades["bloodlines"] = True if (ftt or c_info["bloodlines"]) else False
            upgrades["thumb_ring"] = True if (ftt or c_info["thumb_ring"]) else False
            upgrades["parthian"] = True if (ftt or c_info["parthian"]) else False
            upgrades["chemistry"] = True if (ftt or c_info["chemistry"]) else False
            upgrades["gambesons"] = True if (ftt or c_info["gambesons"]) else False
            
            # Unique techs under FU
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
            st.markdown("**Upgrades & Technologies:**")
            col_a, col_b = st.columns(2)
            with col_a:
                if is_melee:
                    opts = list(range(max_m_atk + 1))
                    tier = st.selectbox(
                        "Melee Attack",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: MELEE_ATK_NAMES[x],
                        key=f"m_atk_{side_idx}"
                    )
                    upgrades["m_atk_tier"] = tier
                    upgrades["m_atk_val"] = MELEE_ATK_VALUES[tier]
                else:
                    upgrades["m_atk_val"] = 0

                if is_ranged:
                    opts = list(range(max_r_atk + 1))
                    tier = st.selectbox(
                        "Ranged Attack",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: RANGED_ATK_NAMES[x],
                        key=f"r_atk_{side_idx}"
                    )
                    upgrades["r_atk_tier"] = tier
                    upgrades["r_atk_val"] = RANGED_ATK_VALUES[tier]
                else:
                    upgrades["r_atk_val"] = 0

                # Armor selectors with full descriptive names
                m_arm_v, p_arm_v = 0, 0
                if is_inf:
                    opts = list(range(max_i_arm + 1))
                    tier = st.selectbox(
                        "Infantry Armor",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: INF_ARM_NAMES[x],
                        key=f"i_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = INF_ARM_VALUES[tier]
                elif is_cav:
                    opts = list(range(max_c_arm + 1))
                    tier = st.selectbox(
                        "Cavalry Armor",
                        opts,
                        index=len(opts) - 1,
                        format_func=lambda x: CAV_ARM_NAMES[x],
                        key=f"c_arm_{side_idx}"
                    )
                    m_arm_v, p_arm_v = CAV_ARM_VALUES[tier]
                elif is_arch:
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
                if is_cav and (ftt or c_info["bloodlines"]):
                    upgrades["bloodlines"] = st.checkbox("Bloodlines (+20 HP)", key=f"bl_{side_idx}")
                if is_arch and (ftt or c_info["thumb_ring"]):
                    upgrades["thumb_ring"] = st.checkbox("Thumb Ring (100% Acc)", key=f"tr_{side_idx}")
                if is_cav_arch and (ftt or c_info["parthian"]):
                    upgrades["parthian"] = st.checkbox("Parthian Tactics (+1/+2)", key=f"pt_{side_idx}")
                if is_ranged and (ftt or c_info["chemistry"]):
                    upgrades["chemistry"] = st.checkbox("Chemistry (+1 Attack)", key=f"chem_{side_idx}")
                if is_inf and (ftt or c_info["gambesons"]):
                    upgrades["gambesons"] = st.checkbox("Gambesons (+1 Pierce Armor)", key=f"gam_{side_idx}")

            # Relevant Unique Techs
            if civ == "Magyars" and is_cav_arch:
                upgrades["recurve_bow"] = st.checkbox("Recurve Bow (+1 Atk/Range)", key=f"rb_{side_idx}")
            if civ == "Chinese" and "chu ko nu" in unit_name.lower():
                upgrades["rocketry"] = st.checkbox("Rocketry (+2 Attack)", key=f"rock_{side_idx}")
            if civ == "Aztecs" and is_inf:
                upgrades["garland_wars"] = st.checkbox("Garland Wars (+4 Attack)", key=f"gw_{side_idx}")
            if civ == "Malians" and is_cav:
                upgrades["farimba"] = st.checkbox("Farimba (+5 Attack)", key=f"far_{side_idx}")
            if civ == "Dravidians" and (is_inf or is_cav):
                upgrades["wootz_steel"] = st.checkbox("Wootz Steel (Ignore Armor)", key=f"ws_{side_idx}")
            if civ == "Bulgarians" and is_cav:
                upgrades["stirrups"] = st.checkbox("Stirrups (+33% Atk Speed)", key=f"stirr_{side_idx}")
            if civ == "Sicilians" and "knight" in unit_name.lower():
                upgrades["hauberk"] = st.checkbox("Hauberk (+1/+2 Armor)", key=f"haub_{side_idx}")
            if civ == "Turks" and is_cav_arch:
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
    u1, civ1, up1, ok1 = render_unit_config(col1, 1, "Japanese", "Pikeman")
    u2, civ2, up2, ok2 = render_unit_config(col2, 2, "Franks", "Pikeman")

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
