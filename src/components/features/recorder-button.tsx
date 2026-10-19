import { cn } from "@/lib/utils";
import { formatClock } from "@/lib/utils";
import type { RecorderState } from "@/hooks/use-recorder";

interface Props {
  state: RecorderState;
  seconds: number;
  busy: boolean;
  onStart: () => void;
  onStop: () => void;
}

export function RecorderButton({ state, seconds, busy, onStart, onStop }: Props) {
  const recording = state === "recording";
  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        {recording && <span aria-hidden className="animate-ring absolute inset-0 rounded-full bg-danger/40" />}
        <button
          type="button"
          onClick={recording ? onStop : onStart}
          disabled={busy || state === "processing"}
          aria-label={recording ? "Stop and submit answer" : "Start recording"}
          className={cn(
            "relative grid size-20 place-items-center rounded-full transition-colors disabled:opacity-40",
            recording ? "bg-danger text-white" : "bg-accent text-accent-ink hover:bg-accent-hover",
          )}
        >
          {recording ? (
            <span className="size-6 rounded-sm bg-current" />
          ) : (
            <svg viewBox="0 0 24 24" className="size-7" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
              <rect x="9" y="3" width="6" height="12" rx="3" />
              <path d="M5 11a7 7 0 0 0 14 0M12 18v3" />
            </svg>
          )}
        </button>
      </div>
      <p className="h-5 text-sm tabular-nums text-muted" aria-live="polite">
        {recording ? `${formatClock(seconds)} · tap to submit` : busy ? "Submitting…" : "Tap to answer"}
      </p>
    </div>
  );
}
