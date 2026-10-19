import { Logo } from "@/components/layout/logo";
import { LinkButton } from "@/components/ui/button";
import { Eyebrow } from "@/components/ui/primitives";

const STEPS = [
  { n: "01", title: "Tell us about you", body: "Your role, skills and background shape every question you get." },
  { n: "02", title: "Answer out loud", body: "Questions are read aloud. Record your answer the way you would in the room." },
  { n: "03", title: "Learn what to fix", body: "Scores, reasoning and an ideal answer for each question, so you know where to improve." },
];

export default function Landing() {
  return (
    <div className="mx-auto flex min-h-dvh max-w-5xl flex-col px-5">
      <header className="flex h-20 items-center justify-between">
        <Logo />
        <LinkButton href="/login" variant="ghost" size="sm">
          Sign in
        </LinkButton>
      </header>

      <main className="flex-1">
        <section className="animate-rise py-20 sm:py-32">
          <Eyebrow>AI mock interviews</Eyebrow>
          <h1 className="mt-5 max-w-3xl font-serif text-5xl leading-[1.05] tracking-tight sm:text-7xl">
            Practice the interview before it counts.
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted">
            Spoken questions tailored to your profile, followed by clear, honest feedback on every answer.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <LinkButton href="/register" size="lg">
              Get started
            </LinkButton>
            <LinkButton href="/login" variant="secondary" size="lg">
              I have an account
            </LinkButton>
          </div>
        </section>

        <section aria-labelledby="how" className="border-t border-line py-16">
          <h2 id="how" className="sr-only">
            How it works
          </h2>
          <ol className="grid gap-10 sm:grid-cols-3">
            {STEPS.map((s) => (
              <li key={s.n}>
                <p className="font-serif text-3xl text-accent">{s.n}</p>
                <h3 className="mt-3 font-medium">{s.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-muted">{s.body}</p>
              </li>
            ))}
          </ol>
        </section>
      </main>

      <footer className="border-t border-line py-8 text-sm text-muted">Rehearse — practice makes calm.</footer>
    </div>
  );
}
