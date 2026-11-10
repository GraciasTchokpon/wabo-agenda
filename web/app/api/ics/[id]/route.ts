import { getEvent } from "@/lib/data";
import { addDays } from "@/lib/dates";

const escapeIcs = (s: string) => s.replace(/\\/g, "\\\\").replace(/;/g, "\\;").replace(/,/g, "\\,").replace(/\n/g, "\\n");

export async function GET(_req: Request, { params }: { params: { id: string } }) {
  const e = await getEvent(params.id);
  if (!e || e.tbc) return new Response("Événement introuvable", { status: 404 });
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
  const body = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Wabo//Agenda Benin//FR",
    "CALSCALE:GREGORIAN",
    "BEGIN:VEVENT",
    `UID:${e.id}@wabo`,
    `DTSTAMP:${stamp}`,
    `DTSTART;VALUE=DATE:${e.start.replace(/-/g, "")}`,
    `DTEND;VALUE=DATE:${addDays(e.end, 1).replace(/-/g, "")}`,
    `SUMMARY:${escapeIcs(e.title)}`,
    `LOCATION:${escapeIcs(e.place + ", Bénin")}`,
    `DESCRIPTION:${escapeIcs(e.description + (e.link ? "\n" + e.link : ""))}`,
    "END:VEVENT",
    "END:VCALENDAR",
  ].join("\r\n");
  return new Response(body, {
    headers: { "Content-Type": "text/calendar; charset=utf-8", "Content-Disposition": `attachment; filename="${e.id}.ics"` },
  });
}
