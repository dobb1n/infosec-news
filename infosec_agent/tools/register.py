import feedparser

_REGISTER_FEED = "https://www.theregister.com/headlines.atom"


def fetch_register_news() -> dict:
    """Fetch the latest news stories from The Register's Atom feed.

    Returns a list of stories with title, summary, link, and published date.
    """
    feed = feedparser.parse(_REGISTER_FEED)
    if feed.bozo and not feed.entries:
        return {"error": f"Failed to fetch feed: {feed.bozo_exception}", "stories": []}

    stories = [
        {
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "link": entry.get("link", ""),
            "published": entry.get("published", ""),
        }
        for entry in feed.entries
    ]
    return {"stories": stories, "total": len(stories)}
