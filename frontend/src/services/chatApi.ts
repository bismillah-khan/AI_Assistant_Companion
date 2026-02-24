export interface ChatRequest {
  message: string;
  session_id?: string;
  model?: string;
  temperature?: number;
}

export interface ChatResponse {
  reply: string;
  session_id?: string;
  structured?: Record<string, unknown> | null;
  reasoning?: string[];
}

interface StreamResult {
  streamed: boolean;
  sessionId?: string;
}

export const sendChat = async (payload: ChatRequest): Promise<ChatResponse> => {
  const response = await fetch("/api/v1/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error("Chat request failed");
  }

  return response.json();
};

export const streamChat = async (
  payload: ChatRequest,
  signal: AbortSignal,
  onChunk: (text: string) => void
): Promise<StreamResult> => {
  const response = await fetch("/api/v1/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/plain"
    },
    body: JSON.stringify(payload),
    signal
  });

  if (!response.ok || !response.body) {
    return { streamed: false };
  }

  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return { streamed: false };
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) {
      break;
    }
    const chunk = decoder.decode(value, { stream: true });
    onChunk(chunk);
  }

  return { streamed: true };
};
