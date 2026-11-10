"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/", label: "Agenda" },
  { href: "/calendrier", label: "Calendrier" },
  { href: "/proposer", label: "Proposer", long: " un événement" },
  { href: "/a-propos", label: "À propos" },
];

export function FlagMark({ size = 30 }: { size?: number }) {
  return (
    <svg width={size} height={(size * 18) / 26} viewBox="0 0 26 18" aria-hidden="true">
      <rect x="0" y="0" width="10" height="18" rx="2" fill="#008751" />
      <rect x="10" y="0" width="16" height="9" fill="#FCD116" />
      <rect x="10" y="9" width="16" height="9" fill="#E8112D" />
    </svg>
  );
}

export default function Header() {
  const path = usePathname();
  return (
    <header className="top">
      <div className="wrap topbar">
        <Link className="brand" href="/" aria-label="Wabo, Agenda Bénin – accueil">
          <FlagMark />
          <b className="display">Wabo</b>
          <small>Agenda Bénin</small>
        </Link>
        <nav className="tabs" aria-label="Sections">
          {TABS.map((t) => (
            <Link key={t.href} href={t.href} aria-current={path === t.href ? "page" : undefined}>
              {t.label}
              {t.long && <span className="long">&nbsp;{t.long.trim()}</span>}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
