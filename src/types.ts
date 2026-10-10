export type MechanicType =
  | 'multishot'
  | 'charge'
  | 'armor_ignore'
  | 'armor_shred'
  | 'dismount'
  | 'dodge_shield'
  | 'mode_switch'
  | 'unshielded'
  | 'none';

export interface UniqueMechanicConfig {
  type: MechanicType;
  description: string;
  extraProjectiles?: number;
  secondaryDamage?: number;
  chargeDamage?: number;
  chargeCooldown?: number;
  armorShredPerHit?: number;
  ignoresArmor?: boolean;
  armorPenetration?: number;
  dismountHp?: number;
  dismountAttack?: number;
  dismountArmor?: [number, number];
  dismountRof?: number;
  shieldCharges?: number;
  supportsRangedMode?: boolean;
  rangedAttack?: number;
  meleeAttack?: number;
}

export interface UnitData {
  name: string;
  hp: number;
  p_attack: number | null;
  m_attack: number | null;
  rof: number;
  armor: number;
  pierce_armor: number;
  attack_bonus: Record<string, number> | null;
  armor_class: string[] | null;
  boost_tech: string | null;
  elite: boolean;
  ageOptions?: { [ageName: string]: number };
  uniqueMechanic?: UniqueMechanicConfig;
}

export interface UnitUpgrades {
  civilization: string; // e.g. "Generic", "Franks", "Britons"
  fullyUpgraded: boolean; // FU toggle
  fullTechTree: boolean; // Overrides civ tech limitations
  selectedAge: number; // 1: Dark, 2: Feudal, 3: Castle, 4: Imperial
  attackBonusTier: number; // 0: None, 1, 2, 3
  armorBonusTier: number; // 0: None, 1, 2, 3
  chemistry: boolean;
  thumbRing: boolean;
  bloodlines: boolean;
  parthianTactics: boolean;
  gambesons: boolean;
  cranequins: boolean;
  loom: boolean;
  rocketry?: boolean;
  wootzSteel?: boolean;
  rathaMode?: 'melee' | 'ranged';
  chargeAttackEnabled?: boolean;
  dismountEnabled?: boolean;
  activeUniqueTechs?: string[];
}

export interface ComparisonResult {
  unit1Name: string;
  unit2Name: string;
  hits1: number;
  time1: number;
  hits2: number;
  time2: number;
  rawText: string;
  winner: string; // 'unit1' | 'unit2' | 'tie' | 'error'
  error?: string;
  unit1CanAttack: boolean;
  unit2CanAttack: boolean;
  unit1DamagePerHit: number;
  unit2DamagePerHit: number;
  unit1BonusDmg: number;
  unit2BonusDmg: number;
  unit1MechanicSummary?: string;
  unit2MechanicSummary?: string;
  combatLog?: string[];
}
