import React from 'react';

type Model = 'claude' | 'llama' | 'openai' | 'gemini' | 'openrouter';

interface ModelSelectorProps {
  currentModel: Model;
  isSwitching: boolean;
  onSwitch: (model: Model) => void;
}

const models: Model[] = ['claude', 'llama', 'openai', 'gemini', 'openrouter'];

const ModelSelector: React.FC<ModelSelectorProps> = ({ currentModel, isSwitching, onSwitch }) => (
  <div className="space-y-2 mb-4">
    {models.map((model) => (
      <button
        key={model}
        onClick={() => onSwitch(model)}
        disabled={isSwitching}
        className={`w-full text-left px-3 py-2 rounded ${currentModel === model ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'}`}
      >
        {model}
      </button>
    ))}
  </div>
);

export default ModelSelector;
