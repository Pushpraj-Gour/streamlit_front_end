"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";
import { useSession } from "@/providers/session";
import { Button } from "@/components/ui/button";
import { Field, Input } from "@/components/ui/field";
import { Notice } from "@/components/ui/primitives";

export default function LoginPage() {
  const router = useRouter();
  const { signIn } = useSession();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const profile = await login(email.trim());
      if (!profile) {
        setError("We couldn't find an account with that email.");
        return;
      }
      signIn(profile);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="animate-rise">
      <h1 className="font-serif text-4xl tracking-tight">Welcome back</h1>
      <p className="mt-2 text-muted">Enter your email to pick up where you left off.</p>

      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <Field label="Email">
          {(id) => (
            <Input
              id={id}
              type="email"
              required
              autoFocus
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          )}
        </Field>
        {error && <Notice>{error}</Notice>}
        <Button type="submit" size="lg" className="w-full" loading={loading}>
          Continue
        </Button>
      </form>

      <p className="mt-6 text-sm text-muted">
        New here?{" "}
        <Link href="/register" className="text-ink underline underline-offset-4 hover:text-accent">
          Create a profile
        </Link>
      </p>
    </div>
  );
}
