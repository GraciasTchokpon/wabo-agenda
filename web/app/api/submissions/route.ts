import { createHash } from "crypto";
import { NextResponse } from "next/server";
import { adminClient } from "@/lib/data";

type Body = { title?: string; date?: string; time?: string; place?: string; category?: string; price?: string; link?: string; description?: string; contact?: string; website?: string };

const clip = (s: unknown, n: number) => (typeof s === "string" ? s.trim().slice(0, n) : "");

export async function POST(req: Request) {
  let b: Body;
  try { b = await req.json(); } catch { return NextResponse.json({ error: "Requête invalide" }, { status: 400 }); }
  // Champ piège invisible : les robots le remplissent, les humains non.
  if (b.website) return NextResponse.json({ ok: true });
  const title = clip(b.title, 200);
  const place = clip(b.place, 200);
  if (!title || !place) return NextResponse.json({ error: "Le nom et le lieu sont obligatoires." }, { status: 400 });

  const text = [
    `Nom : ${title}`,
    b.date && `Date : ${clip(b.date, 20)}${b.time ? " à " + clip(b.time, 10) : ""}`,
    `Lieu : ${place}`,
    b.category && `Catégorie : ${clip(b.category, 40)}`,
    b.price && `Prix : ${clip(b.price, 80)}`,
    b.link && `Inscription / contact : ${clip(b.link, 300)}`,
    b.description && `Remarque : ${clip(b.description, 2000)}`,
  ].filter(Boolean).join("\n");

  const db = adminClient();
  if (!db) return NextResponse.json({ error: "La base de données n'est pas encore configurée." }, { status: 503 });

  const { data: src } = await db.from("sources").select("id").eq("kind", "formulaire").limit(1).maybeSingle();
  const hash = createHash("sha256").update(text.toLowerCase()).digest("hex");
  const { error } = await db.from("raw_items").insert({
    source_id: src?.id ?? null,
    text,
    submitter_contact: clip(b.contact, 120) || null,
    content_hash: hash,
  });
  if (error && !error.message.includes("duplicate")) {
    console.error(error);
    return NextResponse.json({ error: "Enregistrement impossible, réessayez plus tard." }, { status: 500 });
  }
  return NextResponse.json({ ok: true });
}
