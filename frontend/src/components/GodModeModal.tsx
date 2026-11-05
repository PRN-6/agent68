import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { X, Send, Zap } from 'lucide-react';

const PRESET_EVENTS = [
  {
    type: 'community',
    description: 'Arthur Vance announces the Autumn Town Harvest Festival with music and food stalls!',
    location: 'town_square',
    significance: 8.5,
  },
  {
    type: 'weather',
    description: 'A sudden torrential thunderstorm strikes, sending pedestrians scurrying for indoor shelter.',
    location: 'town_square',
    significance: 7.0,
  },
  {
    type: 'economic',
    description: 'Hannah Abbott arrives with an abundant harvest of sweet honey apples at discounted prices!',
    location: 'marketplace',
    significance: 7.5,
  },
  {
    type: 'social',
    description: 'Julian Cole announces an evening live balladeer concert with complimentary hot spiced cider.',
    location: 'tavern',
    significance: 8.0,
  },
  {
    type: 'discovery',
    description: 'Elena Rostova uncovers an ancient parchment diary behind the archive bookshelves!',
    location: 'library',
    significance: 9.0,
  },
];

export const GodModeModal: React.FC = () => {
  const { isGodModeOpen, setIsGodModeOpen, injectEvent, mapMetadata } = useSimulationStore();

  const [eventType, setEventType] = useState('community');
  const [description, setDescription] = useState('');
  const [locationId, setLocationId] = useState('town_square');
  const [significance, setSignificance] = useState(7.5);

  if (!isGodModeOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description.trim()) return;
    injectEvent(eventType, description.trim(), locationId, significance);
    setIsGodModeOpen(false);
    setDescription('');
  };

  const handleApplyPreset = (preset: typeof PRESET_EVENTS[0]) => {
    setEventType(preset.type);
    setDescription(preset.description);
    setLocationId(preset.location);
    setSignificance(preset.significance);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-xl shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/70">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-xl bg-gradient-to-tr from-amber-500 to-rose-500 text-white shadow-md">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center space-x-2">
                <span>God Mode: Inject Emergent World Event</span>
              </h2>
              <p className="text-xs text-slate-400">
                Trigger unexpected external occurrences to watch agents replan and spread news
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsGodModeOpen(false)}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Presets */}
        <div className="p-4 bg-slate-950/40 border-b border-slate-800 space-y-2">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
            Quick Preset Scenarios
          </span>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            {PRESET_EVENTS.map((preset, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleApplyPreset(preset)}
                className="text-left p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-sky-500/60 transition group"
              >
                <div className="flex items-center justify-between font-semibold text-slate-200 group-hover:text-sky-300 capitalize text-xs">
                  <span>{preset.type} Event</span>
                  <span className="text-[10px] text-amber-400">★ {preset.significance}</span>
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">{preset.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Event Description
            </label>
            <textarea
              rows={3}
              required
              placeholder="Describe what occurs in the town..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl p-3 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-sky-500 resize-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Event Category
              </label>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
              >
                <option value="community">Community / Celebration</option>
                <option value="economic">Economic / Trade</option>
                <option value="weather">Weather / Natural</option>
                <option value="social">Social / Gossip</option>
                <option value="conflict">Conflict / Dispute</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Town Location
              </label>
              <select
                value={locationId}
                onChange={(e) => setLocationId(e.target.value)}
                className="w-full bg-slate-800/80 border border-slate-700/80 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-sky-500"
              >
                {mapMetadata?.locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>
                    {loc.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="font-semibold text-slate-300">Significance Rating</span>
              <span className="font-bold text-amber-400">{significance.toFixed(1)} / 10</span>
            </div>
            <input
              type="range"
              min={1}
              max={10}
              step={0.5}
              value={significance}
              onChange={(e) => setSignificance(parseFloat(e.target.value))}
              className="w-full accent-amber-500"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-white font-bold text-xs shadow-lg shadow-rose-950/40 flex items-center justify-center space-x-2 transition"
          >
            <Send className="w-4 h-4" />
            <span>Broadcast Event into World</span>
          </button>
        </form>
      </div>
    </div>
  );
};
