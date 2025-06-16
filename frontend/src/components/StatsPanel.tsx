import React from 'react';

interface StatsPanelProps {
  stats: Record<string, number>;
}

const StatsPanel: React.FC<StatsPanelProps> = ({ stats }) => (
  <div className="mb-4">
    <h2 className="text-lg font-semibold mb-2">Stats</h2>
    <ul className="space-y-1">
      {Object.entries(stats).map(([key, value]) => (
        <li key={key}>{key}: {value}</li>
      ))}
    </ul>
  </div>
);

export default StatsPanel;
