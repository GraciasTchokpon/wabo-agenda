import Agenda from "@/components/Agenda";
import { getUpcomingEvents } from "@/lib/data";
import { todayBenin } from "@/lib/dates";

export const revalidate = 300; // la page se met à jour toutes les 5 minutes

export default async function Home() {
  const events = await getUpcomingEvents();
  return (
    <>
      <section className="hero">
        <h1 className="display">Que faire au <span>Bénin</span> ?</h1>
        <p>Concerts, festivals, conférences, soirées : {events.length} événements à venir, vérifiés, avec les dates, les lieux et les liens pour s’inscrire.</p>
      </section>
      <Agenda events={events} today={todayBenin()} />
    </>
  );
}
