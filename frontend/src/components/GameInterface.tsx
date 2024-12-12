import React, { useState, useEffect, useRef } from 'react';
import StatsPanel from './StatsPanel';
import ModelSelector from './ModelSelector';
import MessageList from './MessageList';
import { GameState, Message } from './types';

const GameInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [currentModel, setCurrentModel] = useState<'claude' | 'llama'>('claude');
    const [isModelSwitching, setIsModelSwitching] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        startGame();
    }, []);

    const startGame = async () => {
        try {
            const response = await fetch('http://localhost:8000/game/start');
            const data = await response.json();
            addMessage('system', data.message);
        } catch (error) {
            console.error('Error starting game:', error);
            addMessage('error', 'Failed to connect to game server');
        }
    };

    const switchModel = async (newModel: 'claude' | 'llama') => {
        try {
            setIsModelSwitching(true);
            const response = await fetch('http://localhost:8000/game/switch-model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: newModel }),
            });

            if (!response.ok) {
                throw new Error('Failed to switch model');
            }

            setCurrentModel(newModel);
            addMessage('system', `Switched to ${newModel} model`);
        } catch (error) {
            console.error('Error switching model:', error);
            addMessage('error', `Failed to switch to ${newModel} model`);
        } finally {
            setIsModelSwitching(false);
        }
    };

    const addMessage = (type: Message['type'], content: string) => {
        setMessages((prev) => [...prev, { type, content }]);
    };

    const handleCommand = async () => {
        if (!inputText.trim()) return;

        addMessage('player', inputText);
        setIsThinking(true);

        try {
            const response = await fetch('http://localhost:8000/game/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    command: inputText,
                    use_ai: true,
                    model: currentModel,
                }),
            });

            const data = await response.json();
            addMessage('system', data.message);
            if (data.game_state) {
                setGameState(data.game_state);
            }
        } catch (error) {
            console.error('Error sending command:', error);
            addMessage('error', 'Failed to send command');
        } finally {
            setIsThinking(false);
            setInputText('');
        }
    };

    return (
        <div className="flex h-screen bg-gray-900 text-white">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-800 p-4">
        <ModelSelector
        currentModel={currentModel}
        isSwitching={isModelSwitching}
        onSwitch={switchModel}
        />
        {gameState && <StatsPanel stats={gameState.player_stats} />}
        </aside>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
        <MessageList messages={messages} ref={messagesEndRef} />
        {/* Input Area */}
        <footer className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="flex gap-2">
        <input
        type="text"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        onKeyDown={(e) => {
            if (e.key === 'Enter' && !isThinking) handleCommand();
        }}
        className="flex-1 bg-gray-700 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Enter your command..."
        disabled={isThinking}
        aria-label="Command Input"
        />
        <button
        onClick={handleCommand}
        disabled={isThinking}
        className={`px-4 py-2 rounded flex items-center font-semibold transition-colors duration-200 ${
            isThinking
            ? 'bg-gray-600 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
        aria-label="Send Command"
        >
        {isThinking ? (
            <div className="animate-spin mr-2 h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
        ) : (
            'Send'
        )}
        </button>
        </div>
        </footer>
        </div>
        </div>
    );
};

export default GameInterface;
