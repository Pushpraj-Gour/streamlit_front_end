import { Logo } from "@/components/layout/logo";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="mx-auto flex min-h-dvh w-full max-w-md flex-col px-5 py-8">
      <Logo />
      <main className="flex flex-1 flex-col justify-center py-10">{children}</main>
    </div>
  );
}
