import { useCallback, useEffect, useRef, useState } from "react";
import { ChevronDownIcon, VolumeIcon } from "./Icons";

interface VoiceInfo {
  id: string;
  name: string;
  gender: string;
}

interface VoicePickerProps {
  selectedVoice: string;
  onSelect: (voiceId: string) => void;
}

export default function VoicePicker({
  selectedVoice,
  onSelect,
}: VoicePickerProps) {
  const [voices, setVoices] = useState<VoiceInfo[]>([]);
  const [open, setOpen] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/voices")
      .then((r) => r.json())
      .then((data: VoiceInfo[]) => setVoices(data))
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!open) return;
    function onClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", onClickOutside);
    return () => document.removeEventListener("mousedown", onClickOutside);
  }, [open]);

  const preview = useCallback(
    async (voiceId: string) => {
      setPreviewing(true);
      try {
        const fd = new FormData();
        fd.append("text", "This is how I sound.");
        fd.append("voice", voiceId);
        const res = await fetch("/api/tts", { method: "POST", body: fd });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        audio.onended = () => {
          URL.revokeObjectURL(url);
          setPreviewing(false);
        };
        await audio.play();
      } catch {
        setPreviewing(false);
      }
    },
    [],
  );

  const selectedLabel =
    voices.find((v) => v.id === selectedVoice)?.name ?? selectedVoice;

  const shortLabel = selectedLabel
    .replace("Microsoft ", "")
    .replace(" Online (Natural)", "");

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 text-[10px] font-mono text-text-muted hover:text-text transition-colors cursor-pointer"
      >
        <VolumeIcon className="text-xs" />
        <span className="max-w-[90px] truncate">{shortLabel}</span>
        <ChevronDownIcon
          className={`text-[10px] transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div
          className="absolute top-full right-0 mt-1.5 w-64 max-h-52 overflow-y-auto rounded-xl border border-glass-border py-1"
          style={{
            background: "rgba(10, 10, 18, 0.92)",
            backdropFilter: "blur(20px)",
            animation: "slide-up 0.15s ease-out",
            zIndex: 50,
          }}
        >
          {voices.length === 0 ? (
            <p className="px-3 py-2 text-[10px] font-mono text-text-muted">
              Loading voices…
            </p>
          ) : (
            voices.map((v) => {
              const label = v.name
                .replace("Microsoft ", "")
                .replace(" Online (Natural)", "");
              const isActive = v.id === selectedVoice;
              return (
                <div
                  key={v.id}
                  className="flex items-center justify-between group"
                >
                  <button
                    onClick={() => {
                      onSelect(v.id);
                      setOpen(false);
                    }}
                    className={`flex-1 text-left px-3 py-1.5 text-[11px] font-mono transition-colors cursor-pointer ${
                      isActive
                        ? "text-accent bg-accent-dim/30"
                        : "text-text-secondary hover:text-text hover:bg-surface-hover"
                    }`}
                  >
                    {label}
                    <span className="ml-1.5 text-[9px] text-text-muted/60">
                      {v.gender === "Male" ? "M" : "F"}
                    </span>
                  </button>
                  <button
                    onClick={() => preview(v.id)}
                    disabled={previewing}
                    className="shrink-0 px-2 py-1.5 text-[10px] text-text-muted hover:text-accent transition-colors cursor-pointer opacity-0 group-hover:opacity-100"
                  >
                    <VolumeIcon />
                  </button>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
