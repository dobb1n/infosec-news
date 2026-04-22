"""
Custom runner that wires up session and memory services.

Usage:
    python runner.py

Local mode (default when Vertex AI env vars are absent):
    Uses InMemorySessionService and InMemoryMemoryService.
    Memory is lost when the process exits.

Production mode (when GOOGLE_CLOUD_PROJECT and AGENT_ENGINE_ID are set):
    Uses VertexAiSessionService and VertexAiMemoryBankService.
    Memory persists across runs.

    Prerequisites:
    1. Create a Vertex AI Agent Engine resource and note its ID.
       See: https://cloud.google.com/vertex-ai/docs/reasoning-engine/overview
    2. Set the environment variables in .env (copy from .env.example).
    3. Authenticate: gcloud auth application-default login
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.memory import InMemoryMemoryService, VertexAiMemoryBankService
from google.adk.sessions import InMemorySessionService, VertexAiSessionService
from google.genai import types as genai_types
from infosec_agent.agent import root_agent

load_dotenv()

_APP_NAME = "infosec_news_agent"
_USER_ID = os.environ.get("AGENT_USER_ID", "default-user")
_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT")
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
_AGENT_ENGINE_ID = os.environ.get("AGENT_ENGINE_ID")

_USE_VERTEX = bool(_PROJECT and _AGENT_ENGINE_ID)


def build_runner() -> Runner:
    if _USE_VERTEX:
        print(f"Using Vertex AI services (project={_PROJECT}, engine={_AGENT_ENGINE_ID})")
        session_service = VertexAiSessionService(project=_PROJECT, location=_LOCATION)
        memory_service = VertexAiMemoryBankService(
            project=_PROJECT,
            location=_LOCATION,
            agent_engine_id=_AGENT_ENGINE_ID,
        )
    else:
        print("Vertex AI env vars not set — running in local mode (in-memory, no persistence)")
        session_service = InMemorySessionService()
        memory_service = InMemoryMemoryService()

    return Runner(
        app_name=_APP_NAME,
        agent=root_agent,
        session_service=session_service,
        memory_service=memory_service,
    )


async def run() -> None:
    runner = build_runner()

    session = await runner.session_service.create_session(
        app_name=_APP_NAME, user_id=_USER_ID
    )

    print("Running infosec news agent...\n")
    async for event in runner.run_async(
        user_id=_USER_ID,
        session_id=session.id,
        new_message=genai_types.Content(
            role="user",
            parts=[genai_types.Part(text="Fetch and summarise today's infosec news.")],
        ),
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text)

    # Archive the session to memory so the agent can recall it next run
    await runner.memory_service.add_session_to_memory(session)


if __name__ == "__main__":
    asyncio.run(run())
