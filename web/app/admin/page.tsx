import { revalidatePath } from "next/cache";
import { adminClient } from "@/lib/data";
import { CATEGORIES, catLabel } from "@/lib/categories";
import type { EventRow } from "@/lib/types";

export const dynamic = "force-dynamic";
export const metadata = { title: "Back-office", robots: { index: false } };

type Raw = { id: number; received_at: string; text: string | null; origin_url: string | null; submitter_contact: string | null; status: string; sources: { name: string } | null };

async function publish(form: FormData) {
  "use server";
  const db = adminClient();
  if (!db) return;
  const id = String(form.get("id"));
  const patch = {
    title: String(form.get("title")),
    category: String(form.get("category")),
    start_date: String(form.get("start_date")),
    end_date: String(form.get("end_date")) || String(form.get("start_date")),
    start_time: String(form.get("start_time")) || null,
    city: String(form.get("city")),
    place: String(form.get("place")),
    price_text: String(form.get("price_text")) || "Non communiqué",
    is_free: form.get("is_free") === "on",
    dates_tbc: form.get("dates_tbc") === "on",
    link: String(form.get("link")) || null,
    description: String(form.get("description")),
    status: "publie",
    verified_at: new Date().toISOString(),
  };
  await db.from("events").update(patch).eq("id", id);
  revalidatePath("/admin");
  revalidatePath("/");
}

async function setStatus(form: FormData) {
  "use server";
  const db = adminClient();
  if (!db) return;
  await db.from("events").update({ status: String(form.get("status")) }).eq("id", String(form.get("id")));
  revalidatePath("/admin");
  revalidatePath("/");
}

async function rejectRaw(form: FormData) {
  "use server";
  const db = adminClient();
  if (!db) return;
  await db.from("raw_items").update({ status: "rejete" }).eq("id", Number(form.get("id")));
  revalidatePath("/admin");
}

export default async function Admin() {
  const db = adminClient();
  if (!db) {
    return <section className="view prose"><h1 className="display">Back-office</h1><p className="err">Base de données non configurée : renseignez les variables Supabase (voir README).</p></section>;
  }
  const [{ data: pending }, { data: raw }, { count: published }] = await Promise.all([
    db.from("events").select("*").eq("status", "a_valider").order("start_date"),
    db.from("raw_items").select("id, received_at, text, origin_url, submitter_contact, status, sources(name)").eq("status", "nouveau").order("received_at", { ascending: false }).limit(50),
    db.from("events").select("id", { count: "exact", head: true }).eq("status", "publie"),
  ]);
  const queue = (pending ?? []) as EventRow[];
  const inbox = (raw ?? []) as unknown as Raw[];

  return (
    <section className="view" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div>
        <h1 className="display" style={{ margin: "0 0 4px" }}>Modération</h1>
        <p className="note" style={{ margin: 0 }}>{queue.length} fiche(s) à valider · {inbox.length} élément(s) reçu(s) pas encore lus par le robot · {published ?? 0} événement(s) publié(s)</p>
      </div>

      <div>
        <h2 className="display">Fiches à valider</h2>
        {queue.length === 0 && <p className="empty">Rien à valider pour l’instant.</p>}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {queue.map((e) => (
            <form key={e.id} action={publish} className="formcard" style={{ maxWidth: "none" }}>
              <input type="hidden" name="id" value={e.id} />
              <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                <strong>{e.title}</strong>
                <span className="badge tbc">Confiance {e.confidence != null ? Math.round(e.confidence * 100) + " %" : "?"}</span>
              </div>
              <div className="row2">
                <div className="field"><label>Titre</label><input name="title" defaultValue={e.title} /></div>
                <div className="field"><label>Catégorie</label>
                  <select name="category" defaultValue={e.category}>{Object.entries(CATEGORIES).map(([k, c]) => <option key={k} value={k}>{c.label}</option>)}</select>
                </div>
                <div className="field"><label>Début</label><input type="date" name="start_date" defaultValue={e.start_date} /></div>
                <div className="field"><label>Fin</label><input type="date" name="end_date" defaultValue={e.end_date} /></div>
                <div className="field"><label>Heure</label><input name="start_time" defaultValue={e.start_time ?? ""} /></div>
                <div className="field"><label>Ville</label><input name="city" defaultValue={e.city} /></div>
                <div className="field"><label>Lieu</label><input name="place" defaultValue={e.place} /></div>
                <div className="field"><label>Prix</label><input name="price_text" defaultValue={e.price_text} /></div>
                <div className="field"><label>Lien d’inscription</label><input name="link" defaultValue={e.link ?? ""} /></div>
                <div className="field" style={{ justifyContent: "end" }}>
                  <label><input type="checkbox" name="is_free" defaultChecked={e.is_free} /> Gratuit</label>
                  <label><input type="checkbox" name="dates_tbc" defaultChecked={e.dates_tbc} /> Dates à confirmer</label>
                </div>
              </div>
              <div className="field"><label>Description</label><textarea name="description" rows={3} defaultValue={e.description} /></div>
              <p className="note" style={{ margin: 0 }}>Sources : {(e.sources || []).map((s) => <a key={s.url} href={s.url} target="_blank" rel="noopener noreferrer" style={{ marginRight: 8 }}>{s.label}</a>)}</p>
              <div className="actions">
                <button className="btn primary" type="submit">Valider et publier</button>
                <button className="btn danger" formAction={setStatus} name="status" value="rejete">Rejeter</button>
              </div>
            </form>
          ))}
        </div>
      </div>

      <div>
        <h2 className="display">Reçus (WhatsApp, formulaire, robots)</h2>
        <div className="scroll">
          <table className="admin">
            <thead><tr><th>Reçu</th><th>Source</th><th>Contenu</th><th>Action</th></tr></thead>
            <tbody>
              {inbox.length === 0 && <tr><td colSpan={4}>Rien de nouveau.</td></tr>}
              {inbox.map((r) => (
                <tr key={r.id}>
                  <td>{new Date(r.received_at).toLocaleString("fr-FR", { timeZone: "Africa/Porto-Novo" })}</td>
                  <td>{r.sources?.name ?? "?"}</td>
                  <td style={{ whiteSpace: "pre-wrap", maxWidth: 520 }}>{r.text}{r.origin_url && <><br /><a href={r.origin_url} target="_blank" rel="noopener noreferrer">origine</a></>}{r.submitter_contact && <><br /><span className="note">Contact : {r.submitter_contact}</span></>}</td>
                  <td><form action={rejectRaw}><input type="hidden" name="id" value={r.id} /><button className="btn danger" type="submit">Rejeter</button></form></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="note">Le robot de collecte (dossier collector) lit ces éléments, en extrait les informations et crée les fiches « à valider » ci-dessus.</p>
      </div>
      <p className="note">Catégories disponibles : {Object.keys(CATEGORIES).map(catLabel).join(", ")}.</p>
    </section>
  );
}
