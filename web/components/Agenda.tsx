"use client";
import { useMemo, useState } from "react";
import Link from "next/link";
import type { WaboEvent } from "@/lib/types";
import { overlaps, periods } from "@/lib/dates";
import { catLabel } from "@/lib/categories";
import EventCard from "./EventCard";

const norm = (s: string) => s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");

function Chips({ items, value, onChange, label, small }: { items: { id: string; label: string }[]; value: string; onChange: (v: string) => void; label: string; small?: boolean }) {
  return (
    <div className={`chips${small ? " small" : ""}`} role="group" aria-label={label}>
      {items.map((i) => (
        <button key={i.id} className="chip" aria-pressed={value === i.id} onClick={() => onChange(i.id)}>{i.label}</button>
      ))}
    </div>
  );
}

export default function Agenda({ events, today }: { events: WaboEvent[]; today: string }) {
  const [q, setQ] = useState("");
  const [period, setPeriod] = useState("tout");
  const [cat, setCat] = useState("toutes");
  const [city, setCity] = useState("toutes");
  const P = useMemo(() => periods(today), [today]);
  const cats = useMemo(() => [...new Set(events.map((e) => e.category))], [events]);
  const cities = useMemo(() => [...new Set(events.flatMap((e) => e.city.split(" · ")))].sort(), [events]);

  const p = P.find((x) => x.id === period) ?? P[0];
  const nq = norm(q);
  const res = events.filter((e) =>
    (p.id === "tout" || (e.tbc ? p.id.startsWith("m") && overlaps(e, p.a, p.b) : overlaps(e, p.a, p.b))) &&
    (cat === "toutes" || e.category === cat) &&
    (city === "toutes" || e.city.split(" · ").includes(city)) &&
    (!nq || norm(`${e.title} ${e.place} ${e.city} ${catLabel(e.category)} ${e.description}`).includes(nq)));

  return (
    <section className="view" aria-labelledby="agendaTitle">
      <div className="filters">
        <label className="sr" htmlFor="q">Rechercher un événement</label>
        <div className="search">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#5E5850" strokeWidth="2" strokeLinecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
          <input id="q" type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Festival, concert, Ouidah, fintech…" autoComplete="off" />
        </div>
        <Chips items={P} value={period} onChange={setPeriod} label="Période" />
        <Chips small items={[{ id: "toutes", label: "Toutes catégories" }, ...cats.map((k) => ({ id: k, label: catLabel(k) }))]} value={cat} onChange={setCat} label="Catégorie" />
        <Chips small items={[{ id: "toutes", label: "Toutes les villes" }, ...cities.map((c) => ({ id: c, label: c }))]} value={city} onChange={setCity} label="Ville" />
      </div>
      <div className="resultbar">
        <h2 id="agendaTitle" className="display">{p.id === "tout" ? "À venir" : p.label}</h2>
        <span>{res.length} {res.length > 1 ? "événements" : "événement"}</span>
      </div>
      <div className="grid">
        {res.length ? res.map((e) => <EventCard key={e.id} e={e} today={today} />) : (
          <div className="empty">Aucun événement pour ces filtres.<br /><Link href="/proposer">Vous en connaissez un ? Proposez-le</Link></div>
        )}
      </div>
    </section>
  );
}
