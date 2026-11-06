import { useEffect } from 'react';
import { useSimulationStore } from './store/simulationStore';
import { Header } from './components/Header';
import { WorldCanvas } from './components/WorldCanvas';
import { NPCProfileDrawer } from './components/NPCProfileDrawer';
import { MemoryViewerModal } from './components/MemoryViewerModal';
import { SocialGraphView } from './components/SocialGraphView';
import { TimelineView } from './components/TimelineView';
import { PartyExpeditionsView } from './components/PartyExpeditionsView';
import { GodModeModal } from './components/GodModeModal';
import { KenneyTilesetModal } from './components/KenneyTilesetModal';
import { Shield } from 'lucide-react';

export function App() {
  const {
    state,
    setState,
    activeTab,
    fetchInitialData,
    setIsConnected,
    selectedNpcId,
    setSelectedNpcId,
    mapTheme,
  } = useSimulationStore();

  // Initial Data Fetch & WebSocket Connection
  useEffect(() => {
    fetchInitialData();

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/simulation`;

    let socket: WebSocket | null = null;
    let reconnectTimeout: any = null;

    const connectWebSocket = () => {
      try {
        socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          setIsConnected(true);
        };

        socket.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (payload.type === 'TICK_UPDATE' || payload.type === 'INITIAL_STATE') {
              setState(payload.data);
            }
          } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
          }
        };

        socket.onclose = () => {
          setIsConnected(false);
          // Try reconnecting after 2 seconds
          reconnectTimeout = setTimeout(connectWebSocket, 2000);
        };

        socket.onerror = (err) => {
          console.error('WebSocket error:', err);
          socket?.close();
        };
      } catch (e) {
        console.error('Could not create WebSocket:', e);
        reconnectTimeout = setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (socket) socket.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [fetchInitialData, setIsConnected, setState]);

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      {/* Top Header */}
      <Header />

      {/* Main Content Area */}
      <div className="flex-1 relative flex overflow-hidden">
        {/* Left NPC Roster Sidebar (Collapsible / Compact) */}
        <div className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col flex-shrink-0 z-10 hidden md:flex">
          <div className="p-3 border-b border-slate-800 flex items-center justify-between">
            <span className="text-xs font-bold text-slate-300 flex items-center space-x-1.5 uppercase tracking-wider">
              <Shield className="w-3.5 h-3.5 text-sky-400" />
              <span>Adventurers (25)</span>
            </span>
            <span className="text-[10px] text-amber-400 font-mono font-bold">MMORPG</span>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {state?.npcs.map((npc) => {
              const isSelected = selectedNpcId === npc.id;
              const maxHp = npc.max_hp || 100;
              const currentHp = npc.hp ?? 100;
              const hpPct = Math.max(0, Math.min(currentHp / maxHp, 1));

              return (
                <button
                  key={npc.id}
                  onClick={() => setSelectedNpcId(npc.id)}
                  className={`w-full text-left p-2 rounded-xl flex items-center space-x-2.5 transition ${
                    isSelected
                      ? 'bg-sky-950/70 border border-sky-600/70 shadow-md'
                      : 'hover:bg-slate-800/60 border border-transparent'
                  }`}
                >
                  <div className="w-9 h-9 rounded-lg overflow-hidden bg-slate-800 border border-slate-700 flex-shrink-0 flex items-center justify-center shadow-sm">
                    <img
                      src={
                        mapTheme === 'kenney_urban'
                          ? `/assets/characters/profile/kenney/kenney_char_${((npc.id.charCodeAt(npc.id.length - 1) || 0) % 5) + 1}.png`
                          : `/assets/characters/profile/${npc.sprite_name || 'Klaus_Mueller'}.png`
                      }
                      alt={npc.name}
                      className="w-full h-full object-cover"
                      style={{ imageRendering: 'pixelated' }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-200 truncate">
                        {npc.name}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded bg-indigo-950/80 text-indigo-300 font-bold border border-indigo-800/60">
                        Lv.{npc.level || 1}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 mt-0.5">
                      <span className="truncate text-sky-400 font-medium">{npc.rpg_class || npc.occupation}</span>
                      <span className="text-slate-400 font-mono text-[9px]">
                        {currentHp}/{maxHp} HP
                      </span>
                    </div>
                    {/* Micro HP Bar */}
                    <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden mt-1">
                      <div
                        className="h-full bg-emerald-500 transition-all duration-300"
                        style={{ width: `${hpPct * 100}%` }}
                      />
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Dynamic Center Stage */}
        <div className="flex-1 relative h-full w-full overflow-hidden">
          {activeTab === 'world' && <WorldCanvas />}
          {activeTab === 'parties' && <PartyExpeditionsView />}
          {activeTab === 'social' && <SocialGraphView />}
          {activeTab === 'timeline' && <TimelineView />}

          {/* Side Drawer Profile */}
          <NPCProfileDrawer />
        </div>
      </div>

      {/* Modals */}
      <MemoryViewerModal />
      <GodModeModal />
      <KenneyTilesetModal />
    </div>
  );
}

export default App;
