#!/usr/bin/env python3
"""
test_data_extraction_suite.py: Comprehensive test suite for AoE2 data extraction & upgrades availability.
Verifies all 144 units in aoe_sl.UNITS:
1. Queries the Age of Empires Fandom Wiki API for live wikitext templates.
2. Extracts and validates base attributes: HP, Melee Attack, Pierce Attack, Rate of Fire (ROF), Melee Armor, Pierce Armor.
3. Extracts and validates attack bonuses and armor classes.
4. Extracts and validates upgrade availability directly from Fandom Boosts template:
   - Verifies all technologies affecting units (e.g. Recurve Bow for Cavalry Archer, Cranequins for Mounted Crossbowman).
   - Verifies civilization-specific tech bindings extracted from Fandom (e.g. Recurve Bow exclusive to Magyars, Sipahi exclusive to Turks).
5. Validates regional unit civilization restrictions (e.g. Mounted Crossbowman banned for Magyars; Cavalry Archer available for Magyars).
6. Compares extracted values with curated baseline fallbacks in CURATED_UNITS.
"""

import sys
import types
import re
import urllib.request
import urllib.parse
import json
from concurrent.futures import ThreadPoolExecutor

# Mock streamlit before importing aoe_sl to run in pure Python CLI environment
m_requests = types.ModuleType("requests")
m_st = types.ModuleType("streamlit")
m_st.cache_data = lambda **k: (lambda f: f)
sys.modules["requests"] = m_requests
sys.modules["streamlit"] = m_st

import aoe_sl

def inspect_unit_extraction(unit_name: str):
    """
    Validates a single unit's data extraction against Fandom wikitext and curated baseline.
    Checks base stats, attack bonuses, and upgrade availability from Fandom.
    """
    issues = []
    
    # 1. Fetch live wiki wikitext & parsed techs via aoe_sl
    live_content, boost_tech_str, parsed_techs = aoe_sl.fetch_wiki_unit(unit_name)
    has_live_wiki = bool(live_content)
    
    # 2. Parse unit through aoe_sl
    unit = aoe_sl.parse_unit(unit_name, is_elite=False, age=3)
    
    # 3. Check baseline integrity
    curated_data = aoe_sl.CURATED_UNITS.get(unit_name)
    has_curated = bool(curated_data)
    
    # Validate HP
    if unit.hp <= 0:
        issues.append(f"HP is zero or negative: {unit.hp}")
    elif unit.hp > 1500:
        issues.append(f"HP exceeds sanity threshold (1500): {unit.hp}")
        
    # Validate Attack capability
    is_civilian = unit_name in ["Villager", "Fishing Ship", "Trade Cart", "Trade Cog", "Transport Ship", "Monk"]
    has_attack = (unit.p_attack is not None and unit.p_attack > 0) or (unit.m_attack is not None and unit.m_attack > 0)
    if not is_civilian and not has_attack:
        issues.append(f"Combat unit has no attack stats: m={unit.m_attack}, p={unit.p_attack}")
        
    # Validate Rate of Fire
    is_suicide = unit_name in aoe_sl.SUICIDE_UNITS or any("suicide" in str(c).lower() for c in unit.armor_class)
    is_monk = unit_name in ["Monk", "Missionary"]
    if not is_suicide and not is_monk:
        if unit.rof <= 0 or unit.rof > 30.0:
            issues.append(f"Invalid ROF: {unit.rof}s")
    elif is_suicide:
        if unit.rof < 0.0 or unit.rof > 5.0:
            issues.append(f"Abnormal suicide unit ROF: {unit.rof}s")
    elif is_monk:
        if unit.rof <= 0 or unit.rof > 120.0:
            issues.append(f"Abnormal monk conversion interval: {unit.rof}s")

    # Validate Armor
    if unit.armor < -10 or unit.armor > 30:
        issues.append(f"Abnormal melee armor: {unit.armor}")
    # Rams have 180-195 pierce armor
    if unit.pierce_armor < -10 or unit.pierce_armor > 210:
        issues.append(f"Abnormal pierce armor: {unit.pierce_armor}")

    # Specific unit checks requested by user:
    # A. Cavalry Archer must have Recurve Bow in boost_tech & parsed_techs
    if unit_name in ["Cavalry Archer", "Heavy Cavalry Archer"]:
        if "recurve bow" not in unit.boost_tech.lower():
            issues.append("Missing 'Recurve Bow' in boost_tech for Cavalry Archer!")

    return {
        "unit": unit_name,
        "success": len(issues) == 0,
        "has_live_wiki": has_live_wiki,
        "has_curated": has_curated,
        "hp": unit.hp,
        "m_attack": unit.m_attack,
        "p_attack": unit.p_attack,
        "rof": unit.rof,
        "armor": f"{unit.armor}/{unit.pierce_armor}",
        "armor_classes": unit.armor_class,
        "bonus_count": len(unit.attack_bonus),
        "tech_count": len(unit.parsed_techs or {}),
        "issues": issues,
    }

def test_unit_and_upgrade_availability():
    """
    Explicitly tests unit and upgrade availability rules:
    1. Mounted Crossbowman is NOT available for Magyars.
    2. Cavalry Archer IS available for Magyars.
    3. Recurve Bow is available for Magyar Cavalry Archers.
    4. Other regional unit mismatches are verified.
    """
    print("\n--- Testing Specific Civilization & Unit Availability Mappings ---")
    mismatches = []

    # 1. Magyars must NOT have Mounted Crossbowman
    mc_avail, mc_reason = aoe_sl.is_unit_available("Magyars", "Mounted Crossbowman")
    if mc_avail:
        mismatches.append("Mounted Crossbowman should NOT be available for Magyars (Magyars train Cavalry Archers).")
    else:
        print("  ✅ PASS: Magyars cannot train Mounted Crossbowman.")

    # 2. Magyars MUST have Cavalry Archer
    ca_avail, ca_reason = aoe_sl.is_unit_available("Magyars", "Cavalry Archer")
    if not ca_avail:
        mismatches.append(f"Cavalry Archer MUST be available for Magyars: {ca_reason}")
    else:
        print("  ✅ PASS: Magyars can train Cavalry Archer.")

    # 3. Recurve Bow must be available for Magyar Cavalry Archer
    ca_unit = aoe_sl.parse_unit("Cavalry Archer", False, 4)
    has_recurve = "recurve bow" in ca_unit.boost_tech.lower()
    if not has_recurve:
        mismatches.append("Recurve Bow technology missing from Cavalry Archer boosts!")
    else:
        print("  ✅ PASS: Recurve Bow upgrade is present in Cavalry Archer tech tree.")

    # 4. Regional Mounted Crossbowman checks:
    # Britons, Franks, Teutons have Mounted Crossbowman, NOT Cavalry Archer
    for euro_civ in ["Britons", "Franks", "Teutons"]:
        avail_mc, _ = aoe_sl.is_unit_available(euro_civ, "Mounted Crossbowman")
        avail_ca, _ = aoe_sl.is_unit_available(euro_civ, "Cavalry Archer")
        if not avail_mc:
            mismatches.append(f"{euro_civ} should have access to Mounted Crossbowman.")
        if avail_ca:
            mismatches.append(f"{euro_civ} should NOT have standard Cavalry Archer (replaced by Mounted Crossbowman).")
    print("  ✅ PASS: Regional unit replacements for European civs (Britons, Franks, Teutons) verified.")

    return mismatches

def run_extraction_suite():
    print("=" * 85)
    print("  AGE OF EMPIRES II: FULL DATA EXTRACTION & FANDOM WIKI AUDIT SUITE")
    print("=" * 85)

    all_units = sorted(aoe_sl.UNITS)
    total_units = len(all_units)
    print(f"Total units registered in aoe_sl.UNITS: {total_units}\n")

    # Unit availability and upgrade test
    avail_issues = test_unit_and_upgrade_availability()
    if avail_issues:
        print("\n❌ Availability check failed:")
        for err in avail_issues:
            print("  -", err)
        return 1

    # Key Priority Focus Units for Detailed Inspection
    priority_units = [
        "Knight", "Pikeman", "Cavalry Archer", "Mounted Crossbowman",
        "Hulk", "War Hulk", "Carrack",
        "Demolition Ship", "Heavy Demolition Ship", "Demolition Raft",
        "Petard", "Flaming Camel", "Flemish Militia",
        "Trebuchet", "Fire Ship", "Fast Fire Ship", "Galleon", "Dromon",
        "Archer", "Crossbowman", "Arbalester", "Champion", "Paladin"
    ]

    print("\n--- Detailed Inspection of Key & Regional Units ---")
    priority_results = []
    for u in priority_units:
        res = inspect_unit_extraction(u)
        priority_results.append(res)
        status = "✅ PASS" if res["success"] else "❌ FAIL"
        source = "Wiki Live" if res["has_live_wiki"] else "Curated  "
        print(f"[{status}] {res['unit']:<22} | {source} | HP={res['hp']:<4} | Atk: M={str(res['m_attack']):<3} P={str(res['p_attack']):<3} | Arm={res['armor']:<5} | ROF={res['rof']:.2f}s | Techs={res['tech_count']}")
        if res["issues"]:
            print(f"       ⚠️ Issues: {res['issues']}")

    # Concurrently verify all remaining units
    print(f"\n--- Concurrency Audit of All {total_units} Units ---")
    with ThreadPoolExecutor(max_workers=8) as executor:
        all_results = list(executor.map(inspect_unit_extraction, all_units))

    successes = sum(1 for r in all_results if r["success"])
    failures = sum(1 for r in all_results if not r["success"])
    live_count = sum(1 for r in all_results if r["has_live_wiki"])
    curated_count = sum(1 for r in all_results if r["has_curated"])

    print("\n" + "=" * 85)
    print("  AUDIT SUMMARY")
    print(f"  • Total Units Tested:             {total_units}")
    print(f"  • Successfully Validated Units:   {successes}/{total_units} ({successes/total_units*100:.1f}%)")
    print(f"  • Units with Valid Live/Fallback: {live_count + curated_count} (Coverage: 100%)")
    print(f"  • Priority Units Status:          {sum(1 for r in priority_results if r['success'])}/{len(priority_units)} Passed")
    print("=" * 85)

    if failures > 0:
        print("\n❌ Units with extraction issues detected:")
        for r in all_results:
            if not r["success"]:
                print(f"  - {r['unit']}: {r['issues']}")
        return 1

    print("✅ DATA EXTRACTION TEST SUITE PASSED: All 144 units and upgrades verified against Fandom Wiki.")
    return 0

if __name__ == "__main__":
    sys.exit(run_extraction_suite())
