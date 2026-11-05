import React from 'react';
import { useSimulationStore } from '../store/simulationStore';
import {
  Play,
  Pause,
  SkipForward,
  RotateCcw,
  Sun,
  Moon,
  CloudSun,
  CloudRain,
  Wind,
  Zap,
  Map,
  Share2,
  Clock,
  Sparkles,
} from 'lucide-react';

export const Header: React.FC = () => {
  const {
    state,
    activeTab,
    setActiveTab,
    togglePlayPause,
    stepSimulation,
    setSpeed,
    resetSimulation,
    setIsGodModeOpen,
    isConnected,
  } = useSimulationStore();

  const clock = state?.clock;
  const weather = state?.weather;
  const isRunning = clock?.is_running ?? false;
  const currentSpeed = clock?.speed ?? 1.0;

  const getWeatherIcon = (type?: string) => {
    switch (type?.toLowerCase()) {
      case 'sunny':
        return <Sun className="w-4 h-4 text-amber-400" />;
      case 'partly cloudy':
        return <CloudSun className="w-4 h-4 text-amber-300" />;
      case 'gentle rain':
      case 'thunderstorm':
        return <CloudRain className="w-4 h-4 text-sky-400" />;
      case 'windy':
        return <Wind className="w-4 h-4 text-slate-300" />;
      default:
        return <Sun className="w-4 h-4 text-amber-400" />;
    }
  };

  return (
    <header className="h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-4 flex items-center justify-between flex-shrink-0 z-30 select-none">
      {/* Brand & Connection Status */}
      <div className="flex items-center space-x-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 via-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-950/40">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-black tracking-wider text-white flex items-center space-x-2">
            <span>PROJECT GENESIS</span>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-indigo-950/70 text-indigo-300 border border-indigo-800/60 uppercase">
              AI Society
            </span>
          </h1>
          <div className="flex items-center space-x-2 text-[11px] text-slate-400">
            <span
              className={`w-2 h-2 rounded-full ${
                isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
              }`}
            ></span>
            <span>{isConnected ? 'Sim Connected' : 'Connecting to Server...'}</span>
            <span className="text-slate-600">•</span>
            <span className="font-mono text-slate-300">25 Generative Agents</span>
          </div>
        </div>
      </div>

      {/* World Clock & Weather Widget */}
      {clock && weather && (
        <div className="hidden lg:flex items-center space-x-3 bg-slate-950/70 border border-slate-800/80 px-4 py-1.5 rounded-xl shadow-inner">
          {/* Time & Day */}
          <div className="flex items-center space-x-2">
            {clock.is_daylight ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-indigo-300" />
            )}
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="text-xs font-bold text-white font-mono">
                  {clock.formatted_time}
                </span>
                <span className="text-[10px] font-semibold px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                  {clock.day_phase}
                </span>
              </div>
              <div className="text-[10px] text-slate-400">Day {clock.sim_day}</div>
            </div>
          </div>

          <div className="h-6 w-px bg-slate-800"></div>

          {/* Weather */}
          <div className="flex items-center space-x-2">
            {getWeatherIcon(weather.type)}
            <div>
              <div className="text-xs font-semibold text-slate-200">
                {weather.temperature}°C
              </div>
              <div className="text-[10px] text-slate-400">{weather.type}</div>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/80 text-xs">
        <button
          onClick={() => setActiveTab('world')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition ${
            activeTab === 'world'
              ? 'bg-sky-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Map className="w-3.5 h-3.5" />
          <span>Town Map</span>
        </button>

        <button
          onClick={() => setActiveTab('social')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition ${
            activeTab === 'social'
              ? 'bg-sky-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Share2 className="w-3.5 h-3.5" />
          <span>Social Network</span>
        </button>

        <button
          onClick={() => setActiveTab('timeline')}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition ${
            activeTab === 'timeline'
              ? 'bg-sky-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Clock className="w-3.5 h-3.5" />
          <span>Timeline</span>
        </button>
      </div>

      {/* Controls & God Mode */}
      <div className="flex items-center space-x-2">
        {/* Speed Buttons */}
        <div className="hidden sm:flex items-center space-x-1 bg-slate-950/60 p-1 rounded-xl border border-slate-800/80 text-xs font-bold text-slate-300">
          {[1.0, 2.0, 5.0, 10.0].map((spd) => (
            <button
              key={spd}
              onClick={() => setSpeed(spd)}
              className={`px-2 py-1 rounded-lg transition ${
                currentSpeed === spd
                  ? 'bg-indigo-600 text-white'
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              {spd}x
            </button>
          ))}
        </div>

        {/* Step */}
        <button
          onClick={stepSimulation}
          title="Step 1 Tick"
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
        >
          <SkipForward className="w-4 h-4" />
        </button>

        {/* Play / Pause */}
        <button
          onClick={togglePlayPause}
          className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-xl font-bold text-xs text-white shadow-md transition ${
            isRunning
              ? 'bg-amber-600 hover:bg-amber-500 shadow-amber-950/40'
              : 'bg-emerald-600 hover:bg-emerald-500 shadow-emerald-950/40'
          }`}
        >
          {isRunning ? (
            <>
              <Pause className="w-3.5 h-3.5 fill-white" />
              <span>Pause</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-white" />
              <span>Resume</span>
            </>
          )}
        </button>

        {/* God Mode Inject Event */}
        <button
          onClick={() => setIsGodModeOpen(true)}
          className="flex items-center space-x-1.5 px-3 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-white font-bold text-xs shadow-md shadow-rose-950/40 transition active:scale-95"
        >
          <Zap className="w-3.5 h-3.5 fill-white" />
          <span className="hidden md:inline">God Mode</span>
        </button>

        {/* Reset */}
        <button
          onClick={resetSimulation}
          title="Reset Simulation"
          className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
