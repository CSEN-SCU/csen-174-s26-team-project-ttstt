import { useCallback, useEffect, useRef, useState } from "react";
import { SendIcon } from "./Icons";

interface TextInputProps {
  onSend: (text: string) => void;
  focusInput?: number;
}

export default function TextInput({ onSend, focusInput }: TextInputProps) {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed) return;
    onSend(trimmed);
    setValue("");
  }, [value, onSend]);

  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (e.key === "/" && document.activeElement !== inputRef.current) {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === "Escape" && document.activeElement === inputRef.current) {
        inputRef.current?.blur();
      }
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, []);

  useEffect(() => {
    if (focusInput && focusInput > 0) {
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [focusInput]);

  return (
    <div className="flex items-center gap-1.5 bg-surface border border-glass-border rounded-xl px-2.5 py-1.5 transition-colors focus-within:border-voice/40 focus-within:bg-surface-hover">
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
          }
        }}
        placeholder="Type to speak aloud…  / to focus"
        className="flex-1 bg-transparent text-xs text-text font-mono placeholder:text-text-muted/60 outline-none min-w-0"
      />
      <button
        onClick={handleSubmit}
        disabled={!value.trim()}
        className="shrink-0 w-6 h-6 rounded-lg bg-voice/80 text-bg flex items-center justify-center text-xs transition-all hover:bg-voice disabled:opacity-25 disabled:cursor-default cursor-pointer"
      >
        <SendIcon />
      </button>
    </div>
  );
}
