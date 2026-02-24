import type { ChatMessage as ChatMessageType } from "./types";

interface ChatMessageProps {
  message: ChatMessageType;
  index: number;
}

const ChatMessage = ({ message, index }: ChatMessageProps) => {
  const isUser = message.role === "user";

  return (
    <article
      className={`message message-${isUser ? "user" : "assistant"}`}
      style={{
        animationDelay: `${index * 60}ms`
      }}
    >
      <div className="message-meta">
        <span>{isUser ? "You" : "AI"}</span>
        {message.isStreaming && <span className="message-stream">Streaming...</span>}
      </div>
      <p className="message-content">{message.content || "..."}</p>
    </article>
  );
};

export default ChatMessage;
