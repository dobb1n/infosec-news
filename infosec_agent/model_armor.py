import os
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.genai import types

_PROJECT = "the-tinkering-shed"
_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "europe-west2")
_TEMPLATE_ID = os.environ.get("MODEL_ARMOR_TEMPLATE_ID")

_TEMPLATE_NAME = (
    f"projects/{_PROJECT}/locations/{_LOCATION}/templates/{_TEMPLATE_ID}"
    if _TEMPLATE_ID
    else None
)


def _make_client():
    from google.cloud import modelarmor_v1
    from google.api_core.client_options import ClientOptions
    return modelarmor_v1.ModelArmorClient(
        transport="rest",
        client_options=ClientOptions(
            api_endpoint=f"modelarmor.{_LOCATION}.rep.googleapis.com"
        ),
    )


_client = _make_client() if _TEMPLATE_NAME else None


def _is_blocked(filter_match_state) -> bool:
    # FilterMatchState 2 == MATCH_FOUND (blocked)
    return int(filter_match_state) == 2


def _blocked_response(reason: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part.from_text(f"Request blocked by security policy: {reason}")],
        )
    )


def before_model_callback(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Sanitise user prompt through Model Armor before it reaches the LLM."""
    if not _client:
        return None

    try:
        from google.cloud import modelarmor_v1
        text = ""
        if llm_request.messages:
            last = llm_request.messages[-1]
            if last.parts:
                text = last.parts[0].text or ""

        if not text:
            return None

        response = _client.sanitize_user_prompt(
            request=modelarmor_v1.SanitizeUserPromptRequest(
                name=_TEMPLATE_NAME,
                user_prompt_data=modelarmor_v1.DataItem(text=text),
            )
        )
        if _is_blocked(response.sanitization_result.filter_match_state):
            return _blocked_response("prompt injection detected")
    except Exception as e:
        print(f"[ModelArmor] input check error: {e}")

    return None


def after_model_callback(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Sanitise model response through Model Armor before it reaches the user."""
    if not _client:
        return None

    try:
        from google.cloud import modelarmor_v1
        text = ""
        if llm_response.content and llm_response.content.parts:
            text = llm_response.content.parts[0].text or ""

        if not text:
            return None

        response = _client.sanitize_model_response(
            request=modelarmor_v1.SanitizeModelResponseRequest(
                name=_TEMPLATE_NAME,
                model_response_data=modelarmor_v1.DataItem(text=text),
            )
        )
        if _is_blocked(response.sanitization_result.filter_match_state):
            return _blocked_response("response filtered")
    except Exception as e:
        print(f"[ModelArmor] output check error: {e}")

    return None
