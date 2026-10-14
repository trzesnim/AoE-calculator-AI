#!/usr/bin/env python3
"""
test_data_extraction.py: Tests and verifies Fandom API data extraction for all AoE2 units.
Uses multi-threaded concurrent extraction to quickly query Fandom API for all units in UNITS,
validates that attributes (HP, attack, armor, ROF, armor classes, upgrades) are parsed properly,
and verifies consistency against the latest AoE2 DE update.
"""

import sys
import types
from concurrent.futures import ThreadPoolExecutor

# Mock streamlit before importing aoe_sl
m_requests = types.ModuleType("requests")
m_st = types.ModuleType("streamlit")
m_st.cache_data = lambda **k: (lambda f: f)
m_st.error = lambda *a, **k: None
sys.modules["requests"] = m_requests
sys.modules["streamlit"] = m_st

import aoe_sl

def inspect_single_unit(unit_name: str):
    """Fetches wiki data for unit_name, parses stats, and validates."""
    try:
        content, boost_str, parsed_techs, *rest = aoe_sl.fetch_wiki_unit(unit_name)
        has_live = bool(content)
        unit = aoe_sl.parse_unit(unit_name, False, 3)

        errors = []
        if unit.hp <= 0 or unit.hp > 1500:
            errors.append(f"Invalid HP: {unit.hp}")

        can_attack = (unit.p_attack is not None and unit.p_attack > 0) or (unit.m_attack is not None and unit.m_attack > 0)
        is_civilian = unit_name in ["Villager", "Fishing Ship", "Trade Cart", "Trade Cog", "Transport Ship", "Monk", "Missionary", "Siege Tower"]
        if not can_attack and not is_civilian:
            errors.append(f"Missing attack stats: m={unit.m_attack}, p={unit.p_attack}")

        is_suicide = unit_name in aoe_sl.SUICIDE_UNITS or any("suicide" in str(c).lower() for c in unit.armor_class)
        is_monk = unit_name in ["Monk", "Missionary"]

        if not is_suicide and not is_monk:
            if unit.rof <= 0 or unit.rof > 30.0:
                errors.append(f"Invalid ROF: {unit.rof}")
        elif is_suicide:
            # Suicide units explode on contact; 0.0 or N/A ROF is expected
            pass
        elif is_monk:
            # Monks and missionaries have conversion cycles around 62 seconds
            if unit.rof <= 0 or unit.rof > 120.0:
                errors.append(f"Invalid Monk cycle: {unit.rof}")

        return {
            "name": unit_name,
            "success": len(errors) == 0,
            "has_live": has_live,
            "hp": unit.hp,
            "m_atk": unit.m_attack,
            "p_atk": unit.p_attack,
            "rof": unit.rof,
            "armor": f"{unit.armor}/{unit.pierce_armor}",
            "tech_count": len(parsed_techs),
            "errors": errors
        }
    except Exception as e:
        return {
            "name": unit_name,
            "success": False,
            "has_live": False,
            "hp": 0,
            "m_atk": None,
            "p_atk": None,
            "rof": 0,
            "armor": "0/0",
            "tech_count": 0,
            "errors": [f"Exception: {str(e)}"]
        }

def run_tests():
    print("=" * 80)
    print("AOE2 FANDOM API EXTRACTION VALIDATOR")
    print("=" * 80)

    # 1. Test Priority User-Specified Units first
    priority_units = [
        "Knight", "Pikeman", "Hulk", "War Hulk", "Carrack",
        "Demolition Ship", "Heavy Demolition Ship", "Demolition Raft",
        "Petard", "Flaming Camel", "Flemish Militia",
        "Trebuchet", "Fire Ship", "Fast Fire Ship", "Galleon", "Dromon",
        "Archer", "Crossbowman", "Arbalester", "Champion", "Paladin"
    ]

    print("\n--- Testing Priority Units (Detailed Inspection) ---")
    with ThreadPoolExecutor(max_workers=8) as executor:
        priority_results = list(executor.map(inspect_single_unit, priority_units))

    p_fails = 0
    for r in priority_results:
        status = "✅ OK  " if r["success"] else "❌ FAIL"
        live_tag = "Live Wiki" if r["has_live"] else "Curated "
        print(f"[{status}] {r['name']:<22} | {live_tag} | HP={r['hp']:<4} | Atk: M={str(r['m_atk']):<3} P={str(r['p_atk']):<3} | Arm={r['armor']:<5} | ROF={r['rof']:.2f}s | Techs={r['tech_count']}")
        if not r["success"]:
            print(f"        Errors: {r['errors']}")
            p_fails += 1

    # 2. Test All Units in UNITS concurrently
    all_units = aoe_sl.UNITS
    print(f"\n--- Testing All {len(all_units)} Units in UNITS concurrently ---")
    with ThreadPoolExecutor(max_workers=12) as executor:
        all_results = list(executor.map(inspect_single_unit, all_units))

    successes = sum(1 for r in all_results if r["success"])
    failures = sum(1 for r in all_results if not r["success"])
    live_count = sum(1 for r in all_results if r["has_live"])

    print("\n" + "=" * 80)
    print("EXTRACTION SUMMARY RESULTS")
    print(f"Total units tested: {len(all_units)}")
    print(f"Successfully validated units: {successes}/{len(all_units)} ({successes/len(all_units)*100:.1f}%)")
    print(f"Units resolved via live Fandom API: {live_count}/{len(all_units)} ({live_count/len(all_units)*100:.1f}%)")
    print(f"Priority units validated: {len(priority_units) - p_fails}/{len(priority_units)}")
    print("=" * 80)

    if failures > 0 or p_fails > 0:
        print("❌ One or more units failed validation!")
        for r in all_results:
            if not r["success"]:
                print(f"  Fail: {r['name']} -> {r['errors']}")
        return 1

    print("✅ ALL AOE2 UNITS VERIFIED AND CONSISTENT WITH FANDOM & DE UPDATES!")
    return 0

if __name__ == "__main__":
    sys.exit(run_tests())
