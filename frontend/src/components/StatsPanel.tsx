import React from 'react';
import { PlayerStats } from '../types';

interface StatsPanelProps {
  stats: PlayerStats;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats }) => {
  return (
    <div className="mt-4 text-sm" data-testid="stats-panel">
      <h3 className="font-semibold mb-2">Player Stats</h3>
      <ul className="space-y-1">
        {Object.entries(stats).map(([key, value]) => (
          <li key={key} className="flex justify-between">
            <span className="capitalize">{key.replace('_', ' ')}</span>
            <span>{String(value)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default StatsPanel;
