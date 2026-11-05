import { useEffect } from 'react';
import { useSimulationStore } from './store/simulationStore';
import { Header } from './components/Header';
import { WorldCanvas } from './components/WorldCanvas';
import { NPCProfileDrawer } from './components/NPCProfileDrawer';
import { MemoryViewerModal } from './components/MemoryViewerModal';
import { SocialGraphView } from './components/SocialGraphView';
import { TimelineView } from './components/TimelineView';
import { GodModeModal } from './components/GodModeModal';
import { Users } from 'lucide-react';

export function App() {
  const {
    state,
    setState,
    activeTab,
    fetchInitialData,
    setIsConnected,
    selectedNpcId,
    setSelectedNpcId,
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
              <Users className="w-3.5 h-3.5 text-sky-400" />
              <span>Town Inhabitants (25)</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono">Autonomous</span>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {state?.npcs.map((npc) => {
              const isSelected = selectedNpcId === npc.id;
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
                  <div
                    className="w-7 h-7 rounded-full flex items-center justify-center font-bold text-xs text-white flex-shrink-0 shadow-sm"
                    style={{ backgroundColor: npc.avatar_color }}
                  >
                    {npc.name[0]}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-semibold text-slate-200 truncate">
                        {npc.name}
                      </span>
                      <span className="text-[10px] text-slate-400">{npc.emotion.current}</span>
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="truncate">{npc.occupation}</span>
                      <span className="text-emerald-400 font-mono">
                        {Math.round(npc.needs.energy)}%⚡
                      </span>
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
          {activeTab === 'social' && <SocialGraphView />}
          {activeTab === 'timeline' && <TimelineView />}

          {/* Side Drawer Profile */}
          <NPCProfileDrawer />
        </div>
      </div>

      {/* Modals */}
      <MemoryViewerModal />
      <GodModeModal />
    </div>
  );
}

export default App;
