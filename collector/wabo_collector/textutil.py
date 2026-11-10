import hashlib
import re
import unicodedata


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def normalize(s: str) -> str:
    """Minuscules, sans accents ni ponctuation, espaces simplifiés."""
    s = strip_accents((s or "").lower())
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def slugify(s: str, max_len: int = 60) -> str:
    return normalize(s).replace(" ", "-")[:max_len].strip("-")


def content_hash(*parts: str) -> str:
    return hashlib.sha256(normalize(" ".join(p or "" for p in parts)).encode()).hexdigest()
