import React from 'react';
import { ModelSelectorProps } from './types';

const ModelSelector: React.FC<ModelSelectorProps> = ({ currentModel, isSwitching, onSwitch }) => (
    <div className="bg-gray-700 p-3 rounded mb-4">
    <h3 className="font-bold mb-2">AI Model</h3>
    <div className="flex items-center justify-between">
    <select
    value={currentModel}
    onChange={(e) => onSwitch(e.target.value as 'claude' | 'llama')}
    className="bg-gray-800 text-white px-2 py-1 rounded"
    disabled={isSwitching}
    aria-label="AI Model Selector"
    >
    <option value="claude">Claude</option>
    <option value="llama">Llama</option>
    </select>
    <div className="flex items-center ml-2">
    <div
    className={`w-2 h-2 rounded-full transition-colors ${
        isSwitching ? 'bg-yellow-500' : 'bg-green-500'
    }`}
    />
    <span className="text-sm ml-2">{isSwitching ? 'Switching...' : 'Active'}</span>
    </div>
    </div>
    </div>
);

export default ModelSelector;
