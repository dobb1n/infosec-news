import os
from datetime import datetime
from pathlib import Path

_OUTPUT_DIR = Path(__file__).parent.parent.parent / "output"
_GCS_BUCKET = os.environ.get("GCS_BUCKET_NAME")


def write_report(content: str) -> dict:
    """Write the final digest report to a markdown file.

    Writes to Google Cloud Storage when GCS_BUCKET_NAME is set,
    otherwise writes to the local output/ directory.

    Args:
        content: The full markdown content of the report to write.

    Returns a dict with the location and filename of the written file.
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_str}_infosec_digest.md"

    if _GCS_BUCKET:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(_GCS_BUCKET)
        blob = bucket.blob(filename)
        blob.upload_from_string(content, content_type="text/markdown")
        return {
            "filename": filename,
            "location": f"gs://{_GCS_BUCKET}/{filename}",
        }

    _OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = _OUTPUT_DIR / filename
    output_path.write_text(content, encoding="utf-8")
    return {
        "filename": filename,
        "location": str(output_path),
    }
