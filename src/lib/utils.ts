export function cn(...parts: Array<string | false | null | undefined>) {
  return parts.filter(Boolean).join(" ");
}

export function splitList(value: string | string[] | null | undefined): string[] {
  if (!value) return [];
  const items = Array.isArray(value) ? value : value.split(/[,\n]/);
  return items.map((s) => s.trim()).filter(Boolean);
}

export function formatDate(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

export function formatClock(totalSeconds: number) {
  const m = Math.floor(totalSeconds / 60).toString().padStart(2, "0");
  const s = Math.floor(totalSeconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

/** "Python Programming: 7" -> { label: "Python Programming", score: 7 } */
export function parseScored(entry: string) {
  const i = entry.lastIndexOf(":");
  if (i === -1) return { label: entry, score: null as number | null };
  const score = Number.parseFloat(entry.slice(i + 1));
  return { label: entry.slice(0, i).trim(), score: Number.isNaN(score) ? null : score };
}
