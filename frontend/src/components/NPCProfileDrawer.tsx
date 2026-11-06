import React from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { X, Brain, Heart, Compass, Clock, Activity, Target, Users } from 'lucide-react';

export const NPCProfileDrawer: React.FC = () => {
  const { state, selectedNpcId, setSelectedNpcId, setIsMemoryModalOpen, fetchNpcMemories } = useSimulationStore();

  if (!selectedNpcId || !state) return null;

  const npc = state.npcs.find((n) => n.id === selectedNpcId);
  if (!npc) return null;

  const handleOpenMemories = () => {
    fetchNpcMemories(npc.id);
    setIsMemoryModalOpen(true);
  };

  return (
    <div className="absolute right-0 top-0 bottom-0 w-96 bg-slate-900/95 backdrop-blur-xl border-l border-slate-700/70 shadow-2xl z-20 flex flex-col overflow-hidden text-slate-100 transition-all duration-300">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 flex items-start justify-between bg-slate-950/60">
        <div className="flex items-center space-x-3">
          <div className="relative w-14 h-14 rounded-2xl overflow-hidden bg-slate-800 border-2 border-slate-600 shadow-md flex-shrink-0 flex items-center justify-center">
            <img
              src={`/assets/characters/profile/${npc.sprite_name || 'Klaus_Mueller'}.png`}
              alt={npc.name}
              className="w-full h-full object-cover"
              style={{ imageRendering: 'pixelated' }}
            />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <span>{npc.name}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-normal">
                Age {npc.age}
              </span>
            </h2>
            <p className="text-xs text-sky-400 font-medium">{npc.occupation}</p>
            <p className="text-[11px] text-slate-400">Wealth: §{npc.wealth} | Memories: {npc.memory_count}</p>
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
        {/* Status Card */}
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
              <Heart className="w-3.5 h-3.5 text-rose-400" />
              <span>Emotion:</span>
            </span>
            <span className="px-2 py-0.5 rounded-full bg-rose-950/60 text-rose-300 border border-rose-800/50 font-semibold text-[11px]">
              {npc.emotion.current} (Valence {npc.emotion.valence > 0 ? `+${npc.emotion.valence}` : npc.emotion.valence})
            </span>
          </div>
        </div>

        {/* Biological Needs */}
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

        {/* Big Five Personality */}
        <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 space-y-2.5">
          <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
            <Brain className="w-3.5 h-3.5 text-indigo-400" />
            <span>Personality Matrix (Big Five)</span>
          </h3>
          <div className="space-y-1 text-[11px]">
            <TraitBar label="Openness" value={npc.personality.openness} />
            <TraitBar label="Conscientiousness" value={npc.personality.conscientiousness} />
            <TraitBar label="Extraversion" value={npc.personality.extraversion} />
            <TraitBar label="Agreeableness" value={npc.personality.agreeableness} />
            <TraitBar label="Neuroticism" value={npc.personality.neuroticism} />
          </div>
        </div>

        {/* Goals & Beliefs */}
        <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 space-y-2">
          <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
            <Target className="w-3.5 h-3.5 text-rose-400" />
            <span>Life Objectives & Beliefs</span>
          </h3>
          {npc.goals && npc.goals.length > 0 && (
            <div className="space-y-1">
              <span className="text-[11px] text-slate-400 font-semibold">Current Goal:</span>
              <p className="text-xs text-sky-200 bg-sky-950/40 p-2 rounded-lg border border-sky-800/40">
                {npc.goals[0]}
              </p>
            </div>
          )}
          {npc.beliefs && npc.beliefs.length > 0 && (
            <div className="space-y-1">
              <span className="text-[11px] text-slate-400 font-semibold">Core Belief:</span>
              <p className="text-xs text-slate-300 bg-slate-900/60 p-2 rounded-lg border border-slate-800 italic">
                "{npc.beliefs[0]}"
              </p>
            </div>
          )}
        </div>

        {/* Relationships */}
        <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/50 space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
              <Users className="w-3.5 h-3.5 text-blue-400" />
              <span>Social Bonds ({npc.relationships.length})</span>
            </h3>
          </div>
          <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
            {npc.relationships.slice(0, 6).map((rel) => {
              const targetNpc = state.npcs.find((n) => n.id === rel.target_npc_id);
              return (
                <div key={rel.target_npc_id} className="p-2 rounded-lg bg-slate-900/50 border border-slate-800 text-xs flex items-center justify-between">
                  <div>
                    <span className="font-semibold text-slate-200">{targetNpc?.name || rel.target_npc_id}</span>
                    <span className="text-[10px] ml-1.5 px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                      {rel.relationship_type}
                    </span>
                  </div>
                  <div className="text-right text-[11px] text-slate-400">
                    <span>Trust: {Math.round(rel.trust)}%</span>
                  </div>
                </div>
              );
            })}
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

const TraitBar: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="flex items-center justify-between">
    <span className="text-slate-400 w-28">{label}</span>
    <div className="flex-1 bg-slate-700/40 rounded-full h-1.5 overflow-hidden mx-2">
      <div
        className="bg-indigo-400 h-full rounded-full"
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
    <span className="text-slate-300 font-mono w-8 text-right">{Math.round(value * 100)}%</span>
  </div>
);
