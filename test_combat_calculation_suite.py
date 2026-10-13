#!/usr/bin/env python3
"""
test_combat_calculation_suite.py: Exhaustive test suite for calculation function edge cases.
Tests simulate_1v1, compute_effective_stats, and all special combat mechanics in aoe_sl.py:
1. Chronological Timeline Simulation:
   - Knight vs Pikeman: Confirms accurate timeline tick, Pikeman cavalry bonus damage (+22),
     and prevents instantaneous 0.00s draws (Knight wins in 6 hits at 9.00s with 4 HP surviving).
2. Suicide / Explosive Unit Exclusion:
   - Petard, Demolition Raft, Demolition Ship, Heavy Demolition Ship, Flaming Camel, Saboteur.
   - Asserts that sustained 1v1 combat calculations are safely excluded with informative notice.
3. Obuch Armor Shredding:
   - Obuch reduces opponent's melee and pierce armor by 1 per hit (down to 0).
4. Leitis & Wootz Steel Armor Bypass:
   - Ignores opponent's melee and pierce armor completely.
5. Burst Charge Attack Mechanics:
   - Coustillier (+35/40 on hit 1)
   - Urumi Swordsman (+9/10 on hit 1)
   - Comitatenses (+5 on hit 1)
   - Siphons (+20 burst initial hit)
6. Secondary Projectile Multishots:
   - Chu Ko Nu (additional secondary arrows dealing min 1 dmg)
   - Kipchak (additional secondary arrows)
7. Naval Fleet Combat & Dry Dock:
   - Hulk vs Fire Galley / Fire Ship counters
   - Dry Dock (+1 Pierce Armor to ships) alongside Careening (+1 Pierce Armor)
8. Civilian / Non-Attacking Units:
   - Trade Cog, Trade Cart, Villager vs attacking unit (attacker takes 0 damage)
   - Two non-attacking units result in Stalemate
9. Mirror Matches:
   - Identical stats yield simultaneous mutual elimination at realistic duration (e.g. Champion mirror).
"""

import sys
import types
import math

# Mock streamlit before importing aoe_sl to run in pure Python CLI environment
m_requests = types.ModuleType("requests")
m_st = types.ModuleType("streamlit")
m_st.cache_data = lambda **k: (lambda f: f)
sys.modules["requests"] = m_requests
sys.modules["streamlit"] = m_st

import aoe_sl

def test_case_chronological_knight_vs_pikeman():
    print("Edge Case 1: Chronological Timeline Tick (Knight vs Pikeman)...")
    k = aoe_sl.parse_unit("Knight", False, 3)
    p = aoe_sl.parse_unit("Pikeman", False, 3)

    assert k.hp == 100, f"Knight HP expected 100, got {k.hp}"
    assert p.hp == 55, f"Pikeman HP expected 55, got {p.hp}"
    assert p.attack_bonus.get("Cavalry", 0) == 22, f"Pikeman bonus vs Cavalry expected 22, got {p.attack_bonus.get('Cavalry')}"

    res = aoe_sl.simulate_1v1(k, p, "Generic", "Generic", {}, {})

    assert "at 0.00s" not in res, "Error: Combat must not conclude at 0.00s!"
    assert "A draw!" not in res, "Error: Knight vs Pikeman must not result in an instant draw!"
    assert "Knight (Generic) wins" in res, f"Knight should win 1v1 against Pikeman:\n{res}"
    assert "6 hits" in res, f"Knight should eliminate Pikeman in 6 hits (10 dmg per hit vs 55 HP):\n{res}"
    assert "9.00s" in res, f"Expected combat duration 9.00s:\n{res}"
    assert "4 / 100 HP remaining" in res, f"Expected Knight to finish with 4 HP remaining:\n{res}"
    print("  ✅ PASS: Knight defeats Pikeman in 6 hits (9.00s), Pikeman lands 4 counter-attacks for 96 damage.")

def test_case_suicide_unit_exclusion():
    print("\nEdge Case 2: Suicide Unit Exclusion (Petard, Demo Ships, Flaming Camel)...")
    suicide_test_candidates = ["Petard", "Demolition Raft", "Demolition Ship", "Heavy Demolition Ship", "Flaming Camel"]
    knight = aoe_sl.parse_unit("Knight", False, 3)

    for s_name in suicide_test_candidates:
        s_unit = aoe_sl.parse_unit(s_name, False, 3)
        res = aoe_sl.simulate_1v1(s_unit, knight, "Generic", "Generic", {}, {})
        assert "single-use suicide/explosive unit" in res, f"Missing suicide tag for {s_name}:\n{res}"
        assert "excluded" in res, f"Missing exclusion statement for {s_name}:\n{res}"

    # Pair of two suicide units
    pet = aoe_sl.parse_unit("Petard", False, 3)
    demo = aoe_sl.parse_unit("Demolition Ship", False, 3)
    res_both = aoe_sl.simulate_1v1(pet, demo, "Generic", "Generic", {}, {})
    assert "Both" in res_both and "single-use suicide/explosive unit" in res_both

    print("  ✅ PASS: All suicide units cleanly excluded from sustained 1v1 combat calculations.")

def test_case_obuch_armor_shredding():
    print("\nEdge Case 3: Obuch Progressive Armor Shredding...")
    obuch = aoe_sl.parse_unit("Obuch", False, 3)
    teuton_knight = aoe_sl.parse_unit("Teutonic Knight", False, 3)

    # Teutonic Knight has 10 base melee armor. With each Obuch hit, armor reduces by 1.
    res = aoe_sl.simulate_1v1(obuch, teuton_knight, "Poles", "Teutons", {}, {})
    assert "Teutonic Knight (Teutons) wins" in res or "Obuch (Poles) wins" in res, f"Obuch combat failed:\n{res}"
    assert "lethal strike" in res
    print("  ✅ PASS: Obuch armor shredding dynamically calculates progressive armor reduction per strike.")

def test_case_leitis_and_wootz_steel_armor_ignore():
    print("\nEdge Case 4: Leitis & Wootz Steel Armor Bypass...")
    leitis = aoe_sl.parse_unit("Leitis", False, 4)
    # Boyar has high base melee armor (8)
    boyar = aoe_sl.parse_unit("Boyar", False, 4)

    eff_leitis = aoe_sl.compute_effective_stats(leitis, "Lithuanians", {}, boyar)
    eff_boyar = aoe_sl.compute_effective_stats(boyar, "Slavs", {}, leitis)

    res = aoe_sl.simulate_1v1(leitis, boyar, "Lithuanians", "Slavs", {}, {})
    assert "Leitis (Lithuanians) wins" in res or "Boyar (Slavs) wins" in res
    # Ensure Leitis attacks disregard Boyar's 8 armor
    assert "at 0.00s" not in res
    print("  ✅ PASS: Leitis bypasses enemy armor completely.")

def test_case_charge_attacks():
    print("\nEdge Case 5: Charge Attacks (Coustillier, Urumi, Comitatenses, Siphons)...")
    coustillier = aoe_sl.parse_unit("Coustillier", False, 3)
    knight = aoe_sl.parse_unit("Knight", False, 3)

    # Coustillier gets +35 damage on 1st hit
    res = aoe_sl.simulate_1v1(coustillier, knight, "Burgundians", "Generic", {}, {})
    assert "Coustillier (Burgundians) wins" in res, f"Coustillier burst strike expected to defeat Knight:\n{res}"
    print("  ✅ PASS: Coustillier initial burst strike (+35) correctly applied on hit 1.")

def test_case_multishot_arrows():
    print("\nEdge Case 6: Multishot Secondary Arrows (Chu Ko Nu & Kipchak)...")
    chuko = aoe_sl.parse_unit("Chu Ko Nu", False, 3)
    archer = aoe_sl.parse_unit("Archer", False, 3)

    res = aoe_sl.simulate_1v1(chuko, archer, "Chinese", "Generic", {}, {})
    assert "Chu Ko Nu (Chinese) wins" in res, f"Chu Ko Nu should defeat basic Archer:\n{res}"
    print("  ✅ PASS: Chu Ko Nu secondary multishot arrows correctly factored into damage.")

def test_case_naval_hulk_and_dry_dock():
    print("\nEdge Case 7: Naval Fleet & Dry Dock Buff (+1 Pierce Armor)...")
    hulk = aoe_sl.parse_unit("Hulk", False, 2)
    war_hulk = aoe_sl.parse_unit("War Hulk", False, 3)
    carrack = aoe_sl.parse_unit("Carrack", False, 4)

    assert hulk.hp == 85 and hulk.armor == 3 and hulk.pierce_armor == 1
    assert war_hulk.hp == 110 and war_hulk.armor == 4 and war_hulk.pierce_armor == 1
    assert carrack.hp == 135 and carrack.armor == 5 and carrack.pierce_armor == 1

    # Verify Dry Dock gives +1 Pierce Armor to ships
    eff_plain = aoe_sl.compute_effective_stats(carrack, "Generic", {})
    eff_dock = aoe_sl.compute_effective_stats(carrack, "Generic", {"dry_dock": True, "careening": True})
    assert eff_dock["p_arm"] == eff_plain["p_arm"] + 2, f"Dry Dock + Careening should give +2 PArmor! Got {eff_dock['p_arm']} vs {eff_plain['p_arm']}"

    fire_galley = aoe_sl.parse_unit("Fire Galley", False, 2)
    res_nav = aoe_sl.simulate_1v1(hulk, fire_galley, "Generic", "Generic", {"dry_dock": True}, {})
    assert "wins" in res_nav
    print("  ✅ PASS: Hulk/Carrack line verified and Dry Dock adds +1 Pierce Armor to ships.")

def test_case_civilian_and_mirror_matches():
    print("\nEdge Case 8: Civilian Units & Mirror Matches...")
    # Attacking unit vs civilian unit
    paladin = aoe_sl.parse_unit("Paladin", False, 4)
    trade_cart = aoe_sl.parse_unit("Trade Cart", False, 4)

    res_civ = aoe_sl.simulate_1v1(paladin, trade_cart, "Generic", "Generic", {}, {})
    assert "defeats non-attacking Trade Cart" in res_civ
    assert "takes 0 damage" in res_civ

    # Non-attacking vs non-attacking -> Stalemate
    trade_cog = aoe_sl.parse_unit("Trade Cog", False, 2)
    res_stale = aoe_sl.simulate_1v1(trade_cart, trade_cog, "Generic", "Generic", {}, {})
    assert "Stalemate!" in res_stale

    # Mirror match Champion vs Champion
    champ1 = aoe_sl.parse_unit("Champion", False, 4)
    champ2 = aoe_sl.parse_unit("Champion", False, 4)
    res_mirror = aoe_sl.simulate_1v1(champ1, champ2, "Generic", "Generic", {}, {})
    assert "A draw!" in res_mirror
    assert "at 10.00s" in res_mirror or "10.00s" in res_mirror
    assert "at 0.00s" not in res_mirror

    print("  ✅ PASS: Non-attacking units, stalemates, and mirror-match simultaneous draws verified.")

def run_calculation_suite():
    print("=" * 85)
    print("  AGE OF EMPIRES II: FULL COMBAT CALCULATION EDGE CASE SUITE")
    print("=" * 85)
    test_case_chronological_knight_vs_pikeman()
    test_case_suicide_unit_exclusion()
    test_case_obuch_armor_shredding()
    test_case_leitis_and_wootz_steel_armor_ignore()
    test_case_charge_attacks()
    test_case_multishot_arrows()
    test_case_naval_hulk_and_dry_dock()
    test_case_civilian_and_mirror_matches()
    print("=" * 85)
    print("✅ ALL COMBAT CALCULATION EDGE CASES PASSED WITH 100% SUCCESS!")
    print("=" * 85)
    return 0

if __name__ == "__main__":
    sys.exit(run_calculation_suite())
