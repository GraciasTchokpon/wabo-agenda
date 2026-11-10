"""Usage :
    python -m wabo_collector collect   # lit les sources et enregistre le contenu brut
    python -m wabo_collector extract   # transforme le contenu brut en fiches « à valider »
    python -m wabo_collector all       # les deux
"""
import sys
from datetime import date

import yaml

from . import db, settings
from .dedup import find_duplicate
from .extract import extract
from .fetchers import meta, rss, web
from .textutil import content_hash, slugify


def collect() -> None:
    conf = yaml.safe_load(open(settings.SOURCES_FILE, encoding="utf-8"))
    keywords = conf.get("keywords", [])
    for s in conf["sources"]:
        if not s.get("active", True):
            continue
        print(f"→ {s['name']}")
        kind = s["kind"]
        db_kind = "instagram" if kind.startswith("instagram") else ("manuel" if kind == "facebook_page" else kind)
        sid = db.source_id(s["name"], db_kind, s.get("url"), s.get("reliability", 0.5))
        try:
            if kind == "rss":
                items = rss.fetch(s["url"], keywords)
            elif kind == "site":
                items = web.fetch(s["url"])
            elif kind == "instagram":
                items = meta.instagram_account(s["username"])
            elif kind == "instagram_hashtag":
                items = meta.instagram_hashtag(s["tag"])
            elif kind == "facebook_page":
                items = meta.facebook_page(s["page"])
            else:
                print(f"  type inconnu : {kind}")
                continue
        except Exception as e:  # noqa: BLE001
            print(f"  erreur : {e}")
            continue
        added = sum(db.insert_raw(sid, it["text"], content_hash(it.get("key") or it["text"]), it.get("url"), it.get("media_urls"))
                    for it in items)
        print(f"  {len(items)} élément(s) lu(s), {added} nouveau(x)")


def _unique_id(title: str, start: str) -> str:
    base = slugify(title)
    year = start[:4]
    if not base.endswith(year):
        base = f"{base}-{year}"
    candidate, n = base, 2
    while db.event_id_taken(candidate):
        candidate, n = f"{base}-{n}", n + 1
    return candidate


def process() -> None:
    today = date.today().isoformat()
    existing = db.comparable_events(today)
    for raw in db.new_raw_items():
        src = raw.get("sources") or {}
        label = src.get("name", "Source")
        source_ref = {"label": label, "url": raw["origin_url"]} if raw.get("origin_url") else None
        try:
            found = extract(raw.get("text") or "", raw.get("media_urls") or [])
        except Exception as e:  # noqa: BLE001
            db.set_raw_status(raw["id"], "erreur", str(e)[:500])
            print(f"  #{raw['id']} erreur : {e}")
            continue
        for ev in found:
            if ev["end_date"] < today:
                continue
            dup = find_duplicate(ev, existing)
            if dup:
                db.add_source_to_event(dup["id"], raw["id"], source_ref)
                db.save_extraction(raw["id"], ev, ev["confidence"], ev["warnings"], settings.LLM_MODEL, dup["id"])
                print(f"  #{raw['id']} doublon de « {dup['title']} »")
                continue
            eid = _unique_id(ev["title"], ev["start_date"])
            row = {
                "id": eid, "title": ev["title"], "category": ev["category"],
                "start_date": ev["start_date"], "end_date": ev["end_date"], "start_time": ev.get("start_time"),
                "city": ev["city"], "place": ev["place"], "price_text": ev["price_text"], "is_free": ev["is_free"],
                "dates_tbc": ev["dates_tbc"], "description": ev["description"], "link": ev.get("link"),
                "sources": [source_ref] if source_ref else [], "status": "a_valider", "confidence": ev["confidence"],
            }
            db.upsert_pending_event(row)
            db.add_source_to_event(eid, raw["id"], None)
            db.save_extraction(raw["id"], ev, ev["confidence"], ev["warnings"], settings.LLM_MODEL, eid)
            existing.append(row)
            print(f"  #{raw['id']} nouvelle fiche à valider : {ev['title']} ({ev['start_date']})")
        db.set_raw_status(raw["id"], "extrait" if found else "traite")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("collect", "all"):
        collect()
    if cmd in ("extract", "all"):
        process()
