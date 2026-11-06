import React from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { X, Brain, Heart, Compass, Clock, Activity, Shield, Swords, Sparkles, Coins, Trophy } from 'lucide-react';

export const NPCProfileDrawer: React.FC = () => {
  const { state, selectedNpcId, setSelectedNpcId, setIsMemoryModalOpen, fetchNpcMemories, mapTheme } = useSimulationStore();

  if (!selectedNpcId || !state) return null;

  const npc = state.npcs.find((n) => n.id === selectedNpcId);
  if (!npc) return null;

  const handleOpenMemories = () => {
    fetchNpcMemories(npc.id);
    setIsMemoryModalOpen(true);
  };

  const portraitSrc =
    mapTheme === 'kenney_urban'
      ? `/assets/characters/profile/kenney/kenney_char_${((npc.id.charCodeAt(npc.id.length - 1) || 0) % 5) + 1}.png`
      : `/assets/characters/profile/${npc.sprite_name || 'Klaus_Mueller'}.png`;

  const maxHp = npc.max_hp || 100;
  const currentHp = Math.max(0, Math.min(npc.hp ?? 100, maxHp));
  const hpPct = currentHp / maxHp;

  const maxMana = npc.max_mana || 50;
  const currentMana = Math.max(0, Math.min(npc.mana ?? 50, maxMana));
  const manaPct = currentMana / maxMana;

  return (
    <div className="absolute right-0 top-0 bottom-0 w-96 bg-slate-900/95 backdrop-blur-xl border-l border-slate-700/70 shadow-2xl z-20 flex flex-col overflow-hidden text-slate-100 transition-all duration-300">
      {/* MMORPG Header */}
      <div className="p-4 border-b border-slate-800 flex items-start justify-between bg-slate-950/70">
        <div className="flex items-center space-x-3">
          <div className="relative w-14 h-14 rounded-2xl overflow-hidden bg-slate-800 border-2 border-slate-600 shadow-md flex-shrink-0 flex items-center justify-center">
            <img
              src={portraitSrc}
              alt={npc.name}
              className="w-full h-full object-cover"
              style={{ imageRendering: 'pixelated' }}
            />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-base font-bold text-white">{npc.name}</h2>
              <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-950 text-indigo-300 border border-indigo-700 font-bold">
                Lv.{npc.level || 1}
              </span>
            </div>
            <p className="text-xs text-sky-400 font-semibold">
              {npc.rpg_class || 'Warrior'} • {npc.role || 'DPS'}
            </p>
            <p className="text-[11px] text-amber-300 italic">"{npc.title || 'Adventurer'}"</p>
          </div>
        </div>
        <button
          onClick={() => setSelectedNpcId(null)}
          className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Scrollable Body */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* MMORPG Vital Combat Bars (HP & Mana) */}
        <div className="bg-slate-800/80 rounded-xl p-3 border border-slate-700/60 space-y-2.5">
          {/* HP Bar */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-emerald-400 font-bold flex items-center space-x-1">
                <Heart className="w-3.5 h-3.5 fill-emerald-400" />
                <span>Health (HP)</span>
              </span>
              <span className="font-mono text-slate-200">
                {currentHp} / {maxHp}
              </span>
            </div>
            <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-700/50">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-green-400 rounded-full transition-all duration-300"
                style={{ width: `${hpPct * 100}%` }}
              />
            </div>
          </div>

          {/* Mana Bar */}
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-sky-400 font-bold flex items-center space-x-1">
                <Sparkles className="w-3.5 h-3.5 text-sky-400" />
                <span>Mana (MP)</span>
              </span>
              <span className="font-mono text-slate-200">
                {currentMana} / {maxMana}
              </span>
            </div>
            <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-700/50">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full transition-all duration-300"
                style={{ width: `${manaPct * 100}%` }}
              />
            </div>
          </div>

          {/* Currency & Dungeon Clears */}
          <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-xs">
            <span className="text-yellow-400 flex items-center space-x-1 font-semibold">
              <Coins className="w-3.5 h-3.5" />
              <span>{Math.round(npc.wealth)} Gold Coins</span>
            </span>
            <span className="text-purple-300 flex items-center space-x-1 font-semibold">
              <Trophy className="w-3.5 h-3.5" />
              <span>{npc.dungeon_clears || 0} Clears</span>
            </span>
          </div>
        </div>

        {/* Current Location & Activity */}
        <div className="bg-slate-800/60 rounded-xl p-3 border border-slate-700/50 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center space-x-1">
              <Compass className="w-3.5 h-3.5 text-sky-400" />
              <span>Location:</span>
            </span>
            <span className="text-slate-200 font-semibold">{npc.current_location}</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>Activity:</span>
            </span>
            <span className="text-emerald-300 font-medium">{npc.current_activity}</span>
          </div>
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center space-x-1">
              <Swords className="w-3.5 h-3.5 text-rose-400" />
              <span>Monsters Slain:</span>
            </span>
            <span className="text-rose-300 font-bold">{npc.monsters_slain || 0} defeated</span>
          </div>
        </div>

        {/* Equipment Loadout */}
        {npc.equipment && Object.keys(npc.equipment).length > 0 && (
          <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/50 space-y-2">
            <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
              <Shield className="w-3.5 h-3.5 text-amber-400" />
              <span>Equipment Loadout</span>
            </h3>
            <div className="space-y-1.5 text-xs">
              {Object.entries(npc.equipment).map(([slot, item]) => (
                <div key={slot} className="flex justify-between items-center p-1.5 rounded-lg bg-slate-900/60 border border-slate-800">
                  <span className="text-slate-400 capitalize">{slot}:</span>
                  <span className="text-amber-200 font-semibold">{item}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Vital Needs */}
        <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 space-y-2.5">
          <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
            <Activity className="w-3.5 h-3.5 text-amber-400" />
            <span>Vital Needs</span>
          </h3>
          <div className="space-y-1.5 text-xs">
            <NeedBar label="Energy" value={npc.needs.energy} color="bg-cyan-500" />
            <NeedBar label="Hunger" value={npc.needs.hunger} color="bg-amber-500" />
            <NeedBar label="Social" value={npc.needs.social} color="bg-purple-500" />
            <NeedBar label="Fun" value={npc.needs.fun} color="bg-pink-500" />
            <NeedBar label="Purpose" value={npc.needs.purpose} color="bg-emerald-500" />
          </div>
        </div>

        {/* Schedule Summary */}
        <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 space-y-2">
          <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>Today's Daily Plan</span>
          </h3>
          <p className="text-xs text-slate-300 italic">{npc.plan_summary}</p>
        </div>
      </div>

      {/* Footer / Action Buttons */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/80">
        <button
          onClick={handleOpenMemories}
          className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-950/40 transition active:scale-[0.98]"
        >
          <Brain className="w-4 h-4" />
          <span>Inspect Memories & Reflections</span>
        </button>
      </div>
    </div>
  );
};

const NeedBar: React.FC<{ label: string; value: number; color: string }> = ({ label, value, color }) => (
  <div>
    <div className="flex justify-between text-[11px] mb-0.5">
      <span className="text-slate-400">{label}</span>
      <span className="font-semibold text-slate-300">{Math.round(value)}%</span>
    </div>
    <div className="w-full bg-slate-700/50 rounded-full h-1.5 overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-300 ${color}`}
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  </div>
);
