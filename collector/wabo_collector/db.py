"""Accès à la base Supabase (clé service_role, côté serveur uniquement)."""
from functools import lru_cache

from supabase import Client, create_client

from . import settings


@lru_cache
def client() -> Client:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL et SUPABASE_SERVICE_ROLE_KEY doivent être définis (fichier .env).")
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


def source_id(name: str, kind: str, url: str | None = None, reliability: float = 0.5) -> int:
    db = client()
    found = db.table("sources").select("id").eq("name", name).limit(1).execute().data
    if found:
        return found[0]["id"]
    row = db.table("sources").insert({"name": name, "kind": kind, "url": url, "reliability": reliability}).execute().data
    return row[0]["id"]


def insert_raw(source: int, text: str, chash: str, origin_url: str | None = None,
               media_urls: list[str] | None = None, contact: str | None = None) -> bool:
    """Enregistre un élément brut. Renvoie False s'il était déjà connu (même empreinte)."""
    db = client()
    if db.table("raw_items").select("id").eq("content_hash", chash).limit(1).execute().data:
        return False
    db.table("raw_items").insert({
        "source_id": source, "text": text[:20000], "origin_url": origin_url,
        "media_urls": media_urls or [], "submitter_contact": contact, "content_hash": chash,
    }).execute()
    return True


def new_raw_items(limit: int = 50) -> list[dict]:
    return (client().table("raw_items")
            .select("id, text, media_urls, origin_url, received_at, source_id, sources(name, reliability)")
            .eq("status", "nouveau").order("received_at").limit(limit).execute().data)


def set_raw_status(raw_id: int, status: str, error: str | None = None) -> None:
    client().table("raw_items").update({"status": status, "error": error}).eq("id", raw_id).execute()


def save_extraction(raw_id: int, data: dict, confidence: float, warnings: list[str], model: str, event_id: str | None) -> None:
    client().table("extractions").insert({
        "raw_item_id": raw_id, "data": data, "confidence": confidence,
        "warnings": warnings, "model": model, "event_id": event_id,
    }).execute()


def comparable_events(start: str) -> list[dict]:
    """Événements pas encore terminés, pour la recherche de doublons."""
    return (client().table("events").select("id, title, city, start_date, end_date, sources, status")
            .gte("end_date", start).neq("status", "rejete").execute().data)


def upsert_pending_event(row: dict) -> None:
    client().table("events").upsert(row, on_conflict="id", ignore_duplicates=True).execute()


def add_source_to_event(event_id: str, raw_id: int, src: dict | None) -> None:
    db = client()
    db.table("event_sources").upsert({"event_id": event_id, "raw_item_id": raw_id}).execute()
    if src:
        ev = db.table("events").select("sources").eq("id", event_id).single().execute().data
        sources = ev.get("sources") or []
        if all(s.get("url") != src.get("url") for s in sources):
            db.table("events").update({"sources": sources + [src]}).eq("id", event_id).execute()


def event_id_taken(event_id: str) -> bool:
    return bool(client().table("events").select("id").eq("id", event_id).limit(1).execute().data)


def upload_poster(path: str, content: bytes, mime: str) -> str:
    storage = client().storage.from_(settings.POSTER_BUCKET)
    storage.upload(path, content, {"content-type": mime, "upsert": "true"})
    return storage.get_public_url(path)
