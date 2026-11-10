import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { getEvent } from "@/lib/data";
import { addDays, dateText } from "@/lib/dates";
import { catBg, catLabel } from "@/lib/categories";
import type { WaboEvent } from "@/lib/types";

export const revalidate = 300;

const SITE = process.env.NEXT_PUBLIC_SITE_URL || "";

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const e = await getEvent(params.id);
  if (!e) return { title: "Événement introuvable" };
  const desc = `${dateText(e)} · ${e.place}. ${e.description}`.slice(0, 200);
  return { title: e.title, description: desc, openGraph: { title: e.title, description: desc, type: "article" } };
}

function gcal(e: WaboEvent) {
  const p = new URLSearchParams({
    action: "TEMPLATE",
    text: e.title,
    dates: `${e.start.replace(/-/g, "")}/${addDays(e.end, 1).replace(/-/g, "")}`,
    details: `${e.description}${e.link ? "\n" + e.link : ""}\nVu sur Wabo – Agenda Bénin`,
    location: `${e.place}, Bénin`,
  });
  return `https://calendar.google.com/calendar/render?${p}`;
}

function waShare(e: WaboEvent) {
  const url = SITE ? `${SITE}/evenement/${e.id}` : e.link || e.sources[0]?.url || "";
  return `https://wa.me/?text=${encodeURIComponent(`${e.title}\n${dateText(e)}\n${e.place}\n${url}\n\nVu sur Wabo – Agenda Bénin`)}`;
}

/** Données structurées schema.org : permettent à Google d'afficher l'événement dans ses résultats. */
function jsonLd(e: WaboEvent) {
  return {
    "@context": "https://schema.org",
    "@type": "Event",
    name: e.title,
    startDate: e.start,
    endDate: e.end,
    eventStatus: "https://schema.org/EventScheduled",
    eventAttendanceMode: "https://schema.org/OfflineEventAttendanceMode",
    location: { "@type": "Place", name: e.place, address: { "@type": "PostalAddress", addressLocality: e.city.split(" · ")[0], addressCountry: "BJ" } },
    description: e.description,
    ...(e.link ? { url: e.link } : {}),
    ...(e.free ? { isAccessibleForFree: true } : {}),
  };
}

export default async function EventPage({ params }: { params: { id: string } }) {
  const e = await getEvent(params.id);
  if (!e) notFound();
  return (
    <article className="detail">
      {!e.tbc && <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd(e)) }} />}
      <div className="poster" style={{ background: catBg(e.category) }}>
        <Link href="/" style={{ fontSize: 14, fontWeight: 600 }}>← Retour à l’agenda</Link>
        <span className="cat">{catLabel(e.category)}</span>
        <h1 className="display">{e.title}</h1>
        {e.tbc && <span className="badge tbc">Dates à confirmer</span>}
      </div>
      <div className="sbody">
        <div className="facts">
          <div className="fact"><div><b>{dateText(e)}</b>{e.tbc && <span>Les organisateurs n’ont pas encore publié les dates exactes.</span>}</div></div>
          <div className="fact"><div><b>{e.place}</b><span>{e.city}</span></div></div>
          <div className="fact"><div><b>{e.price}</b></div></div>
        </div>
        <p style={{ margin: 0, color: "#3D3832" }}>{e.description}</p>
        <div className="actions">
          {e.link && <a className="btn primary" href={e.link} target="_blank" rel="noopener noreferrer">Site officiel / inscription ↗</a>}
          <a className="btn" href={waShare(e)} target="_blank" rel="noopener noreferrer">Partager sur WhatsApp</a>
          {!e.tbc && <a className="btn" href={gcal(e)} target="_blank" rel="noopener noreferrer">Ajouter à Google Agenda</a>}
          {!e.tbc && <a className="btn" href={`/api/ics/${e.id}`}>Fichier calendrier (.ics)</a>}
        </div>
        <div className="src">
          <span>
            Source{e.sources.length > 1 ? "s" : ""} :{" "}
            {e.sources.map((s, i) => (
              <span key={s.url}>{i > 0 && " · "}<a href={s.url} target="_blank" rel="noopener noreferrer">{s.label}</a></span>
            ))}
          </span>
          <span>Vérifiez auprès de l’organisateur avant de vous déplacer.</span>
          <Link href={`/proposer?correction=${encodeURIComponent(e.title)}`} style={{ color: "var(--red-dark)", fontWeight: 600 }}>Signaler une erreur</Link>
        </div>
      </div>
    </article>
  );
}
