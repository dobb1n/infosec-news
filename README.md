# infosec-news

An AI agent that fetches infosec news from [The Register](https://www.theregister.com) and the [SANS Internet Storm Center podcast](https://isc.sans.edu/podcast.html), filters stories against a keyword list you control, and writes a dated markdown digest.

Built with [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs) and deployed to [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/reasoning-engine/overview).

---

## How it works

Each time the agent runs it follows these steps:

1. **Recall** — checks memory for stories already covered in previous runs to avoid repetition
2. **Load keywords** — reads `config/keywords.yaml` to know what topics you care about
3. **Fetch The Register** — pulls the latest stories from the Atom feed and filters by keyword
4. **Fetch SANS ISC** — pulls the latest podcast episode notes from the RSS feed
5. **Write digest** — composes a markdown report with an executive summary and saves it
6. **Save to memory** — archives the session so future runs know what was already covered

### Output

- **Locally** — written to `output/YYYY-MM-DD_infosec_digest.md`
- **In production** — uploaded to `gs://YOUR_BUCKET/YYYY-MM-DD_infosec_digest.md`

---

## Project structure

```
infosec-news/
├── infosec_agent/
│   ├── agent.py              # Agent definition and instructions
│   └── tools/
│       ├── keywords.py       # Loads config/keywords.yaml
│       ├── register.py       # Fetches The Register Atom feed
│       ├── sans_isc.py       # Fetches SANS ISC podcast RSS feed
│       └── report.py         # Writes the digest (local or GCS)
├── infosec_agent/
│   └── config/
│       └── keywords.yaml     # ← edit this to change what you track
├── runner.py                 # Local runner with Vertex AI memory support
├── deploy_agent.py           # CI deployment script (create or update engine)
├── requirements.txt
└── .env.example
```

---

## Configuring your keywords

Edit `infosec_agent/config/keywords.yaml` — add or remove topics at any time:

```yaml
keywords:
  - ransomware
  - zero-day
  - CVE
  - data breach
```

No code changes needed. The agent reads this file on every run.

---

## Running locally

### Quick start (no GCP required)

```bash
git clone https://github.com/dobb1n/infosec-news.git
cd infosec-news
pip install -r requirements.txt
cp .env.example .env          # add your GOOGLE_API_KEY
adk web                       # opens a browser UI at localhost:8000
```

### With persistent memory

Set the Vertex AI variables in `.env` (see `.env.example`) then:

```bash
python runner.py
```

`runner.py` automatically detects whether Vertex AI env vars are present:
- **Set** → uses `VertexAiSessionService` + `VertexAiMemoryBankService` (persistent across runs)
- **Not set** → falls back to in-memory services (no persistence, no GCP needed)

---

## Deploying to Vertex AI Agent Engine

Deployment is handled automatically by GitHub Actions on every push to `main`.

### One-time GCP setup

```bash
# Enable required APIs
gcloud services enable \
  aiplatform.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com

# Create a GCS bucket (used for staging and report output)
gsutil mb -l europe-west2 gs://YOUR_BUCKET_NAME

# Store your Gemini API key in Secret Manager
echo -n "YOUR_GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=-

# Create a service account for GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions deployer"

SA=github-actions@YOUR_PROJECT.iam.gserviceaccount.com

for ROLE in \
  roles/aiplatform.admin \
  roles/secretmanager.secretAccessor \
  roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding YOUR_PROJECT \
    --member="serviceAccount:$SA" \
    --role="$ROLE" \
    --condition=None
done

# Grant the SA access to the staging bucket
gsutil iam ch serviceAccount:$SA:admin gs://YOUR_BUCKET_NAME

# Download the SA key to add as a GitHub secret
gcloud iam service-accounts keys create key.json --iam-account=$SA
```

Grant the Cloud Run compute identity access to Vertex AI, GCS, and Secret Manager:

```bash
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT --format='value(projectNumber)')
COMPUTE_SA=$PROJECT_NUMBER-compute@developer.gserviceaccount.com

for ROLE in \
  roles/aiplatform.user \
  roles/storage.objectCreator \
  roles/secretmanager.secretAccessor; do
  gcloud projects add-iam-policy-binding YOUR_PROJECT \
    --member="serviceAccount:$COMPUTE_SA" \
    --role="$ROLE" \
    --condition=None
done
```

### GitHub secrets

Add these in your repo under **Settings → Secrets and variables → Actions**:

| Secret | Value |
|---|---|
| `GCP_PROJECT_ID` | your GCP project ID |
| `GCP_SA_KEY` | full contents of `key.json` (then delete the file) |
| `GCP_REGION` | `europe-west2` |
| `GCS_BUCKET_NAME` | your bucket name |
| `AGENT_ENGINE_ID` | leave blank on first deploy, add after (see below) |

### First deploy

Push to `main`. Because `AGENT_ENGINE_ID` is not yet set, the workflow will create a new Agent Engine and print its ID in the Actions logs:

```
AGENT_ENGINE_ID=1234567890
```

Add that number as the `AGENT_ENGINE_ID` GitHub secret. All subsequent pushes will update the existing engine in place.

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Yes | Gemini API key |
| `GOOGLE_CLOUD_PROJECT` | Production only | GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | Production only | GCP region (e.g. `europe-west2`) |
| `AGENT_ENGINE_ID` | Production only | Vertex AI Reasoning Engine ID (for memory) |
| `GCS_BUCKET_NAME` | Production only | GCS bucket for report output |
| `AGENT_USER_ID` | No | Scopes memory per user (default: `default-user`) |
