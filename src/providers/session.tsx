"use client";

import { createContext, useCallback, useContext, useMemo, useSyncExternalStore } from "react";
import type { Profile } from "@/types";

const KEY = "mi.session";
const listeners = new Set<() => void>();

let cachedRaw: string | null | undefined;
let cachedValue: Profile | null = null;

function read(): Profile | null {
  let raw: string | null = null;
  try {
    raw = localStorage.getItem(KEY);
  } catch {
    /* storage blocked */
  }
  if (raw !== cachedRaw) {
    cachedRaw = raw;
    try {
      cachedValue = raw ? (JSON.parse(raw) as Profile) : null;
    } catch {
      cachedValue = null;
    }
  }
  return cachedValue;
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  window.addEventListener("storage", cb);
  return () => {
    listeners.delete(cb);
    window.removeEventListener("storage", cb);
  };
}

function write(profile: Profile | null) {
  try {
    if (profile) localStorage.setItem(KEY, JSON.stringify(profile));
    else localStorage.removeItem(KEY);
  } catch {
    /* ignore */
  }
  listeners.forEach((l) => l());
}

interface SessionContext {
  /** `undefined` while hydrating, `null` when signed out. */
  profile: Profile | null | undefined;
  signIn: (p: Profile) => void;
  signOut: () => void;
}

const Ctx = createContext<SessionContext | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const profile = useSyncExternalStore<Profile | null | undefined>(subscribe, read, () => undefined);
  const signIn = useCallback((p: Profile) => write(p), []);
  const signOut = useCallback(() => write(null), []);
  const value = useMemo(() => ({ profile, signIn, signOut }), [profile, signIn, signOut]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSession() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useSession must be used inside <SessionProvider>");
  return ctx;
}
