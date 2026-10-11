# AoE2 1v1 Battle Calculator - Complete Streamlit Specification (Patch 185872 & All DLCs)

This revised implementation plan establishes the architecture and complete tech tree data for `aoe_sl.py` based on **Age of Empires II: Definitive Edition Patch 185872**, including all multiplayer expansions: **The Viking Sagas** (Danes, Saxons, Varangians), **The Last Chieftains** (Mapuche, Muisca, Tupi), **The Mountain Royals** (Armenians, Georgians), **Return of Rome** (Romans), **Dynasties of India**, **Dawn of the Dukes**, and **Lords of the West**.

### User Review & Critical Decisions

> [!IMPORTANT]
> The following revisions have been incorporated:
> - **Patch 185872 & Full DLC Coverage**: Complete integration of all 51+ multiplayer civilizations, including the 3 civilizations from *The Viking Sagas* (**Danes**, **Saxons**, **Varangians**) and the 3 from *The Last Chieftains* (**Mapuche**, **Muisca**, **Tupi**), alongside Romans, Armenians, Georgians, etc.
> - **New Units & Regional Reworks**: Incorporates new patch units including **Varangian Guard**, **Mounted Crossbowman**, **Jomsviking**, **Hearth Troop**, **Bolas Rider**, **Kona**, **Guecha Warrior**, and **Ibirapema Warrior**.
> - **Unit Availability Gate**: Enforces exact civilization availability (e.g., Turks cannot select Halberdier, Mayans cannot select Knight) while keeping alliance units (**Condottiero**, **Genitour**, **Imperial Skirmisher**, **Kipchak**) accessible to all civilizations.
> - **Conditional Age Inputs**: Age selector only renders for units whose base stats scale by Age (**Scout Cavalry**, **Eagle Scout**, **Flemish Militia**, **Serjeant**).
> - **Granular Blacksmith Upgrades & Unique Techs**: Full interactive upgrade selectors for each unit class, overridden when *Fully Upgraded* is selected.
> - **Full Tech Tree (FTT) Override**: Allows selecting upgrades normally unavailable to a civilization (e.g. Plate Barding Armor on Malay) while retaining civilization bonuses.
> - **Deliverable Delivery**: Pure Python file (`/aoe_sl.py`) formatted for direct deployment in Streamlit with `requirements.txt`.

---

### 1. Overview & Comprehensive Civilization Roster

- **Complete Civilization Roster (52 Options)**:
  - *Generic* (Benchmark civ with full tech tree access)
  - *Base Game & Kings*: Britons, Byzantines, Celts, Chinese, Franks, Goths, Japanese, Mongols, Persians, Saracens, Teutons, Turks, Vikings (with Patch 185872 rework)
  - *The Conquerors*: Aztecs, Huns, Koreans, Mayans, Spanish
  - *The Forgotten*: Incas, Indians (Hindustanis), Italians, Magyars, Slavs
  - *The African Kingdoms*: Berbers, Ethiopians, Malians, Portuguese
  - *Rise of the Rajas*: Burmese, Khmer, Malay, Vietnamese
  - *Definitive Edition*: Bulgarians, Cumans, Lithuanians, Tatars
  - *Lords of the West*: Burgundians, Sicilians
  - *Dawn of the Dukes*: Bohemians, Poles
  - *Dynasties of India*: Bengalis, Dravidians, Gurjaras, Hindustanis
  - *Return of Rome*: Romans
  - *The Mountain Royals*: Armenians, Georgians
  - *The Last Chieftains*: Mapuche, Muisca, Tupi
  - *The Viking Sagas (Patch 185872)*: Danes, Saxons, Varangians

---

### 2. User Experience & Visual Design

- **Layout Structure**:
  - **Header**: Clean title and brief description of Patch 185872 calculator capabilities.
  - **Two-Column Setup (`Unit 1` vs `Unit 2`)**:
    - **Civilization Selector**: Dropdown containing all 52 civilizations.
    - **Unit Selector**: Searchable selectbox with all standard, regional, and unique units.
    - **Availability Warning**: If the selected civilization lacks access to the unit, an explicit alert displays (`"{civ} does not get access to {unit}"`) and the simulation halts. Alliance units (Condottiero, Genitour, Imperial Skirmisher, Kipchak) remain valid for all civilizations.
    - **Conditional Age Selector**: Appears *only* if the selected unit is Scout Cavalry, Eagle Scout, Flemish Militia, or Serjeant.
    - **Elite Toggle**: Checkbox appears only for units with Elite upgrades.
    - **Toggles**:
      - `Fully Upgraded (FU)`: Overrides manual upgrade pickers and applies all tech tree upgrades available to the civilization.
      - `Full Tech Tree (FTT)`: Unlocks upgrades unavailable to that civilization without stripping civilization-specific bonuses.
    - **Granular Upgrade Pickers (Visible when FU is unchecked)**:
      - Attack Upgrades (Forging, Iron Casting, Blast Furnace / Fletching, Bodkin Arrow, Bracer).
      - Armor Upgrades (Scale/Chain/Plate Mail, Barding Armor, Padded/Leather/Ring Archer Armor).
      - Core Technologies (Bloodlines, Thumb Ring, Parthian Tactics, Chemistry, Gambesons).
      - Relevant Unique Techs (e.g. Magyars Recurve Bow, Chinese Rocketry, Britons Yeomen, Dravidians Wootz Steel, Danes/Saxons/Varangians unique techs).
  - **Simulation Outcome**:
    - Number of hits to kill for each unit.
    - Time-to-kill in seconds (accounting for ROF and reload frames).
    - Battle winner or uncontested victory if one unit has no attack (e.g. Monk vs Knight, Villager vs Spearman).
    - Full unit property breakdown cards.

---

### 3. Key Product Decisions & Trade-Offs

- **Decision 1: Patch 185872 Mechanics & Unit Pool Expansion**
  - *Chosen Approach*: Embed the complete unit and tech matrix reflecting Patch 185872, including Varangian Guard, Mounted Crossbowman, Hearth Troop, Jomsviking, Kona, Bolas Rider, Guecha Warrior, and Ibirapema Warrior.
  - *Why*: Ensures total fidelity to modern competitive AoE2 DE multiplayer balance.
- **Decision 2: Strict Availability Matrix with Alliance Exceptions**
  - *Chosen Approach*: An explicit lookup dictionary defining unit bans and regional allowances per civilization, while whitelisting Condottiero, Genitour, Imperial Skirmisher, and Kipchak for all civilizations.
  - *Why*: Matches exact game rules while providing immediate feedback when an illegal pairing is chosen.
- **Decision 3: Dynamic Tech Availability & FTT Independence**
  - *Chosen Approach*: Upgrades shown respect the civilization's historical limitations when FTT is disabled. When FTT is enabled, all upgrade maximums expand, but civilization bonuses (e.g. Frank cavalry HP, Viking infantry HP, Burmese attack, Romans double armor) remain fully active.
  - *Why*: Fulfills the exact user example (Malay with FTT retaining civ bonuses while gaining Plate Barding Armor).
- **Decision 4: Live Wiki API Grounding with Defensive Fallbacks**
  - *Chosen Approach*: Live query to `ageofempires.fandom.com/api.php` for base unit stat lines and regex extraction, paired with verified in-memory fallback stats for every Patch 185872 unit in case of offline runs or API latency.

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
│  │  - Dynamic Upgrades       │ │  - Dynamic Upgrades      │ │
│  │  - Relevant Unique Techs  │ │  - Relevant Unique Techs │ │
│  └─────────────┬─────────────┘ └────────────┬─────────────┘ │
└────────────────┼────────────────────────────┼───────────────┘
                 │                            │
                 ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Validation & Tech Tree Engine               │
│  - Check Civ Unit Availability (with Alliance Exceptions)   │
│  - Patch 185872 Civilization Tech Tree Rules                │
│  - Derive Available Techs (Civ Caps vs. FTT Override)       │
│  - Live Wiki API Fetch & Regex Parsing                      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Combat Simulation Engine                 │
│  - Damage = max(1, Atk - Armor) + Bonus Damage              │
│  - Unique Mechanics (Obuch shred, Coustillier charge, etc.) │
│  - Special Civ Modifiers (Sicilians -33%, Romans 2x armor)  │
│  - Non-Attacking Unit Resolution (Time-to-Kill Display)     │
└─────────────────────────────────────────────────────────────┘
```

- **File Delivery**:
  - `/aoe_sl.py`: The single, complete, copy-paste-ready Python file for Streamlit.
  - `/requirements.txt`: Python package requirements (`streamlit`, `requests`).
