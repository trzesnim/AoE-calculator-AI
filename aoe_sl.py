import re
import math
import urllib.request
import urllib.parse
import json
try:
    import requests
except ImportError:
    requests = None
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
# - Full Naval Fleet (Warships, Unique Vessels, and Civilian Ships)
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

SUICIDE_UNITS = [
    "Petard", "Demolition Raft", "Demolition Ship", "Heavy Demolition Ship", "Flaming Camel", "Saboteur"
]

UNITS = [
    "Arambai", "Arbalester", "Archer", "Armored Elephant", "Ballista Elephant",
    "Battering Ram", "Battle Elephant", "Berserk", "Blackwood Archer", "Bolas Rider",
    "Bombard Cannon", "Boyar", "Camel Archer", "Camel Rider", "Camel Scout",
    "Cannon Galleon", "Capped Ram", "Caravel", "Carrack", "Cataphract", "Cavalier",
    "Cavalry Archer", "Centurion", "Chakram Thrower", "Champion", "Chu Ko Nu",
    "Composite Bowman", "Condottiero", "Conquistador", "Coustillier", "Crossbowman",
    "Demolition Raft", "Demolition Ship", "Dromon", "Eagle Scout", "Eagle Warrior",
    "Elephant Archer", "Elite Battle Elephant", "Elite Cannon Galleon", "Elite Caravel",
    "Elite Eagle Warrior", "Elite Elephant Archer", "Elite Longship", "Elite Skirmisher",
    "Elite Steppe Lancer", "Elite Turtle Ship", "Fast Fire Ship", "Fire Galley",
    "Fire Ship", "Fishing Ship", "Flaming Camel", "Flemish Militia", "Galley", "Galleon", "Gbeto",
    "Genitour", "Genoese Crossbowman", "Ghulam", "Guecha Warrior", "Halberdier",
    "Hand Cannoneer", "Hearth Troop", "Heavy Camel Rider", "Heavy Cavalry Archer",
    "Heavy Demolition Ship", "Heavy Scorpion", "Houfnice", "Hulk", "Huskarl", "Hussar",
    "Hussite Wagon", "Ibirapema Warrior", "Imperial Camel Rider", "Imperial Skirmisher",
    "Janissary", "Jian Swordsman", "Jomsviking", "Kamayuk", "Karambit Warrior",
    "Keshik", "Kipchak", "Knight", "Kona", "Konnik", "Legionary", "Leitis",
    "Light Cavalry", "Long Swordsman", "Longbowman", "Longship", "Magyar Huszar",
    "Mameluke", "Man-at-Arms", "Mangonel", "Mangudai", "Militia", "Missionary",
    "Monaspa", "Monk", "Mounted Crossbowman", "Obuch", "Onager", "Organ Gun",
    "Paladin", "Petard", "Pikeman", "Plumed Archer", "Ratha", "Rattan Archer", "Samurai",
    "Savar", "Scorpion", "Scout Cavalry", "Serjeant", "Shotel Warrior",
    "Shrivamsha Rider", "Siege Elephant", "Siege Onager", "Siege Ram", "Siege Tower",
    "Skirmisher", "Slinger", "Spearman", "Steppe Lancer", "Teutonic Knight",
    "Thirisadai", "Throwing Axeman", "Trade Cart", "Trade Cog", "Transport Ship",
    "Trebuchet", "Turtle Ship", "Two-Handed Swordsman", "Urumi Swordsman",
    "Varangian Guard", "Villager", "War Elephant", "War Galley", "War Hulk", "War Wagon",
    "Warrior Priest", "Winged Hussar", "Woad Raider", "Xianbei Raider"
]

ELITE_UNITS = [
    "Arambai", "Ballista Elephant", "Berserk", "Bolas Rider", "Boyar", "Camel Archer",
    "Cannon Galleon", "Caravel", "Cataphract", "Centurion", "Chakram Thrower",
    "Chu Ko Nu", "Composite Bowman", "Conquistador", "Coustillier", "Gbeto",
    "Genitour", "Genoese Crossbowman", "Ghulam", "Guecha Warrior", "Hearth Troop",
    "Huskarl", "Hussite Wagon", "Ibirapema Warrior", "Janissary", "Jomsviking",
    "Kamayuk", "Karambit Warrior", "Keshik", "Kipchak", "Kona", "Konnik",
    "Leitis", "Longbowman", "Longship", "Magyar Huszar", "Mameluke", "Mangudai",
    "Monaspa", "Obuch", "Organ Gun", "Plumed Archer", "Ratha", "Rattan Archer",
    "Samurai", "Serjeant", "Shotel Warrior", "Shrivamsha Rider", "Teutonic Knight",
    "Throwing Axeman", "Turtle Ship", "Urumi Swordsman", "Varangian Guard",
    "War Elephant", "War Wagon", "Woad Raider", "Xianbei Raider"
]

CIV_DATA = {
    "Generic": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Armenians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Aztecs": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Bengalis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Berbers": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Bohemians": {"max_m_atk": 2, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Britons": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Bulgarians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 0, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Burgundians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Burmese": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Byzantines": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Celts": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Chinese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Cumans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Danes": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Dravidians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Ethiopians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Franks": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Georgians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Goths": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Gurjaras": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Hindustanis": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Huns": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Incas": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Italians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Japanese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Khmer": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Koreans": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Lithuanians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Magyars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Malay": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 1, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Malians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Mapuche": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Mayans": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Mongols": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Muisca": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Persians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Poles": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Portuguese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Romans": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Saracens": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Saxons": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Sicilians": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Slavs": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Spanish": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Tatars": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Teutons": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": False, "siege_engineers": True, "siphons": False},
    "Tupi": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 0, "max_i_arm": 3, "bloodlines": False, "thumb_ring": True, "parthian": False, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Turks": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 3, "max_i_arm": 2, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": False, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Varangians": {"max_m_atk": 3, "max_r_atk": 2, "max_a_arm": 2, "max_c_arm": 3, "max_i_arm": 3, "bloodlines": True, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": True},
    "Vietnamese": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": True, "thumb_ring": True, "parthian": True, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False},
    "Vikings": {"max_m_atk": 3, "max_r_atk": 3, "max_a_arm": 3, "max_c_arm": 2, "max_i_arm": 3, "bloodlines": False, "thumb_ring": False, "parthian": False, "chemistry": True, "gambesons": True, "careening": True, "dry_dock": True, "siege_engineers": True, "siphons": False}
}

EXCLUSIVE_UNIQUE_UNITS = {
    "Arambai": ["Burmese"],
    "Ballista Elephant": ["Khmer"],
    "Berserk": ["Vikings"],
    "Bolas Rider": ["Mapuche"],
    "Boyar": ["Slavs"],
    "Camel Archer": ["Berbers"],
    "Caravel": ["Portuguese"],
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
    "Longship": ["Vikings", "Danes", "Saxons", "Varangians"],
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
    "Thirisadai": ["Dravidians"],
    "Throwing Axeman": ["Franks"],
    "Turtle Ship": ["Koreans"],
    "Urumi Swordsman": ["Dravidians"],
    "Varangian Guard": ["Varangians", "Byzantines"],
    "War Elephant": ["Persians"],
    "War Wagon": ["Koreans"],
    "Warrior Priest": ["Armenians"],
    "Winged Hussar": ["Poles", "Lithuanians"],
    "Woad Raider": ["Celts"]
}

NO_STABLE_CIVS = ["Aztecs", "Incas", "Mayans", "Muisca", "Tupi"]

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
    "Houfnice": {
        "allowed": ["Bohemians"]
    },
    "Dromon": {
        "allowed": ["Romans", "Byzantines", "Armenians", "Goths", "Huns"]
    },
    "Cannon Galleon": {
        "banned": ["Romans", "Byzantines", "Armenians", "Goths", "Huns", "Aztecs", "Incas", "Mayans", "Muisca", "Tupi"]
    },
    "Elite Cannon Galleon": {
        "banned": ["Romans", "Byzantines", "Armenians", "Goths", "Huns", "Aztecs", "Incas", "Mayans", "Muisca", "Tupi", "Britons", "Celts", "Chinese", "Cumans", "Ethiopians", "Japanese", "Malay", "Mongols", "Sicilians", "Slavs", "Tatars", "Vikings"]
    },
    "Galleon": {
        "banned": ["Aztecs", "Malians"]
    },
    "Fast Fire Ship": {
        "banned": ["Aztecs", "Celts", "Chinese", "Cumans", "Dravidians", "Ethiopians", "Goths", "Huns", "Incas", "Malay", "Malians", "Mayans", "Mongols", "Poles", "Portuguese", "Slavs", "Vikings"]
    },
    "Heavy Demolition Ship": {
        "banned": ["Aztecs", "Burmese", "Byzantines", "Incas", "Italians", "Japanese", "Khmer", "Koreans", "Mayans", "Persians", "Romans", "Spanish"]
    },
    "Carrack": {
        "banned": ["Britons", "Danes", "Georgians", "Huns", "Mongols", "Romans", "Tupi"]
    },
    "Flaming Camel": {
        "allowed": ["Tatars"]
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
            return False, f"{civ} does not get access to {unit_name} (exclusive to {', '.join(allowed)})."

    if civ in NO_STABLE_CIVS:
        cavalry_units = ["Knight", "Cavalier", "Paladin", "Scout Cavalry", "Light Cavalry", "Hussar", "Camel Rider", "Heavy Camel Rider", "Steppe Lancer", "Battle Elephant", "Cavalry Archer", "Heavy Cavalry Archer"]
        if base_name in cavalry_units:
            return False, f"{civ} does not have access to Stables ({unit_name})."

    if base_name in ["Eagle Scout", "Eagle Warrior", "Elite Eagle Warrior"]:
        if civ not in ["Aztecs", "Incas", "Mayans", "Mapuche", "Muisca", "Tupi"]:
            return False, f"{civ} does not get access to {unit_name} (Mesoamerican/American civs only)."

    if base_name in UNIT_RESTRICTIONS:
        rule = UNIT_RESTRICTIONS[base_name]
        if "banned" in rule and civ in rule["banned"]:
            if base_name == "Hussar" and civ in ["Lithuanians", "Poles"]:
                return False, f"{civ} upgrades Light Cavalry to Winged Hussar, not regular Hussar."
            return False, f"{civ} does not get access to {unit_name} in the standard tech tree."
        if "allowed" in rule and civ not in rule["allowed"]:
            return False, f"{civ} does not get access to {unit_name}."

    return True, ""

class Unit:
    def __init__(self, name, hp, p_attack=None, m_attack=None, rof=2.0, armor=0, pierce_armor=0, attack_bonus=None, armor_class=None, boost_tech=None, elite=False, parsed_techs=None):
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

    def __str__(self):
        bonus_str = ", ".join([f"+{v} vs {k}" for k, v in self.attack_bonus.items()]) if self.attack_bonus else "None"
        class_str = ", ".join(self.armor_class) if self.armor_class else "None"
        p_str = str(self.p_attack) if self.p_attack is not None else "None"
        m_str = str(self.m_attack) if self.m_attack is not None else "None"
        return f"Name: {self.name}\nHP: {self.hp}\nMelee Attack: {m_str}\nPierce Attack: {p_str}\nRate of Fire (ROF): {self.rof:.2f}s\nMelee Armor: {self.armor}\nPierce Armor: {self.pierce_armor}\nAttack Bonuses: {bonus_str}\nArmor Classes: {class_str}"

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

WIKI_TITLE_OVERRIDES = {
    "Carrack": "Carrack (unit)",
    "Springald Ship": "Springald ship",
}

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_wiki_unit(unit_name: str):
    clean = unit_name.replace("Elite ", "").strip()
    override = WIKI_TITLE_OVERRIDES.get(clean, clean)
    candidates = [
        f"{override} (Age of Empires II)",
        override,
        f"{override} (unit)"
    ]

    headers = {"User-Agent": "AoE2BattleCalculator/2.0"}
    content = ""

    for cand in candidates:
        url = f"https://ageofempires.fandom.com/api.php?action=parse&page={urllib.parse.quote(cand)}&prop=wikitext&redirects=1&format=json"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if "parse" in data and "wikitext" in data["parse"]:
                    wt = data["parse"]["wikitext"].get("*", "")
                    if any(m in wt[:400].lower() for m in ["{{disambig", "{{for|"]) and "infobox aoe2 unit" not in wt.lower():
                        continue
                    ibox = extract_template(wt, "Infobox AoE2 unit")
                    if ibox:
                        content = wt
                        break
        except Exception:
            continue

    if not content:
        return None, "", {}

    boost_block = extract_template(content, "Boosts|Technologies")
    if not boost_block:
        boost_block = extract_template(content, "Boosts")

    parsed_techs = {}
    if boost_block:
        for line in boost_block.splitlines():
            icons = re.findall(r"\{\{2icons\|([^}|]+)", line)
            if not icons:
                continue
            tech_name = icons[0].strip()
            civs = re.findall(r"\[\[(?:[^|\]]+\|)?([A-Za-z]+)\]\]\s*only", line, re.I)
            descs = re.findall(r"\(([^)]+)\)", line)
            clean_descs = [d for d in descs if "only" not in d.lower()]
            desc_str = ", ".join(clean_descs) if clean_descs else ""
            desc_str = re.sub(r"\{\{[^}]+\}\}", "", desc_str).strip()
            desc_str = re.sub(r"\[\[(?:[^|\]]+\|)?([^\]]+)\]\]", r"\1", desc_str).strip()

            key = tech_name.lower()
            if key not in parsed_techs:
                parsed_techs[key] = {"name": tech_name, "civs": civs, "desc": desc_str}
            else:
                if civs and not parsed_techs[key]["civs"]:
                    parsed_techs[key]["civs"] = civs
                if desc_str and not parsed_techs[key]["desc"]:
                    parsed_techs[key]["desc"] = desc_str

    boost_tech_str = ", ".join([v["name"] for v in parsed_techs.values()])
    return content, boost_tech_str, parsed_techs

# Curated unit baseline fallbacks for Patch 185872 including complete naval fleet
CURATED_UNITS = {
    "Trebuchet": (150, 200, None, 10.0, 2, 8, {"Building": 250}, ["Siege weapon"], "Kataparuto, Warwolf, Ironclad, Furor Celticus, Siege Engineers, Counterweights"),
    "Knight": (100, None, 10, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Hauberk, Stirrups, Farimba, Wootz Steel, Comitatenses"),
    "Cavalier": (120, None, 12, 1.8, 2, 2, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Hauberk, Stirrups, Farimba, Wootz Steel, Comitatenses"),
    "Paladin": (160, None, 14, 1.9, 2, 3, {}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Hauberk, Stirrups, Farimba"),
    "Scout Cavalry": (45, None, 3, 2.04, 0, 2, {"Monk": 6}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Silk Armor, Stirrups, Farimba"),
    "Light Cavalry": (60, None, 7, 2.0, 0, 2, {"Monk": 10}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Silk Armor, Stirrups, Farimba"),
    "Hussar": (75, None, 7, 1.9, 0, 2, {"Monk": 12}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Silk Armor, Stirrups, Farimba"),
    "Winged Hussar": (80, None, 9, 1.9, 1, 2, {"Monk": 12}, ["Cavalry"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Lechitic Legacy"),
    "Pikeman": (55, None, 4, 3.0, 0, 0, {"Cavalry": 22, "Camel": 18, "War elephant": 25}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Garland Wars, Wootz Steel, Tower Shields"),
    "Halberdier": (60, None, 6, 3.05, 1, 0, {"Cavalry": 32, "Camel": 26, "War elephant": 28}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Garland Wars, Wootz Steel, Tower Shields"),
    "Archer": (30, 4, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bogsveigar"),
    "Crossbowman": (35, 5, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bogsveigar, Cranequins"),
    "Arbalester": (40, 6, None, 2.0, 0, 0, {"Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bogsveigar, Cranequins"),
    "Skirmisher": (30, 2, None, 3.0, 0, 3, {"Archer": 3, "Spearman": 3}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Tower Shields"),
    "Elite Skirmisher": (35, 3, None, 3.0, 0, 4, {"Archer": 4, "Spearman": 3, "Cavalry archer": 2}, ["Archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Tower Shields"),
    "Cavalry Archer": (50, 6, None, 2.0, 0, 0, {}, ["Cavalry", "Cavalry archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines, Thumb Ring, Parthian Tactics, Chemistry, Recurve Bow, Sipahi, Silk Armor"),
    "Heavy Cavalry Archer": (60, 7, None, 2.0, 1, 0, {}, ["Cavalry", "Cavalry archer"], "Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Bloodlines, Thumb Ring, Parthian Tactics, Chemistry, Recurve Bow, Sipahi, Silk Armor"),
    "Champion": (70, None, 13, 2.0, 1, 1, {"Eagle Warrior": 8}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons, Garland Wars, Wootz Steel, Bagains"),
    "Two-Handed Swordsman": (60, None, 12, 2.0, 0, 1, {"Eagle Warrior": 6}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons, Garland Wars, Wootz Steel, Bagains"),
    "Long Swordsman": (60, None, 9, 2.0, 1, 1, {"Eagle Warrior": 4}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons"),
    "Man-at-Arms": (45, None, 6, 2.0, 0, 1, {"Eagle Warrior": 2}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons"),
    "Militia": (40, None, 4, 2.0, 0, 1, {}, ["Infantry"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
    "Camel Rider": (100, None, 6, 2.0, 0, 0, {"Cavalry": 9, "Camel": 5}, ["Camel"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Farimba"),
    "Heavy Camel Rider": (120, None, 7, 2.0, 0, 0, {"Cavalry": 18, "Camel": 9}, ["Camel"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines, Farimba"),
    "Imperial Camel Rider": (140, None, 9, 2.0, 0, 0, {"Cavalry": 18, "Camel": 9}, ["Camel"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Coustillier": (115, None, 11, 1.9, 2, 2, {}, ["Cavalry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines"),
    "Obuch": (80, None, 8, 2.0, 2, 2, {}, ["Infantry", "Unique unit"], "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor"),
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
    "Trade Cart": (70, None, None, 2.0, 0, 0, {}, [], ""),
    # Naval Ships & Upgrades
    "Galley": (120, 6, None, 3.0, 0, 6, {"Ship": 6, "Building": 6}, ["Ship"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock"),
    "War Galley": (135, 7, None, 3.0, 0, 6, {"Ship": 7, "Building": 7}, ["Ship"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock"),
    "Galleon": (165, 8, None, 3.0, 0, 8, {"Ship": 8, "Building": 8}, ["Ship"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock"),
    "Fire Galley": (100, 1, None, 0.25, 0, 4, {"Ship": 3, "Building": 1}, ["Ship"], "Careening, Dry Dock, Siphons, Greek Fire"),
    "Fire Ship": (120, 2, None, 0.25, 0, 6, {"Ship": 4, "Building": 2}, ["Ship"], "Careening, Dry Dock, Siphons, Greek Fire"),
    "Fast Fire Ship": (140, 3, None, 0.25, 0, 8, {"Ship": 5, "Building": 3}, ["Ship"], "Careening, Dry Dock, Siphons, Greek Fire"),
    "Hulk": (85, None, 4, 1.75, 3, 1, {"Fire Ships": 1, "Building": -3}, ["Ship"], "Forging, Iron Casting, Blast Furnace, Careening, Dry Dock"),
    "War Hulk": (110, None, 4, 1.5, 4, 1, {"Fire Ships": 1, "Building": -3}, ["Ship"], "Forging, Iron Casting, Blast Furnace, Careening, Dry Dock"),
    "Carrack": (135, None, 4, 1.5, 5, 1, {"Fire Ships": 1, "Building": -3}, ["Ship"], "Forging, Iron Casting, Blast Furnace, Careening, Dry Dock"),
    "Demolition Raft": (45, 90, None, 0.0, 0, 1, {"Ship": 110, "Building": 110}, ["Ship", "Suicide unit"], "Careening, Dry Dock"),
    "Demolition Ship": (50, 95, None, 0.0, 1, 0, {"Ship": 130, "Building": 220}, ["Ship", "Suicide unit"], "Careening, Dry Dock"),
    "Heavy Demolition Ship": (70, 140, None, 0.0, 2, 0, {"Ship": 160, "Building": 280}, ["Ship", "Suicide unit"], "Careening, Dry Dock"),
    "Petard": (50, 25, None, 0.0, 0, 2, {"Walls and Gates": 900, "Building": 500, "Castles": 100, "Siege weapon": 60}, ["Siege weapon", "Suicide unit"], "Siege Engineers"),
    "Flaming Camel": (55, 20, None, 0.0, 0, 2, {"Building": 200, "Elephant": 130, "Cavalry": 50, "Camel": 50, "Siege weapon": 25}, ["Camel", "Siege weapon", "Suicide unit"], "Siege Engineers"),
    "Saboteur": (45, 100, None, 0.0, 1, 3, {"Building": 500}, ["Suicide unit"], "Siege Engineers"),
    "Cannon Galleon": (120, 35, None, 10.0, 0, 6, {"Building": 200, "Siege weapon": 25}, ["Ship", "Gunpowder unit"], "Careening, Dry Dock, Artillery"),
    "Elite Cannon Galleon": (150, 45, None, 10.0, 0, 8, {"Building": 275, "Siege weapon": 40}, ["Ship", "Gunpowder unit"], "Careening, Dry Dock, Artillery"),
    "Dromon": (125, 50, None, 7.0, 1, 6, {"Building": 135, "Siege weapon": 20}, ["Ship", "Siege weapon"], "Careening, Dry Dock"),
    "Longship": (130, 7, None, 3.0, 0, 6, {"Ship": 7, "Building": 7}, ["Ship", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock, Bogsveigar"),
    "Elite Longship": (160, 8, None, 3.0, 0, 7, {"Ship": 8, "Building": 8}, ["Ship", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock, Bogsveigar"),
    "Turtle Ship": (200, 50, None, 6.0, 6, 5, {"Ship": 0}, ["Ship", "Unique unit"], "Careening, Dry Dock, Panokseon"),
    "Elite Turtle Ship": (300, 50, None, 6.0, 8, 6, {"Ship": 0}, ["Ship", "Unique unit"], "Careening, Dry Dock, Panokseon"),
    "Caravel": (130, 6, None, 3.0, 0, 8, {"Ship": 6, "Building": 6}, ["Ship", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock, Carracks"),
    "Elite Caravel": (150, 8, None, 3.0, 0, 8, {"Ship": 7, "Building": 7}, ["Ship", "Unique unit"], "Fletching, Bodkin Arrow, Bracer, Chemistry, Careening, Dry Dock, Carracks"),
    "Thirisadai": (175, 4, None, 0.25, 0, 8, {"Ship": 5}, ["Ship", "Unique unit"], "Careening, Dry Dock"),
    "Fishing Ship": (60, None, None, 2.0, 0, 4, {}, ["Ship", "Fishing Ship"], "Careening, Dry Dock"),
    "Trade Cog": (80, None, None, 2.0, 0, 6, {}, ["Ship"], "Careening, Dry Dock"),
    "Transport Ship": (100, None, None, 2.0, 0, 8, {}, ["Ship"], "Careening, Dry Dock")
}

def parse_unit(unit_name: str, is_elite: bool, age: int) -> Unit:
    norm = unit_name.lower()

    content, boost_tech_str, parsed_techs = fetch_wiki_unit(unit_name)

    # Flemish Militia: Feudal/Dark 40 HP, 5 atk, 1/1 arm; Castle 55 HP, 8 atk, 1/1 arm; Imperial 60 HP, 11 atk, 1/1 arm
    # Note: Spearman class was removed in patch 153015. Gambesons does NOT affect Flemish Militia!
    if "flemish militia" in norm:
        stats = {1: (40, 5, 1, 1), 2: (40, 5, 1, 1), 3: (55, 8, 1, 1), 4: (60, 11, 1, 1)}
        hp, atk, arm, parm = stats.get(age, (60, 11, 1, 1))
        # Exclude gambesons from boost_tech if present
        b_tech = "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Squires"
        if boost_tech_str:
            b_tech = boost_tech_str
        return Unit("Flemish Militia", hp, m_attack=atk, rof=2.0, armor=arm, pierce_armor=parm, attack_bonus={"Cavalry": 8, "Camel": 6}, armor_class=["Infantry"], boost_tech=b_tech, elite=is_elite, parsed_techs=parsed_techs)

    if "serjeant" in norm:
        if age <= 2:
            return Unit("Serjeant", 45, m_attack=5, rof=2.0, armor=1, pierce_armor=1, armor_class=["Infantry", "Unique unit"], boost_tech=boost_tech_str or "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite, parsed_techs=parsed_techs)
        elif age == 3:
            return Unit("Serjeant", 60, m_attack=8, rof=2.0, armor=2, pierce_armor=2, armor_class=["Infantry", "Unique unit"], boost_tech=boost_tech_str or "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite, parsed_techs=parsed_techs)
        else:
            return Unit("Elite Serjeant" if is_elite else "Serjeant", 75 if is_elite else 60, m_attack=11 if is_elite else 8, rof=2.0, armor=3 if is_elite else 2, pierce_armor=3 if is_elite else 2, armor_class=["Infantry", "Unique unit"], boost_tech=boost_tech_str or "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons", elite=is_elite, parsed_techs=parsed_techs)

    if "scout cavalry" in norm:
        atk = 3 if age <= 1 else (5 if age == 2 else 5)
        return Unit("Scout Cavalry", 45, m_attack=atk, rof=2.04, armor=0, pierce_armor=2, attack_bonus={"Monk": 6}, armor_class=["Cavalry"], boost_tech=boost_tech_str or "Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines", elite=is_elite, parsed_techs=parsed_techs)

    if "eagle scout" in norm:
        atk = 4 if age <= 2 else 7
        return Unit("Eagle Scout", 50 if age <= 2 else 55, m_attack=atk, rof=2.0, armor=0, pierce_armor=2 if age <= 2 else 3, attack_bonus={"Cavalry": 3, "Camel": 1}, armor_class=["Infantry", "Eagle Warrior"], boost_tech=boost_tech_str or "Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, El Dorado", elite=is_elite, parsed_techs=parsed_techs)

    # Use live wiki boost text if available, fallback to curated
    curated_boost = CURATED_UNITS.get(unit_name, ("", "", "", "", "", "", "", "", ""))[8]
    effective_boost = boost_tech_str if boost_tech_str else curated_boost

    if not content and unit_name in CURATED_UNITS:
        c = CURATED_UNITS[unit_name]
        return Unit(f"Elite {unit_name}" if (is_elite and not unit_name.startswith("Elite")) else unit_name, c[0], c[1], c[2], c[3], c[4], c[5], dict(c[6]), list(c[7]), effective_boost, is_elite, parsed_techs=parsed_techs)

    if not content:
        return Unit(unit_name, 60, m_attack=10, rof=2.0, armor=1, pierce_armor=1, armor_class=["Infantry"], boost_tech=effective_boost, elite=is_elite, parsed_techs=parsed_techs)

    ibox = extract_template(content, "Infobox AoE2 unit")
    if not ibox:
        ibox = extract_template(content, "Infobox")

    pattern = r"^\s*\|\s*([A-Za-z0-9_]+)\s*=\s*(.+?)\s*$"
    data = dict(re.findall(pattern, ibox, re.M)) if ibox else {}

    final_name = data.get("Name", unit_name).strip()
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

    # Baseline values from CURATED_UNITS fallback if available
    cur_base = CURATED_UNITS.get(unit_name, (50, None, 10, 2.0, 0, 0, {}, [], ""))
    def_hp, def_patk, def_matk, def_rof, def_arm, def_parm = cur_base[0], cur_base[1], cur_base[2], cur_base[3], cur_base[4], cur_base[5]

    parsed_hp = parse_stat(data.get("HP"))
    hp = int(parsed_hp) if (parsed_hp is not None and parsed_hp > 0) else def_hp

    p_atk = int(parse_stat(data.get("PAttack"))) if data.get("PAttack") else def_patk
    m_atk = int(parse_stat(data.get("MAttack"))) if data.get("MAttack") else def_matk
    rof = float(parse_stat(data.get("ROF")) or def_rof)
    arm = int(parse_stat(data.get("Armor")) if data.get("Armor") is not None else def_arm)
    parm = int(parse_stat(data.get("PierceArmor")) if data.get("PierceArmor") is not None else def_parm)

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

    return Unit(final_name, hp, p_atk, m_atk, rof, arm, parm, attack_bonus, armor_class, effective_boost, is_elite, parsed_techs=parsed_techs)

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
    if (up.get("furor_celticus") or up.get("furor_celtica")) and ("siege" in str(u.armor_class).lower() or "trebuchet" in u.name.lower()):
        hp = int(hp * 1.4)

    rof = u.rof
    if civ == "Japanese" and any(c in u.armor_class for c in ["Infantry"]):
        rof *= 0.75
    elif civ == "Mongols" and any(c in u.armor_class for c in ["Cavalry archer"]):
        rof *= 0.80
    elif civ == "Hindustanis" and any(c in u.armor_class for c in ["Camel"]):
        rof *= 0.833
    elif civ == "Saracens" and any(c in u.armor_class for c in ["Ship"]) and any(w in u.name.lower() for w in ["galley", "galleon"]):
        rof *= 0.80
    elif civ == "Byzantines" and "fire" in u.name.lower():
        rof *= 0.80
    elif up.get("stirrups") and any(c in u.armor_class for c in ["Cavalry"]):
        rof *= 0.75
    elif up.get("kataparuto") and "trebuchet" in u.name.lower():
        rof *= 0.75

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
        if up.get("bogsveigar") and any(c in u.armor_class for c in ["Archer", "Ship"]):
            p_atk += 1
        if up.get("cranequins") and any(c in u.name.lower() for c in ["crossbowman", "arbalester"]):
            p_atk += 1
        if up.get("counterweights") and "trebuchet" in u.name.lower():
            p_atk = int(p_atk * 1.15)

    armor_mult = 2 if civ == "Romans" else 1
    m_arm = u.armor + up.get("m_arm_val", 0) * armor_mult
    p_arm = u.pierce_armor + up.get("p_arm_val", 0) * armor_mult

    if civ == "Teutons" and any(c in u.armor_class for c in ["Infantry", "Cavalry"]):
        m_arm += 2
    if civ == "Malians" and any(c in u.armor_class for c in ["Infantry"]):
        p_arm += 3
    if up.get("gambesons") and any(c in u.armor_class for c in ["Infantry"]):
        p_arm += 1
    if up.get("careening") and any(c in u.armor_class for c in ["Ship"]):
        p_arm += 1
    if up.get("dry_dock") and any(c in u.armor_class for c in ["Ship"]):
        p_arm += 1
    if up.get("carracks") and any(c in u.armor_class for c in ["Ship"]):
        m_arm += 1
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
        if up.get("parthian") and any(c in u.armor_class for c in ["Cavalry archer"]) and any(c in opponent.armor_class for c in ["Spearman"]):
            bonus += 4
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
        rate_txt = "11% Faster Attack" if "cavalry archer" in str(u.armor_class).lower() else "18% Faster Attack"
        special.append(f"Thumb Ring ({rate_txt})")
    if up.get("careening"):
        special.append("Careening (+1 Pierce Armor)")
    if up.get("dry_dock"):
        special.append("Dry Dock (+1 Pierce Armor)")
    if up.get("carracks"):
        special.append("Carracks (+1/+1 Ship Armor)")
    if civ == "Sicilians":
        special.append("Takes 33% Less Bonus Damage")
    if civ == "Romans" and any(c in u.armor_class for c in ["Infantry"]):
        special.append("2x Blacksmith Armor Effect")
    if u.name in SUICIDE_UNITS:
        special.append("Single-Use Explosive/Suicide Unit")

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
    # Exclude suicide units from 1v1 calculations per user instruction
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

    if not can_attack2:
        # u1 attacks non-attacking u2
        is_p1 = eff1["p_atk"] is not None
        atk1 = eff1["p_atk"] if is_p1 else eff1["m_atk"]
        target_arm2 = eff2["p_arm"] if is_p1 else eff2["m_arm"]
        dmg1 = max(1, atk1 - target_arm2) + eff1["bonus"]
        hits1 = math.ceil(eff2["hp"] / dmg1)
        time1 = (hits1 - 1) * eff1["rof"] if hits1 > 0 else 0.0
        return f"{u1_label} defeats non-attacking {u2_label} in {hits1} hits ({time1:.2f}s)!\n\nOutcome: {u1_label} takes 0 damage and finishes with {eff1['hp']} HP remaining."

    if not can_attack1:
        # u2 attacks non-attacking u1
        is_p2 = eff2["p_atk"] is not None
        atk2 = eff2["p_atk"] if is_p2 else eff2["m_atk"]
        target_arm1 = eff1["p_arm"] if is_p2 else eff1["m_arm"]
        dmg2 = max(1, atk2 - target_arm1) + eff2["bonus"]
        hits2 = math.ceil(eff1["hp"] / dmg2)
        time2 = (hits2 - 1) * eff2["rof"] if hits2 > 0 else 0.0
        return f"{u2_label} defeats non-attacking {u1_label} in {hits2} hits ({time2:.2f}s)!\n\nOutcome: {u2_label} takes 0 damage and finishes with {eff2['hp']} HP remaining."

    hp1, max_hp1 = eff1["hp"], eff1["hp"]
    hp2, max_hp2 = eff2["hp"], eff2["hp"]
    rof1 = eff1["rof"]
    rof2 = eff2["rof"]

    is_p1 = eff1["p_atk"] is not None
    atk1 = eff1["p_atk"] if is_p1 else eff1["m_atk"]
    bonus1 = eff1["bonus"]

    is_p2 = eff2["p_atk"] is not None
    atk2 = eff2["p_atk"] if is_p2 else eff2["m_atk"]
    bonus2 = eff2["bonus"]

    cur_arm1_m = eff1["m_arm"]
    cur_arm1_p = eff1["p_arm"]
    cur_arm2_m = eff2["m_arm"]
    cur_arm2_p = eff2["p_arm"]

    t = 0.0
    next_atk1 = 0.0
    next_atk2 = 0.0
    hits1 = 0
    hits2 = 0

    max_steps = 4000
    for _ in range(max_steps):
        next_t = min(next_atk1, next_atk2)
        t = next_t

        hit1_now = abs(next_atk1 - t) < 1e-5
        hit2_now = abs(next_atk2 - t) < 1e-5

        dead1 = False
        dead2 = False

        if hit1_now:
            target_arm = (cur_arm2_p if is_p1 else cur_arm2_m)
            if "leitis" in u1.name.lower() or up1.get("wootz_steel"):
                target_arm = 0
            dmg = max(1, atk1 - target_arm) + bonus1
            if hits1 == 0:
                if "coustillier" in u1.name.lower():
                    dmg += (40 if getattr(u1, "elite", False) else 35)
                elif "urumi" in u1.name.lower():
                    dmg += (10 if getattr(u1, "elite", False) else 9)
                elif up1.get("comitatenses"):
                    dmg += 5
                elif up1.get("siphons"):
                    dmg += 20
            if "chu ko nu" in u1.name.lower():
                extra = 4 if getattr(u1, "elite", False) else 2
                dmg += extra * max(1, 3 - cur_arm2_p)
            elif "kipchak" in u1.name.lower():
                extra = 3 if getattr(u1, "elite", False) else 2
                dmg += extra * max(1, 3 - cur_arm2_p)

            hp2 -= dmg
            hits1 += 1
            next_atk1 += rof1
            if "obuch" in u1.name.lower():
                cur_arm2_m = max(0, cur_arm2_m - 1)
                cur_arm2_p = max(0, cur_arm2_p - 1)
            if hp2 <= 0:
                dead2 = True

        if hit2_now:
            target_arm = (cur_arm1_p if is_p2 else cur_arm1_m)
            if "leitis" in u2.name.lower() or up2.get("wootz_steel"):
                target_arm = 0
            dmg = max(1, atk2 - target_arm) + bonus2
            if hits2 == 0:
                if "coustillier" in u2.name.lower():
                    dmg += (40 if getattr(u2, "elite", False) else 35)
                elif "urumi" in u2.name.lower():
                    dmg += (10 if getattr(u2, "elite", False) else 9)
                elif up2.get("comitatenses"):
                    dmg += 5
                elif up2.get("siphons"):
                    dmg += 20
            if "chu ko nu" in u2.name.lower():
                extra = 4 if getattr(u2, "elite", False) else 2
                dmg += extra * max(1, 3 - cur_arm1_p)
            elif "kipchak" in u2.name.lower():
                extra = 3 if getattr(u2, "elite", False) else 2
                dmg += extra * max(1, 3 - cur_arm1_p)

            hp1 -= dmg
            hits2 += 1
            next_atk2 += rof2
            if "obuch" in u2.name.lower():
                cur_arm1_m = max(0, cur_arm1_m - 1)
                cur_arm1_p = max(0, cur_arm1_p - 1)
            if hp1 <= 0:
                dead1 = True

        if dead1 and dead2:
            return f"A draw! Both {u1_label} and {u2_label} eliminate each other simultaneously in {hits1} vs {hits2} hits at {t:.2f}s."
        elif dead2:
            rem1 = max(0, hp1)
            dealt2 = max_hp1 - rem1
            pct1 = (rem1 / max_hp1) * 100 if max_hp1 > 0 else 0
            return f"{u1_label} wins 1v1 against {u2_label}!\n\nOutcome:\n- {u1_label} lands lethal strike in {hits1} hits ({t:.2f}s).\n- {u2_label} dealt {dealt2} dmg across {hits2} hits.\n- Winner surviving HP: {rem1} / {max_hp1} HP remaining ({pct1:.1f}%)."
        elif dead1:
            rem2 = max(0, hp2)
            dealt1 = max_hp2 - rem2
            pct2 = (rem2 / max_hp2) * 100 if max_hp2 > 0 else 0
            return f"{u2_label} wins 1v1 against {u1_label}!\n\nOutcome:\n- {u2_label} lands lethal strike in {hits2} hits ({t:.2f}s).\n- {u1_label} dealt {dealt1} dmg across {hits1} hits.\n- Winner surviving HP: {rem2} / {max_hp2} HP remaining ({pct2:.1f}%)."

    return f"Stalemate! Battle between {u1_label} and {u2_label} timed out after {max_steps} iterations."

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

def render_unit_config(col, side_idx: int, default_civ: str, default_unit: str):
    with col:
        st.subheader(f"Unit {side_idx}")
        civ = st.selectbox(f"Civilization {side_idx}", CIVILIZATIONS, index=CIVILIZATIONS.index(default_civ), key=f"civ_{side_idx}")

        def_unit_idx = sorted(UNITS).index(default_unit) if default_unit in UNITS else 0
        unit_name = st.selectbox(f"Unit {side_idx}", sorted(UNITS), index=def_unit_idx, key=f"unit_name_{side_idx}")

        ftt = st.checkbox("Full Tech Tree (FTT)", key=f"ftt_{side_idx}", help="Enable unhistorical units and upgrades for testing")

        is_avail, reason = is_unit_available(civ, unit_name)
        if not is_avail:
            if not ftt:
                st.error(f"⚠️ **{unit_name}** is not available to **{civ}** in Age of Empires II: DE.\n\n*{reason}*\n\nPlease select an accessible unit, choose another civilization, or enable **Full Tech Tree (FTT)**.")
                return None, civ, None, False
            else:
                st.info(f"ℹ️ {civ} does not normally train {unit_name}, but calculation is permitted under Full Tech Tree (FTT).")

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

        upgrades = {}
        max_m_atk = 3 if ftt else c_info["max_m_atk"]
        max_r_atk = 3 if ftt else c_info["max_r_atk"]
        max_i_arm = 3 if ftt else c_info["max_i_arm"]
        max_c_arm = 3 if ftt else c_info["max_c_arm"]
        max_a_arm = 3 if ftt else c_info["max_a_arm"]

        base_unit = parse_unit(unit_name, is_elite, age)
        boost = base_unit.boost_tech.lower()
        parsed_techs = base_unit.parsed_techs or {}

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
        has_careening = "careening" in boost
        has_dry_dock = "dry dock" in boost
        has_siege_engineers = "siege engineers" in boost
        has_cranequins = "cranequins" in boost
        has_siphons = "siphons" in boost

        has_kataparuto = "kataparuto" in boost
        has_warwolf = "warwolf" in boost
        has_ironclad = "ironclad" in boost
        has_furor = "furor celticus" in boost or "furor celtica" in boost
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
        has_carracks = "carracks" in boost
        has_panokseon = "panokseon" in boost
        has_artillery = "artillery" in boost
        has_greek_fire = "greek fire" in boost
        has_counterweights = "counterweights" in boost

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
            upgrades["careening"] = has_careening and (ftt or c_info.get("careening", True))
            upgrades["dry_dock"] = has_dry_dock and (ftt or c_info.get("dry_dock", True))
            upgrades["siege_engineers"] = has_siege_engineers and (ftt or c_info.get("siege_engineers", True))
            upgrades["cranequins"] = has_cranequins and (ftt or civ == "Burgundians")
            upgrades["siphons"] = has_siphons and (ftt or c_info.get("siphons", True))
            
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
            upgrades["carracks"] = has_carracks and (ftt or civ == "Portuguese")
            upgrades["panokseon"] = has_panokseon and (ftt or civ == "Koreans")
            upgrades["artillery"] = has_artillery and (ftt or civ == "Turks")
            upgrades["greek_fire"] = has_greek_fire and (ftt or civ == "Byzantines")
            upgrades["counterweights"] = has_counterweights and (ftt or civ == "Saracens")
        else:
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
                    upgrades["parthian"] = st.checkbox("Parthian Tactics (+1/+2 Armor)", key=f"pt_{side_idx}")
                if has_chemistry and (ftt or c_info["chemistry"]):
                    upgrades["chemistry"] = st.checkbox("Chemistry (+1 Attack)", key=f"chem_{side_idx}")
                if has_gambesons and (ftt or c_info["gambesons"]):
                    upgrades["gambesons"] = st.checkbox("Gambesons (+1 Pierce Armor)", key=f"gam_{side_idx}")
                if has_careening and (ftt or c_info.get("careening", True)):
                    upgrades["careening"] = st.checkbox("Careening (+1 Pierce Armor)", key=f"car_{side_idx}")
                if has_dry_dock and (ftt or c_info.get("dry_dock", True)):
                    upgrades["dry_dock"] = st.checkbox("Dry Dock (+15% Ship Speed)", key=f"dd_{side_idx}")
                if has_siege_engineers and (ftt or c_info.get("siege_engineers", True)):
                    upgrades["siege_engineers"] = st.checkbox("Siege Engineers (+20% vs Build)", key=f"se_{side_idx}")
                if has_cranequins and (ftt or civ == "Burgundians"):
                    upgrades["cranequins"] = st.checkbox("Cranequins (+1 Attack)", key=f"cran_{side_idx}")
                if has_siphons and (ftt or c_info.get("siphons", True)):
                    upgrades["siphons"] = st.checkbox("Siphons (Explosive Initial Burst Strike)", key=f"siph_{side_idx}")

            if has_kataparuto and (ftt or civ == "Japanese"):
                upgrades["kataparuto"] = st.checkbox("Kataparuto (33% Faster Attack & 4x Pack Speed)", key=f"kata_{side_idx}")
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
            if has_carracks and (ftt or civ == "Portuguese"):
                upgrades["carracks"] = st.checkbox("Carracks (+1/+1 Ship Armor)", key=f"carrak_{side_idx}")
            if has_panokseon and (ftt or civ == "Koreans"):
                upgrades["panokseon"] = st.checkbox("Panokseon (+15% Ship Speed)", key=f"panok_{side_idx}")
            if has_artillery and (ftt or civ == "Turks"):
                upgrades["artillery"] = st.checkbox("Artillery (+2 Cannon Galleon Range)", key=f"artill_{side_idx}")
            if has_greek_fire and (ftt or civ == "Byzantines"):
                upgrades["greek_fire"] = st.checkbox("Greek Fire (+1 Fire Ship Range)", key=f"gf_{side_idx}")
            if has_counterweights and (ftt or civ == "Saracens"):
                upgrades["counterweights"] = st.checkbox("Counterweights (+15% Trebuchet Attack)", key=f"cw_{side_idx}")

        return base_unit, civ, upgrades, True

def main():
    st.set_page_config(page_title="AoE2 1v1 Battle Calculator", page_icon="⚔️", layout="wide")
    st.title("⚔️ Age of Empires 2 1v1 Battle Calculator (Patch 185872 & Naval Fleet)")
    st.markdown("Calculate 1v1 battles with civilization bonuses, live Fandom wiki upgrade extraction, naval ships & upgrades (including Siphons), full tech tree overrides, and Patch 185872 DLCs.")

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
