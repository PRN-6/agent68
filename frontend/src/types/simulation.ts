export interface Personality {
  openness: number;
  conscientiousness: number;
  extraversion: number;
  agreeableness: number;
  neuroticism: number;
}

export interface Needs {
  energy: number;
  hunger: number;
  social: number;
  fun: number;
  hygiene: number;
  purpose: number;
}

export interface Emotion {
  current: string;
  valence: number;
  arousal: number;
  intensity: number;
}

export interface ScheduleStep {
  start_hour: number;
  start_minute: number;
  duration_minutes: number;
  activity: string;
  location: string;
  description: string;
  is_completed?: boolean;
}

export interface RelationshipEdge {
  source_npc_id: string;
  target_npc_id: string;
  familiarity: number;
  trust: number;
  affinity: number;
  respect: number;
  conflict: number;
  shared_experiences_count: number;
  relationship_type: string;
  last_interaction_minute: number;
}

export interface Memory {
  id: string;
  npc_id: string;
  memory_type: 'short_term' | 'long_term' | 'observation' | 'conversation' | 'reflection';
  content: string;
  importance: number;
  sim_timestamp: number;
  retrieved_count?: number;
}

export interface NPC {
  id: string;
  name: string;
  age: number;
  occupation: string;
  personality: Personality;
  background: string;
  interests: string[];
  skills: string[];
  beliefs: string[];
  goals: string[];
  home_id: string;
  workplace_id: string;
  avatar_color: string;
  x: number;
  y: number;
  current_location: string;
  current_activity: string;
  action_minutes_remaining: number;
  is_moving: boolean;
  needs: Needs;
  emotion: Emotion;
  wealth: number;
  memory_count: number;
  plan_summary: string;
  current_plan_step?: ScheduleStep | null;
  relationships: RelationshipEdge[];
  full_schedule?: {
    summary: string;
    schedule: ScheduleStep[];
  };
}

export interface LocationItem {
  id: string;
  name: string;
  zone: string;
  x: number;
  y: number;
  width: number;
  height: number;
  capacity: number;
  description: string;
  objects: string[];
  color: string;
  icon: string;
}

export interface Road {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  width: number;
}

export interface District {
  name: string;
  bounds: { x: number; y: number; w: number; h: number };
  color: string;
}

export interface MapMetadata {
  width: number;
  height: number;
  roads: Road[];
  locations: LocationItem[];
  districts: District[];
}

export interface ClockState {
  tick: number;
  sim_day: number;
  sim_hour: number;
  sim_minute: number;
  formatted_time: string;
  day_phase: string;
  is_daylight: boolean;
  is_running: boolean;
  speed: number;
  total_sim_minutes: number;
}

export interface WeatherState {
  type: string;
  description: string;
  comfort_mod: number;
  is_rain: boolean;
  temperature: number;
}

export interface WorldEventItem {
  id: string;
  event_type: string;
  description: string;
  location_id: string;
  initiator_id?: string;
  participants: string[];
  sim_timestamp: number;
  significance: number;
}

export interface ConversationMessage {
  speaker_id: string;
  speaker_name: string;
  message: string;
  thought?: string;
}

export interface ActiveConversation {
  id: string;
  participants: string[];
  participant_names: string[];
  location_id: string;
  topic: string;
  messages: ConversationMessage[];
  is_completed: boolean;
}

export interface SimulationState {
  clock: ClockState;
  weather: WeatherState;
  npcs: NPC[];
  recent_events: WorldEventItem[];
  recent_conversations: ActiveConversation[];
  stats: {
    total_decisions: number;
    total_conversations: number;
    total_reflections: number;
    sim_tick_duration_ms: number;
  };
}

