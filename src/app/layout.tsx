import type { Metadata, Viewport } from "next";
import { Inter, Newsreader } from "next/font/google";
import { SessionProvider } from "@/providers/session";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const serif = Newsreader({ subsets: ["latin"], variable: "--font-serif-display" });

export const metadata: Metadata = {
  title: { default: "Rehearse — mock interviews", template: "%s · Rehearse" },
  description: "Practice spoken interviews with AI-generated questions and get detailed, honest feedback.",
};

export const viewport: Viewport = {
  colorScheme: "light dark",
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#faf8f5" },
    { media: "(prefers-color-scheme: dark)", color: "#121311" },
  ],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${serif.variable}`}>
      <body className="min-h-dvh antialiased">
        <SessionProvider>{children}</SessionProvider>
      </body>
    </html>
  );
}
