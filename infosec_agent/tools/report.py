from datetime import datetime
from pathlib import Path

_OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"


def write_report(content: str) -> dict:
    """Write the final digest report to a markdown file in the output directory.

    Args:
        content: The full markdown content of the report to write.

    Returns a dict with the path of the written file.
    """
    _OUTPUT_DIR.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = _OUTPUT_DIR / f"{date_str}_infosec_digest.md"
    output_path.write_text(content, encoding="utf-8")
    return {"path": str(output_path), "filename": output_path.name}
