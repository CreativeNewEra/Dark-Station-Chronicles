import React from 'react';
import { Heart, Battery, Brain } from 'lucide-react';
import { StatsPanelProps } from '../types';

const StatsPanel: React.FC<StatsPanelProps> = ({ stats }) => (
    <div className="space-y-4">
    <div className="bg-gray-700 p-3 rounded">
    <div className="flex items-center mb-2">
    <Heart className="mr-2 text-red-500" size={18} />
    <span>Health</span>
    </div>
    <div className="h-2 bg-gray-600 rounded">
    <div
    className="h-full bg-red-500 rounded transition-all duration-300"
    style={{ width: `${Math.max(0, Math.min(100, (stats.health / 100) * 100))}%` }}
    />
    </div>
    </div>
    <div className="bg-gray-700 p-3 rounded">
    <div className="flex items-center mb-2">
    <Battery className="mr-2 text-blue-500" size={18} />
    <span>Energy</span>
    </div>
    <div className="h-2 bg-gray-600 rounded">
    <div
    className="h-full bg-blue-500 rounded transition-all duration-300"
    style={{ width: `${Math.max(0, Math.min(100, (stats.energy / 100) * 100))}%` }}
    />
    </div>
    </div>
    <div className="bg-gray-700 p-3 rounded">
    <div className="flex items-center">
    <Brain className="mr-2 text-purple-500" size={18} />
    <span>Level {stats.level}</span>
    </div>
    </div>
    </div>
);

export default StatsPanel;
