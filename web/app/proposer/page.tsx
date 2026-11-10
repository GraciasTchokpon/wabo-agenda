import { Suspense } from "react";
import ProposeForm from "@/components/ProposeForm";
import { CATEGORIES } from "@/lib/categories";

export const metadata = { title: "Proposer un événement" };

const WA = process.env.NEXT_PUBLIC_WABO_WHATSAPP || "";

export default function ProposePage() {
  return (
    <section className="view" aria-labelledby="propTitle">
      <div className="wa-card">
        <span className="k">Le plus rapide</span>
        <h2 id="propTitle" className="display">Envoyez simplement l’affiche sur WhatsApp</h2>
        <p>
          {WA
            ? "Envoyez l’affiche et, si vous l’avez, le lien d’inscription : nous lisons la date, le lieu et le prix, puis nous publions après vérification."
            : "Le numéro WhatsApp de Wabo sera bientôt activé. En attendant, utilisez le formulaire ci-dessous."}
        </p>
        {WA && (
          <a className="btn" style={{ background: "#fff", width: "fit-content" }} href={`https://wa.me/${WA}?text=${encodeURIComponent("Bonjour Wabo, voici un événement à publier :")}`} target="_blank" rel="noopener noreferrer">
            Écrire à Wabo sur WhatsApp
          </a>
        )}
      </div>
      <Suspense>
        <ProposeForm categories={Object.entries(CATEGORIES).map(([id, c]) => ({ id, label: c.label }))} />
      </Suspense>
    </section>
  );
}
