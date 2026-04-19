import { useCallback, useEffect, useState } from "react";
import type { Message } from "../types";
import ChatPanel from "./ChatPanel";
import {
  VolumeIcon,
  VolumeMuteIcon,
  MinimizeIcon,
  MaximizeIcon,
  MicIcon,
  KeyboardIcon,
} from "./Icons";

interface OverlayDemoProps {
  messages: Message[];
  isRecording: boolean;
  isProcessing: boolean;
  elapsed: number;
  selectedVoice: string;
  onVoiceChange: (voiceId: string) => void;
  onRecordToggle: () => void;
  onSendText: (text: string) => void;
  onBack: () => void;
  muted: boolean;
  onToggleMute: () => void;
}

export default function OverlayDemo({
  messages,
  isRecording,
  isProcessing,
  elapsed,
  selectedVoice,
  onVoiceChange,
  onRecordToggle,
  onSendText,
  onBack,
  muted,
  onToggleMute,
}: OverlayDemoProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [focusInput, setFocusInput] = useState(0);
  const lastMessage = messages[messages.length - 1];

  const expandAndFocus = useCallback(() => {
    setCollapsed(false);
    setFocusInput((n) => n + 1);
  }, []);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "/" && collapsed) {
        e.preventDefault();
        expandAndFocus();
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [collapsed, expandAndFocus]);

  return (
    <div className="h-full w-full relative overflow-hidden select-none">
      {/* Game screenshot background */}
      <div className="absolute inset-0">
        <img
          src="/desktop-bg.jpg"
          alt=""
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/20" />
      </div>

      {/* Back to intro */}
      <button
        onClick={onBack}
        className="absolute top-5 left-5 z-30 font-mono text-[11px] text-white/50 hover:text-white/90 transition-colors cursor-pointer backdrop-blur-sm bg-black/20 px-2.5 py-1 rounded-lg"
      >
        &larr; intro
      </button>

      {collapsed ? (
        /* ── Collapsed bar ── */
        <div
          className="absolute top-4 right-4 z-20 flex items-center gap-3 rounded-xl border border-white/10 px-4 py-2.5"
          style={{
            background: "rgba(10, 10, 18, 0.35)",
            backdropFilter: "blur(20px) saturate(1.3)",
            WebkitBackdropFilter: "blur(20px) saturate(1.3)",
            maxWidth: "min(420px, calc(100vw - 100px))",
            animation: "collapse-in 0.3s ease-out",
          }}
        >
          {/* Live indicator */}
          <span className="relative flex h-1.5 w-1.5 shrink-0">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75" />
            <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent" />
          </span>

          {/* Latest message */}
          {lastMessage ? (
            <div className="flex items-center gap-2 min-w-0 flex-1">
              <span className="shrink-0 text-[10px]">
                {lastMessage.source === "voice" ? (
                  <span className="text-accent"><MicIcon /></span>
                ) : (
                  <span className="text-voice"><KeyboardIcon /></span>
                )}
              </span>
              <span className="text-[11px] text-white/70 truncate font-mono">
                {lastMessage.text}
              </span>
            </div>
          ) : (
            <span className="text-[11px] text-white/40 font-mono">
              No messages yet
            </span>
          )}

          {/* Mute toggle */}
          <button
            onClick={onToggleMute}
            className="shrink-0 w-7 h-7 flex items-center justify-center rounded-lg text-xs transition-colors cursor-pointer hover:bg-white/10"
            style={{ color: muted ? "var(--color-danger)" : "rgba(255,255,255,0.5)" }}
            title={muted ? "Unmute TTS" : "Mute TTS"}
          >
            {muted ? <VolumeMuteIcon /> : <VolumeIcon />}
          </button>

          {/* Expand button */}
          <button
            onClick={expandAndFocus}
            className="shrink-0 w-7 h-7 flex items-center justify-center rounded-lg text-white/50 text-xs hover:text-white/90 hover:bg-white/10 transition-colors cursor-pointer"
            title="Expand overlay"
          >
            <MaximizeIcon />
          </button>
        </div>
      ) : (
        /* ── Expanded panel ── */
        <div
          className="absolute top-5 right-5 z-20"
          style={{
            width: "min(370px, calc(100vw - 40px))",
            height: "min(500px, calc(100vh - 40px))",
            animation: "expand-in 0.3s ease-out",
          }}
        >
          <ChatPanel
            messages={messages}
            isRecording={isRecording}
            isProcessing={isProcessing}
            elapsed={elapsed}
            selectedVoice={selectedVoice}
            onVoiceChange={onVoiceChange}
            onRecordToggle={onRecordToggle}
            onSend={onSendText}
            muted={muted}
            onToggleMute={onToggleMute}
            onCollapse={() => setCollapsed(true)}
            focusInput={focusInput}
          />
        </div>
      )}
    </div>
  );
}
