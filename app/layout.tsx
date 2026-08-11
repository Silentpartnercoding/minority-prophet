import type { Metadata } from "next";
import { headers } from "next/headers";
import "./globals.css";

export async function generateMetadata(): Promise<Metadata> {
  const requestHeaders = await headers();
  const host = requestHeaders.get("host") ?? "localhost";
  const protocol = host.includes("localhost") ? "http" : "https";
  const metadataBase = new URL(`${protocol}://${host}`);
  const title = "Minority Prophet — Truth Is Not Popularity";
  const description = "Public research and experiments for distinguishing independent evidence from copied consensus.";
  return {
    metadataBase,
    title,
    description,
    icons: { icon: "/favicon.svg" },
    openGraph: { title, description, images: [{ url: "/og-capability-v1.png", width: 1731, height: 909 }] },
    twitter: { card: "summary_large_image", title, description, images: ["/og-capability-v1.png"] },
  };
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
