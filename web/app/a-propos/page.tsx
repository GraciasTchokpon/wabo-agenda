export const metadata = { title: "À propos" };

export default function About() {
  return (
    <section className="view prose">
      <h1 className="display">Wabo, c’est quoi ?</h1>
      <p>Wabo rassemble les événements qui se passent au Bénin (concerts, festivals, conférences, soirées, ateliers, lancements) pour qu’on trouve en quelques secondes quoi faire cette semaine, ce week-end ou en décembre.</p>
      <h2 className="display">D’où viennent les événements ?</h2>
      <p>Nous suivons les sites des organisateurs et des lieux, la presse en ligne et les réseaux sociaux, et nous recevons les affiches que vous nous envoyez. Chaque fiche indique sa source. Rien n’est publié sans vérification.</p>
      <h2 className="display">Une erreur, un événement annulé ?</h2>
      <p>Utilisez « Signaler une erreur » sur la fiche ou la page « Proposer un événement ». Les dates marquées « à confirmer » n’ont pas encore été publiées par les organisateurs.</p>
      <h2 className="display">Organisateurs</h2>
      <p>Publier un événement sur Wabo est gratuit. Envoyez l’affiche et le lien d’inscription : nous nous occupons du reste.</p>
    </section>
  );
}
