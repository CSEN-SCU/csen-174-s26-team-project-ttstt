import { useEffect, useRef } from "react";
import type { Message } from "../types";
import ChatMessage from "./ChatMessage";
import TextInput from "./TextInput";
import RecordButton from "./RecordButton";
import VoicePicker from "./VoicePicker";
import {
  KeyboardIcon,
  MicIcon,
  VolumeIcon,
  VolumeMuteIcon,
  MinimizeIcon,
} from "./Icons";

interface ChatPanelProps {
  messages: Message[];
  isRecording: boolean;
  isProcessing: boolean;
  elapsed: number;
  selectedVoice: string;
  onVoiceChange: (voiceId: string) => void;
  onRecordToggle: () => void;
  onSend: (text: string) => void;
  muted: boolean;
  onToggleMute: () => void;
  onCollapse: () => void;
  focusInput?: number;
}

export default function ChatPanel({
  messages,
  isRecording,
  isProcessing,
  elapsed,
  selectedVoice,
  onVoiceChange,
  onRecordToggle,
  onSend,
  muted,
  onToggleMute,
  onCollapse,
  focusInput,
}: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages.length]);

  return (
    <div
      className="flex flex-col h-full rounded-2xl border border-white/[0.08] overflow-hidden"
      style={{
        background: "rgba(10, 10, 18, 0.3)",
        backdropFilter: "blur(24px) saturate(1.3)",
        WebkitBackdropFilter: "blur(24px) saturate(1.3)",
      }}
    >
      {/* Header */}
      <div className="shrink-0 flex items-center justify-between px-4 py-2.5 border-b border-white/[0.06]">
        <div className="flex items-center gap-2">
          <span className="relative flex h-1.5 w-1.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent" />
          </span>
          <span className="font-mono text-[10px] font-semibold text-white/60 tracking-widest uppercase">
            TTSTT
          </span>
        </div>

        <div className="flex items-center gap-1">
          <VoicePicker
            selectedVoice={selectedVoice}
            onSelect={onVoiceChange}
          />

          {/* Mute toggle */}
          <button
            onClick={onToggleMute}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-xs transition-colors cursor-pointer hover:bg-white/10"
            style={{
              color: muted ? "var(--color-danger)" : "rgba(255,255,255,0.45)",
            }}
            title={muted ? "Unmute TTS" : "Mute TTS"}
          >
            {muted ? <VolumeMuteIcon /> : <VolumeIcon />}
          </button>

          {/* Collapse button */}
          <button
            onClick={onCollapse}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-white/40 text-xs hover:text-white/80 hover:bg-white/10 transition-colors cursor-pointer"
            title="Collapse overlay"
          >
            <MinimizeIcon />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto py-3 min-h-0">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-text-muted px-8">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-8 h-8 rounded-lg bg-accent/10 flex items-center justify-center text-accent text-sm">
                <MicIcon />
              </div>
              <div className="text-white/20 text-sm">+</div>
              <div className="w-8 h-8 rounded-lg bg-voice/10 flex items-center justify-center text-voice text-sm">
                <KeyboardIcon />
              </div>
            </div>
            <p className="text-[11px] font-mono text-center leading-relaxed text-white/30">
              Press <span className="text-accent">Speak</span> to record
              <br />
              or <span className="text-voice">/</span> to type
            </p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              style={{
                animation: `slide-up 0.25s ease-out ${Math.min(i * 0.03, 0.2)}s both`,
              }}
            />
          ))
        )}
      </div>

      {/* Controls footer */}
      <div className="shrink-0 border-t border-white/[0.06] px-4 py-3 flex flex-col gap-2.5">
        <TextInput onSend={onSend} focusInput={focusInput} />
        <div className="flex items-center justify-between">
          <RecordButton
            isRecording={isRecording}
            isProcessing={isProcessing}
            elapsed={elapsed}
            onToggle={onRecordToggle}
          />
          <span className="text-[9px] font-mono text-white/25 mr-0.5">
            <kbd className="text-white/35 bg-white/5 px-1 py-px rounded text-[8px]">
              /
            </kbd>{" "}
            to type
          </span>
        </div>
      </div>
    </div>
  );
}
