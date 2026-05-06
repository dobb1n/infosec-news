import os
from datetime import datetime

import markdown
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from google.cloud import storage

app = FastAPI(title="Infosec News")

_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
_REPORT_SUFFIX = "_infosec_digest.md"


def _get_bucket() -> storage.Bucket:
    return storage.Client().bucket(_BUCKET_NAME)


def _list_reports() -> list[dict]:
    bucket = _get_bucket()
    blobs = sorted(
        [b for b in bucket.list_blobs() if b.name.endswith(_REPORT_SUFFIX)],
        key=lambda b: b.name,
        reverse=True,
    )
    reports = []
    for blob in blobs:
        date_str = blob.name.replace(_REPORT_SUFFIX, "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")
        except ValueError:
            date = date_str
        reports.append({"slug": date_str, "date": date, "filename": blob.name})
    return reports


_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1rem; color: #1a1a1a; }}
  a {{ color: #0066cc; }}
  nav {{ margin-bottom: 2rem; font-size: 0.9rem; }}
  h1 {{ border-bottom: 2px solid #e0e0e0; padding-bottom: 0.5rem; }}
  ul.index {{ list-style: none; padding: 0; }}
  ul.index li {{ padding: 0.5rem 0; border-bottom: 1px solid #f0f0f0; }}
  ul.index li a {{ text-decoration: none; font-size: 1.1rem; }}
  ul.index li a:hover {{ text-decoration: underline; }}
  .report img {{ max-width: 100%; }}
  code {{ background: #f5f5f5; padding: 0.1em 0.3em; border-radius: 3px; }}
  pre code {{ display: block; padding: 1rem; overflow-x: auto; }}
  hr {{ border: none; border-top: 1px solid #e0e0e0; }}
</style>
</head>
<body>
{body}
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    reports = _list_reports()
    if not reports:
        items = "<p>No reports yet.</p>"
    else:
        items = "<ul class='index'>" + "".join(
            f"<li><a href='/report/{r['slug']}'>{r['date']}</a></li>"
            for r in reports
        ) + "</ul>"
    body = f"<h1>Infosec Digest</h1>{items}"
    return _PAGE.format(title="Infosec Digest", body=body)


@app.get("/report/{slug}", response_class=HTMLResponse)
def report(slug: str):
    filename = f"{slug}{_REPORT_SUFFIX}"
    bucket = _get_bucket()
    blob = bucket.blob(filename)
    if not blob.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    content = blob.download_as_text()
    html = markdown.markdown(content, extensions=["tables", "fenced_code"])
    body = f"<nav><a href='/'>← All reports</a></nav><div class='report'>{html}</div>"
    try:
        date = datetime.strptime(slug, "%Y-%m-%d").strftime("%B %-d, %Y")
    except ValueError:
        date = slug
    return _PAGE.format(title=f"Infosec Digest — {date}", body=body)


@app.get("/healthz")
def healthz():
    return {"ok": True}
