import type { Metadata } from "next";
import Header from "@/components/Header";
import "./globals.css";

const site = process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(site),
  title: { default: "Wabo – Agenda Bénin", template: "%s · Wabo – Agenda Bénin" },
  description: "Tous les événements du Bénin au même endroit : concerts, festivals, conférences, soirées, avec dates, lieux et liens d'inscription.",
  openGraph: { siteName: "Wabo – Agenda Bénin", locale: "fr_BJ", type: "website" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* eslint-disable-next-line @next/next/no-page-custom-font */}
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700&family=Inter:wght@400;500;600;700&display=swap" />
      </head>
      <body>
        <div className="flag" aria-hidden="true"><i /><i /><i /></div>
        <Header />
        <main className="wrap">{children}</main>
        <footer>
          <div className="wrap">
            <span>Wabo – Agenda Bénin</span>
            <span>Les informations viennent des organisateurs et de la presse : vérifiez auprès d’eux avant de vous déplacer.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
