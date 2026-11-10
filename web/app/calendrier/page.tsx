import CalendarView from "@/components/CalendarView";
import { getUpcomingEvents } from "@/lib/data";
import { todayBenin } from "@/lib/dates";

export const revalidate = 300;
export const metadata = { title: "Calendrier" };

export default async function CalendarPage() {
  const events = await getUpcomingEvents();
  return (
    <>
      <section className="hero"><h1 className="display">Calendrier</h1></section>
      <CalendarView events={events} today={todayBenin()} />
    </>
  );
}
