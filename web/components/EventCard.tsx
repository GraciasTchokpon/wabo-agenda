import Link from "next/link";
import type { WaboEvent } from "@/lib/types";
import { MONTHS_SHORT, fromKey, shortDates } from "@/lib/dates";
import { catBg, catLabel } from "@/lib/categories";

export default function EventCard({ e, today }: { e: WaboEvent; today: string }) {
  const bg = catBg(e.category);
  const live = !e.tbc && e.start <= today && e.end >= today;
  const shown = fromKey(e.start < today ? today : e.start);
  const end = fromKey(e.end);
  return (
    <Link className="card" href={`/evenement/${e.id}`}>
      {e.tbc ? (
        <div className="tile" style={{ background: bg }}>
          <b className="display" style={{ fontSize: 20 }}>?</b>
          <small>{MONTHS_SHORT[fromKey(e.start).getUTCMonth()]}</small>
          <em>à confirmer</em>
        </div>
      ) : (
        <div className="tile" style={{ background: bg }}>
          <b className="display">{shown.getUTCDate()}</b>
          <small>{MONTHS_SHORT[shown.getUTCMonth()]}</small>
          {e.start !== e.end && <em>{e.start < today ? "en cours" : `→ ${end.getUTCDate()} ${MONTHS_SHORT[end.getUTCMonth()]}`}</em>}
        </div>
      )}
      <div className="cbody">
        <span className="cat">{catLabel(e.category)}</span>
        <span className="ctitle">{e.title}</span>
        <span className="cmeta">{shortDates(e)} · {e.city}</span>
        <span className="cprice" style={{ color: e.free ? "var(--green-dark)" : "var(--ink)" }}>{e.price}</span>
        {live && <span className="badge live">En ce moment</span>}
        {e.tbc && <span className="badge tbc">Dates à confirmer</span>}
      </div>
    </Link>
  );
}
