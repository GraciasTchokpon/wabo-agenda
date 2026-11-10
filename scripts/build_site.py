"""Construit site/index.html à partir de site-src/template.html et data/events.json.

Usage : python3 scripts/build_site.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
template = (ROOT / "site-src" / "template.html").read_text(encoding="utf-8")
events = json.loads((ROOT / "data" / "events.json").read_text(encoding="utf-8"))
marker = "/*__EVENTS__*/[]"
if marker not in template:
    raise SystemExit("Marqueur des événements introuvable dans le modèle.")
html = template.replace(marker, json.dumps(events, ensure_ascii=False))
(ROOT / "site" / "index.html").write_text(html, encoding="utf-8")
print(f"site/index.html construit avec {len(events)} événements.")
