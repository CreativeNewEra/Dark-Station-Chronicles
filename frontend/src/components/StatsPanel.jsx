import React from 'react';
import { Heart, Battery, Brain } from 'lucide-react';

const StatsPanel = ({ stats }) => (
    <div className="space-y-4">
    <div className="bg-gray-700 p-3 rounded">
    <Heart className="mr-2 text-red-500" size={18} />
    <span>Health</span>
    <div className="h-2 bg-gray-600 rounded">
    <div
    className="h-full bg-red-500 rounded"
    style={{ width: `${(stats.health / 100) * 100}%` }}
    />
    </div>
    </div>
    <div className="bg-gray-700 p-3 rounded">
    <Battery className="mr-2 text-blue-500" size={18} />
    <span>Energy</span>
    <div className="h-2 bg-gray-600 rounded">
    <div
    className="h-full bg-blue-500 rounded"
    style={{ width: `${(stats.energy / 100) * 100}%` }}
    />
    </div>
    </div>
    <div className="bg-gray-700 p-3 rounded">
    <Brain className="mr-2 text-purple-500" size={18} />
    <span>Level {stats.level}</span>
    </div>
    </div>
);

export default StatsPanel;
