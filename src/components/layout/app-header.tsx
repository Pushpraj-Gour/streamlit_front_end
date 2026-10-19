"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Logo } from "./logo";
import { Button } from "@/components/ui/button";
import { useSession } from "@/providers/session";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/interview", label: "Interview" },
];

export function AppHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const { signOut } = useSession();

  return (
    <header className="sticky top-0 z-10 border-b border-line bg-bg/85 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-5xl items-center justify-between px-5">
        <div className="flex items-center gap-8">
          <Logo href="/dashboard" />
          <nav className="hidden gap-1 sm:flex">
            {NAV.map((n) => (
              <Link
                key={n.href}
                href={n.href}
                aria-current={pathname.startsWith(n.href) ? "page" : undefined}
                className={cn(
                  "rounded-full px-3.5 py-1.5 text-sm transition-colors",
                  pathname.startsWith(n.href) ? "bg-ink/5 text-ink" : "text-muted hover:text-ink",
                )}
              >
                {n.label}
              </Link>
            ))}
          </nav>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => {
            signOut();
            router.replace("/");
          }}
        >
          Sign out
        </Button>
      </div>
    </header>
  );
}
