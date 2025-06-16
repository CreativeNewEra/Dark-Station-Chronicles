import React from 'react';
import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const MessageList = React.forwardRef<HTMLDivElement, MessageListProps>(({ messages }, ref) => {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-2" data-testid="message-list">
      {messages.map((msg) => (
        <div key={msg.id} className={msg.type === 'error' ? 'text-red-400' : msg.type === 'player' ? 'text-green-300' : ''}>
          {msg.content}
        </div>
      ))}
      <div ref={ref} />
    </div>
  );
});

export default MessageList;
