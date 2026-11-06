import React from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { Trophy, Coins, Play } from 'lucide-react';

export const PartyExpeditionsView: React.FC = () => {
  const { state, launchExpedition, setSelectedNpcId } = useSimulationStore();

  const parties = state?.parties || [];
  const npcs = state?.npcs || [];

  return (
    <div className="w-full h-full bg-slate-950 p-6 overflow-y-auto text-slate-100 space-y-6">
      {/* Title Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-xl font-black text-white flex items-center space-x-2">
            <span className="text-2xl">⚔️</span>
            <span>MMORPG Adventuring Parties & Dungeon Expeditions</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Autonomous party formations venturing from the Adventurer's Guild into the Shadow Crypts, fighting bosses, and returning with loot.
          </p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center space-x-2">
            <Trophy className="w-4 h-4 text-amber-400" />
            <span className="text-slate-300">
              Total Clears: <strong className="text-white">{parties.reduce((acc, p) => acc + (p.dungeon_clears || 0), 0)}</strong>
            </span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center space-x-2">
            <Coins className="w-4 h-4 text-yellow-400" />
            <span className="text-slate-300">
              Total Gold: <strong className="text-white">{parties.reduce((acc, p) => acc + (p.total_loot_gold || 0), 0)}g</strong>
            </span>
          </div>
        </div>
      </div>

      {/* Parties Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {parties.map((party) => {
          const leader = npcs.find((n) => n.id === party.leader_id);
          const members = npcs.filter((n) => party.member_ids.includes(n.id));

          // Status Badge details
          let statusBadgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
          let statusIcon = '🛡️';
          if (party.status.includes('DUNGEON') || party.status.includes('MARCH')) {
            statusBadgeColor = 'bg-sky-950/80 text-sky-300 border-sky-700/60 animate-pulse';
            statusIcon = '⚔️';
          } else if (party.status.includes('CRYPT') || party.status.includes('CATACOMBS')) {
            statusBadgeColor = 'bg-purple-950/80 text-purple-300 border-purple-700/60 animate-pulse';
            statusIcon = '💀';
          } else if (party.status.includes('BOSS')) {
            statusBadgeColor = 'bg-rose-950/80 text-rose-300 border-rose-700/60 animate-pulse';
            statusIcon = '🔥';
          } else if (party.status.includes('VICTORIOUS') || party.status.includes('CELEBRATING')) {
            statusBadgeColor = 'bg-amber-950/80 text-amber-300 border-amber-700/60';
            statusIcon = '🍺';
          }

          return (
            <div
              key={party.party_id}
              className="bg-slate-900/80 rounded-2xl border border-slate-800/80 shadow-xl overflow-hidden flex flex-col hover:border-slate-700 transition"
            >
              {/* Card Banner Header */}
              <div
                className="p-4 border-b border-slate-800 flex items-center justify-between"
                style={{
                  background: `linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, ${party.banner_color}25 100%)`,
                }}
              >
                <div>
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <span
                      className="w-3 h-3 rounded-full flex-shrink-0"
                      style={{ backgroundColor: party.banner_color }}
                    />
                    <span>{party.name}</span>
                  </h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Leader: <span className="text-slate-200 font-semibold">{leader?.name || party.leader_id}</span>
                  </p>
                </div>

                <button
                  onClick={() => launchExpedition(party.party_id)}
                  title="Dispatch party into the Shadow Crypts now"
                  className="px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white text-xs font-bold shadow-md flex items-center space-x-1.5 transition active:scale-95"
                >
                  <Play className="w-3 h-3 fill-white" />
                  <span>Explore</span>
                </button>
              </div>

              {/* Status & Latest Expedition Log */}
              <div className="p-4 space-y-3 flex-1 flex flex-col">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Current State:</span>
                  <span className={`px-2.5 py-1 rounded-full text-xs font-bold border flex items-center space-x-1 ${statusBadgeColor}`}>
                    <span>{statusIcon}</span>
                    <span>{party.status.replace(/_/g, ' ')}</span>
                  </span>
                </div>

                {/* Latest Encounter / Combat Log */}
                <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80 text-xs font-mono text-slate-300">
                  <span className="text-sky-400 font-bold block mb-1">Dungeon Chronicle:</span>
                  <p className="leading-relaxed">{party.latest_log || 'Preparing for next expedition at the Guild.'}</p>
                </div>

                {/* Party Members Roster */}
                <div className="space-y-2 pt-2 flex-1">
                  <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold block">
                    Party Roster ({members.length} Adventurers):
                  </span>
                  <div className="space-y-1.5">
                    {members.map((m) => {
                      const hpPct = Math.max(0, Math.min((m.hp || 100) / (m.max_hp || 100), 1));
                      const manaPct = Math.max(0, Math.min((m.mana || 50) / (m.max_mana || 50), 1));

                      return (
                        <div
                          key={m.id}
                          onClick={() => setSelectedNpcId(m.id)}
                          className="bg-slate-800/50 hover:bg-slate-800 p-2 rounded-xl border border-slate-700/50 cursor-pointer transition flex items-center justify-between text-xs"
                        >
                          <div className="flex items-center space-x-2">
                            <span className="w-2 h-2 rounded-full bg-emerald-400" />
                            <div>
                              <span className="font-semibold text-slate-100 block">{m.name}</span>
                              <span className="text-[10px] text-sky-400">
                                Lv.{m.level || 1} {m.rpg_class || 'Adventurer'} ({m.role || 'DPS'})
                              </span>
                            </div>
                          </div>

                          {/* HP and Mana bars */}
                          <div className="w-24 space-y-1">
                            <div className="w-full bg-slate-950 h-1.5 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-emerald-500 to-green-400 transition-all duration-300"
                                style={{ width: `${hpPct * 100}%` }}
                              />
                            </div>
                            <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 transition-all duration-300"
                                style={{ width: `${manaPct * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Party Stats Footer */}
                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span>Clears: <strong className="text-white">{party.dungeon_clears}</strong></span>
                  <span>Loot: <strong className="text-yellow-400 font-mono">{party.total_loot_gold}g</strong></span>
                  <span className="text-[11px] text-emerald-400">Ready</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
