"""Construit le site public à partir de site-src/template.html et data/events.json.

Produit :
- site/index.html  (page avec les événements et les données lisibles par Google)
- site/sitemap.xml (plan du site pour les moteurs de recherche)

Usage : python3 scripts/build_site.py
"""
import json
from datetime import date
from pathlib import Path

SITE_URL = "https://wabo-agenda.netlify.app/"
# Code de validation Google Search Console (balise meta « google-site-verification »).
# Laisser vide tant qu'il n'est pas fourni.
GOOGLE_VERIFICATION = "1Yo3GwoEvlcCx2ERLPvAdntEuufmnTcifN98eOCaEmU"

ROOT = Path(__file__).resolve().parent.parent
template = (ROOT / "site-src" / "template.html").read_text(encoding="utf-8")
events = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))


def event_ld(e):
    """Fiche schema.org Event, pour l'affichage des événements dans Google."""
    start = e["start"] + (f"T{e['time']}:00+01:00" if e.get("time") else "")
    item = {
        "@type": "Event",
        "name": e["title"],
        "startDate": start,
        "endDate": e.get("end") or e["start"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {
            "@type": "Place",
            "name": e["place"],
            "address": {"@type": "PostalAddress", "addressLocality": e["city"], "addressCountry": "BJ"},
        },
        "description": e.get("description", ""),
        "image": [SITE_URL + "og-image.png"],
        "url": SITE_URL + "#" + e["id"],
    }
    if e.get("free"):
        item["offers"] = {"@type": "Offer", "price": 0, "priceCurrency": "XOF",
                          "availability": "https://schema.org/InStock", "url": e.get("link") or SITE_URL}
    elif e.get("link"):
        item["offers"] = {"@type": "Offer", "url": e["link"], "availability": "https://schema.org/InStock"}
    return item


graph = [
    {"@type": "WebSite", "name": "Wabo – Agenda Bénin", "alternateName": ["Wabo", "Wabo Agenda Bénin"],
     "url": SITE_URL, "inLanguage": "fr"},
    {"@type": "Organization", "name": "Wabo – Agenda Bénin", "url": SITE_URL,
     "logo": SITE_URL + "apple-touch-icon.png", "email": "wabo.agenda.benin@gmail.com",
     "sameAs": ["https://www.instagram.com/wabo_agenda_benin/"]},
] + [event_ld(e) for e in events if not e.get("tbc")]  # dates non confirmées : pas de fiche Google

jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)
jsonld = jsonld.replace("</", "<\\/")

marker = "/*__EVENTS__*/[]"
for m in (marker, "<!--__JSONLD__-->", "<!--__GOOGLE_VERIFICATION__-->"):
    if m not in template:
        raise SystemExit(f"Marqueur {m} introuvable dans le modèle.")
html = (template
        .replace(marker, json.dumps(events, ensure_ascii=False))
        .replace("<!--__JSONLD__-->", f'<script type="application/ld+json">\n{jsonld}\n</script>')
        .replace("<!--__GOOGLE_VERIFICATION__-->",
                 f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">' if GOOGLE_VERIFICATION else ""))
(ROOT / "site" / "index.html").write_text(html, encoding="utf-8")

(ROOT / "site" / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    f"  <url><loc>{SITE_URL}</loc><lastmod>{date.today().isoformat()}</lastmod><changefreq>daily</changefreq></url>\n"
    "</urlset>\n", encoding="utf-8")

print(f"site/index.html construit avec {len(events)} événements "
      f"({len(graph) - 2} fiches Google) et site/sitemap.xml.")
