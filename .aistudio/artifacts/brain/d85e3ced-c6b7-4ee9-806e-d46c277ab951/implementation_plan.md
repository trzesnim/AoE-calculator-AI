# AoE2 1v1 Battle Calculator - Streamlit Upgrade & Fix Plan

This implementation plan refines `aoe_sl.py` to eliminate hardcoded assumptions by dynamically extracting unit upgrades directly from the Age of Empires Fandom MediaWiki `{{Boosts|Technologies}}` section, strictly enforcing AoE2 DE civilization tech trees (including regional lines and unit replacements like Winged Hussar for Lithuanians and Poles), and accurately modeling combat mechanics such as Thumb Ring attack rate increases.

### User Review & Critical Decisions

> [!IMPORTANT]
> The following mechanics and architectural choices have been confirmed:
> - **Dynamic Tech Extraction from Wiki**: Instead of guessing upgrade categories, parse the unit's wiki `{{Boosts|Technologies...}}` section to determine exactly which Blacksmith upgrades, university techs, and unique technologies (e.g. Kataparuto for Trebuchets, Rocketry for Scorpions/Chu Ko Nu, Recurve Bow for Cavalry Archers) apply to that specific unit.
> - **Strict AoE2 DE Tech Tree Enforcement**: Prevent invalid unit selections with strict rules (e.g., Lithuanians and Poles get Winged Hussar but NOT standard Hussar; Turks get Pikeman but NOT Halberdier; Franks do NOT get Cavalry Archer or Arbalester; Persians get Savar instead of Paladin; Romans get Legionary instead of Two-Handed/Champion).
> - **Thumb Ring Fire-Rate Implementation**: Thumb Ring reduces the unit's attack interval / Rate of Fire (Foot archers attack ~18% faster with 0.85x ROF multiplier; Cavalry Archers attack ~11% faster with 0.90x ROF multiplier), properly reflecting its combat value.

---

### 1. Overview & Dynamic Architecture

- **Dynamic Tech Ingestion**:
  - The live wiki API fetcher extracts the `{{Boosts|Technologies}}` text block for each unit.
  - The application inspects this text block to detect which blacksmith upgrade lines (Forging/Iron Casting/Blast Furnace, Fletching/Bodkin/Bracer, Scale/Chain/Plate Mail, Scale/Chain/Plate Barding, Padded/Leather/Ring Archer Armor), core technologies (Bloodlines, Thumb Ring, Parthian Tactics, Chemistry, Gambesons, Siege Engineers), and unique technologies (Kataparuto, Warwolf, Rocketry, Recurve Bow, Wootz Steel, Stirrups, Hauberk, Sipahi, El Dorado, Chatras, Comitatenses, Bogsveigar, etc.) affect the unit.
  - Units like Trebuchets will ONLY be offered technologies present in their Boosts section (e.g. Kataparuto, Warwolf, Siege Engineers, Ironclad) and will never be offered irrelevant upgrades like Fletching.
- **Tech Tree Availability Matrix**:
  - Strict mapping for each civilization that accounts for regional unit lines, unique replacements, and bans.
  - Alliance units (**Condottiero**, **Genitour**, **Imperial Skirmisher**, **Kipchak**) remain accessible to all civilizations.

---

### 2. User Experience & Visual Design

- **Left & Right Unit Configuration Columns**:
  - **Civilization Selector**: 52 civilizations (including Generic, Danes, Saxons, Varangians, Mapuche, Muisca, Tupi, Romans, Armenians, Georgians).
  - **Unit Selector**: Searchable selectbox. If a unit is unavailable for the selected civ (e.g. Hussar for Lithuanians, Cavalry Archer for Franks, Halberdier for Turks), an explicit warning appears and calculation stops.
  - **Conditional Age Selector**: Displayed *only* if unit base stats scale with Age (Scout Cavalry, Eagle Scout, Flemish Militia, Serjeant).
  - **Toggles**:
    - `Fully Upgraded (FU)`: Applies all upgrades available to the civilization for that unit based on its Boosts section.
    - `Full Tech Tree (FTT)`: Unlocks tech tree tiers beyond the civilization's usual limits (e.g. Plate Barding Armor for Malay) while preserving civilization-specific bonuses.
  - **Contextual Upgrades (When FU is unchecked)**:
    - Only renders upgrades actually listed in the unit's `boost_tech`.
    - Selectboxes display clear names with bonus values: `Fletching (+1)`, `Bodkin Arrow (+2)`, `Bracer (+3)`, `Forging (+1)`, `Scale Mail Armor (+1/+1)`, etc.
    - Thumb Ring accurately describes its combat effect: `Thumb Ring (Faster Fire Rate & Accuracy)`.
- **Simulation Outcome**:
  - Clear time-to-kill and hit count calculation.
  - Winner announcement includes civilization name in parentheses (e.g. `Pikeman (Japanese) wins 1v1`).
- **Dual Stat Cards**:
  - **Generic Base Stats**: Unmodified baseline unit attributes.
  - **Actual Combat Stats (Upgraded)**: Effective HP, effective attack, effective ROF, effective armor, and active special mechanics taken into account in the fight.

---

### 3. Key Product Decisions & Trade-Offs

- **Decision 1: Wiki Boosts Parsing with Curated Resilient Fallback**
  - *Chosen Approach*: Regex parses `{{Boosts|Technologies...}}` from live wiki data, while maintaining an offline curated boost dictionary for all 135+ units to protect against API downtime or network drops.
  - *Why*: Eliminates incorrect upgrade pairings (e.g. Fletching on Trebuchets) while ensuring offline reliability.
- **Decision 2: Accurate Thumb Ring Combat Simulation**
  - *Chosen Approach*: Thumb Ring applies standard AoE2 fire rate reduction multipliers (0.85x for Foot Archers, 0.90x for Cavalry Archers), speeding up time-to-kill.
  - *Why*: Properly reflects competitive AoE2 combat math where accuracy is already factored at close 1v1 range.
- **Decision 3: Unit Availability Whitelist & Ban Validation**
  - *Chosen Approach*: Explicitly map unique line replacements (e.g. Lithuanians and Poles only get Winged Hussar, not Hussar; Persians only get Savar, not Paladin; Romans only get Legionary, not Two-Handed/Champion).
  - *Why*: Prevents misleading or impossible matchups while honoring alliance units.

---

### 4. Technical Architecture & Data Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                     │
│  ┌───────────────────────────┐ ┌──────────────────────────┐ │
│  │     Unit 1 Configuration   │ │   Unit 2 Configuration   │ │
│  │  - Civ Dropdown (52 civs) │ │  - Civ Dropdown (52 civs)│ │
│  │  - Unit Dropdown          │ │  - Unit Dropdown         │ │
│  │  - [Conditional Age]      │ │  - [Conditional Age]     │ │
│  │  - FU / FTT Checkboxes    │ │  - FU / FTT Checkboxes   │ │
│  │  - Dynamic Upgrades from  │ │  - Dynamic Upgrades from │ │
│  │    unit's Boosts section  │ │    unit's Boosts section │ │
│  └─────────────┬─────────────┘ └────────────┬─────────────┘ │
└────────────────┼────────────────────────────┼───────────────┘
                 │                            │
                 ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Validation & Tech Tree Engine               │
│  - Strict AoE2 DE Unit Availability (Hussar / Winged Hussar)│
│  - Parse {{Boosts|Technologies}} for unit-specific techs    │
│  - Filter available techs by Civilization Tech Tree & FTT   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Combat Simulation Engine                 │
│  - Damage per hit = max(1, Atk - Armor) + Bonus             │
│  - Thumb Ring Fire-Rate Modifier (0.85x Foot / 0.90x Cav)   │
│  - Obuch Shred, Coustillier Charge, Leitis Armor Ignore     │
│  - Kataparuto / Warwolf / Rocketry / Unique Techs           │
│  - Output Winner with (Civilization) in Results             │
└─────────────────────────────────────────────────────────────┘
```

- **File Delivery**:
  - `/aoe_sl.py`: Complete plain Python script ready for GitHub and Streamlit.
  - `/requirements.txt`: Streamlit and Requests dependencies.
