# AoE2 1v1 Battle Calculator - Live Fandom Technology Extraction (Revised)

This revised implementation plan establishes a live, cached Fandom API extraction architecture where each selected unit dynamically derives its available upgrades, civilization constraints, and combat modifiers directly from the wiki's `{{Boosts|Technologies}}` block, correctly modeling technologies like **Siphons** (a general University technology available to multiple civilizations for the Fire Galley line) and civilizational unique techs.

### User Review & Critical Decisions

> [!IMPORTANT]
> The following revisions have been incorporated:
> - **Siphons as a General Naval Technology**: In modern AoE2 DE (*The Last Chieftains*), Siphons is a Castle Age University technology available across multiple civilizations (not just Byzantines) that grants Fire Galleys, Fire Ships, and Fast Fire Ships an explosive charge attack when engaging ships.
> - **Live Unit Technology Parsing via Cached Fandom API**: When a unit is selected, the application queries and caches the Fandom page, parsing each entry in `{{Boosts|Technologies}}`:
>   - The technology name from `{{2icons|<Tech Name>}}`.
>   - The specific effect description from adjacent text (e.g. `(deals an explosive charge attack every 25 seconds)`, `(+1, [[Byzantines]] only)`).
>   - Any civilization exclusivity tag (e.g. `[[Civ]] only`). If no civ is restricted, it is treated as a general technology and checked against the civ's tech tree.
> - **Strict Dynamic Filtering**: No hardcoded upgrade lists; units only receive upgrade options actually present in their live wiki `{{Boosts|Technologies}}` block.

---

### 1. Overview & Dynamic Architecture

- **Live Data & Caching Pipeline**:
  - `fetch_wiki_unit(unit_name)` queries `ageofempires.fandom.com/api.php` and caches the wiki text.
  - An intelligent extractor parses:
    1. Base combat statistics (HP, attack, ROF, melee/pierce armor, attack bonuses, armor classes).
    2. The `{{Boosts|Technologies...}}` section, identifying all valid `{{2icons|<Tech Name>}}` tags and parenthetical effects.
    3. Civilization restrictions indicated in the wiki text (e.g. `[[Britons]] only`, `[[Byzantines]] only`).
- **Contextual Upgrade UI**:
  - Only upgrades verified to boost the selected unit will be rendered in the UI.
  - General upgrades (such as Siphons, Careening, Dry Dock, Forging, Blast Furnace, Bloodlines, Thumb Ring) are presented to any civilization that has access in their tech tree.
  - Unique upgrades with civilization tags are shown only if the chosen civilization matches or if *Full Tech Tree (FTT)* is enabled.

---

### 2. User Experience & Visual Design

- **Unit Configuration Flow**:
  - **Unit Selection**: Changing a unit instantly loads its live wiki profile (cached for seamless re-render).
  - **Dynamic Upgrade Selectors & Toggles**:
    - Blacksmith Attack & Armor tiers (only shown if listed in unit's Boosts).
    - University / Dock technologies (Siphons, Careening, Dry Dock, Chemistry, Siege Engineers).
    - Unique Technologies (Greek Fire, Kataparuto, Warwolf, Rocketry, Recurve Bow, etc.) shown when applicable.
  - **Accurate Labels**: Each toggle displays its name and parsed wiki effect string.
- **Combat Simulation & Outcome**:
  - Charge / Burst Attacks: Models first-hit burst damage for Coustillier, Urumi, Siphons (Fire Ships), and Roman Comitatenses.
  - Fire Rate: Applies exact ROF reductions for Thumb Ring, Kataparuto, Japanese infantry, Saracen galleys, and Byzantine fire ships.
  - Winner announcement includes civilization in parentheses (e.g. `Pikeman (Japanese) wins 1v1`).

---

### 3. Key Product Decisions & Trade-Offs

- **Decision 1: Dynamic Tech Availability Resolution**
  - *Chosen Approach*: Intersect the technologies parsed from `{{Boosts|Technologies}}` with the chosen civilization's tech capabilities. If a tech is general (like Siphons), check if the civilization has access (defaulting to accessible unless specifically banned).
  - *Why*: Perfectly handles general technologies introduced in new DLCs without manual code edits.
- **Decision 2: Live Wiki Parsing with Resilient In-Memory Fallback**
  - *Chosen Approach*: Parse directly from live Fandom API responses, backed by offline fallback entries to prevent crashes in disconnected or latency-constrained environments.
  - *Why*: Future-proofs the application for upcoming balance patches while maintaining zero downtime.

---

### 4. Technical Architecture & Data Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                      Streamlit Frontend                     │
│  ┌───────────────────────────┐ ┌──────────────────────────┐ │
│  │     Unit 1 Configuration   │ │   Unit 2 Configuration   │ │
│  │  - Civ Dropdown           │ │  - Civ Dropdown          │ │
│  │  - Unit Dropdown          │ │  - Unit Dropdown         │ │
│  │  - Live Boosts Toggles    │ │  - Live Boosts Toggles   │ │
│  │    (Siphons, Careening...)│ │    (Siphons, Careening...)│ │
│  └─────────────┬─────────────┘ └────────────┬─────────────┘ │
└────────────────┼────────────────────────────┼───────────────┘
                 │                            │
                 ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Live Fandom Extraction Engine               │
│  - Query MediaWiki API (cached per unit)                    │
│  - Extract {{Boosts|Technologies}} text block               │
│  - Regex extract {{2icons|<Tech>}} + (parsed effect text)   │
│  - Detect civ exclusivity [[Civ only]] vs general techs     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Combat Simulation Engine                 │
│  - First-hit charge bursts (Coustillier, Siphons, Urumi)    │
│  - Accurate Rate of Fire multipliers (Thumb Ring, Kataparuto│
│  - Output Winner with (Civilization) in Results             │
└─────────────────────────────────────────────────────────────┘
```

- **File Delivery**:
  - `/aoe_sl.py`: Complete plain Python script ready for GitHub and Streamlit.
  - `/requirements.txt`: Python dependencies (`streamlit`, `requests`).
