"use client";

import { useCallback, useEffect, useState } from "react";

export function useSpeech() {
  const [speaking, setSpeaking] = useState(false);

  const cancel = useCallback(() => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) window.speechSynthesis.cancel();
    setSpeaking(false);
  }, []);

  const speak = useCallback((text: string) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    u.rate = 1;
    u.volume = 0.9;
    const voice = window.speechSynthesis
      .getVoices()
      .find((v) => v.lang.startsWith("en") && /Google|Microsoft/.test(v.name));
    if (voice) u.voice = voice;
    u.onstart = () => setSpeaking(true);
    u.onend = u.onerror = () => setSpeaking(false);
    window.speechSynthesis.speak(u);
  }, []);

  useEffect(() => cancel, [cancel]);

  return { speak, cancel, speaking };
}
