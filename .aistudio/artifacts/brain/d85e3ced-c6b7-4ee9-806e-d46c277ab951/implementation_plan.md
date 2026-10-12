# AoE2 1v1 Battle Calculator - Complete Naval & Patch Data Update

This implementation plan incorporates all naval ships (military combat vessels, unique ships, regional vessels, and civilian ships), naval upgrades (Careening, Dry Dock, Blacksmith ranged upgrades, Chemistry, and naval unique technologies), accurate Flemish Militia statistics per the latest balance patch, and enhanced live wiki stat extraction.

### User Review & Critical Decisions

> [!IMPORTANT]
> The following mechanics and parameters have been confirmed:
> - **Comprehensive Ship Roster**: Add all naval vessels (Galley line, Fire Ship line, Demolition Ship line, Cannon Galleon line, Dromon, Longship, Turtle Ship, Caravel, Thirisadai, Fishing Ship, Trade Cog, and Transport Ship) as distinct selectable entries in the unit dropdown.
> - **Dynamic Naval Boosts**: Automatically present applicable upgrades for each ship based on its wiki `{{Boosts|Technologies}}` section, including Careening (+1 pierce armor), Fletching / Bodkin / Bracer, Chemistry, and civ unique techs (Carracks, Panokseon, Artillery).
> - **Accurate Flemish Militia Statistics**: Updated to current AoE2 DE patch stats:
>   - Feudal Age (and Dark Age fallback): 40 HP, 6 attack, 0/1 armor
>   - Castle Age: 55 HP, 8 attack, 1/1 armor
>   - Imperial Age: 60 HP, 10 attack, 1/1 armor
>   - Bonus vs Cavalry (+8) and Camel (+6).
> - **Civilian & Unarmed Ships in 1v1**: Unarmed vessels (Fishing Ship, Trade Cog, Transport Ship) take hits without retaliating, correctly displaying time-to-kill statistics and awarding uncontested victory to the attacker.

---

### 1. Overview & Comprehensive Unit Expansion

- **Land & Naval Combined Catalog (155+ Units)**:
  - All existing land units, unique units, and regional units.
  - **Standard Warships**: Galley, War Galley, Galleon.
  - **Fire Warships**: Fire Galley, Fire Ship, Fast Fire Ship.
  - **Demolition Warships**: Demolition Raft, Demolition Ship, Heavy Demolition Ship.
  - **Gunpowder Warships**: Cannon Galleon, Elite Cannon Galleon, Dromon.
  - **Unique & Regional Ships**:
    - Longship, Elite Longship (Vikings, Danes, Saxons, Varangians).
    - Turtle Ship, Elite Turtle Ship (Koreans).
    - Caravel, Elite Caravel (Portuguese).
    - Thirisadai (Dravidians).
  - **Civilian & Transport Vessels**: Fishing Ship, Trade Cog, Transport Ship.

---

### 2. User Experience & Visual Design

- **Unit Configuration Columns**:
  - **Unit Selector**: Alphabetical searchable dropdown featuring all land and naval units.
  - **Ship Availability Validation**:
    - Dromon strictly validated for Romans, Byzantines, Armenians, Goths, Huns.
    - Cannon Galleon disallowed for civs that replace it with Dromon.
    - Unique ships restricted to their respective civilizations.
    - Standard ship upgrade restrictions (e.g., Aztecs lack Galleon and Fast Fire Ship).
  - **Naval Upgrade Selectors**:
    - Blacksmith Ranged Attack (`Fletching (+1)`, `Bodkin Arrow (+2)`, `Bracer (+3)`) offered only if present in ship's `boost_tech` (e.g. Galley line, Longship, Caravel).
    - `Chemistry (+1 Attack)` for arrow/gunpowder ships.
    - `Careening (+1 Pierce Armor)` offered for ships with the dock technology in `boost_tech`.
    - Civ unique techs (Portuguese **Carracks**, Korean **Panokseon**, Turk **Artillery**).
- **Civilian Ships in Battle**:
  - Selecting a Trade Cog or Fishing Ship against a combat ship calculates exact hits and time-to-kill, awarding uncontested victory.
  - Comparing two unarmed ships reports a peaceful stalemate without errors.

---

### 3. Key Product Decisions & Trade-Offs

- **Decision 1: Direct Dropdown Tier Selection for Ships**
  - *Chosen Approach*: Users choose the exact ship tier (e.g. "War Galley" vs "Galleon") directly from the dropdown.
  - *Why*: Provides explicit control over matchup analysis across game stages without conflating unit identity with Age parameters.
- **Decision 2: Live Wiki Ingestion with Curated Naval Fallback**
  - *Chosen Approach*: Query Fandom wiki API for each ship's base stats and `{{Boosts|Technologies}}`, backed by a verified offline dictionary for all 18+ naval vessels.
  - *Why*: Ensures zero crashes even when testing offline or under API rate limits.
- **Decision 3: Naval Damage Formulas & Ship Armor Classes**
  - *Chosen Approach*: Incorporates naval armor classes ("Ship", "Fishing Ship") and bonus damage (e.g. Fire Ships dealing bonus damage against Ships, Galley line dealing bonus damage against Ships/Buildings, Demolition ships dealing massive blast damage).
  - *Why*: Reflects real AoE2 rock-paper-scissors naval combat dynamics.

---

### 4. Technical Architecture & Data Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                     │
│  ┌───────────────────────────┐ ┌──────────────────────────┐ │
│  │     Unit 1 Configuration   │ │   Unit 2 Configuration   │ │
│  │  - Civ Dropdown (52 civs) │ │  - Civ Dropdown (52 civs)│ │
│  │  - Unit (Land & Ships)    │ │  - Unit (Land & Ships)   │ │
│  │  - Contextual Upgrades    │ │  - Contextual Upgrades   │ │
│  │    (Careening, Chemistry, │ │    (Careening, Chemistry,│ │
│  │     Blacksmith, Unique)   │ │     Blacksmith, Unique)  │ │
│  └─────────────┬─────────────┘ └────────────┬─────────────┘ │
└────────────────┼────────────────────────────┼───────────────┘
                 │                            │
                 ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Validation & Tech Tree Engine               │
│  - Validate Naval Unit Access (Dromon vs Cannon Galleon)    │
│  - Parse {{Boosts|Technologies}} for Careening & Blacksmith │
│  - Accurate Flemish Militia Stats (40 / 55 / 60 HP)         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Combat Simulation Engine                 │
│  - Naval Rock-Paper-Scissors (Fire > Galley > Demo > Fire)  │
│  - Unarmed Civilian Ships (Time-to-Kill Display)            │
│  - Dual Stat Cards: Baseline vs Actual Upgraded Combat Stats│
└─────────────────────────────────────────────────────────────┘
```

- **File Delivery**:
  - `/aoe_sl.py`: Complete Python script updated with full naval and patch mechanics.
  - `/requirements.txt`: Python dependencies (`streamlit`, `requests`).
