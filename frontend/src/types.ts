export interface PlayerStats {
  health: number;
  energy: number;
  level: number;
  exp: number;
  [key: string]: number; // allow additional stats
}

export interface GameState {
  current_room: string;
  player_stats: PlayerStats;
  inventory: string[];
  available_exits: string[];
  character_class?: string | null;
}

export interface Message {
  type: 'system' | 'player' | 'error';
  content: string;
}

export interface SaveFile {
  filename: string;
  timestamp: string;
}
