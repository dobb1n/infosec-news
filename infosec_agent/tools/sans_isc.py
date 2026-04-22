import re
import feedparser

_SANS_ISC_FEED = "https://isc.sans.edu/podcast.rss"


def fetch_sans_isc_notes() -> dict:
    """Fetch the latest episode notes from the SANS Internet Storm Center podcast RSS feed.

    Returns the most recent episodes with title, summary, link, and published date.
    """
    feed = feedparser.parse(_SANS_ISC_FEED)
    if feed.bozo and not feed.entries:
        return {"error": f"Failed to fetch feed: {feed.bozo_exception}", "episodes": []}

    episodes = []
    for entry in feed.entries[:10]:
        summary = re.sub(r"<[^>]+>", " ", entry.get("summary", "")).strip()
        summary = re.sub(r"\s+", " ", summary)
        episodes.append({
            "title": entry.get("title", ""),
            "summary": summary,
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        })
    return {"episodes": episodes, "total": len(episodes)}
