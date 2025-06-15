import React, { forwardRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { MessageListProps } from '../types';

const MessageList = forwardRef<HTMLDivElement, MessageListProps>(
    ({ messages }, ref) => (
        <main className="flex-1 p-4 overflow-auto">
        <div className="space-y-4">
        {messages.map((msg, idx) => (
            <div
            key={idx}
            className={`p-3 rounded transition-all duration-300 ${
                msg.type === 'player'
                ? 'bg-gray-800 text-blue-400'
                : msg.type === 'error'
                ? 'bg-red-900 text-red-400'
                : 'bg-gray-700'
            }`}
            >
            {msg.type === 'player' ? (
                <>
                <span className="text-blue-500 font-semibold">&gt; </span>
                {msg.content}
                </>
            ) : (
                <div className="prose prose-invert max-w-none">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
            )}
            </div>
        ))}
        <div ref={ref} />
        </div>
        </main>
    )
);

MessageList.displayName = 'MessageList';

export default MessageList;
