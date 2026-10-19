"use client";

import Link from "next/link";
import { Card, Score } from "@/components/ui/primitives";
import { formatDate } from "@/lib/utils";
import type { InterviewSummary } from "@/types";

export function InterviewList({ interviews }: { interviews: InterviewSummary[] }) {
  return (
    <ul className="space-y-3">
      {interviews.map((i) => (
        <li key={i.id}>
          <Link href={`/feedback/${i.id}`} className="group block">
            <Card className="flex items-start gap-5 p-5 transition-colors group-hover:border-ink/30">
              <div className="w-16 shrink-0">
                <Score value={i.score} />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs text-muted">{formatDate(i.created_at)}</p>
                <p className="mt-1 line-clamp-2 text-sm leading-relaxed">{i.summary || "No summary available."}</p>
              </div>
              <span aria-hidden className="self-center text-muted transition-transform group-hover:translate-x-0.5">
                →
              </span>
            </Card>
          </Link>
        </li>
      ))}
    </ul>
  );
}
