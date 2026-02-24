import { useEffect, useRef, useState } from "react";

import { transcribeAudio } from "../../services/voiceApi";

interface VoiceRecordButtonProps {
  onTranscription: (text: string) => void;
  disabled?: boolean;
}

const VoiceRecordButton = ({ onTranscription, disabled }: VoiceRecordButtonProps) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [previewText, setPreviewText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      stopTimer();
      stopWaveform();
      stopStream();
    };
  }, []);

  const startRecording = async () => {
    if (disabled || isRecording || isProcessing) {
      return;
    }

    setError(null);
    setPreviewText("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream);
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        stopTimer();
        stopWaveform();
        setIsProcessing(true);
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        try {
          const text = await transcribeAudio(blob);
          setPreviewText(text);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Transcription failed");
        } finally {
          setIsProcessing(false);
          setIsRecording(false);
          stopStream();
        }
      };

      recorder.start();
      setElapsedSeconds(0);
      setIsRecording(true);
      startTimer();
      startWaveform(stream);
    } catch (err) {
      setIsRecording(false);
      setIsProcessing(false);
      setError("Microphone access was denied.");
    }
  };

  const stopRecording = () => {
    recorderRef.current?.stop();
  };

  const usePreview = () => {
    if (previewText.trim()) {
      onTranscription(previewText.trim());
      setPreviewText("");
    }
  };

  const discardPreview = () => {
    setPreviewText("");
  };

  const startTimer = () => {
    stopTimer();
    timerRef.current = window.setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const stopStream = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  };

  const startWaveform = (stream: MediaStream) => {
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 1024;

    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);

    audioContextRef.current = audioContext;
    analyserRef.current = analyser;

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    const ctx = canvas.getContext("2d");

    const draw = () => {
      if (!ctx || !analyserRef.current) {
        return;
      }

      analyserRef.current.getByteTimeDomainData(dataArray);
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "rgba(9, 13, 22, 0.6)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.lineWidth = 2;
      ctx.strokeStyle = "rgba(255, 184, 108, 0.9)";
      ctx.beginPath();

      const sliceWidth = canvas.width / dataArray.length;
      let x = 0;

      for (let i = 0; i < dataArray.length; i += 1) {
        const v = dataArray[i] / 128.0;
        const y = (v * canvas.height) / 2;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }

        x += sliceWidth;
      }

      ctx.lineTo(canvas.width, canvas.height / 2);
      ctx.stroke();
      animationRef.current = requestAnimationFrame(draw);
    };

    draw();
  };

  const stopWaveform = () => {
    if (animationRef.current !== null) {
      cancelAnimationFrame(animationRef.current);
      animationRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
  };

  const formattedTime = new Date(elapsedSeconds * 1000).toISOString().slice(14, 19);

  return (
    <div className="voice-panel">
      <div className="voice-controls">
        <button
          className={`voice-button ${isRecording ? "recording" : ""}`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={disabled || isProcessing}
          aria-pressed={isRecording}
        >
          {isProcessing ? "Processing..." : isRecording ? "Stop" : "Record"}
        </button>
        <div className="voice-status">
          <span className="voice-timer">{formattedTime}</span>
          <span>{isRecording ? "Recording" : "Ready"}</span>
        </div>
      </div>

      <canvas ref={canvasRef} className="voice-meter" width={320} height={60} />

      {previewText && (
        <div className="voice-preview">
          <p>Transcription preview</p>
          <div className="voice-preview-text">{previewText}</div>
          <div className="voice-preview-actions">
            <button className="primary-button" onClick={usePreview}>
              Use text
            </button>
            <button className="voice-button" onClick={discardPreview}>
              Discard
            </button>
          </div>
        </div>
      )}

      {error && <div className="voice-error">{error}</div>}
    </div>
  );
};

export default VoiceRecordButton;
