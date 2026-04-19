import { MicIcon, StopIcon, SpinnerIcon, WaveformIcon } from "./Icons";

interface RecordButtonProps {
  isRecording: boolean;
  isProcessing: boolean;
  elapsed: number;
  onToggle: () => void;
}

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function RecordButton({
  isRecording,
  isProcessing,
  elapsed,
  onToggle,
}: RecordButtonProps) {
  if (isProcessing) {
    return (
      <button
        disabled
        className="flex items-center gap-2.5 h-10 pl-3 pr-4 rounded-xl bg-surface border border-glass-border text-text-muted cursor-wait select-none"
      >
        <SpinnerIcon className="text-base text-accent" />
        <span className="font-mono text-xs">Transcribing…</span>
      </button>
    );
  }

  if (isRecording) {
    return (
      <button
        onClick={onToggle}
        className="group flex items-center gap-2.5 h-10 pl-3 pr-4 rounded-xl bg-danger/90 text-white cursor-pointer select-none transition-all hover:bg-danger active:scale-[0.97]"
        style={{ animation: "pulse-record 1.5s ease-in-out infinite" }}
      >
        <WaveformIcon className="text-base" />
        <span className="font-mono text-xs font-500 tracking-wide">
          {formatTime(elapsed)}
        </span>
        <span className="w-px h-4 bg-white/30" />
        <StopIcon className="text-sm" />
        <span className="font-mono text-xs">Send</span>
      </button>
    );
  }

  return (
    <button
      onClick={onToggle}
      className="group flex items-center gap-2 h-10 pl-3 pr-4 rounded-xl bg-accent/15 border border-accent/25 text-accent cursor-pointer select-none transition-all hover:bg-accent/25 hover:border-accent/40 active:scale-[0.97]"
    >
      <MicIcon className="text-base" />
      <span className="font-mono text-xs font-500">Speak</span>
    </button>
  );
}
