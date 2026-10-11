import React, { useState, useEffect, useMemo } from 'react';
import { units, elite } from './lists';
import { fetchUnitRawWiki, parseUnitStats } from './wiki';
import { compareUnits } from './calc';
import { UnitData, UnitUpgrades } from './types';
import { CIVILIZATIONS, CIV_NAMES, isUnitAvailableForCiv, ALL_CIV_TEAM_UNITS, unitStatsDependOnAge } from './civs';
import {
  Shield,
  Swords,
  RefreshCw,
  Trophy,
  Info,
  ArrowRightLeft,
  Zap,
  AlertTriangle,
  Code2,
  Copy,
  Check,
  CheckCircle2,
} from 'lucide-react';

const initialUpgrades: UnitUpgrades = {
  civilization: 'Generic',
  fullyUpgraded: false,
  fullTechTree: false,
  selectedAge: 4, // default to Imperial Age
  attackBonusTier: 0,
  armorBonusTier: 0,
  chemistry: false,
  thumbRing: false,
  bloodlines: false,
  parthianTactics: false,
  gambesons: false,
  cranequins: false,
  loom: false,
  rocketry: false,
  wootzSteel: false,
  rathaMode: 'melee',
  chargeAttackEnabled: true,
  dismountEnabled: true,
  activeUniqueTechs: [],
};

export default function App() {
  const [unit1Name, setUnit1Name] = useState<string>('Knight');
  const [unit2Name, setUnit2Name] = useState<string>('Pikeman');

  const [unit1Elite, setUnit1Elite] = useState<boolean>(false);
  const [unit2Elite, setUnit2Elite] = useState<boolean>(false);

  const [upgrades1, setUpgrades1] = useState<UnitUpgrades>({ ...initialUpgrades });
  const [upgrades2, setUpgrades2] = useState<UnitUpgrades>({ ...initialUpgrades });

  const [raw1, setRaw1] = useState<{ content: string; boost_tech: string } | null>(null);
  const [raw2, setRaw2] = useState<{ content: string; boost_tech: string } | null>(null);

  const [loading1, setLoading1] = useState<boolean>(false);
  const [loading2, setLoading2] = useState<boolean>(false);

  const [error1, setError1] = useState<string | null>(null);
  const [error2, setError2] = useState<string | null>(null);

  const [showPythonModal, setShowPythonModal] = useState<boolean>(false);
  const [copiedPython, setCopiedPython] = useState<boolean>(false);

  // Fetch unit 1 wiki data
  useEffect(() => {
    let active = true;
    setLoading1(true);
    setError1(null);
    fetchUnitRawWiki(unit1Name)
      .then((data) => {
        if (active) {
          setRaw1(data);
          setLoading1(false);
        }
      })
      .catch((err) => {
        if (active) {
          setError1(err.message || 'Failed to load wiki data');
          setLoading1(false);
        }
      });
    return () => {
      active = false;
    };
  }, [unit1Name]);

  // Fetch unit 2 wiki data
  useEffect(() => {
    let active = true;
    setLoading2(true);
    setError2(null);
    fetchUnitRawWiki(unit2Name)
      .then((data) => {
        if (active) {
          setRaw2(data);
          setLoading2(false);
        }
      })
      .catch((err) => {
        if (active) {
          setError2(err.message || 'Failed to load wiki data');
          setLoading2(false);
        }
      });
    return () => {
      active = false;
    };
  }, [unit2Name]);

  // Reset upgrades on unit change
  const handleUnit1Change = (name: string) => {
    setUnit1Name(name);
    setUnit1Elite(false);
    setUpgrades1((prev) => ({
      ...prev,
      attackBonusTier: 0,
      armorBonusTier: 0,
      chemistry: false,
      thumbRing: false,
      bloodlines: false,
      parthianTactics: false,
      gambesons: false,
      activeUniqueTechs: [],
    }));
  };

  const handleUnit2Change = (name: string) => {
    setUnit2Name(name);
    setUnit2Elite(false);
    setUpgrades2((prev) => ({
      ...prev,
      attackBonusTier: 0,
      armorBonusTier: 0,
      chemistry: false,
      thumbRing: false,
      bloodlines: false,
      parthianTactics: false,
      gambesons: false,
      activeUniqueTechs: [],
    }));
  };

  // Swap units function
  const handleSwapUnits = () => {
    const tempName = unit1Name;
    const tempElite = unit1Elite;
    const tempUpgrades = upgrades1;
    const tempRaw = raw1;

    setUnit1Name(unit2Name);
    setUnit1Elite(unit2Elite);
    setUpgrades1(upgrades2);
    setRaw1(raw2);

    setUnit2Name(tempName);
    setUnit2Elite(tempElite);
    setUpgrades2(tempUpgrades);
    setRaw2(tempRaw);
  };

  // Parsed unit models
  const unit1: UnitData | null = useMemo(() => {
    if (!raw1) return null;
    return parseUnitStats(raw1.content, raw1.boost_tech, unit1Elite, upgrades1.selectedAge);
  }, [raw1, unit1Elite, upgrades1.selectedAge]);

  const unit2: UnitData | null = useMemo(() => {
    if (!raw2) return null;
    return parseUnitStats(raw2.content, raw2.boost_tech, unit2Elite, upgrades2.selectedAge);
  }, [raw2, unit2Elite, upgrades2.selectedAge]);

  // Combat comparison
  const comparison = useMemo(() => {
    if (!unit1 || !unit2) return null;
    return compareUnits(unit1, unit2, upgrades1, upgrades2);
  }, [unit1, unit2, upgrades1, upgrades2]);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <header className="mb-8 border-b border-stone-200 pb-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-amber-700 text-white rounded-lg shadow-sm">
              <Swords className="w-7 h-7" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-stone-900">
                Age of Empires 2 1v1 Battle Calculator
              </h1>
              <p className="text-sm text-stone-600 mt-1">
                Precise civ availability, unique tech toggles, Full Tech Tree & FU modes, age-specific scaling, and unique mechanics.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2 self-start sm:self-center">
            <button
              type="button"
              onClick={() => setShowPythonModal(true)}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-stone-900 text-white rounded-lg hover:bg-stone-800 transition-colors shadow-xs"
              title="View Python Streamlit source"
            >
              <Code2 className="w-4 h-4" /> Python (Streamlit)
            </button>
            <button
              type="button"
              onClick={handleSwapUnits}
              className="inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg border border-stone-300 transition-colors shadow-xs"
              title="Swap Unit 1 and Unit 2"
            >
              <ArrowRightLeft className="w-4 h-4" /> Swap
            </button>
          </div>
        </div>
      </header>

      {/* Main Grid: Unit 1 and Unit 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Unit 1 Column */}
        <UnitCard
          unitNumber={1}
          selectedUnit={unit1Name}
          onSelectUnit={handleUnit1Change}
          isElite={unit1Elite}
          onToggleElite={setUnit1Elite}
          unitData={unit1}
          upgrades={upgrades1}
          onUpdateUpgrades={setUpgrades1}
          loading={loading1}
          error={error1}
        />

        {/* Unit 2 Column */}
        <UnitCard
          unitNumber={2}
          selectedUnit={unit2Name}
          onSelectUnit={handleUnit2Change}
          isElite={unit2Elite}
          onToggleElite={setUnit2Elite}
          unitData={unit2}
          upgrades={upgrades2}
          onUpdateUpgrades={setUpgrades2}
          loading={loading2}
          error={error2}
        />
      </div>

      {/* Results Section */}
      <section className="bg-white rounded-xl shadow-sm border border-stone-200 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 pb-3 border-b border-stone-200 gap-2">
          <h2 className="text-xl font-bold flex items-center gap-2 text-stone-900">
            <Trophy className="w-5 h-5 text-amber-600" />
            1v1 Battle Simulation Outcome
          </h2>
          {comparison && (
            <span
              className={`px-3 py-1 rounded-full text-xs font-semibold self-start sm:self-auto ${
                comparison.winner === 'error'
                  ? 'bg-red-100 text-red-900 border border-red-300'
                  : comparison.winner === 'unit1'
                  ? 'bg-amber-100 text-amber-900 border border-amber-300'
                  : comparison.winner === 'unit2'
                  ? 'bg-indigo-100 text-indigo-900 border border-indigo-300'
                  : 'bg-stone-100 text-stone-700 border border-stone-300'
              }`}
            >
              {comparison.winner === 'error'
                ? 'Unavailable Unit Error'
                : comparison.winner === 'unit1'
                ? `Winner: ${unit1?.name} (${upgrades1.civilization}) 👑`
                : comparison.winner === 'unit2'
                ? `Winner: ${unit2?.name} (${upgrades2.civilization}) 👑`
                : 'Stalemate / Tie'}
            </span>
          )}
        </div>

        {!unit1 || !unit2 || !comparison ? (
          <div className="py-8 text-center text-stone-500 flex flex-col items-center justify-center gap-2">
            <RefreshCw className="w-6 h-6 animate-spin text-stone-400" />
            <span>Calculating battle statistics...</span>
          </div>
        ) : comparison.winner === 'error' ? (
          <div className="p-4 bg-red-50 border border-red-300 rounded-lg text-red-800 font-semibold flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <span className="text-sm whitespace-pre-wrap">{comparison.error}</span>
          </div>
        ) : (
          <div>
            {/* Visual Comparison Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              {/* Unit 1 Stats Card */}
              <div
                className={`p-4 rounded-lg border ${
                  comparison.winner === 'unit1'
                    ? 'bg-amber-50/70 border-amber-300'
                    : 'bg-stone-50 border-stone-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-bold text-stone-900">{comparison.unit1Name}</h3>
                    <span className="text-xs text-stone-500 font-medium">{upgrades1.civilization}</span>
                  </div>
                  {comparison.winner === 'unit1' && (
                    <span className="text-xs font-bold text-amber-800 bg-amber-200/80 px-2 py-0.5 rounded">
                      VICTOR
                    </span>
                  )}
                </div>
                <div className="space-y-1.5 text-sm text-stone-700">
                  {comparison.unit1CanAttack ? (
                    <>
                      <div className="flex justify-between">
                        <span>Damage per hit:</span>
                        <span className="font-semibold">
                          {comparison.unit1DamagePerHit}{' '}
                          {comparison.unit1BonusDmg > 0 && `(+${comparison.unit1BonusDmg} bonus)`}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Hits to kill {comparison.unit2Name}:</span>
                        <span className="font-semibold">{comparison.hits1} hits</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Time to kill:</span>
                        <span className="font-semibold">{comparison.time1.toFixed(2)} seconds</span>
                      </div>
                      {comparison.unit1MechanicSummary && (
                        <div className="text-xs text-amber-800 bg-amber-100/60 p-1.5 rounded mt-1">
                          ⚡ {comparison.unit1MechanicSummary}
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="py-2 text-stone-500 italic text-xs">
                      This unit cannot attack (deals 0 damage).
                    </div>
                  )}
                </div>
              </div>

              {/* Unit 2 Stats Card */}
              <div
                className={`p-4 rounded-lg border ${
                  comparison.winner === 'unit2'
                    ? 'bg-indigo-50/70 border-indigo-300'
                    : 'bg-stone-50 border-stone-200'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <h3 className="font-bold text-stone-900">{comparison.unit2Name}</h3>
                    <span className="text-xs text-stone-500 font-medium">{upgrades2.civilization}</span>
                  </div>
                  {comparison.winner === 'unit2' && (
                    <span className="text-xs font-bold text-indigo-800 bg-indigo-200/80 px-2 py-0.5 rounded">
                      VICTOR
                    </span>
                  )}
                </div>
                <div className="space-y-1.5 text-sm text-stone-700">
                  {comparison.unit2CanAttack ? (
                    <>
                      <div className="flex justify-between">
                        <span>Damage per hit:</span>
                        <span className="font-semibold">
                          {comparison.unit2DamagePerHit}{' '}
                          {comparison.unit2BonusDmg > 0 && `(+${comparison.unit2BonusDmg} bonus)`}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span>Hits to kill {comparison.unit1Name}:</span>
                        <span className="font-semibold">{comparison.hits2} hits</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Time to kill:</span>
                        <span className="font-semibold">{comparison.time2.toFixed(2)} seconds</span>
                      </div>
                      {comparison.unit2MechanicSummary && (
                        <div className="text-xs text-indigo-800 bg-indigo-100/60 p-1.5 rounded mt-1">
                          ⚡ {comparison.unit2MechanicSummary}
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="py-2 text-stone-500 italic text-xs">
                      This unit cannot attack (deals 0 damage).
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Streamlit-Exact Output Text */}
            <div className="mt-4 p-4 bg-stone-900 text-stone-100 rounded-lg font-mono text-sm whitespace-pre-wrap leading-relaxed shadow-inner">
              {comparison.rawText}
            </div>
          </div>
        )}
      </section>

      {/* Raw Unit Stats Display */}
      <section className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        {unit1 && (
          <div className="bg-white p-5 rounded-xl border border-stone-200 shadow-sm">
            <h3 className="font-bold text-stone-900 mb-2 flex items-center gap-2">
              <Info className="w-4 h-4 text-stone-500" />
              {unit1.name} Raw Properties ({upgrades1.civilization})
            </h3>
            <pre className="p-3 bg-stone-50 text-stone-800 rounded font-mono text-xs overflow-x-auto whitespace-pre-wrap border border-stone-200">
              {formatUnitStats(unit1)}
            </pre>
          </div>
        )}
        {unit2 && (
          <div className="bg-white p-5 rounded-xl border border-stone-200 shadow-sm">
            <h3 className="font-bold text-stone-900 mb-2 flex items-center gap-2">
              <Info className="w-4 h-4 text-stone-500" />
              {unit2.name} Raw Properties ({upgrades2.civilization})
            </h3>
            <pre className="p-3 bg-stone-50 text-stone-800 rounded font-mono text-xs overflow-x-auto whitespace-pre-wrap border border-stone-200">
              {formatUnitStats(unit2)}
            </pre>
          </div>
        )}
      </section>

      {/* Modal for Python Streamlit Code */}
      {showPythonModal && (
        <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[85vh] flex flex-col overflow-hidden border border-stone-200">
            <div className="p-4 border-b border-stone-200 flex items-center justify-between bg-stone-50">
              <div>
                <h3 className="font-bold text-stone-900">aoe_sl.py (Streamlit Compatible)</h3>
                <p className="text-xs text-stone-500">
                  Ready to copy and run directly with <code className="font-mono bg-stone-200 px-1 rounded">streamlit run aoe_sl.py</code>.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => {
                    navigator.clipboard.writeText(pythonCodeSnippet);
                    setCopiedPython(true);
                    setTimeout(() => setCopiedPython(false), 2000);
                  }}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-amber-600 text-white rounded-lg hover:bg-amber-700"
                >
                  {copiedPython ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  {copiedPython ? 'Copied!' : 'Copy Code'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowPythonModal(false)}
                  className="px-3 py-1.5 text-xs font-semibold bg-stone-200 hover:bg-stone-300 rounded-lg text-stone-800"
                >
                  Close
                </button>
              </div>
            </div>
            <div className="p-4 overflow-y-auto font-mono text-xs bg-stone-900 text-stone-200 whitespace-pre">
              {pythonCodeSnippet}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function formatUnitStats(u: UnitData): string {
  let bonusStr = 'None';
  if (u.attack_bonus) {
    bonusStr = Object.entries(u.attack_bonus)
      .map(([k, v]) => `+${v} vs ${k}`)
      .join(', ');
  }
  let classStr = u.armor_class ? u.armor_class.join(', ') : 'None';

  return `Name: ${u.name}
HP: ${u.hp}
PAttack: ${u.p_attack !== null ? u.p_attack : 'None'}
MAttack: ${u.m_attack !== null ? u.m_attack : 'None'}
ROF: ${u.rof}
Armor: ${u.armor}
PierceArmor: ${u.pierce_armor}
Attack Bonus: ${bonusStr}
Armor Class: ${classStr}${
    u.uniqueMechanic ? `\nUnique Mechanic: [${u.uniqueMechanic.type}] ${u.uniqueMechanic.description}` : ''
  }`;
}

interface UnitCardProps {
  unitNumber: number;
  selectedUnit: string;
  onSelectUnit: (name: string) => void;
  isElite: boolean;
  onToggleElite: (val: boolean) => void;
  unitData: UnitData | null;
  upgrades: UnitUpgrades;
  onUpdateUpgrades: React.Dispatch<React.SetStateAction<UnitUpgrades>>;
  loading: boolean;
  error: string | null;
}

function UnitCard({
  unitNumber,
  selectedUnit,
  onSelectUnit,
  isElite,
  onToggleElite,
  unitData,
  upgrades,
  onUpdateUpgrades,
  loading,
  error,
}: UnitCardProps) {
  const civ = CIVILIZATIONS[upgrades.civilization] || CIVILIZATIONS['Generic'];
  const isAvailable = isUnitAvailableForCiv(selectedUnit, upgrades.civilization);
  const isTeamUnit = ALL_CIV_TEAM_UNITS.some((tu) => tu.toLowerCase() === selectedUnit.toLowerCase());
  const needsAgeSelection = unitStatsDependOnAge(selectedUnit);

  const canBeElite = elite.includes(selectedUnit);
  const boostTech = unitData?.boost_tech || '';
  const mechanic = unitData?.uniqueMechanic;

  const hasFletching = boostTech.includes('Fletching');
  const hasForging = boostTech.includes('Forging');

  const hasArcherArmor = boostTech.includes('Padded Archer Armor');
  const hasCavArmor = boostTech.includes('Scale Barding Armor');
  const hasInfArmor = boostTech.includes('Scale Mail Armor');

  const hasChemistry = boostTech.includes('Chemistry');
  const hasThumbRing =
    boostTech.includes('Thumb Ring') &&
    !selectedUnit.includes('Skirmisher') &&
    !selectedUnit.includes('Genitour');
  const hasBloodlines = boostTech.includes('Bloodlines');
  const hasParthian = boostTech.includes('Parthian Tactics');
  const hasGambesons = boostTech.includes('Gambesons');
  const hasCranequins = boostTech.includes('Cranequins');
  const isVillager = selectedUnit.includes('Villager');

  const isChuKoNu = selectedUnit.toLowerCase().includes('chu ko nu');
  const isUrumi = selectedUnit.toLowerCase().includes('urumi');
  const isRatha = selectedUnit.toLowerCase().includes('ratha');
  const isCoustillier = selectedUnit.toLowerCase().includes('coustillier');
  const isKonnik = selectedUnit.toLowerCase().includes('konnik');

  const hasNoAttack =
    unitData &&
    unitData.p_attack === null &&
    unitData.m_attack === null &&
    !unitData.uniqueMechanic?.supportsRangedMode;

  // Relevant unique techs for this unit & civilization
  const relevantUniqueTechs = civ.uniqueTechs.filter((t) => t.appliesTo(selectedUnit, civ.name));

  return (
    <div className="bg-white rounded-xl shadow-sm border border-stone-200 p-6 flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-stone-900 flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-stone-800 text-white text-xs flex items-center justify-center font-mono">
              {unitNumber}
            </span>
            Unit {unitNumber}
          </h2>
          {loading && (
            <span className="text-xs text-stone-500 flex items-center gap-1">
              <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Fetching stats...
            </span>
          )}
        </div>

        {/* Civilization Dropdown */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-stone-600 mb-1">
            Civilization
          </label>
          <select
            className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-2 text-stone-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
            value={upgrades.civilization}
            onChange={(e) =>
              onUpdateUpgrades((u) => ({
                ...u,
                civilization: e.target.value,
                activeUniqueTechs: [],
              }))
            }
          >
            {CIV_NAMES.map((c) => (
              <option key={c} value={c}>
                {c} {c === 'Generic' ? '(Standard Tech Tree)' : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Unit Selector */}
        <div className="mb-4">
          <label className="block text-xs font-semibold text-stone-600 mb-1">
            Unit Selection
          </label>
          <select
            className="w-full bg-stone-50 border border-stone-300 rounded-lg px-3 py-2 text-stone-900 text-sm focus:ring-2 focus:ring-amber-500 focus:outline-none"
            value={selectedUnit}
            onChange={(e) => onSelectUnit(e.target.value)}
          >
            {units.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
        </div>

        {/* Civ Availability Error Message */}
        {!isAvailable && (
          <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-lg text-red-900 text-xs flex items-start gap-2 font-medium">
            <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
            <span>
              <strong>{upgrades.civilization}</strong> does not get access to <strong>{selectedUnit}</strong>.
            </span>
          </div>
        )}

        {isTeamUnit && upgrades.civilization !== 'Generic' && (
          <div className="mb-3 px-2 py-1 bg-emerald-50 border border-emerald-200 rounded text-emerald-800 text-[11px] flex items-center gap-1.5 font-medium">
            <span>✨ Team bonus unit: Available to all civilizations</span>
          </div>
        )}

        {/* Toggles: Full Tech Tree and Fully Upgraded */}
        <div className="mb-4 p-2.5 bg-stone-50 rounded-lg border border-stone-200 grid grid-cols-2 gap-2">
          <label className="flex items-center gap-2 text-xs font-semibold text-stone-800 cursor-pointer">
            <input
              type="checkbox"
              checked={upgrades.fullTechTree}
              onChange={(e) =>
                onUpdateUpgrades((u) => ({ ...u, fullTechTree: e.target.checked }))
              }
              className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
            />
            Full Tech Tree (All Techs)
          </label>
          <label className="flex items-center gap-2 text-xs font-semibold text-amber-900 cursor-pointer">
            <input
              type="checkbox"
              checked={upgrades.fullyUpgraded}
              onChange={(e) =>
                onUpdateUpgrades((u) => ({ ...u, fullyUpgraded: e.target.checked }))
              }
              className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
            />
            Fully Upgraded (FU)
          </label>
        </div>

        {/* Unique Mechanic Badge & Details */}
        {mechanic && (
          <div className="mb-4 p-3 bg-amber-50/80 border border-amber-200/90 rounded-lg text-amber-900 text-xs">
            <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-[11px] text-amber-800 mb-1">
              <Zap className="w-3.5 h-3.5 text-amber-600" />
              Unique Mechanic: {mechanic.type.replace('_', ' ')}
            </div>
            <p className="text-stone-700 leading-relaxed">{mechanic.description}</p>
          </div>
        )}

        {/* Non-attacking unit badge */}
        {hasNoAttack && (
          <div className="mb-4 p-2.5 bg-blue-50 border border-blue-200 rounded-lg text-blue-800 text-xs flex items-center gap-2">
            <Shield className="w-4 h-4 flex-shrink-0" />
            <span>Support / Non-attacking unit (deals 0 damage in combat)</span>
          </div>
        )}

        {/* Elite Checkbox */}
        {canBeElite && (
          <div className="mb-4 flex items-center gap-2">
            <input
              type="checkbox"
              id={`elite-${unitNumber}`}
              checked={isElite}
              onChange={(e) => onToggleElite(e.target.checked)}
              className="w-4 h-4 text-amber-600 rounded border-stone-300 focus:ring-amber-500"
            />
            <label htmlFor={`elite-${unitNumber}`} className="text-sm font-medium text-stone-800 cursor-pointer">
              Elite {selectedUnit}?
            </label>
          </div>
        )}

        {/* Ratha Mode Selector */}
        {isRatha && (
          <div className="mb-4">
            <label className="block text-xs font-semibold text-stone-600 mb-1">
              Ratha Combat Mode:
            </label>
            <div className="grid grid-cols-2 gap-1 p-1 bg-stone-100 rounded-lg border border-stone-200">
              <button
                type="button"
                onClick={() => onUpdateUpgrades((u) => ({ ...u, rathaMode: 'melee' }))}
                className={`py-1 text-xs font-medium rounded transition-colors ${
                  upgrades.rathaMode !== 'ranged'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'text-stone-700 hover:bg-stone-200'
                }`}
              >
                Melee Mode ({isElite ? '12 Atk' : '10 Atk'})
              </button>
              <button
                type="button"
                onClick={() => onUpdateUpgrades((u) => ({ ...u, rathaMode: 'ranged' }))}
                className={`py-1 text-xs font-medium rounded transition-colors ${
                  upgrades.rathaMode === 'ranged'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'text-stone-700 hover:bg-stone-200'
                }`}
              >
                Ranged Mode ({isElite ? '6 Pierce' : '5 Pierce'})
              </button>
            </div>
          </div>
        )}

        {/* Age Selector ONLY for units where age influences stats */}
        {needsAgeSelection && (
          <div className="mb-5">
            <label className="block text-xs font-semibold text-stone-600 mb-1.5">
              Select Age for {selectedUnit}:
            </label>
            <div className="grid grid-cols-4 gap-1 p-1 bg-stone-100 rounded-lg border border-stone-200">
              {[
                { id: 1, label: 'Dark' },
                { id: 2, label: 'Feudal' },
                { id: 3, label: 'Castle' },
                { id: 4, label: 'Imperial' },
              ].map((age) => (
                <button
                  key={age.id}
                  type="button"
                  onClick={() => onUpdateUpgrades((u) => ({ ...u, selectedAge: age.id }))}
                  className={`py-1 text-xs font-medium rounded transition-colors ${
                    upgrades.selectedAge === age.id
                      ? 'bg-white text-stone-900 shadow-sm border border-stone-200 font-bold'
                      : 'text-stone-600 hover:text-stone-900'
                  }`}
                >
                  {age.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-xs">
            {error}
          </div>
        )}

        {/* Unit Current Base Stats Preview */}
        {unitData && (
          <div className="mb-5 grid grid-cols-4 gap-2 bg-stone-50 p-3 rounded-lg border border-stone-200 text-center">
            <div>
              <span className="block text-[10px] uppercase font-bold text-stone-500">HP</span>
              <span className="font-bold text-stone-900 text-sm">{unitData.hp}</span>
            </div>
            <div>
              <span className="block text-[10px] uppercase font-bold text-stone-500">
                {unitData.p_attack !== null ? 'P. Attack' : unitData.m_attack !== null ? 'M. Attack' : 'Attack'}
              </span>
              <span className="font-bold text-stone-900 text-sm">
                {unitData.p_attack !== null
                  ? unitData.p_attack
                  : unitData.m_attack !== null
                  ? unitData.m_attack
                  : '0'}
              </span>
            </div>
            <div>
              <span className="block text-[10px] uppercase font-bold text-stone-500">Armor</span>
              <span className="font-bold text-stone-900 text-sm">
                {unitData.armor}/{unitData.pierce_armor}
              </span>
            </div>
            <div>
              <span className="block text-[10px] uppercase font-bold text-stone-500">ROF</span>
              <span className="font-bold text-stone-900 text-sm">{unitData.rof}s</span>
            </div>
          </div>
        )}

        {/* Upgrades Section: Displayed EXCEPT when FU is selected */}
        {unitData && upgrades.fullyUpgraded ? (
          <div className="border-t border-stone-200 pt-3 pb-1">
            <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-amber-600 flex-shrink-0" />
              <span>
                <strong>Fully Upgraded (FU) Active:</strong> All available blacksmith, technology, and unique upgrades are automatically maximized for {upgrades.civilization} {upgrades.fullTechTree ? '(All Techs unlocked)' : ''}.
              </span>
            </div>
          </div>
        ) : unitData && (
          <div className="border-t border-stone-200 pt-4 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-stone-500">
                Upgrades Selection
              </h3>
              {upgrades.fullTechTree && (
                <span className="text-[10px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                  Full Tech Tree Active
                </span>
              )}
            </div>

            {/* Attack Upgrades */}
            {hasFletching && (
              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">
                  Attack Upgrades (Archery)
                </label>
                <div className="grid grid-cols-4 gap-1 p-1 bg-stone-100 rounded-lg border border-stone-200">
                  {['None', 'Fletching', 'Bodkin', 'Bracer'].map((name, idx) => {
                    const isDisabled =
                      !upgrades.fullTechTree &&
                      upgrades.civilization !== 'Generic' &&
                      idx > civ.maxRangedAttack;
                    const isSelected = upgrades.attackBonusTier === idx;
                    return (
                      <button
                        key={name}
                        type="button"
                        disabled={isDisabled}
                        onClick={() => onUpdateUpgrades((u) => ({ ...u, attackBonusTier: idx }))}
                        className={`py-1 text-xs font-medium rounded transition-colors ${
                          isSelected
                            ? 'bg-amber-600 text-white shadow-sm font-bold'
                            : isDisabled
                            ? 'text-stone-400 opacity-40 cursor-not-allowed'
                            : 'text-stone-700 hover:bg-stone-200'
                        }`}
                      >
                        {name}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {hasForging && (
              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">
                  Attack Upgrades (Melee)
                </label>
                <div className="grid grid-cols-4 gap-1 p-1 bg-stone-100 rounded-lg border border-stone-200">
                  {['None', 'Forging', 'Iron Cast.', 'Blast Furn.'].map((name, idx) => {
                    const isDisabled =
                      !upgrades.fullTechTree &&
                      upgrades.civilization !== 'Generic' &&
                      idx > civ.maxMeleeAttack;
                    const isSelected = upgrades.attackBonusTier === idx;
                    return (
                      <button
                        key={name}
                        type="button"
                        disabled={isDisabled}
                        onClick={() => onUpdateUpgrades((u) => ({ ...u, attackBonusTier: idx }))}
                        className={`py-1 text-xs font-medium rounded transition-colors ${
                          isSelected
                            ? 'bg-amber-600 text-white shadow-sm font-bold'
                            : isDisabled
                            ? 'text-stone-400 opacity-40 cursor-not-allowed'
                            : 'text-stone-700 hover:bg-stone-200'
                        }`}
                      >
                        {name}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Armor Upgrades */}
            {(hasArcherArmor || hasCavArmor || hasInfArmor) && (
              <div>
                <label className="block text-xs font-semibold text-stone-700 mb-1">
                  Armor Upgrades ({hasArcherArmor ? 'Archer' : hasCavArmor ? 'Cavalry' : 'Infantry'})
                </label>
                <div className="grid grid-cols-4 gap-1 p-1 bg-stone-100 rounded-lg border border-stone-200">
                  {(hasArcherArmor
                    ? ['None', 'Padded', 'Leather', 'Ring Armor']
                    : hasCavArmor
                    ? ['None', 'Scale B.', 'Chain B.', 'Plate B.']
                    : ['None', 'Scale Mail', 'Chain Mail', 'Plate Mail']
                  ).map((name, idx) => {
                    const maxTier = hasArcherArmor
                      ? civ.maxArcherArmor
                      : hasCavArmor
                      ? civ.maxCavalryArmor
                      : civ.maxInfantryArmor;
                    const isDisabled =
                      !upgrades.fullTechTree &&
                      upgrades.civilization !== 'Generic' &&
                      idx > maxTier;
                    const isSelected = upgrades.armorBonusTier === idx;

                    return (
                      <button
                        key={name}
                        type="button"
                        disabled={isDisabled}
                        onClick={() => onUpdateUpgrades((u) => ({ ...u, armorBonusTier: idx }))}
                        className={`py-1 text-xs font-medium rounded transition-colors ${
                          isSelected
                            ? 'bg-stone-800 text-white shadow-sm font-bold'
                            : isDisabled
                            ? 'text-stone-400 opacity-40 cursor-not-allowed'
                            : 'text-stone-700 hover:bg-stone-200'
                        }`}
                      >
                        {name}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* General Tech Checkboxes */}
            <div className="grid grid-cols-2 gap-2 pt-2">
              {hasChemistry && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={!upgrades.fullTechTree && !civ.hasChemistry}
                    checked={upgrades.chemistry}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, chemistry: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Chemistry (+1 Atk)
                </label>
              )}
              {hasThumbRing && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={!upgrades.fullTechTree && !civ.hasThumbRing}
                    checked={upgrades.thumbRing}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, thumbRing: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Thumb Ring (Faster ROF)
                </label>
              )}
              {hasBloodlines && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={!upgrades.fullTechTree && !civ.hasBloodlines}
                    checked={upgrades.bloodlines}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, bloodlines: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Bloodlines (+20 HP)
                </label>
              )}
              {hasParthian && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={!upgrades.fullTechTree && !civ.hasParthianTactics}
                    checked={upgrades.parthianTactics}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, parthianTactics: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Parthian Tactics
                </label>
              )}
              {hasGambesons && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={!upgrades.fullTechTree && !civ.hasGambesons}
                    checked={upgrades.gambesons}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, gambesons: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Gambesons (+1 P.Armor)
                </label>
              )}
              {hasCranequins && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={upgrades.cranequins}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, cranequins: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Cranequins (+2 vs Inf)
                </label>
              )}
              {isVillager && (
                <label className="flex items-center gap-2 text-xs font-medium text-stone-700 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={upgrades.loom}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, loom: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Loom (+15 HP, +1/+2 Armor)
                </label>
              )}

              {/* Unique Unit specific mechanics */}
              {isChuKoNu && (
                <label className="flex items-center gap-2 text-xs font-medium text-amber-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={upgrades.rocketry || false}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, rocketry: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Rocketry (+2 Atk)
                </label>
              )}
              {isUrumi && (
                <label className="flex items-center gap-2 text-xs font-medium text-amber-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={upgrades.wootzSteel || false}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, wootzSteel: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Wootz Steel (Ignore Armor)
                </label>
              )}
              {(isCoustillier || isUrumi) && (
                <label className="flex items-center gap-2 text-xs font-medium text-amber-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={upgrades.chargeAttackEnabled !== false}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, chargeAttackEnabled: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Charge Attack Active
                </label>
              )}
              {isKonnik && (
                <label className="flex items-center gap-2 text-xs font-medium text-amber-800 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={upgrades.dismountEnabled !== false}
                    onChange={(e) =>
                      onUpdateUpgrades((u) => ({ ...u, dismountEnabled: e.target.checked }))
                    }
                    className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300"
                  />
                  Dismount on Death
                </label>
              )}
            </div>

            {/* Relevant Civ Unique Techs */}
            {relevantUniqueTechs.length > 0 && (
              <div className="pt-2 border-t border-stone-200">
                <span className="block text-[11px] font-bold text-amber-900 uppercase tracking-wider mb-1">
                  {upgrades.civilization} Unique Technologies
                </span>
                <div className="space-y-1.5">
                  {relevantUniqueTechs.map((tech) => {
                    const isChecked = (upgrades.activeUniqueTechs || []).includes(tech.id);
                    return (
                      <label
                        key={tech.id}
                        className="flex items-start gap-2 text-xs font-medium text-stone-800 cursor-pointer p-1.5 rounded hover:bg-stone-100"
                      >
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => {
                            const cur = upgrades.activeUniqueTechs || [];
                            const next = e.target.checked
                              ? [...cur, tech.id]
                              : cur.filter((id) => id !== tech.id);
                            onUpdateUpgrades((u) => ({ ...u, activeUniqueTechs: next }));
                          }}
                          className="w-3.5 h-3.5 text-amber-600 rounded border-stone-300 mt-0.5"
                        />
                        <div>
                          <span className="font-semibold">{tech.name}</span>{' '}
                          <span className="text-[10px] text-stone-500">({tech.age} Age)</span>
                          <p className="text-[11px] text-stone-600 font-normal leading-tight">
                            {tech.effectDescription}
                          </p>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const pythonCodeSnippet = `# aoe_sl.py - Age of Empires 2 1v1 Battle Calculator
# Compatible with Streamlit. Run: streamlit run aoe_sl.py

import streamlit as st
import requests
import re

# Complete Civilizations List
CIVILIZATIONS = [
    "Generic", "Armenians", "Aztecs", "Bengalis", "Berbers", "Bohemians",
    "Britons", "Bulgarians", "Burgundians", "Burmese", "Byzantines", "Celts",
    "Chinese", "Cumans", "Dravidians", "Ethiopians", "Franks", "Georgians",
    "Goths", "Gurjaras", "Hindustanis", "Huns", "Incas", "Italians",
    "Japanese", "Khmer", "Koreans", "Lithuanians", "Magyars", "Malay",
    "Malians", "Mayans", "Mongols", "Persians", "Poles", "Portuguese",
    "Romans", "Saracens", "Sicilians", "Slavs", "Spanish", "Tatars",
    "Teutons", "Turks", "Vietnamese", "Vikings"
]

ALL_CIV_TEAM_UNITS = [
    "Condottiero", "Genitour", "Elite Genitour",
    "Imperial Skirmisher", "Kipchak", "Elite Kipchak"
]
`;
