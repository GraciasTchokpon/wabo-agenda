"""Prévient Bing (et les moteurs compatibles IndexNow) des pages du site.

Lancé par Netlify à chaque mise en ligne (voir netlify.toml). Ne fait rien hors production
et n'empêche jamais la mise en ligne en cas d'erreur.
Google n'utilise pas IndexNow : pour lui, le sitemap déclaré dans Search Console suffit.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = "wabo-agenda.netlify.app"


def main():
    if os.environ.get("CONTEXT", "production") != "production":
        print("IndexNow : pas en production, rien à envoyer.")
        return
    key = (ROOT / "site-src" / "indexnow-key.txt").read_text().strip()
    urls = re.findall(r"<loc>(.*?)</loc>", (ROOT / "site" / "sitemap.xml").read_text())
    body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt",
                       "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            print(f"IndexNow : {len(urls)} adresses envoyées, réponse {r.status}.")
    except Exception as err:  # la mise en ligne ne doit jamais échouer pour ça
        print(f"IndexNow : envoi impossible ({err}).")


if __name__ == "__main__":
    main()
