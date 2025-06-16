import React from 'react';

export type AIModel = 'claude' | 'llama' | 'openai' | 'gemini' | 'openrouter';

interface ModelSelectorProps {
  currentModel: AIModel;
  isSwitching?: boolean;
  onSwitch: (model: AIModel) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ currentModel, isSwitching = false, onSwitch }) => {
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onSwitch(e.target.value as AIModel);
  };

  return (
    <div className="mb-4" data-testid="model-selector">
      <label htmlFor="model" className="block text-sm font-semibold mb-1">AI Model</label>
      <select
        id="model"
        value={currentModel}
        onChange={handleChange}
        disabled={isSwitching}
        className="w-full bg-gray-700 p-2 rounded"
      >
        <option value="claude">Claude</option>
        <option value="llama">Llama</option>
        <option value="openai">OpenAI</option>
        <option value="gemini">Gemini</option>
        <option value="openrouter">OpenRouter</option>
      </select>
    </div>
  );
};

export default ModelSelector;
