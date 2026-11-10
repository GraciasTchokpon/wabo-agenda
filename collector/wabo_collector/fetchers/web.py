"""Lecture d'une page web : on garde d'abord les balises schema.org Event, sinon le texte de la page."""
import json
import re
import time
from urllib import robotparser
from urllib.parse import urljoin, urlparse

import extruct
import requests
from bs4 import BeautifulSoup

from .. import settings

_robots: dict[str, robotparser.RobotFileParser] = {}


def allowed(url: str) -> bool:
    """Respecte le fichier robots.txt du site."""
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    if base not in _robots:
        rp = robotparser.RobotFileParser()
        rp.set_url(urljoin(base, "/robots.txt"))
        try:
            rp.read()
        except Exception:
            pass
        _robots[base] = rp
    try:
        return _robots[base].can_fetch(settings.USER_AGENT, url)
    except Exception:
        return True


def _schema_events(html: str, url: str) -> list[dict]:
    data = extruct.extract(html, base_url=url, syntaxes=["json-ld", "microdata"], uniform=True)
    found = []

    def walk(node):
        if isinstance(node, list):
            for n in node:
                walk(n)
        elif isinstance(node, dict):
            t = node.get("@type")
            types = t if isinstance(t, list) else [t]
            if any(isinstance(x, str) and x.endswith("Event") for x in types):
                found.append(node)
            for v in node.values():
                if isinstance(v, (dict, list)):
                    walk(v)

    walk(data.get("json-ld", []) + data.get("microdata", []))
    return found


def fetch(url: str) -> list[dict]:
    if not allowed(url):
        print(f"  robots.txt interdit la lecture de {url}")
        return []
    r = requests.get(url, headers={"User-Agent": settings.USER_AGENT}, timeout=30)
    r.raise_for_status()
    time.sleep(1)  # politesse envers le site
    events = _schema_events(r.text, url)
    if events:
        return [{"text": "Données structurées schema.org :\n" + json.dumps(e, ensure_ascii=False, default=str)[:6000],
                 "url": e.get("url") or url} for e in events]
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()
    main = soup.find("main") or soup.body or soup
    text = re.sub(r"\s+", " ", main.get_text(" ")).strip()
    return [{"text": f"Page : {url}\n\n{text[:15000]}", "url": url}] if text else []
