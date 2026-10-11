import { UnitData, UnitUpgrades, ComparisonResult } from './types';
import { CIVILIZATIONS, isUnitAvailableForCiv } from './civs';

export function computeBonusDmg(u1: UnitData, u2: UnitData, defenderReduction: number = 0): number {
  if (!u2.armor_class || !u1.attack_bonus) {
    return 0;
  }
  let bonus = 0;
  const enemyClasses = u2.armor_class.map((c) => c.toLowerCase());
  const bonusKeys = Object.keys(u1.attack_bonus);

  for (const ac of enemyClasses) {
    for (const bk of bonusKeys) {
      const bkLower = bk.toLowerCase();
      if (
        bkLower === ac ||
        (bkLower === 'spearman' && ac === 'spearmen') ||
        (bkLower === 'spearmen' && ac === 'spearman') ||
        (bkLower === 'archer' && ac === 'archers') ||
        (bkLower === 'archers' && ac === 'archer') ||
        (bkLower === 'camel' && ac === 'camels') ||
        (bkLower === 'camels' && ac === 'camel') ||
        (bkLower === 'unshielded' && ac === 'unshielded')
      ) {
        bonus += u1.attack_bonus[bk];
      }
    }
  }

  if (defenderReduction > 0) {
    bonus = Math.max(0, Math.round(bonus * (1 - defenderReduction)));
  }

  return bonus;
}

export function computeUpgrades(
  unit: UnitData,
  enemy: UnitData,
  upgrades: UnitUpgrades
): {
  attackBonus: number;
  parmorBonus: number;
  marmorBonus: number;
  rofBonus: number;
  hpBonus: number;
  bonusReduction: number;
  ignoresArmor: boolean;
} {
  let attackBonus = 0;
  let parmorBonus = 0;
  let marmorBonus = 0;
  let rofBonus = 1.0;
  let hpBonus = 0;
  let bonusReduction = 0;
  let ignoresArmor = false;

  const boostTech = unit.boost_tech || '';
  const civ = CIVILIZATIONS[upgrades.civilization] || CIVILIZATIONS['Generic'];

  // Determine effective tiers (accounting for FU and Full Tech Tree)
  let atkTier = upgrades.attackBonusTier;
  let armTier = upgrades.armorBonusTier;

  if (upgrades.fullyUpgraded) {
    if (upgrades.fullTechTree) {
      atkTier = 3;
      armTier = 3;
    } else {
      if (boostTech.includes('Fletching')) {
        atkTier = civ.maxRangedAttack;
      } else if (boostTech.includes('Forging')) {
        atkTier = civ.maxMeleeAttack;
      }
      if (boostTech.includes('Padded Archer Armor')) {
        armTier = civ.maxArcherArmor;
      } else if (boostTech.includes('Scale Barding Armor')) {
        armTier = civ.maxCavalryArmor;
      } else if (boostTech.includes('Scale Mail Armor')) {
        armTier = civ.maxInfantryArmor;
      }
    }
  }

  // Attack upgrades
  if (boostTech.includes('Fletching')) {
    attackBonus += atkTier; // 0, 1, 2, 3
  } else if (boostTech.includes('Forging')) {
    if (atkTier === 3) {
      attackBonus += 4; // Blast Furnace is +4 total
    } else {
      attackBonus += atkTier; // 0, 1, 2
    }
  }

  // Armor upgrades
  if (
    boostTech.includes('Padded Archer Armor') ||
    boostTech.includes('Scale Barding Armor') ||
    boostTech.includes('Scale Mail Armor')
  ) {
    if (armTier === 3) {
      parmorBonus += armTier + 1; // +4 pierce armor at tier 3
    } else {
      parmorBonus += armTier;
    }
    marmorBonus += armTier;
  }

  // Chemistry
  const allowChemistry = upgrades.fullTechTree || civ.hasChemistry;
  if (boostTech.includes('Chemistry') && (upgrades.chemistry || (upgrades.fullyUpgraded && allowChemistry))) {
    attackBonus += 1;
  }

  // Thumb Ring
  const allowThumbRing = upgrades.fullTechTree || civ.hasThumbRing;
  if (
    boostTech.includes('Thumb Ring') &&
    !unit.name.includes('Skirmisher') &&
    !unit.name.includes('Genitour') &&
    (upgrades.thumbRing || (upgrades.fullyUpgraded && allowThumbRing))
  ) {
    if (unit.name.includes('Cavalry Archer')) {
      rofBonus *= 0.9;
    } else {
      rofBonus *= 0.85;
    }
  }

  // Bloodlines
  const allowBloodlines = upgrades.fullTechTree || civ.hasBloodlines;
  if (boostTech.includes('Bloodlines') && (upgrades.bloodlines || (upgrades.fullyUpgraded && allowBloodlines))) {
    hpBonus += 20;
  }

  // Parthian Tactics
  const allowParthian = upgrades.fullTechTree || civ.hasParthianTactics;
  if (boostTech.includes('Parthian Tactics') && (upgrades.parthianTactics || (upgrades.fullyUpgraded && allowParthian))) {
    marmorBonus += 1;
    parmorBonus += 1;
    const enemyHasSpear = enemy.armor_class?.some(
      (c) => c.toLowerCase() === 'spearman' || c.toLowerCase() === 'spearmen'
    );
    if (enemyHasSpear) {
      attackBonus += 2;
    }
  }

  // Gambesons
  const allowGambesons = upgrades.fullTechTree || civ.hasGambesons;
  if (boostTech.includes('Gambesons') && (upgrades.gambesons || (upgrades.fullyUpgraded && allowGambesons))) {
    parmorBonus += 1;
  }

  // Cranequins
  if (boostTech.includes('Cranequins') && upgrades.cranequins) {
    const enemyHasInfantry = enemy.armor_class?.some((c) => c.toLowerCase() === 'infantry');
    if (enemyHasInfantry) {
      attackBonus += 2;
    }
  }

  // Loom
  if (unit.name.includes('Villager') && upgrades.loom) {
    marmorBonus += 1;
    parmorBonus += 2;
    hpBonus += 15;
  }

  // Civilization innate bonuses
  const civBonus = civ.getCivBonuses(unit.name, upgrades.selectedAge);
  if (civBonus) {
    if (civBonus.hpPercent) {
      hpBonus += Math.round(unit.hp * civBonus.hpPercent);
    }
    if (civBonus.hpFlat) {
      hpBonus += civBonus.hpFlat;
    }
    if (civBonus.attackFlat) {
      attackBonus += civBonus.attackFlat;
    }
    if (civBonus.meleeArmorFlat) {
      marmorBonus += civBonus.meleeArmorFlat;
    }
    if (civBonus.pierceArmorFlat) {
      parmorBonus += civBonus.pierceArmorFlat;
    }
    if (civBonus.rofMultiplier) {
      rofBonus *= civBonus.rofMultiplier;
    }
    if (civBonus.bonusDamageReduction) {
      bonusReduction = civBonus.bonusDamageReduction;
    }
  }

  // Unique Techs for the civilization
  const activeTechs = upgrades.activeUniqueTechs || [];
  for (const tech of civ.uniqueTechs) {
    const isTechActive = upgrades.fullyUpgraded || activeTechs.includes(tech.id);
    if (isTechActive && tech.appliesTo(unit.name, civ.name)) {
      const statsObj = {
        attack: attackBonus,
        armor: marmorBonus,
        pierceArmor: parmorBonus,
        hp: hpBonus,
        rof: rofBonus,
        bonusDmg: {},
        ignoresArmor: false,
      };
      tech.apply(statsObj);
      attackBonus = statsObj.attack;
      marmorBonus = statsObj.armor;
      parmorBonus = statsObj.pierceArmor;
      hpBonus = statsObj.hp;
      rofBonus = statsObj.rof;
      if (statsObj.ignoresArmor) ignoresArmor = true;
    }
  }

  return {
    attackBonus,
    parmorBonus,
    marmorBonus,
    rofBonus,
    hpBonus,
    bonusReduction,
    ignoresArmor,
  };
}

export function hasAttack(unit: UnitData, upgrades: UnitUpgrades): boolean {
  if (unit.uniqueMechanic?.type === 'mode_switch') {
    return true;
  }
  const p = unit.p_attack;
  const m = unit.m_attack;
  return (p !== null && p !== undefined && p > 0) || (m !== null && m !== undefined && m > 0);
}

export function simulateAttack(
  attacker: UnitData,
  defender: UnitData,
  attackerUpgrades: UnitUpgrades,
  defenderUpgrades: UnitUpgrades
): {
  hits: number;
  time: number;
  damagePerHit: number;
  bonusDmg: number;
  mechanicSummary: string;
} {
  const attackerMods = computeUpgrades(attacker, defender, attackerUpgrades);
  const defenderMods = computeUpgrades(defender, attacker, defenderUpgrades);
  const bonusDmg = computeBonusDmg(attacker, defender, defenderMods.bonusReduction);

  // Determine attack type (pierce vs melee)
  let isPierce = attacker.p_attack !== null && attacker.p_attack !== undefined && attacker.p_attack > 0;
  let rawAttack = isPierce ? attacker.p_attack! : (attacker.m_attack ?? 0);

  // Ratha mode switch override
  if (attacker.uniqueMechanic?.type === 'mode_switch') {
    if (attackerUpgrades.rathaMode === 'ranged') {
      isPierce = true;
      rawAttack = attacker.uniqueMechanic.rangedAttack || (attacker.elite ? 6 : 5);
    } else {
      isPierce = false;
      rawAttack = attacker.uniqueMechanic.meleeAttack || (attacker.elite ? 12 : 10);
    }
  }

  let baseAttack = rawAttack + attackerMods.attackBonus;
  if (attackerUpgrades.rocketry && attacker.name.toLowerCase().includes('chu ko nu')) {
    baseAttack += 2;
  }

  const mechanic = attacker.uniqueMechanic;
  const chargeDamage =
    mechanic?.type === 'charge' && attackerUpgrades.chargeAttackEnabled !== false
      ? mechanic.chargeDamage || 0
      : 0;
  const chargeCooldown = mechanic?.chargeCooldown || 40;
  const ignoresArmor =
    (mechanic?.type === 'armor_ignore' && mechanic.ignoresArmor) ||
    attackerUpgrades.wootzSteel === true ||
    attackerMods.ignoresArmor;
  const armorPen =
    mechanic?.type === 'armor_ignore' && mechanic.armorPenetration ? mechanic.armorPenetration : 0;
  const armorShred = mechanic?.type === 'armor_shred' ? mechanic.armorShredPerHit || 1 : 0;
  const extraProjectiles = mechanic?.type === 'multishot' ? mechanic.extraProjectiles || 0 : 0;
  const secondaryDmg = mechanic?.type === 'multishot' ? mechanic.secondaryDamage || 3 : 0;

  const defenderBaseArmor = defender.armor + defenderMods.marmorBonus;
  const defenderBasePierceArmor = defender.pierce_armor + defenderMods.parmorBonus;
  const defenderShieldCharges =
    defender.uniqueMechanic?.type === 'dodge_shield'
      ? defender.uniqueMechanic.shieldCharges || 0
      : 0;
  const defenderHasDismount =
    defender.uniqueMechanic?.type === 'dismount' && defenderUpgrades.dismountEnabled !== false;
  const dismountHp = defender.uniqueMechanic?.dismountHp || 45;
  const dismountArmor = defender.uniqueMechanic?.dismountArmor || [0, 0];

  let targetHp = Math.max(1, defender.hp + defenderMods.hpBonus);
  let inDismountPhase = false;
  let currentMeleeArmor = defenderBaseArmor;
  let currentPierceArmor = defenderBasePierceArmor;
  let currentShieldCharges = defenderShieldCharges;
  let hits = 0;
  let lastChargeTime = -999;
  let totalDamageDone = 0;
  const rof = Math.max(0.5, attacker.rof * attackerMods.rofBonus);

  while (targetHp > 0 && hits < 1500) {
    const currentTime = hits * rof;

    // Dodge shield mechanics (Shrivamsha Rider absorbs incoming pierce attacks)
    if (isPierce && currentShieldCharges > 0) {
      currentShieldCharges--;
      hits++;
      continue;
    }

    let targetArmor = isPierce ? currentPierceArmor : currentMeleeArmor;
    if (ignoresArmor) {
      targetArmor = 0;
    } else if (armorPen > 0) {
      targetArmor = Math.max(0, targetArmor - armorPen);
    }

    let currentCharge = 0;
    if (chargeDamage > 0) {
      if (hits === 0 || currentTime - lastChargeTime >= chargeCooldown) {
        currentCharge = chargeDamage;
        lastChargeTime = currentTime;
      }
    }

    // Main hit damage (AoE2 minimum damage is 1)
    let mainHitDamage = baseAttack + currentCharge - targetArmor;
    mainHitDamage = Math.max(1, mainHitDamage) + bonusDmg;
    mainHitDamage = Math.max(1, mainHitDamage);

    // Multishot secondary projectiles
    let secondaryDamageTotal = 0;
    if (extraProjectiles > 0) {
      const secArmor = ignoresArmor ? 0 : currentPierceArmor;
      const singleSecDmg = Math.max(1, secondaryDmg - secArmor);
      secondaryDamageTotal = extraProjectiles * singleSecDmg;
    }

    const damageThisHit = mainHitDamage + secondaryDamageTotal;
    targetHp -= damageThisHit;
    totalDamageDone += damageThisHit;
    hits++;

    // Obuch armor stripping
    if (armorShred > 0) {
      currentMeleeArmor -= armorShred;
      currentPierceArmor -= armorShred;
    }

    // Konnik dismounting transition
    if (targetHp <= 0 && defenderHasDismount && !inDismountPhase) {
      inDismountPhase = true;
      targetHp = dismountHp;
      currentMeleeArmor = dismountArmor[0];
      currentPierceArmor = dismountArmor[1];
    }
  }

  const time = hits > 0 ? (hits - 1) * rof : 0;
  const avgDamage = hits > 0 ? Math.round((totalDamageDone / hits) * 10) / 10 : 0;

  // Build summary description
  const summaries: string[] = [];
  if (bonusDmg > 0) summaries.push(`+${bonusDmg} class bonus`);
  if (chargeDamage > 0) summaries.push(`+${chargeDamage} charge attack`);
  if (extraProjectiles > 0) summaries.push(`+${extraProjectiles} secondary projectiles`);
  if (ignoresArmor) summaries.push(`ignores armor`);
  if (armorShred > 0) summaries.push(`-1 armor shred per hit`);
  if (defenderShieldCharges > 0 && isPierce)
    summaries.push(`absorbed ${defenderShieldCharges} pierce hits with shield`);
  if (defenderHasDismount) summaries.push(`killed mounted + dismounted form`);
  if (defenderMods.bonusReduction > 0)
    summaries.push(`target took -${Math.round(defenderMods.bonusReduction * 100)}% bonus dmg`);

  return {
    hits,
    time: Math.max(0, time),
    damagePerHit: avgDamage,
    bonusDmg,
    mechanicSummary: summaries.join(', '),
  };
}

export function compareUnits(
  unit1: UnitData,
  unit2: UnitData,
  upgrades1: UnitUpgrades,
  upgrades2: UnitUpgrades
): ComparisonResult {
  // Check Civilization Availability FIRST!
  const u1Available = isUnitAvailableForCiv(unit1.name, upgrades1.civilization);
  const u2Available = isUnitAvailableForCiv(unit2.name, upgrades2.civilization);

  if (!u1Available || !u2Available) {
    const errorMsg =
      !u1Available && !u2Available
        ? `${upgrades1.civilization} does not get access to ${unit1.name}.\n${upgrades2.civilization} does not get access to ${unit2.name}.`
        : !u1Available
        ? `${upgrades1.civilization} does not get access to ${unit1.name}.`
        : `${upgrades2.civilization} does not get access to ${unit2.name}.`;

    return {
      unit1Name: unit1.name,
      unit2Name: unit2.name,
      hits1: 0,
      time1: 0,
      hits2: 0,
      time2: 0,
      rawText: errorMsg,
      winner: 'error',
      error: errorMsg,
      unit1CanAttack: false,
      unit2CanAttack: false,
      unit1DamagePerHit: 0,
      unit2DamagePerHit: 0,
      unit1BonusDmg: 0,
      unit2BonusDmg: 0,
    };
  }

  const canAttack1 = hasAttack(unit1, upgrades1);
  const canAttack2 = hasAttack(unit2, upgrades2);

  // Case 1: Neither unit can attack
  if (!canAttack1 && !canAttack2) {
    return {
      unit1Name: unit1.name,
      unit2Name: unit2.name,
      hits1: 0,
      time1: 0,
      hits2: 0,
      time2: 0,
      rawText: `Neither ${unit1.name} nor ${unit2.name} has an attack.\n\nStalemate! Both units cannot damage each other.`,
      winner: 'tie',
      unit1CanAttack: false,
      unit2CanAttack: false,
      unit1DamagePerHit: 0,
      unit2DamagePerHit: 0,
      unit1BonusDmg: 0,
      unit2BonusDmg: 0,
    };
  }

  // Case 2: Unit 1 cannot attack, Unit 2 CAN attack
  if (!canAttack1 && canAttack2) {
    const sim2 = simulateAttack(unit2, unit1, upgrades2, upgrades1);
    const text = `${unit1.name} does not attack.\n\n${unit2.name} takes ${
      sim2.hits
    } hits and ${sim2.time.toFixed(2)} seconds to kill ${unit1.name}\n\n${unit2.name} (${upgrades2.civilization}) wins 1v1 (uncontested)`;

    return {
      unit1Name: unit1.name,
      unit2Name: unit2.name,
      hits1: 0,
      time1: 0,
      hits2: sim2.hits,
      time2: sim2.time,
      rawText: text,
      winner: 'unit2',
      unit1CanAttack: false,
      unit2CanAttack: true,
      unit1DamagePerHit: 0,
      unit2DamagePerHit: sim2.damagePerHit,
      unit1BonusDmg: 0,
      unit2BonusDmg: sim2.bonusDmg,
      unit2MechanicSummary: sim2.mechanicSummary,
    };
  }

  // Case 3: Unit 2 cannot attack, Unit 1 CAN attack
  if (canAttack1 && !canAttack2) {
    const sim1 = simulateAttack(unit1, unit2, upgrades1, upgrades2);
    const text = `${unit2.name} does not attack.\n\n${unit1.name} takes ${
      sim1.hits
    } hits and ${sim1.time.toFixed(2)} seconds to kill ${unit2.name}\n\n${unit1.name} (${upgrades1.civilization}) wins 1v1 (uncontested)`;

    return {
      unit1Name: unit1.name,
      unit2Name: unit2.name,
      hits1: sim1.hits,
      time1: sim1.time,
      hits2: 0,
      time2: 0,
      rawText: text,
      winner: 'unit1',
      unit1CanAttack: true,
      unit2CanAttack: false,
      unit1DamagePerHit: sim1.damagePerHit,
      unit2DamagePerHit: 0,
      unit1BonusDmg: sim1.bonusDmg,
      unit2BonusDmg: 0,
      unit1MechanicSummary: sim1.mechanicSummary,
    };
  }

  // Case 4: Both units attack each other
  const sim1 = simulateAttack(unit1, unit2, upgrades1, upgrades2);
  const sim2 = simulateAttack(unit2, unit1, upgrades2, upgrades1);

  const text = `${unit1.name} (${upgrades1.civilization}) takes ${sim1.hits} hits and ${sim1.time.toFixed(
    2
  )} seconds to kill ${unit2.name} (${upgrades2.civilization})\n\n${unit2.name} (${upgrades2.civilization}) takes ${sim2.hits} hits and ${sim2.time.toFixed(
    2
  )} seconds to kill ${unit1.name} (${upgrades1.civilization})`;

  let winner = 'tie';
  let verdict = 'Both units takes the same time to kill each other';

  if (sim1.time < sim2.time) {
    winner = 'unit1';
    verdict = `${unit1.name} (${upgrades1.civilization}) wins 1v1`;
  } else if (sim2.time < sim1.time) {
    winner = 'unit2';
    verdict = `${unit2.name} (${upgrades2.civilization}) wins 1v1`;
  } else {
    if (sim1.hits < sim2.hits) {
      winner = 'unit1';
      verdict = `${unit1.name} (${upgrades1.civilization}) wins 1v1 (fewer hits required)`;
    } else if (sim2.hits < sim1.hits) {
      winner = 'unit2';
      verdict = `${unit2.name} (${upgrades2.civilization}) wins 1v1 (fewer hits required)`;
    }
  }

  return {
    unit1Name: unit1.name,
    unit2Name: unit2.name,
    hits1: sim1.hits,
    time1: sim1.time,
    hits2: sim2.hits,
    time2: sim2.time,
    rawText: `${text}\n\n${verdict}`,
    winner,
    unit1CanAttack: true,
    unit2CanAttack: true,
    unit1DamagePerHit: sim1.damagePerHit,
    unit2DamagePerHit: sim2.damagePerHit,
    unit1BonusDmg: sim1.bonusDmg,
    unit2BonusDmg: sim2.bonusDmg,
    unit1MechanicSummary: sim1.mechanicSummary,
    unit2MechanicSummary: sim2.mechanicSummary,
  };
}
