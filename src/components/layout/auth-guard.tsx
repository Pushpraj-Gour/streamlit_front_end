"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/providers/session";
import { Spinner } from "@/components/ui/button";

/** Renders children only for signed-in users; everyone else is sent to /login. */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { profile } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (profile === null) router.replace("/login");
  }, [profile, router]);

  if (!profile) {
    return (
      <div className="grid min-h-dvh place-items-center text-muted">
        <Spinner />
      </div>
    );
  }
  return <>{children}</>;
}
