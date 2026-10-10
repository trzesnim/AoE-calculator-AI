import { UnitData, UniqueMechanicConfig } from './types';
import { elite as eliteList } from './lists';

const cache = new Map<string, { content: string; boost_tech: string }>();

export function checkBonus(bonusStr: string | null | undefined, isElite: boolean): Record<string, number> | null {
  if (!bonusStr) return null;
  const pattern = /([+-]?\d+(?:\s*,\s*[+-]?\d+)?).*?vs\.?\s*.*?2class\|([^}|]+)/gi;
  const b: Record<string, number> = {};
  let match;
  while ((match = pattern.exec(bonusStr)) !== null) {
    const nums = match[1];
    const cls = match[2].trim();
    const parts = nums.split(',').map((p) => p.trim());
    const val = isElite && parts.length > 1 ? parts[1] : parts[0];
    const parsedVal = parseInt(val, 10);
    if (!isNaN(parsedVal)) {
      const titleCls = cls.charAt(0).toUpperCase() + cls.slice(1).toLowerCase();
      b[titleCls] = parsedVal;
    }
  }
  if ('Mameluke' in b) {
    b['Mamelukes'] = b['Mameluke'];
    delete b['Mameluke'];
  }
  return Object.keys(b).length > 0 ? b : null;
}

export function checkClass(classStr: string | null | undefined): string[] | null {
  if (!classStr) return null;
  const pattern = /2class\|([^}|]+)/gi;
  const list: string[] = [];
  let match;
  while ((match = pattern.exec(classStr)) !== null) {
    let k = match[1].trim();
    if (k === 'Archer') k = 'Archers';
    if (k === 'Gunpowder unit') k = 'Gunpowder Units';
    if (k === 'Unique unit') k = 'Unique Units';
    if (k === 'Mameluke:') k = 'Mamelukes';
    if (k.toLowerCase() === 'unshielded') k = 'Unshielded';
    list.push(k.charAt(0).toUpperCase() + k.slice(1));
  }
  return list.length > 0 ? list : null;
}

export function hasAgeVariations(v: string | null | undefined): boolean {
  if (!v) return false;
  const pattern = /(Dark Age|Feudal Age|Castle Age|Imperial Age)}}\s*(\d+)/i;
  return pattern.test(v);
}

export function extractAgeOptions(v: string | null | undefined): { [ageName: string]: number } | undefined {
  if (!v) return undefined;
  const pattern = /(Dark Age|Feudal Age|Castle Age|Imperial Age)}}\s*(\d+)/gi;
  const map: { [ageName: string]: number } = {};
  let match;
  while ((match = pattern.exec(v)) !== null) {
    map[match[1]] = parseInt(match[2], 10);
  }
  return Object.keys(map).length > 0 ? map : undefined;
}

export function checkV(
  v: string | null | undefined,
  isElite: boolean,
  selectedAge: number = 1
): string | null {
  if (!v) return null;

  const ages: Record<string, string> = {
    '1': 'Dark Age',
    '2': 'Feudal Age',
    '3': 'Castle Age',
    '4': 'Imperial Age',
  };

  const ageMap = extractAgeOptions(v);
  if (ageMap) {
    let age = ages[String(selectedAge)];
    for (let i = 0; i < 3; i++) {
      if (!ageMap[age]) {
        age = ages[String(selectedAge - (i + 1))];
      } else {
        break;
      }
    }
    if (ageMap[age] !== undefined) {
      return String(ageMap[age]);
    }
  }

  let cleanV = v.replace(/\{\{tt\|([^|]+)\|.*?\}\}/g, '$1');
  const commaMatch = /(.+?)\s*,\s*(.+)/.exec(cleanV);
  let stat = cleanV;
  if (commaMatch) {
    stat = isElite ? commaMatch[2] : commaMatch[1];
  }

  const brMatch = /<br \/>(\d+) <small>/.exec(stat);
  if (brMatch) {
    stat = brMatch[1];
  }

  const multiMatch = /(\d+).*?\([xX×\u00d7]\s*(\d+)\)/.exec(stat);
  if (multiMatch) {
    stat = String(parseInt(multiMatch[1], 10) + parseInt(multiMatch[2], 10));
  }

  const numMatch = /([+-]?[\d.]+)/.exec(String(stat));
  return numMatch ? numMatch[1] : stat.trim();
}

export function detectUniqueMechanic(unitName: string, isElite: boolean): UniqueMechanicConfig | undefined {
  const norm = unitName.toLowerCase();
  if (norm.includes('chu ko nu')) {
    return {
      type: 'multishot',
      extraProjectiles: isElite ? 4 : 2,
      secondaryDamage: 3,
      description: `Fires a volley of ${isElite ? 5 : 3} arrows per burst (secondary arrows deal 3 pierce damage each, min 1).`,
    };
  }
  if (norm.includes('kipchak')) {
    return {
      type: 'multishot',
      extraProjectiles: isElite ? 3 : 2,
      secondaryDamage: 3,
      description: `Fires a burst of ${isElite ? 4 : 3} arrows (secondary arrows deal 3 pierce damage each, min 1).`,
    };
  }
  if (norm.includes('coustillier')) {
    return {
      type: 'charge',
      chargeDamage: isElite ? 40 : 35,
      chargeCooldown: 40,
      description: `Deals +${isElite ? 40 : 35} burst charge attack on initial strike (40s recharge cooldown).`,
    };
  }
  if (norm.includes('urumi')) {
    return {
      type: 'charge',
      chargeDamage: isElite ? 10 : 9,
      chargeCooldown: 20,
      description: `Deals +${isElite ? 10 : 9} charge attack on initial strike. Can toggle Wootz Steel to bypass enemy armor.`,
    };
  }
  if (norm.includes('leitis')) {
    return {
      type: 'armor_ignore',
      ignoresArmor: true,
      description: `Attacks completely bypass and ignore enemy melee and pierce armor.`,
    };
  }
  if (norm.includes('obuch')) {
    return {
      type: 'armor_shred',
      armorShredPerHit: 1,
      description: `Permanently degrades enemy melee and pierce armor by 1 with each consecutive hit.`,
    };
  }
  if (norm.includes('konnik')) {
    return {
      type: 'dismount',
      dismountHp: isElite ? 50 : 45,
      dismountAttack: isElite ? 12 : 9,
      dismountArmor: isElite ? [0, 1] : [0, 0],
      dismountRof: 2.4,
      description: `Spawns a Dismounted Konnik (${isElite ? 50 : 45} HP, ${isElite ? 12 : 9} Atk) when mounted form dies.`,
    };
  }
  if (norm.includes('ratha')) {
    return {
      type: 'mode_switch',
      supportsRangedMode: true,
      meleeAttack: isElite ? 12 : 10,
      rangedAttack: isElite ? 6 : 5,
      description: `Can switch between Melee chariot combat and Ranged pierce archery mode.`,
    };
  }
  if (norm.includes('shrivamsha')) {
    return {
      type: 'dodge_shield',
      shieldCharges: isElite ? 7 : 5,
      description: `Equipped with an agile shield that absorbs up to ${isElite ? 7 : 5} incoming pierce attacks completely (0 dmg).`,
    };
  }
  if (norm.includes('hussite wagon')) {
    return {
      type: 'multishot',
      extraProjectiles: 4,
      secondaryDamage: 4,
      description: `Mobile armored wagon firing a cannon shot plus 4 secondary pellets dealing 4 damage each.`,
    };
  }
  if (norm.includes('organ gun')) {
    return {
      type: 'multishot',
      extraProjectiles: isElite ? 5 : 4,
      secondaryDamage: 2,
      description: `Fires a volley of ${isElite ? 6 : 5} bullets (secondary bullets deal 2 pierce damage each).`,
    };
  }
  if (norm.includes('composite bowman')) {
    return {
      type: 'armor_ignore',
      armorPenetration: 2,
      description: `Penetrating recurve bow piercing through up to 2 enemy pierce armor.`,
    };
  }
  if (norm.includes('jian swordsman')) {
    return {
      type: 'unshielded',
      description: `Unshielded heavy swordsman; takes bonus damage from anti-unshielded missile attacks (e.g. Skirmishers).`,
    };
  }
  if (norm.includes('xianbei raider')) {
    return {
      type: 'charge',
      chargeDamage: isElite ? 8 : 6,
      chargeCooldown: 25,
      description: `Nomad raider with charge attack dealing +${isElite ? 8 : 6} bonus burst damage.`,
    };
  }
  return undefined;
}

export async function fetchUnitRawWiki(unitName: string): Promise<{ content: string; boost_tech: string }> {
  let title = unitName;
  if (title === 'Villager') {
    title = 'Villager_(Age_of_Empires_II)';
  }

  const cached = cache.get(title);
  if (cached) {
    return cached;
  }

  const apiUrl = `https://ageofempires.fandom.com/api.php?action=query&prop=revisions&titles=${encodeURIComponent(
    title
  )}&rvprop=content&formatversion=2&format=json&origin=*`;

  try {
    const res = await fetch(apiUrl);
    const data = await res.json();
    const query = data?.query;
    if (!query || !query.pages || query.pages[0]?.missing) {
      throw new Error(`Unit ${unitName} not found on Wiki.`);
    }

    let content: string = query.pages[0].revisions?.[0]?.content || '';
    if (
      (content.includes('Disambig') || content.includes('disambig') || content.includes('ForNoLink')) &&
      !content.includes('Bombard Cannon')
    ) {
      const disambigTitle = `${title}_(Age_of_Empires_II)`;
      const res2 = await fetch(
        `https://ageofempires.fandom.com/api.php?action=query&prop=revisions&titles=${encodeURIComponent(
          disambigTitle
        )}&rvprop=content&formatversion=2&format=json&origin=*`
      );
      const data2 = await res2.json();
      if (data2?.query?.pages?.[0]?.revisions?.[0]?.content) {
        content = data2.query.pages[0].revisions[0].content;
      }
    }

    let boost_tech = '';
    const techMatch = /.+?Boosts\|Technologies(.+?)\{\{Boosts\|.+/s.exec(content);
    if (techMatch) {
      boost_tech = techMatch[1];
    }

    const cleanContent = content.replace(/(<tabber>.+$)|(escription.+$)/s, '');
    const result = { content: cleanContent, boost_tech };
    cache.set(title, result);
    return result;
  } catch (err) {
    const fallback = getCuratedFallback(unitName);
    if (fallback) {
      return fallback;
    }
    throw err;
  }
}

export function parseUnitStats(
  content: string,
  boost_tech: string,
  isElite: boolean,
  selectedAge: number = 1
): UnitData {
  const pattern = /(Name|HP|PAttack|MAttack|ROF|Armor|PierceArmor|AttackBonus|Class)\s*=\s*(.+)/g;
  const rawFields: Record<string, string> = {};
  let match;
  while ((match = pattern.exec(content)) !== null) {
    const key = match[1];
    const val = match[2].trim();
    rawFields[key] = val;
  }

  let finalName = rawFields['Name'] || 'Unknown Unit';
  if (content.includes('ChampionIcon.jpg')) {
    finalName = 'Champion';
  } else if (content.includes('Twohanded aoe2DE.png')) {
    finalName = 'Two-Handed Swordsman';
  }
  if (content.includes('Xolotlicon')) {
    finalName = 'Xolotl Warrior';
    for (const k of Object.keys(rawFields)) {
      rawFields[k] = rawFields[k].replace(/<.+/, '').trim();
    }
  }

  if (eliteList.includes(finalName) && isElite) {
    if (!finalName.startsWith('Elite ')) {
      finalName = `Elite ${finalName}`;
    }
  }

  // Serjeant Age & Elite scaling
  const normName = finalName.toLowerCase();
  let hp = 50;
  let p_attack: number | null = null;
  let m_attack: number | null = null;
  let rof = 2.0;
  let armor = 0;
  let pierce_armor = 0;
  let ageOptions: { [ageName: string]: number } | undefined = undefined;

  if (normName.includes('serjeant')) {
    ageOptions = { 'Feudal Age': 2, 'Castle Age': 3, 'Imperial Age': 4 };
    if (selectedAge <= 2) {
      hp = 45;
      m_attack = 5;
      armor = 1;
      pierce_armor = 1;
    } else if (selectedAge === 3) {
      hp = 60;
      m_attack = 8;
      armor = 2;
      pierce_armor = 2;
    } else {
      hp = isElite ? 75 : 60;
      m_attack = isElite ? 11 : 8;
      armor = isElite ? 3 : 2;
      pierce_armor = isElite ? 3 : 2;
    }
    rof = 2.0;
  } else if (normName.includes('flemish militia')) {
    ageOptions = { 'Dark Age': 1, 'Feudal Age': 2, 'Castle Age': 3, 'Imperial Age': 4 };
    if (selectedAge === 1) {
      hp = 40;
      m_attack = 4;
      armor = 0;
      pierce_armor = 0;
    } else if (selectedAge === 2) {
      hp = 50;
      m_attack = 6;
      armor = 0;
      pierce_armor = 1;
    } else if (selectedAge === 3) {
      hp = 65;
      m_attack = 9;
      armor = 1;
      pierce_armor = 1;
    } else {
      hp = 75;
      m_attack = 12;
      armor = 1;
      pierce_armor = 1;
    }
    rof = 2.0;
  } else {
    const hpStr = checkV(rawFields['HP'], isElite, selectedAge);
    hp = hpStr ? parseInt(hpStr, 10) : 50;

    const pAttackStr = rawFields['PAttack'] ? checkV(rawFields['PAttack'], isElite, selectedAge) : null;
    p_attack = pAttackStr !== null ? parseInt(pAttackStr, 10) : null;

    const mAttackStr = rawFields['MAttack'] ? checkV(rawFields['MAttack'], isElite, selectedAge) : null;
    m_attack = mAttackStr !== null ? parseInt(mAttackStr, 10) : null;

    const rofStr = checkV(rawFields['ROF'], isElite, selectedAge);
    rof = rofStr ? parseFloat(rofStr) : 2.0;

    const armorStr = checkV(rawFields['Armor'], isElite, selectedAge);
    armor = armorStr ? parseInt(armorStr, 10) : 0;

    const pArmorStr = checkV(rawFields['PierceArmor'], isElite, selectedAge);
    pierce_armor = pArmorStr ? parseInt(pArmorStr, 10) : 0;

    ageOptions =
      rawFields['PAttack'] && hasAgeVariations(rawFields['PAttack'])
        ? extractAgeOptions(rawFields['PAttack'])
        : rawFields['MAttack'] && hasAgeVariations(rawFields['MAttack'])
        ? extractAgeOptions(rawFields['MAttack'])
        : undefined;
  }

  const attack_bonus = checkBonus(rawFields['AttackBonus'], isElite);
  let armor_class = checkClass(rawFields['Class']);

  // Jian swordsman unshielded mechanic enforcement
  if (normName.includes('jian swordsman')) {
    if (!armor_class) armor_class = [];
    if (!armor_class.includes('Unshielded')) {
      armor_class.push('Unshielded');
    }
  }

  const uniqueMechanic = detectUniqueMechanic(finalName, isElite);

  return {
    name: finalName,
    hp: isNaN(hp) || hp <= 0 ? 50 : hp,
    p_attack: p_attack !== null && !isNaN(p_attack) ? p_attack : null,
    m_attack: m_attack !== null && !isNaN(m_attack) ? m_attack : null,
    rof: isNaN(rof) || rof <= 0 ? 2.0 : rof,
    armor: isNaN(armor) ? 0 : armor,
    pierce_armor: isNaN(pierce_armor) ? 0 : pierce_armor,
    attack_bonus,
    armor_class,
    boost_tech: boost_tech || null,
    elite: isElite,
    ageOptions,
    uniqueMechanic,
  };
}

// Curated fallbacks including all unique units and non-attacking units
function getCuratedFallback(unit: string): { content: string; boost_tech: string } | null {
  const norm = unit.trim().toLowerCase();
  const db: Record<string, { content: string; boost_tech: string }> = {
    // Unique units
    "chu ko nu": {
      content: `Name = Chu Ko Nu\nHP = 45, 50\nPAttack = 8, 8\nROF = 3.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +2 vs {{2class|Spearman}}\nClass = {{2class|Archer}}, {{2class|Unique unit}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry`,
    },
    kipchak: {
      content: `Name = Kipchak\nHP = 40, 45\nPAttack = 4, 5\nROF = 2.2\nArmor = 0\nPierceArmor = 0\nAttackBonus = +1 vs {{2class|Spearman}}\nClass = {{2class|Archer}}, {{2class|Cavalry Archer}}, {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bloodlines, Parthian Tactics`,
    },
    coustillier: {
      content: `Name = Coustillier\nHP = 115, 145\nMAttack = 11, 14\nROF = 1.9\nArmor = 2\nPierceArmor = 2\nClass = {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "urumi swordsman": {
      content: `Name = Urumi Swordsman\nHP = 55, 65\nMAttack = 8, 10\nROF = 1.2\nArmor = 0\nPierceArmor = 0\nAttackBonus = +1 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    leitis: {
      content: `Name = Leitis\nHP = 100, 130\nMAttack = 12, 14\nROF = 1.9\nArmor = 2, 3\nPierceArmor = 1, 2\nClass = {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    obuch: {
      content: `Name = Obuch\nHP = 80, 95\nMAttack = 8, 10\nROF = 2.0\nArmor = 2\nPierceArmor = 2\nClass = {{2class|Infantry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    konnik: {
      content: `Name = Konnik\nHP = 100, 120\nMAttack = 12, 14\nROF = 1.9\nArmor = 2\nPierceArmor = 2\nClass = {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    ratha: {
      content: `Name = Ratha\nHP = 105, 115\nMAttack = 10, 12\nPAttack = 5, 6\nROF = 2.0\nArmor = 2\nPierceArmor = 1, 2\nAttackBonus = +1 vs {{2class|Spearman}}\nClass = {{2class|Cavalry}}, {{2class|Cavalry Archer}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Fletching, Bodkin Arrow, Bracer, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Bloodlines`,
    },
    "shrivamsha rider": {
      content: `Name = Shrivamsha Rider\nHP = 70, 80\nMAttack = 9, 11\nROF = 1.75\nArmor = 0\nPierceArmor = 1\nAttackBonus = +5, +7 vs {{2class|Archer}}\nClass = {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "hussite wagon": {
      content: `Name = Hussite Wagon\nHP = 200, 250\nPAttack = 11, 13\nROF = 3.45\nArmor = 1, 2\nPierceArmor = 7, 10\nClass = {{2class|Siege weapon}}, {{2class|Unique unit}}\n`,
      boost_tech: `Siege Engineers, Chemistry`,
    },
    "organ gun": {
      content: `Name = Organ Gun\nHP = 60, 70\nPAttack = 7, 9\nROF = 3.45\nArmor = 2\nPierceArmor = 4, 6\nAttackBonus = +1 vs {{2class|Infantry}}\nClass = {{2class|Siege weapon}}, {{2class|Gunpowder unit}}, {{2class|Unique unit}}\n`,
      boost_tech: `Siege Engineers`,
    },
    "composite bowman": {
      content: `Name = Composite Bowman\nHP = 40, 45\nPAttack = 7, 8\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +2 vs {{2class|Spearman}}\nClass = {{2class|Archer}}, {{2class|Unique unit}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring`,
    },
    "flemish militia": {
      content: `Name = Flemish Militia\nHP = 75\nMAttack = 12\nROF = 2.0\nArmor = 1\nPierceArmor = 1\nAttackBonus = +8 vs {{2class|Cavalry}}, +6 vs {{2class|Camel}}\nClass = {{2class|Infantry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons`,
    },
    serjeant: {
      content: `Name = Serjeant\nHP = 60, 75\nMAttack = 8, 11\nROF = 2.0\nArmor = 2, 3\nPierceArmor = 2, 3\nAttackBonus = +2 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons`,
    },
    "jian swordsman": {
      content: `Name = Jian Swordsman\nHP = 65, 75\nMAttack = 9, 12\nROF = 2.0\nArmor = 1, 2\nPierceArmor = 1, 2\nClass = {{2class|Infantry}}, {{2class|Unshielded}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    "xianbei raider": {
      content: `Name = Xianbei Raider\nHP = 90, 110\nMAttack = 9, 11\nROF = 1.9\nArmor = 1, 2\nPierceArmor = 1, 2\nClass = {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },

    // Non-attacking / support units
    monk: {
      content: `Name = Monk\nHP = 30\nROF = 5.5\nArmor = 0\nPierceArmor = 0\nClass = {{2class|Monk}}\n`,
      boost_tech: `Sanctity`,
    },
    missionary: {
      content: `Name = Missionary\nHP = 30\nROF = 5.5\nArmor = 0\nPierceArmor = 0\nClass = {{2class|Monk}}, {{2class|Cavalry}}\n`,
      boost_tech: `Bloodlines, Sanctity`,
    },
    "trade cart": {
      content: `Name = Trade Cart\nHP = 70\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nClass = {{2class|Trade cart}}\n`,
      boost_tech: `Caravan`,
    },
    "siege tower": {
      content: `Name = Siege Tower\nHP = 220\nROF = 2.0\nArmor = -2\nPierceArmor = 100\nClass = {{2class|Siege weapon}}\n`,
      boost_tech: ``,
    },
    "battering ram": {
      content: `Name = Battering Ram\nHP = 175\nROF = 5.0\nArmor = -3\nPierceArmor = 180\nClass = {{2class|Siege weapon}}, {{2class|Ram}}\n`,
      boost_tech: `Siege Engineers`,
    },
    "capped ram": {
      content: `Name = Capped Ram\nHP = 200\nROF = 5.0\nArmor = -3\nPierceArmor = 190\nClass = {{2class|Siege weapon}}, {{2class|Ram}}\n`,
      boost_tech: `Siege Engineers`,
    },
    "siege ram": {
      content: `Name = Siege Ram\nHP = 270\nROF = 5.0\nArmor = -3\nPierceArmor = 195\nClass = {{2class|Siege weapon}}, {{2class|Ram}}\n`,
      boost_tech: `Siege Engineers`,
    },

    // Standard Units with anti-unshielded bonuses where applicable
    skirmisher: {
      content: `Name = Skirmisher\nHP = 30\nPAttack = 2\nROF = 3.05\nArmor = 0\nPierceArmor = 3\nAttackBonus = +3 vs {{2class|Archer}}, +3 vs {{2class|Spearman}}, +3 vs {{2class|Unshielded}}\nClass = {{2class|Archer}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry`,
    },
    "elite skirmisher": {
      content: `Name = Elite Skirmisher\nHP = 35\nPAttack = 3\nROF = 3.05\nArmor = 0\nPierceArmor = 4\nAttackBonus = +4 vs {{2class|Archer}}, +3 vs {{2class|Spearman}}, +2 vs {{2class|Cavalry Archer}}, +4 vs {{2class|Unshielded}}\nClass = {{2class|Archer}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry`,
    },
    "imperial skirmisher": {
      content: `Name = Imperial Skirmisher\nHP = 35\nPAttack = 4\nROF = 3.05\nArmor = 0\nPierceArmor = 4\nAttackBonus = +5 vs {{2class|Archer}}, +3 vs {{2class|Spearman}}, +3 vs {{2class|Cavalry Archer}}, +5 vs {{2class|Unshielded}}\nClass = {{2class|Archer}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry`,
    },
    slinger: {
      content: `Name = Slinger\nHP = 40\nPAttack = 5\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +10 vs {{2class|Infantry}}, +2 vs {{2class|Spearman}}, +2 vs {{2class|Unshielded}}\nClass = {{2class|Archer}}, {{2class|Unique unit}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring`,
    },
    knight: {
      content: `Name = Knight\nHP = 100\nMAttack = 10\nROF = 1.8\nArmor = 2\nPierceArmor = 2\nClass = {{2class|Cavalry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    cavalier: {
      content: `Name = Cavalier\nHP = 120\nMAttack = 12\nROF = 1.8\nArmor = 2\nPierceArmor = 2\nClass = {{2class|Cavalry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    paladin: {
      content: `Name = Paladin\nHP = 160\nMAttack = 14\nROF = 1.9\nArmor = 2\nPierceArmor = 3\nClass = {{2class|Cavalry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    archer: {
      content: `Name = Archer\nHP = 30\nPAttack = 4\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +3 vs {{2class|Spearman}}\nClass = {{2class|Archer}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring`,
    },
    crossbowman: {
      content: `Name = Crossbowman\nHP = 35\nPAttack = 5\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +3 vs {{2class|Spearman}}\nClass = {{2class|Archer}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring`,
    },
    arbalester: {
      content: `Name = Arbalester\nHP = 40\nPAttack = 6\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +3 vs {{2class|Spearman}}\nClass = {{2class|Archer}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring`,
    },
    spearman: {
      content: `Name = Spearman\nHP = 45\nMAttack = 3\nROF = 3.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +15 vs {{2class|Cavalry}}, +12 vs {{2class|War Elephant}}, +7 vs {{2class|Camel}}\nClass = {{2class|Infantry}}, {{2class|Spearman}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    pikeman: {
      content: `Name = Pikeman\nHP = 55\nMAttack = 4\nROF = 3.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +22 vs {{2class|Cavalry}}, +25 vs {{2class|War Elephant}}, +18 vs {{2class|Camel}}\nClass = {{2class|Infantry}}, {{2class|Spearman}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    halberdier: {
      content: `Name = Halberdier\nHP = 60\nMAttack = 6\nROF = 3.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +32 vs {{2class|Cavalry}}, +28 vs {{2class|War Elephant}}, +26 vs {{2class|Camel}}\nClass = {{2class|Infantry}}, {{2class|Spearman}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    champion: {
      content: `Name = Champion\nHP = 70\nMAttack = 13\nROF = 2.0\nArmor = 1\nPierceArmor = 1\nAttackBonus = +2 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}\nChampionIcon.jpg`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons`,
    },
    "long swordsman": {
      content: `Name = Long Swordsman\nHP = 60\nMAttack = 9\nROF = 2.0\nArmor = 1\nPierceArmor = 1\nAttackBonus = +2 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons`,
    },
    "two-handed swordsman": {
      content: `Name = Two-Handed Swordsman\nHP = 60\nMAttack = 12\nROF = 2.0\nArmor = 0\nPierceArmor = 1\nAttackBonus = +2 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}\nTwohanded aoe2DE.png`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons`,
    },
    militia: {
      content: `Name = Militia\nHP = 40\nMAttack = 4\nROF = 2.0\nArmor = 0\nPierceArmor = 1\nClass = {{2class|Infantry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    "man-at-arms": {
      content: `Name = Man-at-Arms\nHP = 45\nMAttack = 6\nROF = 2.0\nArmor = 0\nPierceArmor = 1\nAttackBonus = +2 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    hussar: {
      content: `Name = Hussar\nHP = 75\nMAttack = 7\nROF = 1.9\nArmor = 0\nPierceArmor = 2\nAttackBonus = +12 vs {{2class|Monk}}\nClass = {{2class|Cavalry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "light cavalry": {
      content: `Name = Light Cavalry\nHP = 60\nMAttack = 7\nROF = 2.0\nArmor = 0\nPierceArmor = 2\nAttackBonus = +10 vs {{2class|Monk}}\nClass = {{2class|Cavalry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "scout cavalry": {
      content: `Name = Scout Cavalry\nHP = 45\nMAttack = {{Dark Age}} 3, {{Feudal Age}} 5\nROF = 2.04\nArmor = 0\nPierceArmor = 2\nAttackBonus = +6 vs {{2class|Monk}}\nClass = {{2class|Cavalry}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "camel rider": {
      content: `Name = Camel Rider\nHP = 100\nMAttack = 6\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +9 vs {{2class|Cavalry}}, +5 vs {{2class|Camel}}\nClass = {{2class|Camel}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "heavy camel rider": {
      content: `Name = Heavy Camel Rider\nHP = 120\nMAttack = 7\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +18 vs {{2class|Cavalry}}, +9 vs {{2class|Camel}}\nClass = {{2class|Camel}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor, Bloodlines`,
    },
    "cavalry archer": {
      content: `Name = Cavalry Archer\nHP = 50\nPAttack = 6\nROF = 2.0\nArmor = 0\nPierceArmor = 0\nAttackBonus = +2 vs {{2class|Spearman}}\nClass = {{2class|Archer}}, {{2class|Cavalry Archer}}, {{2class|Cavalry}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Parthian Tactics, Bloodlines`,
    },
    "heavy cavalry archer": {
      content: `Name = Heavy Cavalry Archer\nHP = 60\nPAttack = 7\nROF = 2.0\nArmor = 1\nPierceArmor = 0\nAttackBonus = +2 vs {{2class|Spearman}}\nClass = {{2class|Archer}}, {{2class|Cavalry Archer}}, {{2class|Cavalry}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Parthian Tactics, Bloodlines`,
    },
    villager: {
      content: `Name = Villager\nHP = 25\nMAttack = 3\nROF = 2.03\nArmor = 0\nPierceArmor = 0\nClass = {{2class|Villager}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Loom`,
    },
    "teutonic knight": {
      content: `Name = Teutonic Knight\nHP = 80, 100\nMAttack = 12, 17\nROF = 2.0\nArmor = 7, 10\nPierceArmor = 2\nAttackBonus = +4 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor, Gambesons`,
    },
    mangudai: {
      content: `Name = Mangudai\nHP = 60, 60\nPAttack = 6, 8\nROF = 1.68\nArmor = 0\nPierceArmor = 0, 1\nAttackBonus = +3, +5 vs {{2class|Siege weapon}}, +1 vs {{2class|Spearman}}\nClass = {{2class|Archer}}, {{2class|Cavalry Archer}}, {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Fletching, Bodkin Arrow, Bracer, Padded Archer Armor, Leather Archer Armor, Ring Archer Armor, Chemistry, Thumb Ring, Bloodlines`,
    },
    cataphract: {
      content: `Name = Cataphract\nHP = 110, 150\nMAttack = 9, 12\nROF = 1.8\nArmor = 2\nPierceArmor = 1\nAttackBonus = +9, +12 vs {{2class|Infantry}}\nClass = {{2class|Cavalry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Barding Armor, Chain Barding Armor, Plate Barding Armor`,
    },
    huskarl: {
      content: `Name = Huskarl\nHP = 60, 70\nMAttack = 10, 12\nROF = 2.0\nArmor = 0\nPierceArmor = 6, 8\nAttackBonus = +6, +10 vs {{2class|Archer}}, +2, +3 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
    samurai: {
      content: `Name = Samurai\nHP = 60, 80\nMAttack = 8, 12\nROF = 1.45\nArmor = 1\nPierceArmor = 0, 1\nAttackBonus = +10, +12 vs {{2class|Unique unit}}, +2 vs {{2class|Eagle Warrior}}\nClass = {{2class|Infantry}}, {{2class|Unique unit}}\n`,
      boost_tech: `Forging, Iron Casting, Blast Furnace, Scale Mail Armor, Chain Mail Armor, Plate Mail Armor`,
    },
  };

  return db[norm] || null;
}
