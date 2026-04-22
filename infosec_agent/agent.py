import yaml
import feedparser
from pathlib import Path
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "keywords.yaml"
_REGISTER_FEED = "https://www.theregister.com/headlines.atom"


def load_keywords() -> dict:
    """Load the list of keywords used to filter news stories from the config file."""
    with open(_CONFIG_PATH) as f:
        data = yaml.safe_load(f)
    keywords = data.get("keywords", [])
    return {"keywords": keywords, "count": len(keywords)}


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


root_agent = Agent(
    name="infosec_news_agent",
    model="gemini-2.5-flash",
    description="Curates infosec news from The Register based on configured keywords.",
    instruction="""You are an infosec news curator. Follow these steps every time you are run:

1. Call load_keywords to get the list of interest keywords.
2. Call fetch_register_news to get the latest stories from The Register.
3. Filter the stories: keep only those whose title or summary contains at least one keyword (case-insensitive).
4. Present the matching stories in this format for each one:

   **[Title](link)**
   Published: <date>
   <One-sentence summary>

If no stories match, say so clearly. Always show the total number of stories fetched and how many matched.""",
    tools=[FunctionTool(load_keywords), FunctionTool(fetch_register_news)],
)
