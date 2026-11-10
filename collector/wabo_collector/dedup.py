"""Repérer qu'un événement extrait existe déjà (le même événement arrive souvent par 3 ou 4 canaux)."""
from datetime import date

from rapidfuzz import fuzz

from .textutil import normalize

# Mots trop courants pour distinguer deux événements
STOP = {"de", "du", "la", "le", "les", "des", "a", "au", "et", "en", "edition", "festival", "cotonou", "benin", "2026", "2027", "e"}


def _core(title: str) -> str:
    return " ".join(w for w in normalize(title).split() if w not in STOP)


def _overlap(a_start: str, a_end: str, b_start: str, b_end: str, slack_days: int = 1) -> bool:
    a0, a1 = date.fromisoformat(a_start), date.fromisoformat(a_end)
    b0, b1 = date.fromisoformat(b_start), date.fromisoformat(b_end)
    return (a0 - b1).days <= slack_days and (b0 - a1).days <= slack_days


def similarity(a: dict, b: dict) -> float:
    """Score 0-100 entre deux événements (titres proches + dates qui se chevauchent + même ville)."""
    if not _overlap(a["start_date"], a["end_date"], b["start_date"], b["end_date"]):
        return 0.0
    ca, cb = _core(a["title"]), _core(b["title"])
    # Comparaison mot à mot, et sans espaces pour « WeLovEya » / « We Love Eya »
    t = max(fuzz.token_set_ratio(ca, cb), fuzz.partial_ratio(ca.replace(" ", ""), cb.replace(" ", "")))
    same_city = normalize(a.get("city", "")).split(" ")[0] == normalize(b.get("city", "")).split(" ")[0]
    return t + (5 if same_city else -10)


def find_duplicate(candidate: dict, existing: list[dict], threshold: float = 85) -> dict | None:
    best, best_score = None, 0.0
    for e in existing:
        s = similarity(candidate, e)
        if s > best_score:
            best, best_score = e, s
    return best if best_score >= threshold else None
