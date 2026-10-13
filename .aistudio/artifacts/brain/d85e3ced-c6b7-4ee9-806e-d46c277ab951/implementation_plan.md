# AoE2 Battle Calculator: Comprehensive Verification & Test Suite

Deliver two robust, standalone Python test programs that thoroughly test and validate data extraction against Fandom Wiki and evaluate calculation logic for all combat edge cases in `aoe_sl.py`, ensuring complete correctness and readiness for Git push and Streamlit app deployment.

### User Review & Critical Decisions

> [!IMPORTANT]
> - **Fandom Extraction Strategy**: Test all 144 units with fallback comparison (verifying live Fandom wikitext where available, validating curated baseline integrity, and ensuring graceful handling of HTTP 429 rate limits).
> - **Execution Target**: Self-contained Python scripts executed directly in the environment to verify and guarantee that `aoe_sl.py` is 100% bug-free and production ready.

---

### 1. Overview & Core Concept

- **What It Delivers**:
  1. `test_data_extraction_suite.py`: Tests unit data extraction across all 144 units in `aoe_sl.py`. Extracts Infobox AoE2 unit templates and Boosts from Fandom API, validates HP, attacks, armor values, rate of fire, armor classes, and tech trees, comparing against the curated fallbacks.
  2. `test_combat_calculation_suite.py`: Systematically asserts calculation logic across all edge cases (Knight vs Pikeman chronological tick, suicide units exclusion like Petard and Demolition Ships, Obuch armor shredding, Leitis armor bypass, Coustillier charge attack, Chu Ko Nu secondary arrows, Dry Dock naval buffs, non-attacking civilian units, and mirror match draws).
  3. Validates and refines `aoe_sl.py` so that it passes both test suites with zero failures and is fully ready for Git push and Streamlit deployment.

---

### 2. Technical Architecture & Test Strategy

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Fandom Wiki API                               │
│       https://ageofempires.fandom.com/api.php?action=parse...          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Live Wikitext
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    test_data_extraction_suite.py                       │
│  - Queries all 144 units in aoe_sl.UNITS                               │
│  - Verifies Infobox AoE2 unit parsing (HP, ROF, Armor, Attacks)        │
│  - Compares with CURATED_UNITS baseline fallbacks                      │
│  - Verifies Patch 185872 & The Last Chieftains (Hulk line, Carrack)    │
│  - Verifies Suicide unit tagging (Petard, Demo Ships, Flaming Camel)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Validated Unit Objects
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                              aoe_sl.py                                 │
│  - parse_unit(unit_name, is_elite, age)                                │
│  - compute_effective_stats(unit, civ, upgrades, opponent)              │
│  - simulate_1v1(unit1, unit2, civ1, civ2, up1, up2)                    │
│  - Streamlit UI app layout & interactive options                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   test_combat_calculation_suite.py                    │
│  - Edge Case 1: Chronological tick (Knight vs Pikeman, no 0s draw)     │
│  - Edge Case 2: Suicide unit exclusion (Petard, Demo Ship, Flaming)   │
│  - Edge Case 3: Obuch progressive armor reduction (-1/-1 per hit)     │
│  - Edge Case 4: Leitis / Wootz Steel complete armor bypass             │
│  - Edge Case 5: Coustillier / Urumi burst charge attacks on hit 1      │
│  - Edge Case 6: Chu Ko Nu & Kipchak secondary arrow volley             │
│  - Edge Case 7: Naval fleet & Dry Dock (+1 Pierce Armor to ships)      │
│  - Edge Case 8: Non-attacking units & mirror match simultaneous draw   │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Implementation Steps

1. **Create `test_data_extraction_suite.py`**:
   - Tests all 144 units in `aoe_sl.UNITS`.
   - Compares live API wikitext vs curated baseline fallbacks.
   - Reports exact discrepancies and confirms validity of all stats.

2. **Create `test_combat_calculation_suite.py`**:
   - Executes exhaustive edge case matrix against `simulate_1v1` and `compute_effective_stats`.
   - Asserts mathematical correctness across times, hits, remaining HP, and bonus damage calculations.

3. **Execute & Verify against `aoe_sl.py`**:
   - Run both test programs.
   - Ensure clean compilation with `python3 -m py_compile`, `compile_applet`, and `lint_applet`.
   - Confirm complete readiness for Git push and Streamlit app.
