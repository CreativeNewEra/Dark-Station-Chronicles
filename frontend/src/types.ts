export interface Message {
  type: string;
  content: string;
}

export interface GameState {
  player_stats: Record<string, number>;
}

export interface SaveFile {
  filename: string;
  timestamp: string;
}
