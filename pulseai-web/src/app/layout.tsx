import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Global Pulse AI — Professional Executive Summaries",
  description: "Jargon-free, AI-generated executive summaries covering breakthroughs in LLMs, Healthcare, and Tech.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${outfit.variable} h-full antialiased bg-slate-950`}
    >
      <body className="min-h-full flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200">{children}</body>
    </html>
  );
}
