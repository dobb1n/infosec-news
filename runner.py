"""
Custom runner that wires up Vertex AI session and memory services.

Usage:
    python runner.py

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
from google.adk.memory import VertexAiMemoryBankService
from google.adk.sessions import VertexAiSessionService
from google.genai import types as genai_types
from infosec_agent.agent import root_agent

load_dotenv()

_PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
_AGENT_ENGINE_ID = os.environ["AGENT_ENGINE_ID"]
_APP_NAME = "infosec_news_agent"
_USER_ID = os.environ.get("AGENT_USER_ID", "default-user")


def build_runner() -> Runner:
    session_service = VertexAiSessionService(project=_PROJECT, location=_LOCATION)
    memory_service = VertexAiMemoryBankService(
        project=_PROJECT,
        location=_LOCATION,
        agent_engine_id=_AGENT_ENGINE_ID,
    )
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
