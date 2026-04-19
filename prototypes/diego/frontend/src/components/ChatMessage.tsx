import type { Message } from "../types";
import { MicIcon, KeyboardIcon, VolumeIcon } from "./Icons";

interface ChatMessageProps {
  message: Message;
  style?: React.CSSProperties;
}

export default function ChatMessage({ message, style }: ChatMessageProps) {
  const isVoice = message.source === "voice";
  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className="flex items-start gap-2.5 px-4.5 py-2.5" style={style}>
      <div
        className={`shrink-0 mt-px w-6 h-6 rounded-md flex items-center justify-center text-xs ${
          isVoice ? "bg-accent-dim text-accent" : "bg-voice-dim text-voice"
        }`}
      >
        {isVoice ? <MicIcon /> : <KeyboardIcon />}
      </div>

      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-1.5 mb-px">
          <span
            className={`text-[11px] font-mono font-600 ${
              isVoice ? "text-accent" : "text-voice"
            }`}
          >
            {isVoice ? "Voice User" : "You"}
          </span>
          <span className="text-[9px] font-mono text-text-muted/60">{time}</span>
          <span
            className={`inline-flex items-center gap-0.5 text-[9px] font-mono px-1 py-px rounded ${
              isVoice
                ? "bg-accent-dim/40 text-accent/60"
                : "bg-voice-dim/40 text-voice/60"
            }`}
          >
            {isVoice ? (
              "transcribed"
            ) : (
              <>
                <VolumeIcon className="text-[8px]" /> spoken
              </>
            )}
          </span>
        </div>

        <p className="text-xs text-text/90 leading-relaxed break-words">
          {message.text}
        </p>
      </div>
    </div>
  );
}
