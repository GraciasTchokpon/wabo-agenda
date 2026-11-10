import type { WaboEvent } from "./types";

export const MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
export const MONTHS_SHORT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];
export const DAYS = ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"];

export const pad = (n: number) => (n < 10 ? "0" : "") + n;
export const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
export const toKey = (d: Date) => `${d.getUTCFullYear()}-${pad(d.getUTCMonth() + 1)}-${pad(d.getUTCDate())}`;
export const fromKey = (k: string) => {
  const [y, m, d] = k.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d));
};
export const addDays = (k: string, n: number) => {
  const d = fromKey(k);
  d.setUTCDate(d.getUTCDate() + n);
  return toKey(d);
};

/** Date du jour au Bénin (UTC+1), au format AAAA-MM-JJ. */
export function todayBenin(): string {
  const d = new Date(Date.now() + 60 * 60 * 1000);
  return toKey(d);
}

export const overlaps = (e: WaboEvent, a: string, b: string) => e.start <= b && e.end >= a;

export function dateText(e: WaboEvent): string {
  if (e.dateText) return e.dateText;
  const s = fromKey(e.start);
  const f = fromKey(e.end);
  if (e.start === e.end) {
    return `${cap(DAYS[s.getUTCDay()])} ${s.getUTCDate()} ${MONTHS[s.getUTCMonth()]} ${s.getUTCFullYear()}${e.time ? " · " + e.time : ""}`;
  }
  const same = s.getUTCMonth() === f.getUTCMonth() && s.getUTCFullYear() === f.getUTCFullYear();
  return `Du ${s.getUTCDate()}${same ? "" : " " + MONTHS[s.getUTCMonth()]} au ${f.getUTCDate()} ${MONTHS[f.getUTCMonth()]} ${f.getUTCFullYear()}`;
}

export function shortDates(e: WaboEvent): string {
  if (e.tbc) return "Dates à confirmer";
  const s = fromKey(e.start);
  const f = fromKey(e.end);
  if (e.start === e.end) return `${cap(DAYS[s.getUTCDay()])} ${s.getUTCDate()} ${MONTHS_SHORT[s.getUTCMonth()]}`;
  return `${s.getUTCDate()}${s.getUTCMonth() === f.getUTCMonth() ? "" : " " + MONTHS_SHORT[s.getUTCMonth()]}–${f.getUTCDate()} ${MONTHS_SHORT[f.getUTCMonth()]}`;
}

export type Period = { id: string; label: string; a: string; b: string };

export function periods(today: string): Period[] {
  const dow = fromKey(today).getUTCDay();
  const sat = dow === 0 ? addDays(today, -1) : addDays(today, (6 - dow + 7) % 7);
  const list: Period[] = [
    { id: "tout", label: "Tout", a: today, b: "9999-12-31" },
    { id: "semaine", label: "Cette semaine", a: today, b: addDays(today, 6) },
    { id: "weekend", label: "Ce week-end", a: sat < today ? today : sat, b: addDays(sat, 1) },
  ];
  const t = fromKey(today);
  for (let i = 0; i < 3; i++) {
    const y = t.getUTCFullYear() + Math.floor((t.getUTCMonth() + i) / 12);
    const m = (t.getUTCMonth() + i) % 12;
    const a = `${y}-${pad(m + 1)}-01`;
    const b = toKey(new Date(Date.UTC(y, m + 1, 0)));
    list.push({ id: `m${y}${pad(m + 1)}`, label: cap(MONTHS[m]) + (y !== t.getUTCFullYear() ? " " + y : ""), a: a < today ? today : a, b });
  }
  return list;
}
