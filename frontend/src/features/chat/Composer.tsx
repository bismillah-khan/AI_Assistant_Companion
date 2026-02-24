import LoadingDots from "../../components/LoadingDots";
import type React from "react";

interface ComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
}

const Composer = ({ value, onChange, onSend, disabled }: ComposerProps) => {
  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSend();
    }
  };

  return (
    <div className="composer">
      <textarea
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message or use the microphone..."
        disabled={disabled}
        rows={3}
      />
      <div className="composer-actions">
        <button
          className="primary-button"
          onClick={onSend}
          disabled={disabled || !value.trim()}
        >
          Send
        </button>
        {disabled && <LoadingDots label="Thinking" />}
      </div>
    </div>
  );
};

export default Composer;
