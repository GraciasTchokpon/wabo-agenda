"""Lecture des flux RSS d'actualité, filtrés sur les annonces d'événements."""
import re

import feedparser
from bs4 import BeautifulSoup

from .. import settings
from ..textutil import normalize


def _clean(html: str) -> str:
    return re.sub(r"\s+", " ", BeautifulSoup(html or "", "html.parser").get_text(" ")).strip()


def fetch(url: str, keywords: list[str]) -> list[dict]:
    feed = feedparser.parse(url, agent=settings.USER_AGENT)
    keys = [normalize(k) for k in keywords]
    items = []
    for entry in feed.entries:
        title = entry.get("title", "")
        summary = _clean(entry.get("summary", ""))
        content = _clean(entry["content"][0]["value"]) if entry.get("content") else ""
        blob = normalize(f"{title} {summary}")
        if keys and not any(k in blob for k in keys):
            continue
        items.append({
            "text": f"{title}\n\n{content or summary}\n\nPublié le : {entry.get('published', 'inconnu')}",
            "url": entry.get("link"),
        })
    return items
