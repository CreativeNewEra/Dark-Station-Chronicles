import React from 'react';

import { Message } from '../types';

interface MessageListProps {
  messages: Message[];
}

const MessageList = React.forwardRef<HTMLDivElement, MessageListProps>(
  ({ messages }, ref) => (
    <div className="flex-1 p-4 overflow-y-auto" ref={ref}>
      {messages.map((msg, idx) => (
        <div key={idx} className="mb-2">
          {msg.content}
        </div>
      ))}
    </div>
  )
);

export default MessageList;
