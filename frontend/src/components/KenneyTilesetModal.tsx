import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import { X, Layers, Image as ImageIcon, CheckCircle, ExternalLink } from 'lucide-react';

export const KenneyTilesetModal: React.FC = () => {
  const { isTilesetModalOpen, setIsTilesetModalOpen, mapTheme, setMapTheme } = useSimulationStore();
  const [activeTab, setActiveTab] = useState<'sample' | 'atlas' | 'tiles'>('sample');

  if (!isTilesetModalOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in duration-200">
        {/* Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-400">
              <Layers className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                <span>Kenney RPG Urban Pack</span>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800 font-semibold">
                  Extracted & Integrated
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                486 Tiles (16×16px) • CC0 Public Domain by Kenney.nl
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsTilesetModalOpen(false)}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* View Tabs & Theme Switcher */}
        <div className="px-4 py-2 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('sample')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                activeTab === 'sample'
                  ? 'bg-amber-600 text-white'
                  : 'bg-slate-800/80 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <ImageIcon className="w-3.5 h-3.5" />
              <span>Town Sample Scene</span>
            </button>
            <button
              onClick={() => setActiveTab('atlas')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
                activeTab === 'atlas'
                  ? 'bg-amber-600 text-white'
                  : 'bg-slate-800/80 text-slate-300 hover:bg-slate-800'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>Packed Tilemap Atlas</span>
            </button>
          </div>

          <button
            onClick={() => {
              setMapTheme(mapTheme === 'kenney_urban' ? 'the_ville' : 'kenney_urban');
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center space-x-1.5 border transition ${
              mapTheme === 'kenney_urban'
                ? 'bg-emerald-600/30 text-emerald-300 border-emerald-500/60'
                : 'bg-slate-800 text-slate-200 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>
              {mapTheme === 'kenney_urban' ? 'Active: Kenney Urban Theme' : 'Switch to Kenney Urban'}
            </span>
          </button>
        </div>

        {/* Content Viewer */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col items-center justify-center bg-slate-950/40">
          {activeTab === 'sample' && (
            <div className="flex flex-col items-center space-y-3 max-w-full">
              <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-black/40">
                <img
                  src="/assets/kenney_rpg_urban_pack/Sample.png"
                  alt="Kenney RPG Urban Sample"
                  className="max-h-[55vh] object-contain"
                  style={{ imageRendering: 'pixelated' }}
                />
              </div>
              <p className="text-xs text-slate-400 text-center max-w-xl">
                Kenney RPG Urban Pack includes asphalt streets, crosswalks, brick houses, stores,
                cars, and modern interior decor. Extracted directly into{' '}
                <code className="text-amber-400 font-mono">frontend/public/assets/kenney_rpg_urban_pack/</code>.
              </p>
            </div>
          )}

          {activeTab === 'atlas' && (
            <div className="flex flex-col items-center space-y-3 max-w-full">
              <div className="rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-black/40 p-2">
                <img
                  src="/assets/kenney_rpg_urban_pack/Tilemap/tilemap_packed.png"
                  alt="Kenney Tilemap Atlas"
                  className="max-h-[55vh] object-contain scale-125 origin-center my-4"
                  style={{ imageRendering: 'pixelated' }}
                />
              </div>
              <p className="text-xs text-slate-400 text-center">
                27 columns × 18 rows = 486 seamless 16×16 tiles. Scaled 2x to 32×32 for the 140×100 Project Genesis town grid.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-3 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <span>Asset Location:</span>
            <span className="font-mono text-slate-300">
              frontend/public/assets/kenney_rpg_urban_pack/
            </span>
          </div>
          <a
            href="https://kenney.nl/assets/rpg-urban-pack"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1 text-sky-400 hover:text-sky-300 hover:underline"
          >
            <span>Kenney.nl Source</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};
