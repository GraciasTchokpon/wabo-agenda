import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = os.getenv("WABO_LLM_MODEL", "claude-haiku-5-5")
USER_AGENT = os.getenv("WABO_USER_AGENT", "WaboBot/0.1 (agenda des evenements au Benin)")

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET", "")
GRAPH_API = os.getenv("META_GRAPH_API", "https://graph.facebook.com/v21.0")

# Instagram / Facebook (API officielles Meta)
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")      # jeton longue durée du compte Wabo
IG_USER_ID = os.getenv("IG_USER_ID", "")                    # identifiant du compte Instagram professionnel de Wabo
FACEBOOK_PPCA_ENABLED = os.getenv("FACEBOOK_PPCA_ENABLED", "0") == "1"

SOURCES_FILE = ROOT / "config" / "sources.yaml"
POSTER_BUCKET = "affiches"
