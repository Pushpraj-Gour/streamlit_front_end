"use client";

import { use, useEffect, useState } from "react";
import { getInterviewFeedback } from "@/lib/api";
import { useSession } from "@/providers/session";
import { LinkButton, Spinner } from "@/components/ui/button";
import { Notice } from "@/components/ui/primitives";
import { FeedbackReport } from "@/components/features/feedback-report";
import type { Feedback } from "@/types";

export default function FeedbackPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { profile } = useSession();
  const email = profile?.email;
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!email) return;
    let live = true;
    getInterviewFeedback(id)
      .then((f) => live && setFeedback(f))
      .catch((e: Error) => live && setError(e.message));
    return () => {
      live = false;
    };
  }, [id, email]);

  return (
    <div className="animate-rise">
      <LinkButton href="/dashboard" variant="ghost" size="sm" className="-ml-3.5 mb-6">
        ← Dashboard
      </LinkButton>
      {error ? (
        <div className="max-w-md space-y-4">
          <Notice>{error}</Notice>
        </div>
      ) : feedback ? (
        <FeedbackReport feedback={feedback} />
      ) : (
        <div className="py-16 text-center text-muted">
          <Spinner />
          <p className="mt-3 text-sm">Preparing your feedback…</p>
        </div>
      )}
    </div>
  );
}
