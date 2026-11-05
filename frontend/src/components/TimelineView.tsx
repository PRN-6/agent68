import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { Clock, MessageSquare, AlertCircle, ShoppingBag, CloudSun, Users } from 'lucide-react';

export const TimelineView: React.FC = () => {
  const { state, setSelectedNpcId } = useSimulationStore();
  const [filterType, setFilterType] = useState('all');

  const events = state?.recent_events || [];

  const filteredEvents = events.filter((ev) => {
    if (filterType === 'all') return true;
    return ev.event_type.toLowerCase() === filterType.toLowerCase();
  });

  const getEventIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'dialogue':
        return <MessageSquare className="w-4 h-4 text-sky-400" />;
      case 'economic':
      case 'shopping':
        return <ShoppingBag className="w-4 h-4 text-amber-400" />;
      case 'weather':
        return <CloudSun className="w-4 h-4 text-blue-400" />;
      case 'community':
      case 'social':
        return <Users className="w-4 h-4 text-purple-400" />;
      default:
        return <AlertCircle className="w-4 h-4 text-emerald-400" />;
    }
  };

  return (
    <div className="w-full h-full bg-slate-950 p-6 flex flex-col overflow-hidden text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center space-x-2">
            <Clock className="w-5 h-5 text-sky-400" />
            <span>Chronological Town Timeline & Emergence Feed</span>
          </h2>
          <p className="text-xs text-slate-400">
            Real-time chronological events, conversations, rumor spreading, and economic exchanges.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center space-x-1.5 overflow-x-auto text-xs">
          {['all', 'dialogue', 'social', 'community', 'economic', 'weather'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-3 py-1.5 rounded-lg font-medium capitalize transition ${
                filterType === type
                  ? 'bg-sky-500 text-white'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="flex-1 overflow-y-auto pt-6 space-y-4 max-w-4xl mx-auto w-full">
        {filteredEvents.length === 0 ? (
          <div className="py-24 text-center text-slate-500 text-sm">
            <span>No events recorded yet for this category. Advance simulation time to observe interactions.</span>
          </div>
        ) : (
          filteredEvents
            .slice()
            .reverse()
            .map((ev, idx) => {
              const hour = Math.floor(ev.sim_timestamp / 60) % 24;
              const min = ev.sim_timestamp % 60;
              const formattedTime = `${hour.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;

              return (
                <div
                  key={ev.id || idx}
                  className="flex items-start space-x-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition shadow-sm"
                >
                  <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60 flex-shrink-0">
                    {getEventIcon(ev.event_type)}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-sky-400 font-bold">{formattedTime}</span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700">
                          {ev.event_type}
                        </span>
                        <span className="text-slate-400">@ {ev.location_id}</span>
                      </div>
                      <span className="text-[11px] text-slate-500">Significance: {ev.significance.toFixed(1)}/10</span>
                    </div>

                    <p className="text-sm text-slate-200 leading-snug">{ev.description}</p>

                    {/* Participants */}
                    {ev.participants && ev.participants.length > 0 && (
                      <div className="mt-2 flex items-center space-x-1.5 flex-wrap">
                        <span className="text-[11px] text-slate-400">Involved:</span>
                        {ev.participants.map((pid) => {
                          const pNpc = state?.npcs.find((n) => n.id === pid);
                          return (
                            <button
                              key={pid}
                              onClick={() => setSelectedNpcId(pid)}
                              className="text-[11px] font-medium text-sky-300 hover:text-sky-200 bg-sky-950/40 hover:bg-sky-900/50 px-2 py-0.5 rounded border border-sky-800/40 transition"
                            >
                              {pNpc?.name || pid}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              );
            })
        )}
      </div>
    </div>
  );
};
