import React from 'react';

/**
 * Scrollable container displaying the history of game messages.
 *
 * @param props.messages - Array of messages to render.
 * @param ref - Reference to allow parent components to scroll to bottom.
 */

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

MessageList.displayName = 'MessageList';

export default MessageList;
