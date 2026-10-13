export interface CivBonus {
  hpPercent?: number; // e.g. +20% HP (Franks knights, Vietnamese archers, Vikings infantry)
  hpFlat?: number; // e.g. +20 HP (Turks cavalry archers Sipahi)
  attackFlat?: number; // e.g. +1/+2/+3 for Burmese infantry
  attackPercent?: number;
  rofMultiplier?: number; // e.g. 0.8 for Mongols cav archers (fire 25% faster)
  meleeArmorFlat?: number; // e.g. +1/+2 for Teutons barracks/stable
  pierceArmorFlat?: number; // e.g. +1/+2/+3 for Malians infantry
  bonusDamageReduction?: number; // e.g. 0.33 for Sicilians (take 33% less bonus damage)
  attackVsBuildings?: number;
  ignoreArmor?: boolean; // Wootz Steel
}

export interface UniqueTech {
  id: string;
  name: string;
  age: 'Castle' | 'Imperial';
  appliesTo: (unitName: string, civName: string) => boolean;
  effectDescription: string;
  apply: (stats: {
    attack: number;
    armor: number;
    pierceArmor: number;
    hp: number;
    rof: number;
    bonusDmg: Record<string, number>;
    ignoresArmor: boolean;
  }) => void;
}

export interface CivData {
  name: string;
  uniqueUnits: string[];
  teamBonusUnits?: string[];
  disabledUnits: string[]; // standard units not in tech tree
  // Max available blacksmith upgrades:
  maxMeleeAttack: number; // 0=None, 1=Forging, 2=Iron Casting, 3=Blast Furnace
  maxRangedAttack: number; // 0=None, 1=Fletching, 2=Bodkin, 3=Bracer
  maxArcherArmor: number; // 0=None, 1=Padded, 2=Leather, 3=Ring
  maxCavalryArmor: number; // 0=None, 1=Scale, 2=Chain, 3=Plate
  maxInfantryArmor: number; // 0=None, 1=Scale, 2=Chain, 3=Plate
  hasBloodlines: boolean;
  hasThumbRing: boolean;
  hasParthianTactics: boolean;
  hasChemistry: boolean;
  hasGambesons: boolean;
  uniqueTechs: UniqueTech[];
  getCivBonuses: (unitName: string, age: number) => CivBonus | null;
}

import { CIV_UNIT_MAP } from './civUnitsData';

// Dynamic cache for tech tree map fetched directly from /civ_units_techtree.json
let liveCivUnitMap: Record<string, string[]> = { ...CIV_UNIT_MAP };

// Asynchronously fetch and refresh the complete JSON map directly from trusted source
if (typeof window !== 'undefined') {
  fetch('/civ_units_techtree.json')
    .then((res) => {
      if (res.ok) return res.json();
      throw new Error(`Failed to fetch civ_units_techtree.json: ${res.statusText}`);
    })
    .then((data: Record<string, string[]>) => {
      if (data && typeof data === 'object') {
        liveCivUnitMap = { ...CIV_UNIT_MAP, ...data };
        // Ensure Generic has access to all units
        const allUnits = new Set<string>();
        Object.values(liveCivUnitMap).forEach((list) => {
          if (Array.isArray(list)) list.forEach((u) => allUnits.add(u));
        });
        liveCivUnitMap['Generic'] = Array.from(allUnits);
      }
    })
    .catch((err) => {
      console.warn('Could not refresh liveCivUnitMap, falling back to embedded trusted CIV_UNIT_MAP:', err);
    });
}

// Team units available to EVERY civ through allied bonuses:
export const ALL_CIV_TEAM_UNITS = [
  'Condottiero',
  'Genitour',
  'Elite Genitour',
  'Imperial Skirmisher',
  'Kipchak',
  'Elite Kipchak',
];

export function unitStatsDependOnAge(unitName: string): boolean {
  const norm = unitName.toLowerCase();
  return (
    norm.includes('scout cavalry') ||
    norm.includes('eagle scout') ||
    norm.includes('flemish militia') ||
    norm.includes('serjeant')
  );
}

export const CIVILIZATIONS: Record<string, CivData> = {
  Generic: {
    name: 'Generic',
    uniqueUnits: [],
    disabledUnits: [],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Armenians: {
    name: 'Armenians',
    uniqueUnits: ['Composite Bowman'],
    disabledUnits: ['Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Imperial Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'fereters',
        name: 'Fereters',
        age: 'Castle',
        appliesTo: (u) => isInfantry(u),
        effectDescription: 'Infantry units gain +30 HP.',
        apply: (s) => {
          s.hp += 30;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Aztecs: {
    name: 'Aztecs',
    uniqueUnits: ['Jaguar Warrior'],
    disabledUnits: [
      'Scout Cavalry', 'Light Cavalry', 'Hussar', 'Winged Hussar',
      'Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider',
      'Imperial Camel Rider', 'Steppe Lancer', 'Elite Steppe Lancer',
      'Battle Elephant', 'Elite Battle Elephant'
    ],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 0,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: false,
    uniqueTechs: [
      {
        id: 'garland_wars',
        name: 'Garland Wars',
        age: 'Imperial',
        appliesTo: (u) => isInfantry(u),
        effectDescription: 'Infantry units gain +4 attack.',
        apply: (s) => {
          s.attack += 4;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Bengalis: {
    name: 'Bengalis',
    uniqueUnits: ['Ratha'],
    disabledUnits: ['Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'paiks',
        name: 'Paiks',
        age: 'Castle',
        appliesTo: (u) => u.toLowerCase().includes('ratha') || isElephant(u),
        effectDescription: 'Rathas and Elephants attack 20% faster.',
        apply: (s) => {
          s.rof *= 0.833;
        },
      },
    ],
    getCivBonuses: (u) => {
      if (isElephant(u)) {
        return { bonusDamageReduction: 0.25 };
      }
      return null;
    },
  },

  Berbers: {
    name: 'Berbers',
    uniqueUnits: ['Camel Archer', 'Genitour'],
    disabledUnits: ['Paladin', 'Arbalester', 'Halberdier'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: false,
    uniqueTechs: [
      {
        id: 'maghrebi_camels',
        name: 'Maghrebi Camels',
        age: 'Imperial',
        appliesTo: (u) => isCamel(u) || u.toLowerCase().includes('genitour'),
        effectDescription: 'Camel units and Genitours regenerate HP.',
        apply: () => {},
      },
    ],
    getCivBonuses: () => null,
  },

  Bohemians: {
    name: 'Bohemians',
    uniqueUnits: ['Hussite Wagon', 'Houfnice'],
    disabledUnits: ['Paladin', 'Hussar', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 2,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'wagenburg_tactics',
        name: 'Wagenburg Tactics',
        age: 'Castle',
        appliesTo: (u) => isGunpowder(u),
        effectDescription: 'Gunpowder units move 15% faster.',
        apply: () => {},
      },
    ],
    getCivBonuses: (u) => {
      if (isSpearman(u)) {
        return { attackPercent: 0.25 };
      }
      return null;
    },
  },

  Britons: {
    name: 'Britons',
    uniqueUnits: ['Longbowman'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'yeomen',
        name: 'Yeomen',
        age: 'Castle',
        appliesTo: (u) => isFootArcher(u),
        effectDescription: 'Foot archers gain +1 range and +2 tower attack.',
        apply: () => {},
      },
    ],
    getCivBonuses: () => null,
  },

  Bulgarians: {
    name: 'Bulgarians',
    uniqueUnits: ['Konnik'],
    disabledUnits: ['Paladin', 'Crossbowman', 'Arbalester', 'Hand Cannoneer', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 2,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'stirrups',
        name: 'Stirrups',
        age: 'Castle',
        appliesTo: (u) => isCavalry(u) || u.toLowerCase().includes('konnik'),
        effectDescription: 'Cavalry and Konniks attack 33% faster.',
        apply: (s) => {
          s.rof *= 0.75;
        },
      },
      {
        id: 'bagains',
        name: 'Bagains',
        age: 'Imperial',
        appliesTo: (u) => isMilitiaLine(u),
        effectDescription: 'Militia-line units gain +5 melee armor.',
        apply: (s) => {
          s.armor += 5;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Burgundians: {
    name: 'Burgundians',
    uniqueUnits: ['Coustillier', 'Flemish Militia'],
    disabledUnits: ['Camel Rider', 'Heavy Camel Rider', 'Arbalester'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 2,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Burmese: {
    name: 'Burmese',
    uniqueUnits: ['Arambai'],
    disabledUnits: ['Paladin', 'Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 1,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'howdah',
        name: 'Howdah',
        age: 'Castle',
        appliesTo: (u) => isElephant(u),
        effectDescription: 'Battle Elephants gain +1/+1 armor.',
        apply: (s) => {
          s.armor += 1;
          s.pierceArmor += 1;
        },
      },
      {
        id: 'manipur_cavalry',
        name: 'Manipur Cavalry',
        age: 'Imperial',
        appliesTo: (u) => isCavalry(u) || u.toLowerCase().includes('arambai'),
        effectDescription: 'Cavalry and Arambai gain +4 attack against archers.',
        apply: (s) => {
          s.bonusDmg['Archers'] = (s.bonusDmg['Archers'] || 0) + 4;
        },
      },
    ],
    getCivBonuses: (u, age) => {
      if (isInfantry(u)) {
        const atk = age === 2 ? 1 : age === 3 ? 2 : 3;
        return { attackFlat: atk };
      }
      return null;
    },
  },

  Byzantines: {
    name: 'Byzantines',
    uniqueUnits: ['Cataphract'],
    disabledUnits: ['Heavy Scorpion'],
    maxMeleeAttack: 2,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'logistica',
        name: 'Logistica',
        age: 'Imperial',
        appliesTo: (u) => u.toLowerCase().includes('cataphract'),
        effectDescription: 'Cataphracts cause trample damage and gain +6 attack vs infantry.',
        apply: (s) => {
          s.bonusDmg['Infantry'] = (s.bonusDmg['Infantry'] || 0) + 6;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Celts: {
    name: 'Celts',
    uniqueUnits: ['Woad Raider'],
    disabledUnits: ['Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 2,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Chinese: {
    name: 'Chinese',
    uniqueUnits: ['Chu Ko Nu'],
    disabledUnits: ['Paladin', 'Hussar', 'Hand Cannoneer'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'rocketry',
        name: 'Rocketry',
        age: 'Imperial',
        appliesTo: (u) => u.toLowerCase().includes('chu ko nu'),
        effectDescription: 'Chu Ko Nu gain +2 pierce attack.',
        apply: (s) => {
          s.attack += 2;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Cumans: {
    name: 'Cumans',
    uniqueUnits: ['Kipchak'],
    disabledUnits: ['Arbalester', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Dravidians: {
    name: 'Dravidians',
    uniqueUnits: ['Urumi Swordsman'],
    disabledUnits: ['Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 0,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'wootz_steel',
        name: 'Wootz Steel',
        age: 'Imperial',
        appliesTo: (u) => isInfantry(u) || isCavalry(u),
        effectDescription: 'Infantry and cavalry attacks ignore target armor completely.',
        apply: (s) => {
          s.ignoresArmor = true;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Ethiopians: {
    name: 'Ethiopians',
    uniqueUnits: ['Shotel Warrior'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: (u) => {
      if (isFootArcher(u)) {
        return { rofMultiplier: 0.847 };
      }
      return null;
    },
  },

  Franks: {
    name: 'Franks',
    uniqueUnits: ['Throwing Axeman'],
    disabledUnits: ['Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 2,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: (u) => {
      if (isCavalry(u)) {
        return { hpPercent: 0.2 };
      }
      return null;
    },
  },

  Georgians: {
    name: 'Georgians',
    uniqueUnits: ['Monaspa'],
    disabledUnits: ['Paladin', 'Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Goths: {
    name: 'Goths',
    uniqueUnits: ['Huskarl'],
    disabledUnits: ['Paladin', 'Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Gurjaras: {
    name: 'Gurjaras',
    uniqueUnits: ['Shrivamsha Rider', 'Chakram Thrower'],
    disabledUnits: ['Knight', 'Cavalier', 'Paladin', 'Arbalester', 'Pikeman', 'Halberdier'],
    maxMeleeAttack: 2,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'frontier_guards',
        name: 'Frontier Guards',
        age: 'Imperial',
        appliesTo: (u) => isCamel(u) || isElephant(u),
        effectDescription: 'Camels and Elephants gain +4 melee armor.',
        apply: (s) => {
          s.armor += 4;
        },
      },
    ],
    getCivBonuses: (u) => {
      if (isCamel(u)) {
        return { attackPercent: 0.5 };
      }
      return null;
    },
  },

  Hindustanis: {
    name: 'Hindustanis',
    uniqueUnits: ['Ghulam', 'Imperial Camel Rider'],
    disabledUnits: ['Knight', 'Cavalier', 'Paladin', 'Arbalester'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: (u) => {
      if (isCamel(u)) {
        return { rofMultiplier: 0.833 };
      }
      return null;
    },
  },

  Huns: {
    name: 'Huns',
    uniqueUnits: ['Tarkan'],
    disabledUnits: ['Arbalester', 'Champion', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: false,
    uniqueTechs: [
      {
        id: 'recurve_bow',
        name: 'Recurve Bow',
        age: 'Imperial',
        appliesTo: (u) => isCavArcher(u),
        effectDescription: 'Cavalry Archers gain +1 attack and +1 range.',
        apply: (s) => {
          s.attack += 1;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Incas: {
    name: 'Incas',
    uniqueUnits: ['Kamayuk', 'Slinger'],
    disabledUnits: [
      'Scout Cavalry', 'Light Cavalry', 'Hussar', 'Winged Hussar',
      'Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider',
      'Battle Elephant', 'Steppe Lancer'
    ],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 0,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'fabric_shields',
        name: 'Fabric Shields',
        age: 'Imperial',
        appliesTo: (u) =>
          u.toLowerCase().includes('kamayuk') ||
          u.toLowerCase().includes('slinger') ||
          u.toLowerCase().includes('eagle'),
        effectDescription: 'Kamayuks, Slingers, and Eagles gain +1/+2 armor.',
        apply: (s) => {
          s.armor += 1;
          s.pierceArmor += 2;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Italians: {
    name: 'Italians',
    uniqueUnits: ['Genoese Crossbowman', 'Condottiero'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Halberdier'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'pavise',
        name: 'Pavise',
        age: 'Castle',
        appliesTo: (u) => isFootArcher(u) || u.toLowerCase().includes('condottiero'),
        effectDescription: 'Foot Archers and Condottieri gain +1/+1 armor.',
        apply: (s) => {
          s.armor += 1;
          s.pierceArmor += 1;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Japanese: {
    name: 'Japanese',
    uniqueUnits: ['Samurai'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: (u) => {
      if (isInfantry(u)) {
        return { rofMultiplier: 0.75 };
      }
      return null;
    },
  },

  Khmer: {
    name: 'Khmer',
    uniqueUnits: ['Ballista Elephant'],
    disabledUnits: ['Paladin', 'Champion', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: false,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Koreans: {
    name: 'Koreans',
    uniqueUnits: ['War Wagon', 'Turtle Ship'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 2,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Lithuanians: {
    name: 'Lithuanians',
    uniqueUnits: ['Leitis', 'Winged Hussar'],
    disabledUnits: ['Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 2,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'tower_shields',
        name: 'Tower Shields',
        age: 'Imperial',
        appliesTo: (u) => isSpearman(u) || isSkirmisher(u),
        effectDescription: 'Spearmen and Skirmishers gain +2 pierce armor.',
        apply: (s) => {
          s.pierceArmor += 2;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Magyars: {
    name: 'Magyars',
    uniqueUnits: ['Magyar Huszar'],
    disabledUnits: ['Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: false,
    uniqueTechs: [
      {
        id: 'magyar_recurve_bow',
        name: 'Recurve Bow',
        age: 'Imperial',
        appliesTo: (u) => isCavArcher(u),
        effectDescription: 'Cavalry Archers gain +1 range and +1 attack.',
        apply: (s) => {
          s.attack += 1;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Malay: {
    name: 'Malay',
    uniqueUnits: ['Karambit Warrior'],
    disabledUnits: ['Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 0,
    maxInfantryArmor: 2,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Malians: {
    name: 'Malians',
    uniqueUnits: ['Gbeto'],
    disabledUnits: ['Paladin', 'Hussar', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 2,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'farimba',
        name: 'Farimba',
        age: 'Imperial',
        appliesTo: (u) => isCavalry(u),
        effectDescription: 'Cavalry gains +5 attack.',
        apply: (s) => {
          s.attack += 5;
        },
      },
    ],
    getCivBonuses: (u, age) => {
      if (isInfantry(u)) {
        const pArmor = age === 2 ? 1 : age === 3 ? 2 : 3;
        return { pierceArmorFlat: pArmor };
      }
      return null;
    },
  },

  Mayans: {
    name: 'Mayans',
    uniqueUnits: ['Plumed Archer'],
    disabledUnits: [
      'Scout Cavalry', 'Light Cavalry', 'Hussar', 'Winged Hussar',
      'Knight', 'Cavalier', 'Paladin', 'Camel Rider', 'Heavy Camel Rider',
      'Battle Elephant', 'Steppe Lancer'
    ],
    maxMeleeAttack: 2,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 0,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'el_dorado',
        name: 'El Dorado',
        age: 'Imperial',
        appliesTo: (u) => u.toLowerCase().includes('eagle'),
        effectDescription: 'Eagle Warriors gain +40 HP.',
        apply: (s) => {
          s.hp += 40;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Mongols: {
    name: 'Mongols',
    uniqueUnits: ['Mangudai'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 2,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: (u) => {
      if (isCavArcher(u)) {
        return { rofMultiplier: 0.8 };
      }
      return null;
    },
  },

  Persians: {
    name: 'Persians',
    uniqueUnits: ['War Elephant', 'Savar'],
    disabledUnits: ['Arbalester', 'Paladin'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Poles: {
    name: 'Poles',
    uniqueUnits: ['Obuch', 'Winged Hussar'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 2,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Portuguese: {
    name: 'Portuguese',
    uniqueUnits: ['Organ Gun'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [],
    getCivBonuses: () => null,
  },

  Romans: {
    name: 'Romans',
    uniqueUnits: ['Legionary', 'Centurion'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Steppe Lancer', 'Hand Cannoneer', 'Bombard Cannon', 'Two-Handed Swordsman', 'Champion'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: true,
    hasChemistry: false,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'comitatenses',
        name: 'Comitatenses',
        age: 'Imperial',
        appliesTo: (u) =>
          u.toLowerCase().includes('legionary') ||
          u.toLowerCase().includes('centurion') ||
          u.toLowerCase().includes('knight'),
        effectDescription: 'Legionaries, Centurions, and Knights gain +5 charge attack.',
        apply: (s) => {
          s.attack += 5;
        },
      },
    ],
    getCivBonuses: (u) => {
      if (isMilitiaLine(u) || u.toLowerCase().includes('legionary')) {
        return { meleeArmorFlat: 1, pierceArmorFlat: 1 };
      }
      return null;
    },
  },

  Saracens: {
    name: 'Saracens',
    uniqueUnits: ['Mameluke'],
    disabledUnits: ['Paladin', 'Halberdier'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'zealotry',
        name: 'Zealotry',
        age: 'Imperial',
        appliesTo: (u) => isCamel(u) || u.toLowerCase().includes('mameluke'),
        effectDescription: 'Camels and Mamelukes gain +20 HP.',
        apply: (s) => {
          s.hp += 20;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Sicilians: {
    name: 'Sicilians',
    uniqueUnits: ['Serjeant'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 2,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'hauberk',
        name: 'Hauberk',
        age: 'Imperial',
        appliesTo: (u) => isKnightLine(u),
        effectDescription: 'Knights line gains +1/+2 armor.',
        apply: (s) => {
          s.armor += 1;
          s.pierceArmor += 2;
        },
      },
    ],
    getCivBonuses: () => {
      return { bonusDamageReduction: 0.33 };
    },
  },

  Slavs: {
    name: 'Slavs',
    uniqueUnits: ['Boyar'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'druzhina',
        name: 'Druzhina',
        age: 'Imperial',
        appliesTo: (u) => isInfantry(u),
        effectDescription: 'Infantry units gain trample damage (+2 base attack).',
        apply: (s) => {
          s.attack += 2;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Spanish: {
    name: 'Spanish',
    uniqueUnits: ['Conquistador', 'Missionary'],
    disabledUnits: ['Crossbowman', 'Arbalester', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'supremacy',
        name: 'Supremacy',
        age: 'Imperial',
        appliesTo: (u) => u.toLowerCase().includes('villager'),
        effectDescription: 'Villagers gain +40 HP, +6 attack, and +2/+2 armor.',
        apply: (s) => {
          s.hp += 40;
          s.attack += 6;
          s.armor += 2;
          s.pierceArmor += 2;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Tatars: {
    name: 'Tatars',
    uniqueUnits: ['Keshik'],
    disabledUnits: ['Arbalester', 'Paladin', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 2,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: false,
    uniqueTechs: [
      {
        id: 'silk_armor',
        name: 'Silk Armor',
        age: 'Castle',
        appliesTo: (u) => isCavArcher(u) || isScoutLine(u) || u.toLowerCase().includes('steppe lancer'),
        effectDescription: 'Cavalry Archers, Steppe Lancers, and Scout line gain +1/+1 armor.',
        apply: (s) => {
          s.armor += 1;
          s.pierceArmor += 1;
        },
      },
    ],
    getCivBonuses: () => null,
  },

  Teutons: {
    name: 'Teutons',
    uniqueUnits: ['Teutonic Knight'],
    disabledUnits: ['Light Cavalry', 'Hussar', 'Camel Rider', 'Heavy Camel Rider'],
    maxMeleeAttack: 3,
    maxRangedAttack: 2,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'ironclad',
        name: 'Ironclad',
        age: 'Castle',
        appliesTo: (u) => isSiege(u),
        effectDescription: 'Siege weapons gain +4 melee armor.',
        apply: (s) => {
          s.armor += 4;
        },
      },
    ],
    getCivBonuses: (u, age) => {
      if (isBarracksUnit(u) || isStableUnit(u)) {
        const armor = age >= 4 ? 2 : age === 3 ? 1 : 0;
        return { meleeArmorFlat: armor };
      }
      return null;
    },
  },

  Turks: {
    name: 'Turks',
    uniqueUnits: ['Janissary'],
    disabledUnits: ['Arbalester', 'Elite Skirmisher', 'Pikeman', 'Halberdier', 'Paladin'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: true,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'sipahi',
        name: 'Sipahi',
        age: 'Castle',
        appliesTo: (u) => isCavArcher(u),
        effectDescription: 'Cavalry Archers gain +20 HP.',
        apply: (s) => {
          s.hp += 20;
        },
      },
    ],
    getCivBonuses: (u) => {
      if (isGunpowder(u)) {
        return { hpPercent: 0.25 };
      }
      return null;
    },
  },

  Vietnamese: {
    name: 'Vietnamese',
    uniqueUnits: ['Rattan Archer', 'Imperial Skirmisher'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 2,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 3,
    maxInfantryArmor: 3,
    hasBloodlines: true,
    hasThumbRing: true,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'chatras',
        name: 'Chatras',
        age: 'Castle',
        appliesTo: (u) => isElephant(u),
        effectDescription: 'Battle Elephants gain +100 HP.',
        apply: (s) => {
          s.hp += 100;
        },
      },
    ],
    getCivBonuses: (u) => {
      if (isArcheryRangeUnit(u)) {
        return { hpPercent: 0.2 };
      }
      return null;
    },
  },

  Vikings: {
    name: 'Vikings',
    uniqueUnits: ['Berserk'],
    disabledUnits: ['Paladin', 'Camel Rider', 'Heavy Camel Rider', 'Hussar'],
    maxMeleeAttack: 3,
    maxRangedAttack: 3,
    maxArcherArmor: 3,
    maxCavalryArmor: 2,
    maxInfantryArmor: 3,
    hasBloodlines: false,
    hasThumbRing: false,
    hasParthianTactics: false,
    hasChemistry: true,
    hasGambesons: true,
    uniqueTechs: [
      {
        id: 'bogsveigar',
        name: 'Bogsveigar',
        age: 'Imperial',
        appliesTo: (u) => isFootArcher(u),
        effectDescription: 'Archers gain +1 attack.',
        apply: (s) => {
          s.attack += 1;
        },
      },
    ],
    getCivBonuses: (u) => {
      if (isInfantry(u)) {
        return { hpPercent: 0.2 };
      }
      return null;
    },
  },
};

export const CIV_NAMES: string[] = Object.keys(CIVILIZATIONS);

// Helpers
export function isUnitAvailableForCiv(unitName: string, civName: string): boolean {
  if (!unitName || !civName) return true;
  if (civName === 'Generic') return true;

  // 1. Team units available to all civs through allied bonuses:
  if (ALL_CIV_TEAM_UNITS.some((tu) => tu.toLowerCase() === unitName.toLowerCase())) {
    return true;
  }

  // Normalize names for comparison
  const normUnit = unitName
    .replace(/^Elite\s+/i, '')
    .replace(/\s*\(Packed\)$/i, '')
    .trim()
    .toLowerCase();

  // 2. Query trusted JSON map from SiegeEngineers tech tree:
  const mapToUse = liveCivUnitMap || CIV_UNIT_MAP;
  if (mapToUse) {
    // Find matching civilization key (case-insensitive)
    const civKey = Object.keys(mapToUse).find((k) => k.toLowerCase() === civName.toLowerCase());
    if (civKey && Array.isArray(mapToUse[civKey])) {
      const allowedUnits = mapToUse[civKey];
      const isAllowedInTree = allowedUnits.some((u) => {
        const normAllowed = u
          .replace(/^Elite\s+/i, '')
          .replace(/\s*\(Packed\)$/i, '')
          .trim()
          .toLowerCase();
        return normAllowed === normUnit || u.toLowerCase() === unitName.toLowerCase();
      });

      // If civilization is found in the trusted tech tree map, this authoritative result decides!
      return isAllowedInTree;
    }
  }

  // 3. Fallback to CIVILIZATIONS database if civilization is not present in external map
  const civ = CIVILIZATIONS[civName];
  if (!civ) return true;

  // Check unique units: if unit is a unique unit of another civ, not available
  for (const [otherCivName, otherCiv] of Object.entries(CIVILIZATIONS)) {
    if (otherCivName !== civName && otherCivName !== 'Generic') {
      if (otherCiv.uniqueUnits.some((uu) => uu.toLowerCase() === unitName.toLowerCase())) {
        return false;
      }
    }
  }

  // Check disabled units
  if (civ.disabledUnits.some((du) => du.toLowerCase() === unitName.toLowerCase())) {
    return false;
  }

  return true;
}

function isInfantry(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('swordsman') ||
    norm.includes('militia') ||
    norm.includes('man-at-arms') ||
    norm.includes('champion') ||
    norm.includes('spearman') ||
    norm.includes('pikeman') ||
    norm.includes('halberdier') ||
    norm.includes('berserk') ||
    norm.includes('woad') ||
    norm.includes('huskarl') ||
    norm.includes('samurai') ||
    norm.includes('teutonic knight') ||
    norm.includes('kamayuk') ||
    norm.includes('shotel') ||
    norm.includes('gbeto') ||
    norm.includes('karambit') ||
    norm.includes('obuch') ||
    norm.includes('serjeant') ||
    norm.includes('urumi') ||
    norm.includes('condottiero') ||
    norm.includes('jaguar') ||
    norm.includes('eagle') ||
    norm.includes('legionary') ||
    norm.includes('jian')
  );
}

function isCavalry(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('scout') ||
    norm.includes('light cavalry') ||
    norm.includes('hussar') ||
    norm.includes('knight') ||
    norm.includes('cavalier') ||
    norm.includes('paladin') ||
    norm.includes('camel') ||
    norm.includes('cataphract') ||
    norm.includes('tarkan') ||
    norm.includes('boyar') ||
    norm.includes('magyar huszar') ||
    norm.includes('keshik') ||
    norm.includes('leitis') ||
    norm.includes('konnik') ||
    norm.includes('coustillier') ||
    norm.includes('shrivamsha') ||
    norm.includes('savar') ||
    norm.includes('monaspa') ||
    norm.includes('steppe lancer') ||
    norm.includes('xianbei')
  );
}

function isFootArcher(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('archer') ||
    norm.includes('crossbowman') ||
    norm.includes('arbalester') ||
    norm.includes('longbowman') ||
    norm.includes('chu ko nu') ||
    norm.includes('plumed') ||
    norm.includes('rattan') ||
    norm.includes('composite bowman')
  );
}

function isCavArcher(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('cavalry archer') ||
    norm.includes('mangudai') ||
    norm.includes('kipchak') ||
    norm.includes('camel archer')
  );
}

function isSkirmisher(u: string): boolean {
  const norm = u.toLowerCase();
  return norm.includes('skirmisher') || norm.includes('genitour');
}

function isCamel(u: string): boolean {
  return u.toLowerCase().includes('camel');
}

function isElephant(u: string): boolean {
  return u.toLowerCase().includes('elephant');
}

function isSpearman(u: string): boolean {
  const norm = u.toLowerCase();
  return norm.includes('spearman') || norm.includes('pikeman') || norm.includes('halberdier');
}

function isMilitiaLine(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('militia') ||
    norm.includes('man-at-arms') ||
    norm.includes('long swordsman') ||
    norm.includes('two-handed') ||
    norm.includes('champion')
  );
}

function isKnightLine(u: string): boolean {
  const norm = u.toLowerCase();
  return norm.includes('knight') || norm.includes('cavalier') || norm.includes('paladin');
}

function isScoutLine(u: string): boolean {
  const norm = u.toLowerCase();
  return norm.includes('scout') || norm.includes('light cavalry') || norm.includes('hussar');
}

function isGunpowder(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('hand cannon') ||
    norm.includes('janissary') ||
    norm.includes('conquistador') ||
    norm.includes('organ gun') ||
    norm.includes('bombard') ||
    norm.includes('hussite wagon') ||
    norm.includes('houfnice')
  );
}

function isSiege(u: string): boolean {
  const norm = u.toLowerCase();
  return (
    norm.includes('ram') ||
    norm.includes('mangonel') ||
    norm.includes('onager') ||
    norm.includes('scorpion') ||
    norm.includes('bombard cannon') ||
    norm.includes('siege') ||
    norm.includes('trebuchet')
  );
}

function isBarracksUnit(u: string): boolean {
  return isInfantry(u);
}

function isStableUnit(u: string): boolean {
  return isCavalry(u);
}

function isArcheryRangeUnit(u: string): boolean {
  return isFootArcher(u) || isCavArcher(u) || isSkirmisher(u);
}
