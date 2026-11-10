export type Source = { label: string; url: string };

export type WaboEvent = {
  id: string;
  title: string;
  category: string;
  start: string; // AAAA-MM-JJ
  end: string; // AAAA-MM-JJ
  time?: string | null;
  city: string;
  place: string;
  price: string;
  free: boolean;
  tbc: boolean;
  dateText?: string | null;
  description: string;
  link: string | null;
  sources: Source[];
};

export type EventRow = {
  id: string;
  title: string;
  category: string;
  start_date: string;
  end_date: string;
  start_time: string | null;
  city: string;
  place: string;
  price_text: string;
  is_free: boolean;
  dates_tbc: boolean;
  date_text: string | null;
  description: string;
  link: string | null;
  sources: Source[];
  status: string;
  confidence: number | null;
};

export function rowToEvent(r: EventRow): WaboEvent {
  return {
    id: r.id,
    title: r.title,
    category: r.category,
    start: r.start_date,
    end: r.end_date,
    time: r.start_time,
    city: r.city,
    place: r.place,
    price: r.price_text,
    free: r.is_free,
    tbc: r.dates_tbc,
    dateText: r.date_text,
    description: r.description,
    link: r.link,
    sources: r.sources || [],
  };
}
