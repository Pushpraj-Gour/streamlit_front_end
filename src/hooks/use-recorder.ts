"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toWav } from "@/lib/wav";

export type RecorderState = "idle" | "recording" | "processing";

export function useRecorder() {
  const [state, setState] = useState<RecorderState>("idle");
  const [seconds, setSeconds] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const recorder = useRef<MediaRecorder | null>(null);
  const stream = useRef<MediaStream | null>(null);
  const chunks = useRef<Blob[]>([]);
  const timer = useRef<ReturnType<typeof setInterval>>(undefined);

  const release = useCallback(() => {
    clearInterval(timer.current);
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
  }, []);

  useEffect(() => release, [release]);

  const start = useCallback(async () => {
    setError(null);
    try {
      const media = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.current = media;
      chunks.current = [];
      const rec = new MediaRecorder(media);
      rec.ondataavailable = (e) => e.data.size && chunks.current.push(e.data);
      rec.start();
      recorder.current = rec;
      setSeconds(0);
      timer.current = setInterval(() => setSeconds((s) => s + 1), 1000);
      setState("recording");
    } catch {
      setError("Microphone access was blocked. Allow it in your browser and try again.");
    }
  }, []);

  /** Stops recording and resolves with a WAV blob (or null on failure). */
  const stop = useCallback(
    () =>
      new Promise<Blob | null>((resolve) => {
        const rec = recorder.current;
        if (!rec || rec.state === "inactive") return resolve(null);
        setState("processing");
        rec.onstop = async () => {
          release();
          try {
            resolve(await toWav(new Blob(chunks.current, { type: rec.mimeType })));
          } catch {
            setError("Couldn't process the recording. Please try again.");
            resolve(null);
          } finally {
            setState("idle");
          }
        };
        rec.stop();
      }),
    [release],
  );

  return { state, seconds, error, start, stop };
}
