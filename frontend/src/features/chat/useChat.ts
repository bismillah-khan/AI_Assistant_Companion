import { useCallback, useRef, useState } from "react";

import { sendChat, streamChat } from "../../services/chatApi";
import type { ChatMessage } from "./types";

const createId = () => crypto.randomUUID();

export const useChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) {
      return;
    }

    setError(null);
    setIsLoading(true);

    const userMessage: ChatMessage = {
      id: createId(),
      role: "user",
      content: text
    };

    const assistantMessage: ChatMessage = {
      id: createId(),
      role: "assistant",
      content: "",
      isStreaming: true
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const streamResult = await streamChat(
        {
          message: text,
          session_id: sessionId ?? undefined
        },
        controller.signal,
        (chunk) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id
                ? { ...msg, content: msg.content + chunk }
                : msg
            )
          );
        }
      );

      if (!streamResult.streamed) {
        const response = await sendChat({
          message: text,
          session_id: sessionId ?? undefined
        });
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessage.id
              ? { ...msg, content: response.reply, isStreaming: false }
              : msg
          )
        );
        setSessionId(response.session_id ?? sessionId);
      } else {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantMessage.id ? { ...msg, isStreaming: false } : msg
          )
        );
        setSessionId(streamResult.sessionId ?? sessionId);
      }
    } catch (err) {
      setMessages((prev) => prev.filter((msg) => msg.id !== assistantMessage.id));
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setIsLoading(false);
      abortRef.current = null;
    }
  }, [sessionId]);

  const cancelStream = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    cancelStream,
    clearChat
  };
};
