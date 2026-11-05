import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { X, Search, Brain, Clock, Star } from 'lucide-react';

export const MemoryViewerModal: React.FC = () => {
  const {
    state,
    selectedNpcId,
    isMemoryModalOpen,
    setIsMemoryModalOpen,
    npcMemories,
    fetchNpcMemories,
    isSearchingMemories,
  } = useSimulationStore();

  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  if (!isMemoryModalOpen || !selectedNpcId || !state) return null;

  const npc = state.npcs.find((n) => n.id === selectedNpcId);
  if (!npc) return null;

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchNpcMemories(npc.id, searchQuery, filterType);
  };

  const handleFilterChange = (type: string) => {
    setFilterType(type);
    fetchNpcMemories(npc.id, searchQuery, type);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-3xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/70">
          <div className="flex items-center space-x-3">
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center font-bold text-white shadow-md"
              style={{ backgroundColor: npc.avatar_color }}
            >
              <Brain className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <span>{npc.name}'s Memory Stream & Reflections</span>
              </h2>
              <p className="text-xs text-slate-400">
                Inspect 3-tier memory hierarchy: Short-Term, Long-Term, and Synthesized Reflections
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsMemoryModalOpen(false)}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search & Filter Bar */}
        <div className="p-4 border-b border-slate-800/80 bg-slate-900/50 flex flex-col md:flex-row gap-3">
          <form onSubmit={handleSearch} className="flex-1 flex items-center relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3" />
            <input
              type="text"
              placeholder="Query semantic memory (e.g., 'sourdough', 'doctor', 'festival')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-800/90 border border-slate-700/70 rounded-xl pl-9 pr-24 py-2 text-xs text-slate-100 placeholder-slate-400 focus:outline-none focus:border-sky-500"
            />
            <button
              type="submit"
              className="absolute right-1.5 px-3 py-1 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-medium text-xs transition"
            >
              Retrieve
            </button>
          </form>

          {/* Filter Pills */}
          <div className="flex items-center space-x-1.5 overflow-x-auto text-xs">
            {['all', 'short_term', 'long_term', 'reflection', 'conversation'].map((type) => (
              <button
                key={type}
                onClick={() => handleFilterChange(type)}
                className={`px-3 py-1.5 rounded-lg font-medium capitalize transition ${
                  filterType === type
                    ? 'bg-sky-500 text-white'
                    : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                }`}
              >
                {type.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Memory Stream List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {isSearchingMemories ? (
            <div className="py-16 text-center text-slate-400 text-xs">
              <Brain className="w-8 h-8 animate-pulse mx-auto mb-2 text-sky-400" />
              <span>Scanning memory stream and vector embeddings...</span>
            </div>
          ) : npcMemories.length === 0 ? (
            <div className="py-16 text-center text-slate-400 text-xs">
              <span>No memories match the filter query.</span>
            </div>
          ) : (
            npcMemories.map((mem) => {
              const isReflection = mem.memory_type === 'reflection';
              const isLongTerm = mem.memory_type === 'long_term';

              return (
                <div
                  key={mem.id}
                  className={`p-3.5 rounded-xl border transition ${
                    isReflection
                      ? 'bg-purple-950/20 border-purple-800/50 hover:border-purple-600/70'
                      : isLongTerm
                      ? 'bg-amber-950/15 border-amber-800/40 hover:border-amber-600/60'
                      : 'bg-slate-800/40 border-slate-700/50 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                          isReflection
                            ? 'bg-purple-900/60 text-purple-300 border-purple-700/60'
                            : isLongTerm
                            ? 'bg-amber-900/60 text-amber-300 border-amber-700/60'
                            : 'bg-slate-800 text-slate-300 border-slate-700'
                        }`}
                      >
                        {mem.memory_type}
                      </span>
                      <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                        <Clock className="w-3 h-3" />
                        <span>Minute {mem.sim_timestamp}</span>
                      </span>
                    </div>

                    <div className="flex items-center space-x-1 text-xs text-amber-400 bg-slate-900/60 px-2 py-0.5 rounded-full border border-slate-800">
                      <Star className="w-3 h-3 fill-amber-400" />
                      <span className="font-semibold">{mem.importance.toFixed(1)}/10</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-200 leading-relaxed font-sans">{mem.content}</p>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
