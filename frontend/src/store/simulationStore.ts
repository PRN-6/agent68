import { create } from 'zustand';
import type { SimulationState, MapMetadata, Memory } from '../types/simulation';

interface SimulationStore {
  state: SimulationState | null;
  mapMetadata: MapMetadata | null;
  selectedNpcId: string | null;
  selectedLocationId: string | null;
  activeTab: 'world' | 'npcs' | 'social' | 'timeline';
  mapTheme: 'the_ville' | 'kenney_urban';
  isMemoryModalOpen: boolean;
  isGodModeOpen: boolean;
  isTilesetModalOpen: boolean;
  isConnected: boolean;
  npcMemories: Memory[];
  isSearchingMemories: boolean;

  // Actions
  setState: (state: SimulationState) => void;
  setMapMetadata: (meta: MapMetadata) => void;
  setMapTheme: (theme: 'the_ville' | 'kenney_urban') => void;
  setSelectedNpcId: (id: string | null) => void;
  setSelectedLocationId: (id: string | null) => void;
  setActiveTab: (tab: 'world' | 'npcs' | 'social' | 'timeline') => void;
  setIsMemoryModalOpen: (open: boolean) => void;
  setIsGodModeOpen: (open: boolean) => void;
  setIsTilesetModalOpen: (open: boolean) => void;
  setIsConnected: (connected: boolean) => void;

  // API Calls
  fetchInitialData: () => Promise<void>;
  togglePlayPause: () => Promise<void>;
  stepSimulation: () => Promise<void>;
  setSpeed: (speed: number) => Promise<void>;
  resetSimulation: () => Promise<void>;
  injectEvent: (eventType: string, description: string, locationId: string, significance?: number) => Promise<void>;
  fetchNpcMemories: (npcId: string, query?: string, typeFilter?: string) => Promise<void>;
}

export const useSimulationStore = create<SimulationStore>((set, get) => ({
  state: null,
  mapMetadata: null,
  selectedNpcId: null,
  selectedLocationId: null,
  activeTab: 'world',
  mapTheme: 'the_ville',
  isMemoryModalOpen: false,
  isGodModeOpen: false,
  isTilesetModalOpen: false,
  isConnected: false,
  npcMemories: [],
  isSearchingMemories: false,

  setState: (state) => set({ state }),
  setMapMetadata: (mapMetadata) => set({ mapMetadata }),
  setMapTheme: (mapTheme) => set({ mapTheme }),
  setSelectedNpcId: (selectedNpcId) => set({ selectedNpcId }),
  setSelectedLocationId: (selectedLocationId) => set({ selectedLocationId }),
  setActiveTab: (activeTab) => set({ activeTab }),
  setIsMemoryModalOpen: (isMemoryModalOpen) => set({ isMemoryModalOpen }),
  setIsGodModeOpen: (isGodModeOpen) => set({ isGodModeOpen }),
  setIsTilesetModalOpen: (isTilesetModalOpen) => set({ isTilesetModalOpen }),
  setIsConnected: (isConnected) => set({ isConnected }),

  fetchInitialData: async () => {
    try {
      const [stateRes, mapRes] = await Promise.all([
        fetch('/api/world/state'),
        fetch('/api/world/map'),
      ]);
      if (stateRes.ok) {
        const stateData = await stateRes.json();
        set({ state: stateData });
      }
      if (mapRes.ok) {
        const mapData = await mapRes.json();
        set({ mapMetadata: mapData });
      }
    } catch (err) {
      console.error('Failed to fetch initial simulation data:', err);
    }
  },

  togglePlayPause: async () => {
    const currentState = get().state;
    if (!currentState) return;
    const isRunning = currentState.clock.is_running;
    const endpoint = isRunning ? '/api/simulation/pause' : '/api/simulation/resume';
    try {
      await fetch(endpoint, { method: 'POST' });
    } catch (err) {
      console.error('Toggle play/pause failed:', err);
    }
  },

  stepSimulation: async () => {
    try {
      const res = await fetch('/api/simulation/step', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        if (data.state) {
          set({ state: data.state });
        }
      }
    } catch (err) {
      console.error('Step simulation failed:', err);
    }
  },

  setSpeed: async (speed: number) => {
    try {
      await fetch('/api/simulation/speed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ speed }),
      });
    } catch (err) {
      console.error('Set speed failed:', err);
    }
  },

  resetSimulation: async () => {
    try {
      await fetch('/api/simulation/reset', { method: 'POST' });
      await get().fetchInitialData();
    } catch (err) {
      console.error('Reset failed:', err);
    }
  },

  injectEvent: async (eventType, description, locationId, significance = 7.0) => {
    try {
      await fetch('/api/simulation/inject_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          description,
          location_id: locationId,
          significance,
        }),
      });
    } catch (err) {
      console.error('Inject event failed:', err);
    }
  },

  fetchNpcMemories: async (npcId: string, query?: string, typeFilter?: string) => {
    set({ isSearchingMemories: true });
    try {
      let url = `/api/npcs/${npcId}/memories?`;
      if (query && query.trim()) {
        url += `query=${encodeURIComponent(query.trim())}&`;
      }
      if (typeFilter && typeFilter !== 'all') {
        url += `memory_type=${encodeURIComponent(typeFilter)}&`;
      }
      const res = await fetch(url);
      if (res.ok) {
        const mems = await res.json();
        set({ npcMemories: mems, isSearchingMemories: false });
      }
    } catch (err) {
      console.error('Fetch memories failed:', err);
      set({ isSearchingMemories: false });
    }
  },
}));
