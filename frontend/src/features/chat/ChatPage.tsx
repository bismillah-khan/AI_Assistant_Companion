import { useState, useRef } from "react";

import ErrorBanner from "../../components/ErrorBanner";
import LoadingDots from "../../components/LoadingDots";
import { useChat } from "./useChat";
import ChatMessage from "./ChatMessage";
import MessageList from "./MessageList";
import Composer from "./Composer";
import VoiceRecordButton from "../voice/VoiceRecordButton";
import { uploadTextFile } from "../../services/fileApi";

const ChatPage = () => {
  const { messages, isLoading, error, sendMessage, clearChat } = useChat();
  const [input, setInput] = useState("");
  const [showCodeMode, setShowCodeMode] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = async () => {
    let text = input;
    if (uploadedFile) {
      text = `${text}\n\n[Attached File Content]:\n${uploadedFile}`;
      setUploadedFile(null);
    }
    setInput("");
    await sendMessage(text);
  };

  const handleClearChat = () => {
    if (confirm("Clear all messages?")) {
      clearChat();
      setInput("");
      setUploadedFile(null);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await uploadTextFile(file);
      const fileExtension = result.type.slice(1);
      const fileContext = `[File: ${result.filename}]\n\`\`\`${fileExtension}\n${result.content}\n\`\`\``;
      setUploadedFile(fileContext);
      setInput(prev => prev ? `${prev}\n\n${fileContext}` : fileContext);
    } catch (error) {
      alert(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="app-header-content">
          <p className="app-eyebrow">MY AI FRIEND</p>
          <h1>Chat with your voice-first agent.</h1>
          <p className="app-subtitle">
            Streaming responses, tool-ready outputs, and audio input.
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="secondary-button"
            onClick={() => setShowCodeMode(!showCodeMode)}
            title="Toggle Code Mode"
          >
            {showCodeMode ? '💬 Chat' : '💻 Code'}
          </button>
          <button 
            className="secondary-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isLoading || isUploading}
            title="Upload File"
          >
            {isUploading ? '⏳' : '📎'} Upload
          </button>
          <button 
            className="secondary-button"
            onClick={handleClearChat}
            disabled={isLoading}
            title="Clear Chat"
          >
            🗑️ Clear
          </button>
          <VoiceRecordButton onTranscription={setInput} disabled={isLoading} />
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.js,.ts,.jsx,.tsx,.py,.java,.cpp,.c,.html,.css,.json,.md"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />
        </div>
      </header>

      <section className="chat-card">
        {error && <ErrorBanner message={error} />}
        {uploadedFile && (
          <div className="file-upload-notification">
            ✅ File uploaded and ready to send
          </div>
        )}
        {showCodeMode ? (
          <div className="code-mode-wrapper">
            <div className="code-mode-header">
              <strong>💻 Code Mode</strong> - Ask coding questions, paste code for review, or request code generation
            </div>
            <div className="message-list-wrapper">
              <MessageList>
                {messages.map((message, index) => (
                  <ChatMessage key={message.id} message={message} index={index} />
                ))}
                {isLoading && messages.length === 0 && (
                  <div className="empty-state">
                    <LoadingDots label="Ready for coding tasks" />
                  </div>
                )}
              </MessageList>
            </div>
            <Composer
              value={input}
              onChange={setInput}
              onSend={handleSend}
              disabled={isLoading}
            />
          </div>
        ) : (
          <>
            <div className="message-list-wrapper">
              <MessageList>
                {messages.map((message, index) => (
                  <ChatMessage key={message.id} message={message} index={index} />
                ))}
                {isLoading && messages.length === 0 && (
                  <div className="empty-state">
                    <LoadingDots label="Awaiting your first message" />
                  </div>
                )}
              </MessageList>
            </div>
            <Composer
              value={input}
              onChange={setInput}
              onSend={handleSend}
              disabled={isLoading}
            />
          </>
        )}
      </section>
    </div>
  );
};

export default ChatPage;
