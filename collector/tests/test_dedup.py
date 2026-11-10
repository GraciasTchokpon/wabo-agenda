from wabo_collector.dedup import find_duplicate, similarity
from wabo_collector.textutil import slugify

EXISTING = [
    {"id": "weloveya-2026", "title": "WeLovEya 2026", "city": "Cotonou", "start_date": "2026-12-26", "end_date": "2026-12-27"},
    {"id": "vodun-days-2027", "title": "Vodun Days 2027", "city": "Ouidah", "start_date": "2027-01-02", "end_date": "2027-01-09"},
]


def test_same_event_other_wording_is_duplicate():
    cand = {"title": "Festival We Love Eya - 5e édition", "city": "Cotonou", "start_date": "2026-12-26", "end_date": "2026-12-27"}
    assert find_duplicate(cand, EXISTING)["id"] == "weloveya-2026"


def test_same_title_different_dates_is_not_duplicate():
    cand = {"title": "WeLovEya", "city": "Cotonou", "start_date": "2027-12-26", "end_date": "2027-12-27"}
    assert find_duplicate(cand, EXISTING) is None


def test_one_day_inside_a_festival_matches():
    cand = {"title": "Vodun Days : journée des Egungun", "city": "Ouidah", "start_date": "2027-01-08", "end_date": "2027-01-08"}
    assert similarity(cand, EXISTING[1]) > 0


def test_slugify():
    assert slugify("Fête de l'Indépendance à Porto-Novo !") == "fete-de-l-independance-a-porto-novo"


def test_two_forums_same_hotel_same_days_are_not_duplicates():
    a = {"title": "Cyber Africa Forum 2026", "city": "Cotonou", "start_date": "2026-11-16", "end_date": "2026-11-17"}
    b = {"title": "Next Fintech Forum 2026", "city": "Cotonou", "start_date": "2026-11-16", "end_date": "2026-11-17"}
    assert find_duplicate(a, [dict(b, id="nff")]) is None
