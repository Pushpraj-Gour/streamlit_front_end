import { Card, Eyebrow, Score, scoreTone, Tag } from "@/components/ui/primitives";
import { cn, parseScored } from "@/lib/utils";
import type { Feedback, QuestionAnalysis, QuestionDetail } from "@/types";

const METRICS = [
  ["Communication", "overall_communication_score", "overall_communication_reasoning"],
  ["Content quality", "overall_content_quality_score", "overall_content_quality_reasoning"],
  ["Domain insight", "overall_domain_insight_score", "overall_domain_insight_reasoning"],
] as const;

const DIMENSIONS = [
  ["Communication", "communication"],
  ["Content quality", "content_quality"],
  ["Domain insight", "domain_insight"],
  ["Strategic depth", "strategic_depth"],
  ["Professional tone", "professional_tone"],
] as const;

export function FeedbackReport({ feedback }: { feedback: Feedback }) {
  const { overall, questions, observations } = feedback;
  const technical = (overall.technical_skills_with_score ?? []).map(parseScored);
  const soft = (overall.soft_skills_with_score ?? []).map(parseScored);

  return (
    <div className="space-y-16">
      <section className="grid gap-10 sm:grid-cols-[auto_1fr] sm:items-end">
        <div>
          <Eyebrow>Overall score</Eyebrow>
          <div className="mt-3">
            <Score value={overall.overall_score} size="xl" />
          </div>
        </div>
        <p className="max-w-xl leading-relaxed text-muted">{overall.overall_reasoning}</p>
      </section>

      <section aria-label="Score breakdown" className="grid gap-4 sm:grid-cols-3">
        {METRICS.map(([label, scoreKey, reasonKey]) => (
          <Card key={label} className="p-5">
            <p className="text-xs text-muted">{label}</p>
            <div className="mt-2">
              <Score value={overall[scoreKey]} />
            </div>
            <p className="mt-3 text-sm leading-relaxed text-muted">{overall[reasonKey]}</p>
          </Card>
        ))}
      </section>

      {(technical.length > 0 || soft.length > 0) && (
        <section className="grid gap-10 sm:grid-cols-2">
          <SkillBars title="Technical skills" items={technical} />
          <SkillBars title="Soft skills" items={soft} />
        </section>
      )}

      {observations && (
        <section>
          <h2 className="mb-3 font-serif text-2xl">General observations</h2>
          <p className="max-w-2xl leading-relaxed text-muted">{observations}</p>
        </section>
      )}

      <section aria-labelledby="by-question">
        <h2 id="by-question" className="mb-5 font-serif text-2xl">
          Question by question
        </h2>
        {questions.length ? (
          <div className="space-y-3">
            {questions.map((q, i) => (
              <QuestionCard key={i} n={i + 1} q={q} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-muted">No per-question feedback available.</p>
        )}
      </section>
    </div>
  );
}

function SkillBars({ title, items }: { title: string; items: { label: string; score: number | null }[] }) {
  if (!items.length) return <div />;
  return (
    <div>
      <h2 className="mb-4 text-sm font-medium text-muted">{title}</h2>
      <ul className="space-y-3">
        {items.map((s) => (
          <li key={s.label}>
            <div className="mb-1.5 flex justify-between text-sm">
              <span>{s.label}</span>
              <span className={cn("tabular-nums", scoreTone(s.score))}>{s.score ?? "—"}</span>
            </div>
            <div className="h-1 rounded-full bg-line">
              <div
                className="h-full rounded-full bg-current text-accent"
                style={{ width: `${((s.score ?? 0) / 10) * 100}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function QuestionCard({ n, q }: { n: number; q: QuestionAnalysis }) {
  const d: QuestionDetail | undefined = q.question_and_response_detailed_analysis?.[0];
  return (
    <details className="group rounded-2xl border border-line bg-surface open:border-ink/20">
      <summary className="flex cursor-pointer list-none items-start gap-4 p-5 [&::-webkit-details-marker]:hidden">
        <span className="pt-0.5 text-sm tabular-nums text-muted">{String(n).padStart(2, "0")}</span>
        <span className="flex-1 font-medium leading-snug">{q.question}</span>
        <Score value={q.overall_score} />
        <span aria-hidden className="pt-1 text-muted transition-transform group-open:rotate-90">
          ›
        </span>
      </summary>

      <div className="space-y-8 border-t border-line p-5 pt-6">
        {q.overall_reasoning && <p className="text-sm leading-relaxed">{q.overall_reasoning}</p>}

        {q.response && (
          <div>
            <Eyebrow>Your response</Eyebrow>
            <p className="mt-2 text-sm leading-relaxed text-muted">{q.response}</p>
          </div>
        )}

        {d && (
          <>
            <dl className="grid gap-5 sm:grid-cols-2">
              {DIMENSIONS.map(([label, key]) => {
                const score = d[`${key}_score` as keyof QuestionDetail] as number | undefined;
                const reason = d[`${key}_reasoning` as keyof QuestionDetail] as string | undefined;
                if (score == null && !reason) return null;
                return (
                  <div key={key}>
                    <dt className="flex items-center justify-between text-sm font-medium">
                      {label}
                      <Tag>
                        <span className={scoreTone(score)}>{score ?? "—"}/10</span>
                      </Tag>
                    </dt>
                    <dd className="mt-1.5 text-sm leading-relaxed text-muted">{reason}</dd>
                  </div>
                );
              })}
            </dl>

            {d.ideal_answer && (
              <div className="rounded-xl bg-accent-soft p-5">
                <p className="text-xs font-medium uppercase tracking-[0.14em] text-accent">Ideal answer</p>
                <p className="mt-2 text-sm leading-relaxed">{d.ideal_answer}</p>
              </div>
            )}
          </>
        )}
      </div>
    </details>
  );
}
