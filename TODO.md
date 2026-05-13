# TODO

## Frontend

- [ ] **Personalised digest view** — on load, show only stories published since the user's last visit (store last-visited timestamp in `localStorage`). Include a "Show all" button to reveal older reports without reloading.

- [ ] **Per-story escalation** — add an "Escalate" button next to each story. Clicking it generates and downloads a pre-formatted markdown file suitable for use in internal workflows (incident tracking, Slack posts, etc). File should include story title, link, date, summary, and a placeholder section for analyst notes.

- [ ] **Escalation candidate algorithm** — build a scoring/classification algorithm that identifies stories likely to warrant escalation. Signals to consider: keyword severity weighting, CVE mentions, named vendors/products in the keyword list, CVSS scores if present in the summary, recency. Surface candidates visually in the UI (e.g. highlighted or badged).

## Infrastructure

- [ ] Set up Artifact Registry repo, service accounts, and IAM bindings for Cloud Run deploy (see README setup notes).

- [ ] investigate using the global model endpoint - as its in europe-west2 now, very limited options https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/locations#europe