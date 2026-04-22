import yaml
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "keywords.yaml"


def load_keywords() -> dict:
    """Load the list of keywords used to filter news stories from the config file."""
    with open(_CONFIG_PATH) as f:
        data = yaml.safe_load(f)
    keywords = data.get("keywords", [])
    return {"keywords": keywords, "count": len(keywords)}
