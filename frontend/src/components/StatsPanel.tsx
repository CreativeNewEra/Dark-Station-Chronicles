import React from 'react';

/**
 * Props for {@link StatsPanel}.
 *
 * @property stats - Key/value pairs representing player stats.
 */
interface StatsPanelProps {
  stats: Record<string, number>;
}

/** Displays a simple list of player statistics. */
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
