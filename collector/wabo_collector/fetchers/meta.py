"""Instagram et Facebook par les API officielles de Meta (pas de scraping).

Instagram – Business Discovery : lit les publications publiques de n'importe quel compte
professionnel ou créateur, à partir du compte Instagram professionnel de Wabo.
Instagram – Hashtags : nécessite la fonctionnalité « Instagram Public Content Access »
(validation Meta) et est limité à 30 hashtags différents par période de 7 jours.
Facebook – Pages : nécessite la fonctionnalité « Page Public Content Access » (validation Meta
+ vérification d'entreprise). Désactivé tant que FACEBOOK_PPCA_ENABLED n'est pas à 1.
"""
from datetime import datetime, timedelta, timezone

import requests

from .. import settings

FIELDS = "id,caption,media_type,media_url,permalink,timestamp,children{media_type,media_url}"


def _get(path: str, **params) -> dict:
    params["access_token"] = settings.META_ACCESS_TOKEN
    r = requests.get(f"{settings.GRAPH_API}/{path}", params=params, timeout=30)
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "erreur Meta"))
    return data


def _recent(ts: str, days: int) -> bool:
    try:
        return datetime.fromisoformat(ts.replace("+0000", "+00:00")) >= datetime.now(timezone.utc) - timedelta(days=days)
    except ValueError:
        return True


def _images(media: dict) -> list[str]:
    if media.get("media_type") == "CAROUSEL_ALBUM":
        kids = media.get("children", {}).get("data", [])
        return [k["media_url"] for k in kids if k.get("media_type") == "IMAGE" and k.get("media_url")][:3]
    if media.get("media_type") == "IMAGE" and media.get("media_url"):
        return [media["media_url"]]
    return []  # vidéos : seule la légende est lue


def _items_from_media(medias: list[dict], label: str, days: int) -> list[dict]:
    items = []
    for m in medias:
        if not _recent(m.get("timestamp", ""), days):
            continue
        items.append({
            "text": f"{label}\nPublié le {m.get('timestamp', '')}\n\n{m.get('caption') or '(pas de légende : lire l’affiche)'}",
            "url": m.get("permalink"),
            "media_urls": _images(m),
            "key": m["id"],
        })
    return items


def instagram_account(username: str, days: int = 30) -> list[dict]:
    if not (settings.IG_USER_ID and settings.META_ACCESS_TOKEN):
        raise RuntimeError("IG_USER_ID et META_ACCESS_TOKEN manquants (fichier .env).")
    data = _get(settings.IG_USER_ID, fields=f"business_discovery.username({username}){{username,media.limit(15){{{FIELDS}}}}}")
    medias = data.get("business_discovery", {}).get("media", {}).get("data", [])
    return _items_from_media(medias, f"Publication Instagram de @{username}", days)


def instagram_hashtag(tag: str, days: int = 7) -> list[dict]:
    if not (settings.IG_USER_ID and settings.META_ACCESS_TOKEN):
        raise RuntimeError("IG_USER_ID et META_ACCESS_TOKEN manquants (fichier .env).")
    found = _get("ig_hashtag_search", user_id=settings.IG_USER_ID, q=tag.lstrip("#")).get("data", [])
    if not found:
        return []
    medias = _get(f"{found[0]['id']}/recent_media", user_id=settings.IG_USER_ID,
                  fields="id,caption,media_type,media_url,permalink,timestamp,children{media_type,media_url}", limit=30).get("data", [])
    return _items_from_media(medias, f"Publication Instagram #{tag.lstrip('#')}", days)


def facebook_page(page: str, days: int = 30) -> list[dict]:
    if not settings.FACEBOOK_PPCA_ENABLED:
        print("  Facebook désactivé : en attente de l'autorisation « Page Public Content Access » de Meta.")
        return []
    posts = _get(f"{page}/posts", fields="id,message,created_time,permalink_url,full_picture", limit=15).get("data", [])
    items = []
    for p in posts:
        if not _recent(p.get("created_time", ""), days):
            continue
        items.append({
            "text": f"Publication de la page Facebook {page}\nPubliée le {p.get('created_time', '')}\n\n{p.get('message') or '(pas de texte : lire l’affiche)'}",
            "url": p.get("permalink_url"),
            "media_urls": [p["full_picture"]] if p.get("full_picture") else [],
            "key": p["id"],
        })
    return items
