import React, { useState, useEffect, useRef } from 'react';
import StatsPanel from './StatsPanel';
import ModelSelector from './ModelSelector';
import MessageList from './MessageList';
import { GameState, Message, SaveFile } from '../types'; // Added SaveFile to types import

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const GameInterface: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputText, setInputText] = useState('');
    const [gameState, setGameState] = useState<GameState | null>(null);
    const [currentModel, setCurrentModel] = useState<'claude' | 'llama'>('claude');
    const [isModelSwitching, setIsModelSwitching] = useState(false);
    const [isThinking, setIsThinking] = useState(false);
    const [showLoadGameModal, setShowLoadGameModal] = useState(false);
    const [availableSaves, setAvailableSaves] = useState<SaveFile[]>([]);
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
            const response = await fetch(`${API_BASE_URL}/game/start`);
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
            const response = await fetch(`${API_BASE_URL}/game/switch-model`, {
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
            const response = await fetch(`${API_BASE_URL}/game/command`, {
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

    const handleSaveGame = async () => {
        addMessage('system', 'Saving game...');
        setIsThinking(true);
        try {
            const response = await fetch(`${API_BASE_URL}/game/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename: `savegame_${Date.now()}.json` }), // Example filename
            });
            const data = await response.json();
            if (response.ok) {
                addMessage('system', data.message || 'Game saved successfully.');
                if (data.game_state) setGameState(data.game_state);
            } else {
                addMessage('error', data.detail || 'Failed to save game.');
            }
        } catch (error) {
            console.error('Error saving game:', error);
            addMessage('error', 'An error occurred while saving the game.');
        } finally {
            setIsThinking(false);
        }
    };

    const fetchAvailableSaves = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/game/saves`);
            if (!response.ok) {
                throw new Error('Failed to fetch save files');
            }
            const data: SaveFile[] = await response.json();
            setAvailableSaves(data);
            return data; // Return data for immediate use if needed
        } catch (error) {
            console.error('Error fetching save files:', error);
            addMessage('error', 'Failed to fetch save files.');
            setAvailableSaves([]); // Clear saves on error
            return []; // Return empty array on error
        }
    };

    const handleShowLoadGameModal = async () => {
        addMessage('system', 'Fetching save files...');
        setIsThinking(true);
        await fetchAvailableSaves();
        setShowLoadGameModal(true);
        setIsThinking(false);
    };

    const handleLoadGame = async (filename: string) => {
        setShowLoadGameModal(false);
        addMessage('system', `Loading game: ${filename}...`);
        setIsThinking(true);
        try {
            const response = await fetch(`${API_BASE_URL}/game/load`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ filename }),
            });
            const data = await response.json();
            if (response.ok) {
                addMessage('system', data.message || 'Game loaded successfully.');
                if (data.game_state) {
                    setGameState(data.game_state);
                    // Potentially clear messages and add the room description from loaded state
                    setMessages([{ type: 'system', content: `Game loaded. ${data.game_state.current_room || ''}` }]);

                }
            } else {
                addMessage('error', data.detail || 'Failed to load game.');
            }
        } catch (error) {
            console.error('Error loading game:', error);
            addMessage('error', 'An error occurred while loading the game.');
        } finally {
            setIsThinking(false);
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

        <div className="mt-4 space-y-2">
            <button
                onClick={handleSaveGame}
                disabled={isThinking}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded transition-colors duration-200 disabled:bg-gray-500"
            >
                Save Game
            </button>
            <button
                onClick={handleShowLoadGameModal}
                disabled={isThinking}
                className="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-2 px-4 rounded transition-colors duration-200 disabled:bg-gray-500"
            >
                Load Game
            </button>
        </div>

        </aside>

        {/* Load Game Modal */}
        {showLoadGameModal && (
            <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
                <div className="bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full">
                    <h3 className="text-xl font-semibold mb-4">Load Game</h3>
                    {availableSaves.length > 0 ? (
                        <ul className="space-y-2 max-h-60 overflow-y-auto mb-4">
                            {availableSaves.map((save) => (
                                <li key={save.filename}>
                                    <button
                                        onClick={() => handleLoadGame(save.filename)}
                                        className="w-full text-left px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded"
                                    >
                                        {save.filename} <span className="text-xs text-gray-400">({new Date(save.timestamp).toLocaleString()})</span>
                                    </button>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <p className="text-gray-400 mb-4">No save files found.</p>
                    )}
                    <button
                        onClick={() => setShowLoadGameModal(false)}
                        className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded transition-colors duration-200"
                    >
                        Cancel
                    </button>
                </div>
            </div>
        )}

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
