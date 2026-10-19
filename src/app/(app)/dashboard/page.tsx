"use client";

import { useEffect, useState } from "react";
import { getInterviews } from "@/lib/api";
import { splitList } from "@/lib/utils";
import { useSession } from "@/providers/session";
import { LinkButton, Spinner } from "@/components/ui/button";
import { Card, Eyebrow, Notice, Tag } from "@/components/ui/primitives";
import { InterviewList } from "@/components/features/interview-list";
import type { InterviewSummary } from "@/types";

export default function DashboardPage() {
  const { profile } = useSession();
  const email = profile?.email;
  const [interviews, setInterviews] = useState<InterviewSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!email) return;
    let live = true;
    getInterviews(email)
      .then((list) => live && setInterviews(list))
      .catch((e: Error) => live && (setError(e.message), setInterviews([])));
    return () => {
      live = false;
    };
  }, [email]);

  if (!profile) return null;
  const skills = splitList(profile.skills);

  return (
    <div className="animate-rise space-y-12">
      <section className="flex flex-wrap items-end justify-between gap-6">
        <div>
          <Eyebrow>{profile.role || "Dashboard"}</Eyebrow>
          <h1 className="mt-3 font-serif text-4xl tracking-tight sm:text-5xl">
            Hello, {profile.name.split(" ")[0]}.
          </h1>
        </div>
        <LinkButton href="/interview" size="lg">
          Start an interview
        </LinkButton>
      </section>

      <div className="grid gap-10 lg:grid-cols-[1fr_18rem]">
        <section aria-labelledby="history">
          <h2 id="history" className="mb-4 text-sm font-medium text-muted">
            Past interviews
          </h2>
          {error && <Notice>{error}</Notice>}
          {interviews === null ? (
            <div className="py-10 text-muted">
              <Spinner />
            </div>
          ) : interviews.length ? (
            <InterviewList interviews={interviews} />
          ) : (
            !error && (
              <Card className="px-6 py-14 text-center">
                <p className="font-serif text-2xl">Nothing here yet</p>
                <p className="mx-auto mt-2 max-w-xs text-sm text-muted">
                  Your first interview takes about 15 minutes. Your feedback will show up here.
                </p>
              </Card>
            )
          )}
        </section>

        <aside aria-labelledby="profile" className="space-y-6">
          <h2 id="profile" className="text-sm font-medium text-muted">
            Your profile
          </h2>
          <Card className="space-y-5 p-5 text-sm">
            <div>
              <p className="font-medium">{profile.name}</p>
              <p className="text-muted">{profile.email}</p>
            </div>
            {skills.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {skills.slice(0, 12).map((s) => (
                  <Tag key={s}>{s}</Tag>
                ))}
              </div>
            )}
            {profile.education && (
              <div>
                <p className="text-xs text-muted">Education</p>
                <p className="mt-1 leading-relaxed">{profile.education}</p>
              </div>
            )}
          </Card>
        </aside>
      </div>
    </div>
  );
}
