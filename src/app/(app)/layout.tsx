import { AppHeader } from "@/components/layout/app-header";
import { AuthGuard } from "@/components/layout/auth-guard";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <AppHeader />
      <main className="mx-auto w-full max-w-5xl px-5 py-10 sm:py-14">{children}</main>
    </AuthGuard>
  );
}
