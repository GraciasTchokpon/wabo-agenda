"use client";
import { useState } from "react";
import Link from "next/link";
import type { WaboEvent } from "@/lib/types";
import { DAYS, MONTHS, cap, fromKey, overlaps, pad, toKey } from "@/lib/dates";
import EventCard from "./EventCard";

export default function CalendarView({ events, today }: { events: WaboEvent[]; today: string }) {
  const [month, setMonth] = useState(today.slice(0, 7));
  const [day, setDay] = useState(today);
  const [y, m] = month.split("-").map(Number);
  const offset = (new Date(Date.UTC(y, m - 1, 1)).getUTCDay() + 6) % 7;
  const nd = new Date(Date.UTC(y, m, 0)).getUTCDate();
  const dated = events.filter((e) => !e.tbc);
  const shift = (n: number) => setMonth(toKey(new Date(Date.UTC(y, m - 1 + n, 1))).slice(0, 7));
  const sd = fromKey(day);
  const dayEvents = dated.filter((e) => e.start <= day && e.end >= day);
  const a = `${month}-01`;
  const b = toKey(new Date(Date.UTC(y, m, 0)));
  const tbc = events.filter((e) => e.tbc && overlaps(e, a, b));

  return (
    <section className="view cal-layout" aria-labelledby="calTitle">
      <div className="cal">
        <div className="cal-head">
          <button className="round" onClick={() => shift(-1)} disabled={month <= today.slice(0, 7)} aria-label="Mois précédent">‹</button>
          <h2 id="calTitle" className="display" aria-live="polite">{MONTHS[m - 1]} {y}</h2>
          <button className="round" onClick={() => shift(1)} aria-label="Mois suivant">›</button>
        </div>
        <div className="dow" aria-hidden="true">{["L", "M", "M", "J", "V", "S", "D"].map((d, i) => <span key={i}>{d}</span>)}</div>
        <div className="days">
          {Array.from({ length: offset }, (_, i) => <span key={`b${i}`} />)}
          {Array.from({ length: nd }, (_, i) => {
            const d = i + 1;
            const k = `${y}-${pad(m)}-${pad(d)}`;
            const n = dated.filter((e) => e.start <= k && e.end >= k).length;
            const cls = ["day", n ? "has" : "", k === today ? "today" : "", k < today ? "past" : ""].join(" ");
            return (
              <button key={k} className={cls} aria-pressed={k === day} onClick={() => setDay(k)}
                aria-label={`${d} ${MONTHS[m - 1]}${n ? `, ${n} ${n > 1 ? "événements" : "événement"}` : ""}`}>
                <span>{d}</span>
                <span className="dots">{Array.from({ length: Math.min(n, 3) }, (_, j) => <i key={j} />)}</span>
              </button>
            );
          })}
        </div>
      </div>
      <div className="cal-side">
        <h2 className="display">{cap(DAYS[sd.getUTCDay()])} {sd.getUTCDate()} {MONTHS[sd.getUTCMonth()]}</h2>
        <div className="grid" style={{ gridTemplateColumns: "1fr" }}>
          {dayEvents.length ? dayEvents.map((e) => <EventCard key={e.id} e={e} today={today} />) : (
            <div className="empty">Rien de prévu ce jour-là pour l’instant.<br /><Link href="/proposer">Vous connaissez un événement ? Proposez-le</Link></div>
          )}
        </div>
        {tbc.length > 0 && (
          <div className="tbc-box"><b>Aussi ce mois-ci, dates à confirmer :</b>
            {tbc.map((e) => <div key={e.id}><Link href={`/evenement/${e.id}`}>{e.title}</Link></div>)}
          </div>
        )}
      </div>
    </section>
  );
}
