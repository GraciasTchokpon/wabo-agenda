import "server-only";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import seed from "@/data/events.json";
import type { EventRow, WaboEvent } from "./types";
import { rowToEvent } from "./types";
import { todayBenin } from "./dates";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anon = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
const service = process.env.SUPABASE_SERVICE_ROLE_KEY;

export const hasDatabase = Boolean(url && anon);

function publicClient(): SupabaseClient | null {
  return url && anon ? createClient(url, anon, { auth: { persistSession: false } }) : null;
}

/** Client avec tous les droits : uniquement côté serveur (API, back-office, robot). */
export function adminClient(): SupabaseClient | null {
  return url && service ? createClient(url, service, { auth: { persistSession: false } }) : null;
}

const sortEvents = (list: WaboEvent[]) =>
  [...list].sort((x, y) => Number(x.tbc) - Number(y.tbc) || x.start.localeCompare(y.start) || x.end.localeCompare(y.end));

/** Événements publiés qui ne sont pas encore terminés. */
export async function getUpcomingEvents(): Promise<WaboEvent[]> {
  const today = todayBenin();
  const db = publicClient();
  if (!db) return sortEvents((seed as WaboEvent[]).filter((e) => e.end >= today));
  const { data, error } = await db
    .from("events")
    .select("*")
    .eq("status", "publie")
    .gte("end_date", today)
    .order("start_date", { ascending: true });
  if (error) {
    console.error("Lecture des événements impossible :", error.message);
    return sortEvents((seed as WaboEvent[]).filter((e) => e.end >= today));
  }
  return sortEvents((data as EventRow[]).map(rowToEvent));
}

export async function getEvent(id: string): Promise<WaboEvent | null> {
  const db = publicClient();
  if (!db) return (seed as WaboEvent[]).find((e) => e.id === id) ?? null;
  const { data } = await db.from("events").select("*").eq("id", id).in("status", ["publie", "annule"]).maybeSingle();
  return data ? rowToEvent(data as EventRow) : null;
}
