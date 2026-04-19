import { MicIcon, KeyboardIcon, ArrowRightIcon } from "./Icons";

interface IntroScreenProps {
  onStart: () => void;
}

export default function IntroScreen({ onStart }: IntroScreenProps) {
  return (
    <div className="h-full bg-bg text-text relative overflow-hidden">
      {/* ── Animated background blobs ── */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          className="absolute rounded-full opacity-25 blur-[140px]"
          style={{
            width: 700,
            height: 700,
            background:
              "radial-gradient(circle, var(--color-accent) 0%, transparent 70%)",
            top: "-20%",
            right: "-15%",
            animation: "blob-drift-1 18s ease-in-out infinite",
          }}
        />
        <div
          className="absolute rounded-full opacity-20 blur-[120px]"
          style={{
            width: 500,
            height: 500,
            background:
              "radial-gradient(circle, var(--color-voice) 0%, transparent 70%)",
            bottom: "-15%",
            left: "-10%",
            animation: "blob-drift-2 22s ease-in-out infinite",
          }}
        />
        <div
          className="absolute rounded-full opacity-10 blur-[100px]"
          style={{
            width: 350,
            height: 350,
            background:
              "radial-gradient(circle, #fff 0%, transparent 70%)",
            top: "40%",
            left: "55%",
            animation: "blob-drift-3 15s ease-in-out infinite",
          }}
        />
      </div>

      {/* ── Dot grid texture ── */}
      <div
        className="absolute inset-0 opacity-[0.025] pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle, #fff 0.8px, transparent 0.8px)",
          backgroundSize: "28px 28px",
        }}
      />

      {/* ── Scrollable content ── */}
      <div className="h-full overflow-y-auto">
        <div className="relative z-10 min-h-full flex flex-col items-center justify-center px-8 py-20">
          {/* Decorative accent dots */}
          <div
            className="flex items-center gap-2 mb-8"
            style={{ animation: "fade-in 0.6s ease-out" }}
          >
            <div className="w-2 h-2 rounded-full bg-accent" />
            <div className="w-1.5 h-1.5 rounded-full bg-text-muted/30" />
            <div className="w-2 h-2 rounded-full bg-voice" />
          </div>

          {/* Main title — serif for editorial contrast */}
          <h1
            className="leading-[0.85] tracking-tight mb-5 text-center"
            style={{
              fontFamily: "'Cormorant Garamond', serif",
              fontSize: "clamp(5rem, 12vw, 8.5rem)",
              fontWeight: 600,
              animation: "fade-in-up 0.7s ease-out 0.1s both",
            }}
          >
            <span className="text-accent">TT</span>
            <span
              className="text-text/80"
              style={{ fontStyle: "italic", fontWeight: 400 }}
            >
              S
            </span>
            <span className="text-voice">TT</span>
          </h1>

          {/* Monospace subtitle */}
          <p
            className="font-mono text-[10px] text-text-muted tracking-[0.35em] uppercase mb-14"
            style={{ animation: "fade-in-up 0.7s ease-out 0.2s both" }}
          >
            text &rarr; speech &rarr; text
          </p>

          {/* Tagline */}
          <p
            className="text-lg text-text-secondary max-w-md text-center leading-relaxed mb-16"
            style={{
              fontFamily: "'Sora', sans-serif",
              fontWeight: 300,
              animation: "fade-in-up 0.7s ease-out 0.3s both",
            }}
          >
            A real-time overlay that bridges voice and text, so{" "}
            <span className="text-text font-medium">
              no one gets left behind
            </span>{" "}
            in voice conversations.
          </p>

          {/* Feature cards */}
          <div
            className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg w-full mb-16"
            style={{ animation: "fade-in-up 0.7s ease-out 0.4s both" }}
          >
            {/* Speak card */}
            <div
              className="group relative rounded-2xl border border-accent/20"
              style={{
                background:
                  "linear-gradient(135deg, rgba(0,212,170,0.06), rgba(0,212,170,0.02))",
              }}
            >
              <div className="px-7 py-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-xl bg-accent/10 flex items-center justify-center text-accent text-sm">
                    <MicIcon />
                  </div>
                  <span className="font-mono text-[10px] font-semibold text-accent tracking-widest uppercase">
                    Speak
                  </span>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed">
                  Record your voice — it's transcribed to text and read aloud to
                  confirm.
                </p>
              </div>
            </div>

            {/* Type card */}
            <div
              className="group relative rounded-2xl border border-voice/20"
              style={{
                background:
                  "linear-gradient(135deg, rgba(124,107,240,0.06), rgba(124,107,240,0.02))",
              }}
            >
              <div className="px-7 py-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-9 h-9 rounded-xl bg-voice/10 flex items-center justify-center text-voice text-sm">
                    <KeyboardIcon />
                  </div>
                  <span className="font-mono text-[10px] font-semibold text-voice tracking-widest uppercase">
                    Type
                  </span>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed">
                  Press{" "}
                  <kbd className="font-mono text-accent bg-accent/10 px-1.5 py-0.5 rounded text-[10px]">
                    /
                  </kbd>{" "}
                  to type a message — it's spoken aloud automatically.
                </p>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div
            className="w-12 h-[1px] bg-glass-border mb-16"
            style={{ animation: "fade-in-up 0.7s ease-out 0.45s both" }}
          />

          {/* Who it's for — subtle note */}
          <p
            className="text-xs text-text-muted text-center max-w-sm leading-relaxed mb-14"
            style={{ animation: "fade-in-up 0.7s ease-out 0.5s both" }}
          >
            Built for{" "}
            <span className="text-text-secondary">
              deaf & hard-of-hearing users
            </span>
            , non-verbal participants, and anyone who prefers text over voice.
          </p>

          {/* Start button */}
          <button
            onClick={onStart}
            className="group relative cursor-pointer inline-flex items-center gap-3 text-bg font-semibold text-sm px-10 py-4 rounded-2xl transition-all duration-300 hover:scale-[1.03] active:scale-[0.97]"
            style={{
              background:
                "linear-gradient(135deg, var(--color-accent), #00b894)",
              animation:
                "fade-in-up 0.7s ease-out 0.55s both, glow-breathe 3s ease-in-out infinite 1.2s",
            }}
          >
            Start Demo
            <ArrowRightIcon className="text-base transition-transform duration-300 group-hover:translate-x-1" />
          </button>

          {/* Bottom spacer / version tag */}
          <p
            className="mt-14 font-mono text-[9px] text-text-muted/30 tracking-widest"
            style={{ animation: "fade-in 0.6s ease-out 0.8s both" }}
          >
            prototype v1
          </p>
        </div>
      </div>
    </div>
  );
}
