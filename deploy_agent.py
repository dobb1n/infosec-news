"""
Deploys or updates the agent on Vertex AI Agent Engine.

- First run (no AGENT_ENGINE_ID set): creates a new engine and prints the ID.
  Add that ID as a GitHub secret so subsequent runs update in place.
- Subsequent runs: updates the existing engine with the latest code.
"""

import os
import vertexai
from vertexai.preview import reasoning_engines
from infosec_agent.agent import root_agent

_PROJECT = "the-tinkering-shed"
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "europe-west2")
_STAGING_BUCKET = f"gs://{os.environ['GCS_BUCKET_NAME']}"
_AGENT_ENGINE_ID = os.environ.get("AGENT_ENGINE_ID")

_REQUIREMENTS = [
    "google-adk>=1.0.0",
    "feedparser>=6.0.0",
    "pyyaml>=6.0.0",
    "google-cloud-storage>=2.0.0",
    "python-dotenv>=1.0.0",
]

vertexai.init(project=_PROJECT, location=_LOCATION, staging_bucket=_STAGING_BUCKET)

app = reasoning_engines.AdkApp(agent=root_agent, enable_tracing=False)

# extra_packages ships the local infosec_agent module and config dir
# to Vertex AI so they can be imported at runtime
_KWARGS = dict(
    reasoning_engine=app,
    requirements=_REQUIREMENTS,
    extra_packages=["./infosec_agent", "./config"],
)

if _AGENT_ENGINE_ID:
    print(f"Updating existing engine {_AGENT_ENGINE_ID}...")
    engine = reasoning_engines.ReasoningEngine(
        f"projects/{_PROJECT}/locations/{_LOCATION}/reasoningEngines/{_AGENT_ENGINE_ID}"
    )
    engine.update(**_KWARGS)
else:
    print("No AGENT_ENGINE_ID set — creating new engine...")
    engine = reasoning_engines.ReasoningEngine.create(
        display_name="infosec-news-agent",
        **_KWARGS,
    )
    print(f"\nEngine created: {engine.resource_name}")
    print(f"Add this as a GitHub secret:")
    print(f"  AGENT_ENGINE_ID={engine.resource_name.split('/')[-1]}")

print("Done.")
