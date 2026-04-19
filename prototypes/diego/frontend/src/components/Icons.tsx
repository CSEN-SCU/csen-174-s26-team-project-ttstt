const s = { width: "1em", height: "1em", fill: "currentColor" } as const;

export function MicIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M12 2C10.9 2 10 2.9 10 4V12C10 13.1 10.9 14 12 14C13.1 14 14 13.1 14 12V4C14 2.9 13.1 2 12 2Z" />
      <path d="M17 12C17 14.76 14.76 17 12 17C9.24 17 7 14.76 7 12H5C5 15.53 7.61 18.43 11 18.93V22H13V18.93C16.39 18.43 19 15.53 19 12H17Z" />
    </svg>
  );
}

export function KeyboardIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M20 5H4C2.9 5 2 5.9 2 7V17C2 18.1 2.9 19 4 19H20C21.1 19 22 18.1 22 17V7C22 5.9 21.1 5 20 5ZM11 8H13V10H11V8ZM11 11H13V13H11V11ZM8 8H10V10H8V8ZM8 11H10V13H8V11ZM7 13H5V11H7V13ZM7 10H5V8H7V10ZM16 17H8V15H16V17ZM16 13H14V11H16V13ZM16 10H14V8H16V10ZM19 13H17V11H19V13ZM19 10H17V8H19V10Z" />
    </svg>
  );
}

export function SendIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
    </svg>
  );
}

export function ArrowRightIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      style={{ width: "1em", height: "1em" }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

export function StopIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  );
}

export function WaveformIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 24"
      style={{ width: "1.5em", height: "1em" }}
      fill="currentColor"
      className={className}
    >
      <rect x="2" y="8" width="3" height="8" rx="1.5" opacity="0.5">
        <animate attributeName="height" values="8;16;8" dur="1s" repeatCount="indefinite" />
        <animate attributeName="y" values="8;4;8" dur="1s" repeatCount="indefinite" />
      </rect>
      <rect x="8" y="4" width="3" height="16" rx="1.5" opacity="0.7">
        <animate attributeName="height" values="16;6;16" dur="1.2s" repeatCount="indefinite" />
        <animate attributeName="y" values="4;9;4" dur="1.2s" repeatCount="indefinite" />
      </rect>
      <rect x="14" y="2" width="3" height="20" rx="1.5" opacity="0.9">
        <animate attributeName="height" values="20;8;20" dur="0.8s" repeatCount="indefinite" />
        <animate attributeName="y" values="2;8;2" dur="0.8s" repeatCount="indefinite" />
      </rect>
      <rect x="20" y="6" width="3" height="12" rx="1.5" opacity="0.7">
        <animate attributeName="height" values="12;18;12" dur="1.1s" repeatCount="indefinite" />
        <animate attributeName="y" values="6;3;6" dur="1.1s" repeatCount="indefinite" />
      </rect>
      <rect x="26" y="9" width="3" height="6" rx="1.5" opacity="0.5">
        <animate attributeName="height" values="6;14;6" dur="0.9s" repeatCount="indefinite" />
        <animate attributeName="y" values="9;5;9" dur="0.9s" repeatCount="indefinite" />
      </rect>
    </svg>
  );
}

export function VolumeIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M3 9V15H7L12 20V4L7 9H3ZM16.5 12C16.5 10.23 15.48 8.71 14 7.97V16.02C15.48 15.29 16.5 13.77 16.5 12ZM14 3.23V5.29C16.89 6.15 19 8.83 19 12C19 15.17 16.89 17.85 14 18.71V20.77C18.01 19.86 21 16.28 21 12C21 7.72 18.01 4.14 14 3.23Z" />
    </svg>
  );
}

export function SpinnerIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      style={{ width: "1em", height: "1em" }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      className={className}
    >
      <path d="M12 2a10 10 0 0 1 10 10" opacity="0.9">
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 12 12"
          to="360 12 12"
          dur="0.8s"
          repeatCount="indefinite"
        />
      </path>
    </svg>
  );
}

export function SettingsIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M19.14 12.94C19.18 12.64 19.2 12.33 19.2 12C19.2 11.68 19.18 11.36 19.13 11.06L21.16 9.48C21.34 9.34 21.39 9.07 21.28 8.87L19.36 5.55C19.24 5.33 18.99 5.26 18.77 5.33L16.38 6.29C15.88 5.91 15.35 5.59 14.76 5.35L14.4 2.81C14.36 2.57 14.16 2.4 13.92 2.4H10.08C9.84 2.4 9.65 2.57 9.61 2.81L9.25 5.35C8.66 5.59 8.12 5.92 7.63 6.29L5.24 5.33C5.02 5.25 4.77 5.33 4.65 5.55L2.74 8.87C2.62 9.08 2.66 9.34 2.86 9.48L4.89 11.06C4.84 11.36 4.8 11.69 4.8 12C4.8 12.31 4.82 12.64 4.87 12.94L2.85 14.52C2.67 14.66 2.62 14.93 2.73 15.13L4.65 18.45C4.77 18.67 5.02 18.74 5.24 18.67L7.63 17.71C8.13 18.09 8.66 18.41 9.25 18.65L9.61 21.19C9.65 21.43 9.84 21.6 10.08 21.6H13.92C14.16 21.6 14.36 21.43 14.39 21.19L14.75 18.65C15.34 18.41 15.88 18.09 16.37 17.71L18.76 18.67C18.98 18.75 19.23 18.67 19.35 18.45L21.27 15.13C21.39 14.91 21.34 14.66 21.15 14.52L19.14 12.94ZM12 15.6C10.02 15.6 8.4 13.98 8.4 12C8.4 10.02 10.02 8.4 12 8.4C13.98 8.4 15.6 10.02 15.6 12C15.6 13.98 13.98 15.6 12 15.6Z" />
    </svg>
  );
}

export function ChevronDownIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M7.41 8.59L12 13.17L16.59 8.59L18 10L12 16L6 10L7.41 8.59Z" />
    </svg>
  );
}

export function CloseIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      style={{ width: "1em", height: "1em" }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      className={className}
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export function VolumeMuteIcon({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" style={s} className={className}>
      <path d="M16.5 12C16.5 10.23 15.48 8.71 14 7.97V10.18L16.45 12.63C16.48 12.43 16.5 12.22 16.5 12ZM19 12C19 12.94 18.8 13.82 18.46 14.64L19.97 16.15C20.63 14.91 21 13.5 21 12C21 7.72 18.01 4.14 14 3.23V5.29C16.89 6.15 19 8.83 19 12ZM4.27 3L3 4.27L7.73 9H3V15H7L12 20V13.27L16.25 17.52C15.58 18.04 14.83 18.45 14 18.71V20.77C15.38 20.45 16.63 19.82 17.68 18.96L19.73 21L21 19.73L12 10.73L4.27 3ZM12 4L9.91 6.09L12 8.18V4Z" />
    </svg>
  );
}

export function MinimizeIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      style={{ width: "1em", height: "1em" }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points="4 14 10 14 10 20" />
      <polyline points="20 10 14 10 14 4" />
      <line x1="14" y1="10" x2="21" y2="3" />
      <line x1="3" y1="21" x2="10" y2="14" />
    </svg>
  );
}

export function MaximizeIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      style={{ width: "1em", height: "1em" }}
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points="15 3 21 3 21 9" />
      <polyline points="9 21 3 21 3 15" />
      <line x1="21" y1="3" x2="14" y2="10" />
      <line x1="3" y1="21" x2="10" y2="14" />
    </svg>
  );
}
