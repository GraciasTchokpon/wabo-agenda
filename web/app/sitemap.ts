import type { MetadataRoute } from "next";
import { getUpcomingEvents } from "@/lib/data";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";
  const events = await getUpcomingEvents();
  return [
    { url: base, changeFrequency: "daily", priority: 1 },
    { url: `${base}/calendrier`, changeFrequency: "daily" },
    { url: `${base}/proposer` },
    ...events.map((e) => ({ url: `${base}/evenement/${e.id}`, changeFrequency: "weekly" as const })),
  ];
}
