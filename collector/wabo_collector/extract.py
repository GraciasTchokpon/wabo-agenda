"""Extraction par IA : lit un texte ou une affiche et renvoie des événements structurés."""
import base64
from datetime import date

import anthropic
import requests

from . import settings

CATEGORIES = ["festival", "concert", "soiree", "conference", "atelier", "gastronomie", "humour", "culture",
              "sport", "famille", "lancement", "business", "religieux"]

TOOL = {
    "name": "enregistrer_evenements",
    "description": "Enregistre les événements à venir au Bénin trouvés dans le contenu.",
    "input_schema": {
        "type": "object",
        "properties": {
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "category": {"type": "string", "enum": CATEGORIES},
                        "start_date": {"type": "string", "description": "AAAA-MM-JJ"},
                        "end_date": {"type": "string", "description": "AAAA-MM-JJ, égale à start_date si un seul jour"},
                        "start_time": {"type": ["string", "null"], "description": "HH:MM ou null"},
                        "dates_tbc": {"type": "boolean", "description": "vrai si le contenu ne donne pas de date précise"},
                        "city": {"type": "string"},
                        "place": {"type": "string", "description": "nom du lieu + quartier si connus"},
                        "price_text": {"type": "string", "description": "tel qu'écrit, ou 'Non communiqué'"},
                        "is_free": {"type": "boolean"},
                        "link": {"type": ["string", "null"], "description": "lien d'inscription ou officiel, sinon null"},
                        "description": {"type": "string", "description": "2 phrases maximum, reformulées, en français"},
                        "confidence": {"type": "number", "description": "0 à 1 : certitude sur la date, le lieu et le titre"},
                        "warnings": {"type": "array", "items": {"type": "string"},
                                     "description": "ce qui doit être vérifié par un humain (ex. année absente, lieu imprécis)"},
                    },
                    "required": ["title", "category", "start_date", "end_date", "dates_tbc", "city", "place",
                                 "price_text", "is_free", "description", "confidence", "warnings"],
                },
            }
        },
        "required": ["events"],
    },
}

SYSTEM = """Tu aides Wabo, l'agenda des événements au Bénin.
On te donne un contenu (article, page web, message WhatsApp ou affiche).
Extrais uniquement les événements ouverts au public qui ont lieu au Bénin et qui ne sont pas terminés à la date du jour indiquée.
N'invente rien : un champ absent du contenu reste vague ('Non communiqué', null) et tu l'ajoutes aux warnings.
Si l'année manque, déduis la prochaine occurrence et ajoute un warning. Si aucune date précise n'est donnée, mets dates_tbc à true.
S'il n'y a aucun événement, renvoie une liste vide."""


def _image_block(url: str) -> dict | None:
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        mime = r.headers.get("content-type", "image/jpeg").split(";")[0]
        if mime not in ("image/jpeg", "image/png", "image/webp", "image/gif"):
            return None
        return {"type": "image", "source": {"type": "base64", "media_type": mime, "data": base64.b64encode(r.content).decode()}}
    except Exception as e:  # noqa: BLE001
        print(f"  image illisible {url}: {e}")
        return None


def extract(text: str, image_urls: list[str] | None = None, today: date | None = None) -> list[dict]:
    if not settings.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY manquant (fichier .env).")
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    content: list[dict] = [b for b in (_image_block(u) for u in (image_urls or [])[:4]) if b]
    content.append({"type": "text", "text": f"Date du jour : {(today or date.today()).isoformat()}\n\nContenu :\n{text or '(affiche seule)'}"})
    msg = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=2000,
        system=SYSTEM,
        tools=[TOOL],
        tool_choice={"type": "tool", "name": TOOL["name"]},
        messages=[{"role": "user", "content": content}],
    )
    for block in msg.content:
        if block.type == "tool_use":
            return block.input.get("events", [])
    return []
