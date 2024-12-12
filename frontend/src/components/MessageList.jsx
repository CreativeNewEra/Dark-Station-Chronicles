import React, { forwardRef } from 'react';

const MessageList = forwardRef(({ messages }, ref) => (
    <main className="flex-1 p-4 overflow-auto">
    <div className="space-y-4">
    {messages.map((msg, idx) => (
        <div
        key={idx}
        className={`p-2 rounded ${
            msg.type === 'player'
            ? 'bg-gray-800 text-blue-400'
            : msg.type === 'error'
            ? 'bg-red-900 text-red-400'
            : 'bg-gray-700'
        }`}
        >
        {msg.type === 'player' && <span>> </span>}
        {msg.content}
        </div>
    ))}
    <div ref={ref} />
    </div>
    </main>
));

export default MessageList;
