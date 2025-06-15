export interface GameState {
  player_stats: PlayerStats;
  current_room?: string;
  inventory?: string[];
}

export interface PlayerStats {
  health: number;
  energy: number;
  level: number;
}

export interface Message {
  type: 'player' | 'system' | 'error';
  content: string;
}

export interface ModelSelectorProps {
  currentModel: 'claude' | 'llama';
  isSwitching: boolean;
  onSwitch: (model: 'claude' | 'llama') => void;
}

export interface StatsPanelProps {
  stats: PlayerStats;
}

export interface MessageListProps {
  messages: Message[];
}
