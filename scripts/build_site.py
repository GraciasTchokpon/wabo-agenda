"""Construit le site public de Wabo à partir de site-src/ et data/events.json.

Produit dans site/ :
- index.html                 la page d'accueil (agenda, calendrier, formulaire)
- evenements/<id>/           une page par événement
- ville/<ville>/             une page par ville
- categorie/<categorie>/     une page par catégorie
- agenda/<mois>-<annee>/     une page par mois
- assets/pages.css           le style de ces pages
- sitemap.xml                le plan du site pour Google

Usage : python3 scripts/build_site.py
"""
import json
import re
import shutil
import unicodedata
from datetime import date, timedelta
from html import escape
from pathlib import Path
from urllib.parse import quote, urlencode

SITE_URL = "https://wabo-agenda.netlify.app/"
# Code de validation Google Search Console (balise meta « google-site-verification »).
GOOGLE_VERIFICATION = "1Yo3GwoEvlcCx2ERLPvAdntEuufmnTcifN98eOCaEmU"
EMAIL = "wabo.agenda.benin@gmail.com"
INSTAGRAM = "https://www.instagram.com/wabo_agenda_benin/"

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
TODAY = date.today()

CATS = {
    "festival": ("Festival", "Festivals", "#FEF3C7"),
    "concert": ("Concert", "Concerts", "#FCE2E5"),
    "conference": ("Conférence", "Conférences et forums", "#E3E0F3"),
    "gastronomie": ("Gastronomie", "Événements gastronomiques", "#FDE8D7"),
    "humour": ("Humour", "Spectacles d'humour", "#D9E4F5"),
    "culture": ("Culture et traditions", "Culture et traditions", "#E3F2EA"),
    "soiree": ("Soirée", "Soirées", "#FCE2E5"),
    "atelier": ("Atelier", "Ateliers", "#E3F2EA"),
    "sport": ("Sport", "Événements sportifs", "#FEF3C7"),
    "lancement": ("Lancement", "Lancements", "#E8E1D3"),
    "salon": ("Salon et expo", "Salons et expositions", "#E3E0F3"),
}
MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
          "septembre", "octobre", "novembre", "décembre"]
MONTHS_SHORT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août",
                "sept.", "oct.", "nov.", "déc."]
DAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
FONTS = ("https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700"
         "&family=Inter:wght@400;500;600;700&display=swap")
FLAG_SVG = ('<svg width="30" height="21" viewBox="0 0 26 18" aria-hidden="true"><rect width="10" height="18" rx="2" '
            'fill="#008751"/><rect x="10" width="16" height="9" fill="#FCD116"/><rect x="10" y="9" width="16" '
            'height="9" fill="#E8112D"/></svg>')


# ---------- Outils ----------

def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def d(key):
    return date.fromisoformat(key)


def cities(e):
    return [c.strip() for c in e["city"].split("·") if c.strip()]


def long_date(x):
    return f"{DAYS[x.weekday()]} {x.day}{'er' if x.day == 1 else ''} {MONTHS[x.month - 1]} {x.year}"


def dnum(x):
    return "1er" if x.day == 1 else str(x.day)


def date_text(e):
    if e.get("tbc"):
        return e.get("dateText") or f"{MONTHS[d(e['start']).month - 1].capitalize()} {d(e['start']).year} – dates à confirmer"
    s, f = d(e["start"]), d(e["end"])
    if s == f:
        return long_date(s).capitalize() + (f" à {e['time']}" if e.get("time") else "")
    if s.month == f.month and s.year == f.year:
        return f"Du {dnum(s)} au {f.day} {MONTHS[s.month - 1]} {s.year}"
    if s.year == f.year:
        return f"Du {dnum(s)} {MONTHS[s.month - 1]} au {f.day} {MONTHS[f.month - 1]} {f.year}"
    return f"Du {dnum(s)} {MONTHS[s.month - 1]} {s.year} au {f.day} {MONTHS[f.month - 1]} {f.year}"


def short_dates(e):
    if e.get("tbc"):
        return e.get("dateText") or "Dates à confirmer"
    s, f = d(e["start"]), d(e["end"])
    if s == f:
        return f"{DAYS[s.weekday()].capitalize()} {s.day} {MONTHS_SHORT[s.month - 1]}"
    if s.month == f.month:
        return f"{s.day}–{f.day} {MONTHS_SHORT[s.month - 1]}"
    return f"{s.day} {MONTHS_SHORT[s.month - 1]} – {f.day} {MONTHS_SHORT[f.month - 1]}"


def status(e):
    if d(e["end"]) < TODAY:
        return "past"
    if not e.get("tbc") and d(e["start"]) <= TODAY <= d(e["end"]):
        return "live"
    return "tbc" if e.get("tbc") else "future"


def months_of(e):
    """Mois couverts par l'événement, sous forme (année, mois)."""
    s, f = d(e["start"]), d(e["end"])
    out, y, m = [], s.year, s.month
    while (y, m) <= (f.year, f.month):
        out.append((y, m))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def month_slug(y, m):
    return f"{slug(MONTHS[m - 1])}-{y}"


def gcal(e):
    end = d(e["end"]) + timedelta(days=1)
    q = {"action": "TEMPLATE", "text": e["title"],
         "dates": e["start"].replace("-", "") + "/" + end.isoformat().replace("-", ""),
         "details": e.get("description", "") + (("\n" + e["link"]) if e.get("link") else "") + "\nVu sur Wabo – Agenda Bénin",
         "location": e["place"] + ", Bénin"}
    return "https://calendar.google.com/calendar/render?" + urlencode(q)


def ld(obj):
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=1).replace("</", "<\\/") + "\n</script>")


def event_ld(e):
    start = e["start"] + (f"T{e['time']}:00+01:00" if e.get("time") else "")
    item = {
        "@type": "Event",
        "name": e["title"],
        "startDate": start,
        "endDate": e.get("end") or e["start"],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "location": {"@type": "Place", "name": e["place"],
                     "address": {"@type": "PostalAddress", "addressLocality": cities(e)[0], "addressCountry": "BJ"}},
        "description": e.get("description", ""),
        "image": [SITE_URL + "og-image.png"],
        "url": f"{SITE_URL}evenements/{e['id']}/",
    }
    if e.get("free"):
        item["offers"] = {"@type": "Offer", "price": 0, "priceCurrency": "XOF",
                          "availability": "https://schema.org/InStock", "url": e.get("link") or item["url"]}
    elif e.get("link"):
        item["offers"] = {"@type": "Offer", "url": e["link"], "availability": "https://schema.org/InStock"}
    return item


def breadcrumb_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + u}
                                for i, (n, u) in enumerate(items)]}


# ---------- Gabarit des pages fixes ----------

def page(path, title, description, body, jsonld=(), og_type="website"):
    """Écrit site/<path>/index.html. path sans barre au début, avec barre à la fin."""
    url = SITE_URL + path
    head_ld = "\n".join(ld(x) for x in jsonld)
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#008751">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Wabo – Agenda Bénin">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/apple-touch-icon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="/assets/pages.css">
{head_ld}
</head>
<body>
<div class="flag" aria-hidden="true"><i></i><i></i><i></i></div>
<header class="top">
  <div class="wrap topbar">
    <a class="brand" href="/" aria-label="Wabo, Agenda Bénin – accueil">{FLAG_SVG}<b>Wabo</b><small>Agenda Bénin</small></a>
    <nav class="tabs" aria-label="Sections">
      <a href="/">Agenda</a><a href="/#calendrier">Calendrier</a><a href="/#proposer">Proposer</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
{EXPLORE}
<footer>
  <div class="wrap">
    <span>Wabo – Agenda Bénin · tous les événements du Bénin au même endroit</span>
    <span><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram @wabo_agenda_benin</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></span>
  </div>
</footer>
</body>
</html>
"""
    out = SITE / path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    PAGES.append(path)


def card(e):
    cat = CATS.get(e["category"], (e["category"], e["category"], "#EEE9E1"))
    s = d(e["start"])
    st = status(e)
    sub = "à confirmer" if e.get("tbc") else (f"→ {d(e['end']).day} {MONTHS_SHORT[d(e['end']).month - 1]}" if e["end"] != e["start"] else "")
    badge = {"live": '<span class="badge live">En ce moment</span>',
             "tbc": '<span class="badge tbc">Dates à confirmer</span>',
             "past": '<span class="badge past">Terminé</span>'}.get(st, "")
    return f"""<a class="card" href="/evenements/{e['id']}/">
  <span class="tile" style="background:{cat[2]}"><b>{'?' if e.get('tbc') else s.day}</b><small>{MONTHS_SHORT[s.month - 1]}</small><em>{escape(sub)}</em></span>
  <span class="cbody"><span class="cat">{escape(cat[0])}</span><span class="ctitle">{escape(e['title'])}</span>
  <span class="cmeta">{escape(short_dates(e))} · {escape(e['city'])}</span>{badge}</span>
</a>"""


def listing(evs):
    up = [e for e in evs if status(e) != "past"]
    past = [e for e in evs if status(e) == "past"]
    html = '<div class="grid">' + "".join(card(e) for e in up) + "</div>" if up else \
        '<p class="empty">Aucun événement annoncé pour l\'instant. Vous en connaissez un ? <a href="/#proposer">Proposez-le</a>.</p>'
    if past:
        html += '<h2>Déjà passés</h2><div class="grid">' + "".join(card(e) for e in past[::-1]) + "</div>"
    return html


# ---------- Données ----------

events = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))
events.sort(key=lambda e: (e["start"], e.get("tbc", False), e["title"]))
PAGES = []

by_city, by_cat, by_month = {}, {}, {}
for e in events:
    for c in cities(e):
        by_city.setdefault(c, []).append(e)
    by_cat.setdefault(e["category"], []).append(e)
    for ym in months_of(e):
        by_month.setdefault(ym, []).append(e)

# Liens « Explorer », repris en bas de toutes les pages (Google suit ces liens).
current = (TODAY.year, TODAY.month)
months_shown = sorted(ym for ym in by_month if ym >= current)
EXPLORE = f"""<section class="wrap explore" aria-labelledby="exploreTitle">
  <h2 id="exploreTitle">Explorer l'agenda du Bénin</h2>
  <h3>Par mois</h3>
  <ul class="links">{''.join(f'<li><a href="/agenda/{month_slug(y, m)}/">{MONTHS[m - 1].capitalize()} {y}</a></li>' for y, m in months_shown)}</ul>
  <h3>Par ville</h3>
  <ul class="links">{''.join(f'<li><a href="/ville/{slug(c)}/">{escape(c)}</a></li>' for c in sorted(by_city, key=lambda c: (-len(by_city[c]), c)))}</ul>
  <h3>Par catégorie</h3>
  <ul class="links">{''.join(f'<li><a href="/categorie/{slug(CATS[k][0])}/">{escape(CATS[k][1])}</a></li>' for k in sorted(by_cat, key=lambda k: -len(by_cat[k])) if k in CATS)}</ul>
</section>"""

# Repartir d'un dossier propre pour les pages générées
for sub in ("evenements", "ville", "categorie", "agenda", "assets"):
    shutil.rmtree(SITE / sub, ignore_errors=True)
(SITE / "assets").mkdir(parents=True)
shutil.copy(ROOT / "site-src" / "pages.css", SITE / "assets" / "pages.css")
# Clé IndexNow (Bing) : le fichier doit être servi à la racine du site
_key = (ROOT / "site-src" / "indexnow-key.txt").read_text().strip()
for old in SITE.glob("*.txt"):
    if old.name != "robots.txt":
        old.unlink()
(SITE / f"{_key}.txt").write_text(_key, encoding="utf-8")

# ---------- Pages événement ----------

for e in events:
    cat = CATS.get(e["category"], (e["category"], e["category"], "#EEE9E1"))
    city = cities(e)[0]
    st = status(e)
    badge = {"live": '<span class="badge live">En ce moment</span>',
             "tbc": '<span class="badge tbc">Dates à confirmer</span>',
             "past": '<span class="badge past">Événement terminé</span>'}.get(st, "")
    share = f"{e['title']}\n{date_text(e)}\n{e['place']}\n{SITE_URL}evenements/{e['id']}/"
    buttons = []
    if e.get("link"):
        buttons.append(f'<a class="btn primary" href="{escape(e["link"])}" target="_blank" rel="noopener">S\'inscrire / billetterie</a>')
    if not e.get("tbc") and st != "past":
        buttons.append(f'<a class="btn" href="{escape(gcal(e))}" target="_blank" rel="noopener">Ajouter à mon agenda</a>')
    buttons.append(f'<a class="btn" href="https://wa.me/?text={quote(share)}" target="_blank" rel="noopener">Partager sur WhatsApp</a>')
    sources = " · ".join(f'<a href="{escape(s["url"])}" target="_blank" rel="noopener">{escape(s["label"])}</a>' for s in e.get("sources", []))
    others = [o for o in by_city.get(city, []) if o["id"] != e["id"] and status(o) != "past"][:4]
    if len(others) < 4:
        others += [o for o in events if o["id"] != e["id"] and o not in others and status(o) != "past"][:4 - len(others)]
    month_links = " · ".join(f'<a href="/agenda/{month_slug(y, m)}/">{MONTHS[m - 1]} {y}</a>' for y, m in months_of(e))
    body = f"""<p class="crumbs"><a href="/">Accueil</a> › <a href="/ville/{slug(city)}/">{escape(city)}</a> › {escape(e['title'])}</p>
<article class="sheet">
  <span class="cat"><a href="/categorie/{slug(cat[0])}/" style="color:inherit;text-decoration:none">{escape(cat[0])}</a></span>
  <h1 style="margin:0">{escape(e['title'])}</h1>
  {badge}
  <ul class="facts">
    <li><span class="k">Quand</span><span><b>{escape(date_text(e))}</b></span></li>
    <li><span class="k">Où</span><span><b>{escape(e['place'])}</b>{escape(e['city'])}, Bénin</span></li>
    <li><span class="k">Prix</span><span><b>{escape(e.get('price') or 'Non communiqué')}</b></span></li>
  </ul>
  <div class="actions">{''.join(buttons)}</div>
  <p class="desc">{escape(e.get('description', ''))}</p>
  <p class="src">Source : {sources}. Vérifiez auprès de l'organisateur avant de vous déplacer.
  Une erreur ? <a href="/#proposer">Signalez-la</a>.<br>Voir aussi : {month_links}.</p>
</article>
<h2>À voir aussi{(' à ' + escape(city)) if others and all(city in cities(o) for o in others) else ''}</h2>
{listing(others) if others else ''}"""
    desc = (e.get("description") or e["title"])
    desc = f"{short_dates(e)} · {e['city']}. " + (desc[:140].rsplit(" ", 1)[0] + "…" if len(desc) > 140 else desc)
    page(f"evenements/{e['id']}/",
         f"{e['title']} – {short_dates(e)}, {city} | Wabo Agenda Bénin",
         desc, body,
         jsonld=[{"@context": "https://schema.org", **event_ld(e)} if not e.get("tbc") else {"@context": "https://schema.org", "@type": "WebPage", "name": e["title"]},
                 breadcrumb_ld([("Accueil", ""), (city, f"ville/{slug(city)}/"), (e["title"], f"evenements/{e['id']}/")])],
         og_type="article")

# ---------- Pages ville, catégorie, mois ----------

for c, evs in by_city.items():
    n = len([e for e in evs if status(e) != "past"])
    page(f"ville/{slug(c)}/",
         f"Événements à {c} : concerts, festivals, sorties | Wabo Agenda Bénin",
         f"Que faire à {c} ? {n} événement{'s' if n > 1 else ''} à venir : concerts, festivals, conférences et soirées, avec dates, lieux et liens d'inscription.",
         f"""<p class="crumbs"><a href="/">Accueil</a> › {escape(c)}</p>
<h1>Que faire à {escape(c)} ?</h1>
<p class="lead">Concerts, festivals, conférences, soirées : les événements à venir à {escape(c)}, vérifiés par Wabo, avec les dates, les lieux et les liens pour s'inscrire.</p>
{listing(evs)}""",
         jsonld=[breadcrumb_ld([("Accueil", ""), (c, f"ville/{slug(c)}/")])])

for k, evs in by_cat.items():
    if k not in CATS:
        continue
    label, plural, _ = CATS[k]
    page(f"categorie/{slug(label)}/",
         f"{plural} au Bénin – agenda à venir | Wabo Agenda Bénin",
         f"{plural} au Bénin : toutes les dates à venir à Cotonou et ailleurs, avec lieux, prix et liens d'inscription.",
         f"""<p class="crumbs"><a href="/">Accueil</a> › {escape(plural)}</p>
<h1>{escape(plural)} au Bénin</h1>
<p class="lead">Toutes les dates à venir, vérifiées par Wabo, avec les lieux, les prix et les liens d'inscription.</p>
{listing(evs)}""",
         jsonld=[breadcrumb_ld([("Accueil", ""), (plural, f"categorie/{slug(label)}/")])])

for (y, m), evs in by_month.items():
    name = f"{MONTHS[m - 1]} {y}"
    page(f"agenda/{month_slug(y, m)}/",
         f"Événements au Bénin en {name} : concerts, festivals | Wabo",
         f"Que faire au Bénin en {name} ? Concerts, festivals, conférences et soirées à Cotonou, Ouidah et ailleurs, avec dates et liens d'inscription.",
         f"""<p class="crumbs"><a href="/">Accueil</a> › {escape(name.capitalize())}</p>
<h1>Que faire au Bénin en {escape(name)} ?</h1>
<p class="lead">Les événements de {escape(name)} au Bénin : concerts, festivals, conférences, soirées, avec les dates, les lieux et les liens pour s'inscrire.</p>
{listing(evs)}""",
         jsonld=[breadcrumb_ld([("Accueil", ""), (name.capitalize(), f"agenda/{month_slug(y, m)}/")])])

# ---------- Page d'accueil ----------

template = (ROOT / "site-src" / "template.html").read_text(encoding="utf-8")
graph = [
    {"@type": "WebSite", "name": "Wabo – Agenda Bénin", "alternateName": ["Wabo", "Wabo Agenda Bénin"],
     "url": SITE_URL, "inLanguage": "fr"},
    {"@type": "Organization", "name": "Wabo – Agenda Bénin", "url": SITE_URL,
     "logo": SITE_URL + "apple-touch-icon.png", "email": EMAIL, "sameAs": [INSTAGRAM]},
] + [event_ld(e) for e in events if not e.get("tbc") and status(e) != "past"]

for m in ("/*__EVENTS__*/[]", "<!--__JSONLD__-->", "<!--__GOOGLE_VERIFICATION__-->", "<!--__EXPLORE__-->"):
    if m not in template:
        raise SystemExit(f"Marqueur {m} introuvable dans le modèle.")
html = (template
        .replace("/*__EVENTS__*/[]", json.dumps(events, ensure_ascii=False))
        .replace("<!--__JSONLD__-->", ld({"@context": "https://schema.org", "@graph": graph}))
        .replace("<!--__GOOGLE_VERIFICATION__-->",
                 f'<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">' if GOOGLE_VERIFICATION else "")
        .replace("<!--__EXPLORE__-->", EXPLORE))
(SITE / "index.html").write_text(html, encoding="utf-8")

# ---------- Plan du site ----------

urls = [""] + PAGES
(SITE / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>\n" for u in urls)
    + "</urlset>\n", encoding="utf-8")

print(f"Accueil + {len(PAGES)} pages ({len(events)} événements, {len(by_city)} villes, "
      f"{len([k for k in by_cat if k in CATS])} catégories, {len(by_month)} mois) et sitemap.xml.")
