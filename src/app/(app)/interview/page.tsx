"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { getFirstQuestion, getNextQuestion, uploadAnswer } from "@/lib/api";
import { MAX_QUESTIONS } from "@/lib/constants";
import { useRecorder } from "@/hooks/use-recorder";
import { useSpeech } from "@/hooks/use-speech";
import { useSession } from "@/providers/session";
import { Button, LinkButton } from "@/components/ui/button";
import { Card, Eyebrow, Notice, Progress } from "@/components/ui/primitives";
import { RecorderButton } from "@/components/features/recorder-button";

type Phase = "intro" | "loading" | "asking" | "submitting" | "done";

const TIPS = [
  ["Listen", "Each question is read aloud. You can replay it any time."],
  ["Answer", "Tap the mic, speak naturally, then tap again to submit."],
  ["Review", `After ${MAX_QUESTIONS} questions you get detailed feedback.`],
];

export default function InterviewPage() {
  const router = useRouter();
  const { profile } = useSession();
  const speech = useSpeech();
  const recorder = useRecorder();
  const [phase, setPhase] = useState<Phase>("intro");
  const [question, setQuestion] = useState("");
  const [index, setIndex] = useState(0);
  const [answered, setAnswered] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const spokenFor = useRef("");

  // Read each new question aloud once.
  useEffect(() => {
    if (phase === "asking" && question && spokenFor.current !== question) {
      spokenFor.current = question;
      speech.speak(question);
    }
  }, [phase, question, speech]);

  const loadQuestion = useCallback(
    async (first: boolean) => {
      if (!profile) return;
      setError(null);
      setPhase("loading");
      try {
        const q = first ? await getFirstQuestion(profile.email) : await getNextQuestion();
        setQuestion(q);
        setIndex((i) => i + 1);
        setPhase("asking");
      } catch (e) {
        setError(e instanceof Error ? e.message : "Couldn't load the next question.");
        // Nothing to retry on the first load; mid-interview, let the user retry or wrap up.
        setPhase(first ? "intro" : "asking");
      }
    },
    [profile],
  );

  async function submit() {
    speech.cancel();
    const wav = await recorder.stop();
    if (!wav) return;
    setError(null);
    setPhase("submitting");
    try {
      await uploadAnswer(question, wav);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed. Please record your answer again.");
      setPhase("asking");
      return;
    }
    setAnswered((n) => n + 1);
    if (index >= MAX_QUESTIONS) setPhase("done");
    else await loadQuestion(false);
  }

  function finish() {
    speech.cancel();
    setPhase("done");
  }

  if (phase === "intro" || phase === "loading") {
    return (
      <div className="animate-rise mx-auto max-w-xl">
        <Eyebrow>Interview</Eyebrow>
        <h1 className="mt-3 font-serif text-4xl tracking-tight sm:text-5xl">Ready when you are.</h1>
        <p className="mt-4 text-muted">
          {MAX_QUESTIONS} questions, about 15–20 minutes. Find a quiet spot and allow microphone access.
        </p>
        <ul className="mt-10 divide-y divide-line border-y border-line">
          {TIPS.map(([title, body]) => (
            <li key={title} className="flex gap-6 py-4 text-sm">
              <span className="w-16 font-medium">{title}</span>
              <span className="text-muted">{body}</span>
            </li>
          ))}
        </ul>
        {error && (
          <div className="mt-6">
            <Notice>{error}</Notice>
          </div>
        )}
        <Button size="lg" className="mt-8" loading={phase === "loading"} onClick={() => loadQuestion(true)}>
          Begin interview
        </Button>
      </div>
    );
  }

  if (phase === "done") {
    return (
      <div className="animate-rise mx-auto max-w-xl text-center">
        <Eyebrow>Complete</Eyebrow>
        <h1 className="mt-3 font-serif text-4xl tracking-tight sm:text-5xl">Nicely done.</h1>
        <p className="mt-4 text-muted">
          {answered > 0
            ? `You answered ${answered} question${answered === 1 ? "" : "s"}. Your feedback is ready to review.`
            : "No answers were recorded, so there's nothing to review yet."}
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-3">
          {answered > 0 ? (
            <LinkButton href="/feedback/latest" size="lg">
              View feedback
            </LinkButton>
          ) : (
            <Button
              size="lg"
              onClick={() => {
                setIndex(0);
                setPhase("intro");
              }}
            >
              Try again
            </Button>
          )}
          <LinkButton href="/dashboard" variant="secondary" size="lg">
            Dashboard
          </LinkButton>
        </div>
      </div>
    );
  }

  const busy = phase === "submitting";
  return (
    <div className="animate-rise mx-auto max-w-2xl">
      <div className="flex items-center justify-between text-sm text-muted">
        <span>
          Question {index} of {MAX_QUESTIONS}
        </span>
        <Button variant="danger" size="sm" onClick={finish} disabled={busy || recorder.state !== "idle"}>
          End interview
        </Button>
      </div>
      <div className="mt-3">
        <Progress value={(index - 1) / MAX_QUESTIONS} label="Interview progress" />
      </div>

      <Card className="mt-10 p-8 sm:p-12">
        <p className="font-serif text-2xl leading-snug sm:text-3xl">{question}</p>
        <button
          type="button"
          onClick={() => speech.speak(question)}
          className="mt-6 text-sm text-muted underline-offset-4 hover:text-ink hover:underline"
        >
          {speech.speaking ? "Speaking…" : "Replay question"}
        </button>
      </Card>

      <div className="mt-12 space-y-4">
        <RecorderButton
          state={recorder.state}
          seconds={recorder.seconds}
          busy={busy}
          onStart={() => {
            speech.cancel();
            void recorder.start();
          }}
          onStop={submit}
        />
        <div className="mx-auto max-w-md space-y-3 text-center">
          {(error || recorder.error) && <Notice>{error ?? recorder.error}</Notice>}
        </div>
      </div>
    </div>
  );
}
