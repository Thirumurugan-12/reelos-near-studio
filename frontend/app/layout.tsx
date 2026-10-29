import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReelOS — Your creative studio",
  description:
    "Turn your footage into a considered edit. Direct, preview, and refine with Meta AI.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
