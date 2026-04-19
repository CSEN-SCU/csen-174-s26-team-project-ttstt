import { useCallback, useState } from "react";
import { useAudioRecorder } from "./hooks/useAudioRecorder";
import { useTTS } from "./hooks/useTTS";
import type { Message } from "./types";

import IntroScreen from "./components/IntroScreen";
import OverlayDemo from "./components/OverlayDemo";

type Screen = "intro" | "overlay";

const DEFAULT_VOICE = "en-US-AriaNeural";

export default function App() {
  const [screen, setScreen] = useState<Screen>("intro");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState(DEFAULT_VOICE);
  const [muted, setMuted] = useState(false);

  const { isRecording, elapsed, startRecording, stopRecording } =
    useAudioRecorder();
  const { play: playTTS } = useTTS();

  const addMessage = useCallback(
    (text: string, source: "voice" | "text") => {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          source,
          text,
          timestamp: Date.now(),
        },
      ]);
    },
    [],
  );

  const handleRecordToggle = useCallback(async () => {
    if (isRecording) {
      setIsProcessing(true);
      try {
        const text = await stopRecording();
        if (text.trim()) {
          addMessage(text.trim(), "voice");
          if (!muted) playTTS(text.trim(), selectedVoice).catch(() => {});
        }
      } catch {
        /* transcription error */
      } finally {
        setIsProcessing(false);
      }
    } else {
      try {
        await startRecording();
      } catch {
        /* mic permission denied */
      }
    }
  }, [isRecording, stopRecording, startRecording, addMessage, playTTS, selectedVoice, muted]);

  const handleSendText = useCallback(
    (text: string) => {
      addMessage(text, "text");
      if (!muted) playTTS(text, selectedVoice).catch(() => {});
    },
    [addMessage, playTTS, selectedVoice, muted],
  );

  if (screen === "intro") {
    return <IntroScreen onStart={() => setScreen("overlay")} />;
  }

  return (
    <OverlayDemo
      messages={messages}
      isRecording={isRecording}
      isProcessing={isProcessing}
      elapsed={elapsed}
      selectedVoice={selectedVoice}
      onVoiceChange={setSelectedVoice}
      onRecordToggle={handleRecordToggle}
      onSendText={handleSendText}
      onBack={() => setScreen("intro")}
      muted={muted}
      onToggleMute={() => setMuted((m) => !m)}
    />
  );
}
