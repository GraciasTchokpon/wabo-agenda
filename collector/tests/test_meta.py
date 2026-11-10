from datetime import datetime, timezone

from wabo_collector.fetchers.meta import _images, _items_from_media


def test_items_keep_recent_posts_and_images():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")
    medias = [
        {"id": "1", "caption": "Soirée samedi 14/11 à Haie Vive", "media_type": "IMAGE", "media_url": "https://x/1.jpg", "permalink": "https://instagram.com/p/1", "timestamp": now},
        {"id": "2", "caption": "Vieille publication", "media_type": "IMAGE", "media_url": "https://x/2.jpg", "permalink": "https://instagram.com/p/2", "timestamp": "2020-01-01T10:00:00+0000"},
        {"id": "3", "caption": None, "media_type": "CAROUSEL_ALBUM", "permalink": "https://instagram.com/p/3", "timestamp": now,
         "children": {"data": [{"media_type": "IMAGE", "media_url": "https://x/3a.jpg"}, {"media_type": "VIDEO", "media_url": "https://x/3b.mp4"}]}},
    ]
    items = _items_from_media(medias, "Publication Instagram de @test", days=30)
    assert [i["key"] for i in items] == ["1", "3"]
    assert items[0]["media_urls"] == ["https://x/1.jpg"]
    assert items[1]["media_urls"] == ["https://x/3a.jpg"]
    assert "lire l’affiche" in items[1]["text"]


def test_video_has_no_image():
    assert _images({"media_type": "VIDEO", "media_url": "https://x/v.mp4"}) == []
