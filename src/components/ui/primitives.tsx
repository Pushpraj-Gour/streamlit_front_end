import { cn } from "@/lib/utils";

export function Card({ className, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("rounded-2xl border border-line bg-surface", className)} {...rest} />;
}

export function Tag({ children, tone = "neutral" }: { children: React.ReactNode; tone?: "neutral" | "accent" }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
        tone === "accent" ? "bg-accent-soft text-accent" : "border border-line text-muted",
      )}
    >
      {children}
    </span>
  );
}

export function Notice({ tone = "error", children }: { tone?: "error" | "info"; children: React.ReactNode }) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={cn(
        "rounded-xl px-4 py-3 text-sm",
        tone === "error" ? "bg-danger-soft text-danger" : "bg-accent-soft text-accent",
      )}
    >
      {children}
    </div>
  );
}

export function Eyebrow({ children }: { children: React.ReactNode }) {
  return <p className="text-xs font-medium uppercase tracking-[0.14em] text-muted">{children}</p>;
}

export function Progress({ value, label }: { value: number; label?: string }) {
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuenow={Math.round(value * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
      className="h-1 w-full overflow-hidden rounded-full bg-line"
    >
      <div
        className="h-full rounded-full bg-accent transition-[width] duration-500"
        style={{ width: `${Math.min(1, Math.max(0, value)) * 100}%` }}
      />
    </div>
  );
}

export function scoreTone(score: number | null | undefined) {
  if (score == null) return "text-muted";
  if (score >= 7) return "text-accent";
  if (score >= 5) return "text-warn";
  return "text-danger";
}

export function Score({ value, size = "md" }: { value: number | null | undefined; size?: "md" | "xl" }) {
  return (
    <span
      className={cn(
        "font-serif tabular-nums",
        size === "xl" ? "text-7xl leading-none" : "text-2xl",
        scoreTone(value),
      )}
    >
      {value ?? "—"}
      <span className={cn("text-muted", size === "xl" ? "text-2xl" : "text-sm")}>/10</span>
    </span>
  );
}
