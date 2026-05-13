from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, load_memory
from .tools import load_keywords, fetch_register_news, fetch_sans_isc_notes, write_report
from .model_armor import before_model_callback, after_model_callback

_PROMPT_PATH = Path(__file__).parent / "config" / "prompt.md"
_instruction = _PROMPT_PATH.read_text()

root_agent = Agent(
    name="infosec_news_agent",
    model="gemini-flash-latest",
    location="global",
    description="Curates infosec news from The Register and SANS ISC, then writes a digest report.",
    instruction=_instruction,
    tools=[
        load_memory,
        FunctionTool(load_keywords),
        FunctionTool(fetch_register_news),
        FunctionTool(fetch_sans_isc_notes),
        FunctionTool(write_report),
    ],
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
