import Link from "next/link";

export function Logo({ href = "/" }: { href?: string }) {
  return (
    <Link href={href} className="flex items-center gap-2.5 font-serif text-xl tracking-tight">
      <span aria-hidden className="size-2.5 rounded-full bg-accent" />
      Rehearse
    </Link>
  );
}
