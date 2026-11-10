"""Réception des messages WhatsApp (affiches, textes) via l'API officielle WhatsApp Cloud.

Lancement : uvicorn wabo_collector.whatsapp_webhook:app --host 0.0.0.0 --port 8000
Puis déclarer https://<votre-serveur>/webhook dans Meta for Developers > WhatsApp > Configuration.
Recevoir un message est gratuit ; la réponse automatique part dans la fenêtre de service de 24 h.
"""
import hashlib
import hmac
from datetime import datetime, timezone

import requests
from fastapi import FastAPI, HTTPException, Request, Response

from . import db, settings
from .textutil import content_hash

app = FastAPI(title="Wabo – réception WhatsApp")
AUTH = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}


@app.get("/webhook")
def verify(request: Request):
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and p.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN:
        return Response(p.get("hub.challenge", ""), media_type="text/plain")
    raise HTTPException(403)


def _check_signature(body: bytes, header: str | None) -> None:
    if not settings.WHATSAPP_APP_SECRET:
        return
    expected = "sha256=" + hmac.new(settings.WHATSAPP_APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not header or not hmac.compare_digest(expected, header):
        raise HTTPException(401, "Signature invalide")


def _download_media(media_id: str) -> tuple[bytes, str]:
    meta = requests.get(f"{settings.GRAPH_API}/{media_id}", headers=AUTH, timeout=30).json()
    r = requests.get(meta["url"], headers=AUTH, timeout=60)
    r.raise_for_status()
    return r.content, meta.get("mime_type", "image/jpeg")


def _reply(to: str, text: str) -> None:
    requests.post(f"{settings.GRAPH_API}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages", headers=AUTH, timeout=30,
                  json={"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}})


@app.post("/webhook")
async def receive(request: Request):
    body = await request.body()
    _check_signature(body, request.headers.get("x-hub-signature-256"))
    payload = await request.json()
    sid = db.source_id("WhatsApp Wabo", "whatsapp")
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for m in change.get("value", {}).get("messages", []):
                sender = m.get("from")
                text, media = "", []
                if m["type"] == "text":
                    text = m["text"]["body"]
                elif m["type"] in ("image", "document"):
                    obj = m[m["type"]]
                    text = obj.get("caption", "")
                    content, mime = _download_media(obj["id"])
                    if mime.startswith("image/"):
                        ext = mime.split("/")[1]
                        path = f"{datetime.now(timezone.utc):%Y/%m}/{m['id']}.{ext}"
                        media.append(db.upload_poster(path, content, mime))
                else:
                    continue
                new = db.insert_raw(sid, text, content_hash(text, *media, m["id"]), media_urls=media, contact=sender)
                if new:
                    _reply(sender, "Merci ! Wabo a bien reçu votre événement. Nous le vérifions avant de le publier.")
    return {"ok": True}
