"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/api";
import { JOB_ROLES } from "@/lib/constants";
import { useSession } from "@/providers/session";
import { Button } from "@/components/ui/button";
import { Field, Input, Select, Textarea } from "@/components/ui/field";
import { Notice, Progress } from "@/components/ui/primitives";

const EMAIL_RE = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

const empty = { name: "", email: "", role: "", education: "", skills: "", projects: "", achievements: "", experience: "" };
type Form = typeof empty;
type Errors = Partial<Record<keyof Form, string>>;

function validate(step: 1 | 2, f: Form): Errors {
  const e: Errors = {};
  if (step === 1) {
    if (!f.name.trim()) e.name = "Your name is required.";
    if (!EMAIL_RE.test(f.email.trim())) e.email = "Enter a valid email address.";
    if (!f.role) e.role = "Pick the role you're preparing for.";
  } else {
    if (!f.education.trim()) e.education = "Education is required.";
    if (!f.skills.trim()) e.skills = "Add at least one skill.";
  }
  return e;
}

export default function RegisterPage() {
  const router = useRouter();
  const { signIn } = useSession();
  const [step, setStep] = useState<1 | 2>(1);
  const [form, setForm] = useState<Form>(empty);
  const [errors, setErrors] = useState<Errors>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const set = (k: keyof Form) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate(step, form);
    setErrors(errs);
    if (Object.keys(errs).length) return;

    if (step === 1) return setStep(2);

    setServerError(null);
    setLoading(true);
    try {
      // Emails are unique on the server; a duplicate would otherwise surface as a generic 500.
      if (await login(form.email.trim())) {
        setStep(1);
        setErrors({ email: "An account with this email already exists. Try signing in." });
        return;
      }
      const profile = await register({
        ...form,
        name: form.name.trim(),
        email: form.email.trim(),
        education: form.education.trim(),
        skills: form.skills.trim(),
        projects: form.projects.trim(),
        achievements: form.achievements.trim(),
        experience: form.experience.trim(),
      });
      signIn(profile);
      router.replace("/dashboard");
    } catch (err) {
      setServerError(err instanceof Error ? err.message : "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="animate-rise">
      <p className="mb-3 text-sm text-muted">Step {step} of 2</p>
      <Progress value={step / 2} label="Registration progress" />

      <h1 className="mt-8 font-serif text-4xl tracking-tight">
        {step === 1 ? "Let's start with you" : "Your background"}
      </h1>
      <p className="mt-2 text-muted">
        {step === 1
          ? "The basics, so we can tailor your interview."
          : "Questions are generated from this, so be specific."}
      </p>

      <form onSubmit={onSubmit} noValidate className="mt-8 space-y-5">
        {step === 1 ? (
          <>
            <Field label="Full name" error={errors.name}>
              {(id) => <Input id={id} autoFocus autoComplete="name" value={form.name} onChange={set("name")} />}
            </Field>
            <Field label="Email" error={errors.email}>
              {(id) => (
                <Input id={id} type="email" autoComplete="email" value={form.email} onChange={set("email")} />
              )}
            </Field>
            <Field label="Role" error={errors.role}>
              {(id) => (
                <Select id={id} value={form.role} onChange={set("role")}>
                  <option value="" disabled>
                    Select a role
                  </option>
                  {JOB_ROLES.map((r) => (
                    <option key={r}>{r}</option>
                  ))}
                </Select>
              )}
            </Field>
          </>
        ) : (
          <>
            <Field label="Education" error={errors.education}>
              {(id) => (
                <Textarea
                  id={id}
                  autoFocus
                  placeholder="B.Tech in Computer Science, XYZ University"
                  value={form.education}
                  onChange={set("education")}
                />
              )}
            </Field>
            <Field label="Skills" hint="Comma separated." error={errors.skills}>
              {(id) => (
                <Textarea id={id} placeholder="Python, SQL, Communication" value={form.skills} onChange={set("skills")} />
              )}
            </Field>
            <Field label="Experience" optional>
              {(id) => <Textarea id={id} value={form.experience} onChange={set("experience")} />}
            </Field>
            <Field label="Projects" optional>
              {(id) => <Textarea id={id} value={form.projects} onChange={set("projects")} />}
            </Field>
            <Field label="Achievements" optional>
              {(id) => <Textarea id={id} value={form.achievements} onChange={set("achievements")} />}
            </Field>
          </>
        )}

        {serverError && <Notice>{serverError}</Notice>}

        <div className="flex gap-3">
          {step === 2 && (
            <Button type="button" variant="secondary" size="lg" onClick={() => setStep(1)}>
              Back
            </Button>
          )}
          <Button type="submit" size="lg" className="flex-1" loading={loading}>
            {step === 1 ? "Continue" : "Create profile"}
          </Button>
        </div>
      </form>

      <p className="mt-6 text-sm text-muted">
        Already registered?{" "}
        <Link href="/login" className="text-ink underline underline-offset-4 hover:text-accent">
          Sign in
        </Link>
      </p>
    </div>
  );
}
