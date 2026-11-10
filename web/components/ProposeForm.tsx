"use client";
import { useState } from "react";
import { useSearchParams } from "next/navigation";

export default function ProposeForm({ categories }: { categories: { id: string; label: string }[] }) {
  const params = useSearchParams();
  const correction = params.get("correction");
  const [status, setStatus] = useState<"idle" | "sending" | "ok" | "error">("idle");
  const [message, setMessage] = useState("");

  async function submit(ev: React.FormEvent<HTMLFormElement>) {
    ev.preventDefault();
    const f = new FormData(ev.currentTarget);
    const body = Object.fromEntries(f.entries());
    setStatus("sending");
    try {
      const res = await fetch("/api/submissions", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Erreur");
      setStatus("ok");
    } catch (e) {
      setStatus("error");
      setMessage(e instanceof Error ? e.message : "Erreur");
    }
  }

  if (status === "ok") {
    return (
      <div className="formcard">
        <p className="ok" role="status">Merci ! Votre proposition est bien reçue. L’équipe la vérifie avant de la publier.</p>
        <button className="btn" onClick={() => setStatus("idle")}>Proposer un autre événement</button>
      </div>
    );
  }

  return (
    <form className="formcard" onSubmit={submit}>
      <p className="note" style={{ margin: 0 }}>Tous les événements ouverts au public sont les bienvenus. Chaque proposition est vérifiée avant publication.</p>
      <div className="field"><label htmlFor="f-title">Nom de l’événement *</label><input id="f-title" name="title" required defaultValue={correction ? `Correction : ${correction}` : ""} /></div>
      <div className="row2">
        <div className="field"><label htmlFor="f-date">Date</label><input id="f-date" name="date" type="date" /></div>
        <div className="field"><label htmlFor="f-time">Heure</label><input id="f-time" name="time" type="time" /></div>
      </div>
      <div className="field"><label htmlFor="f-place">Lieu (nom, quartier, ville) *</label><input id="f-place" name="place" required /></div>
      <div className="row2">
        <div className="field">
          <label htmlFor="f-cat">Catégorie</label>
          <select id="f-cat" name="category">{categories.map((c) => <option key={c.id} value={c.id}>{c.label}</option>)}<option value="autre">Autre</option></select>
        </div>
        <div className="field"><label htmlFor="f-price">Prix</label><input id="f-price" name="price" placeholder="Gratuit, 5 000 FCFA…" /></div>
      </div>
      <div className="field"><label htmlFor="f-link">Lien d’inscription</label><input id="f-link" name="link" placeholder="https://…" /></div>
      <div className="field"><label htmlFor="f-desc">Description ou remarque</label><textarea id="f-desc" name="description" rows={3} defaultValue={correction ? "Ce qui est inexact sur la fiche : " : ""} /></div>
      <div className="field"><label htmlFor="f-contact">Votre contact (facultatif, non publié)</label><input id="f-contact" name="contact" placeholder="Téléphone ou e-mail" /></div>
      <div aria-hidden="true" style={{ position: "absolute", left: -9999 }}><label>Site web<input name="website" tabIndex={-1} autoComplete="off" /></label></div>
      {status === "error" && <p className="err" role="alert">{message}</p>}
      <button className="btn primary" type="submit" disabled={status === "sending"}>{status === "sending" ? "Envoi…" : "Envoyer pour vérification"}</button>
    </form>
  );
}
