from collections.abc import Sequence

from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai.types.shared_params import ResponseFormatJSONSchema
from pydantic import BaseModel, ValidationError

from src.config import settings

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
MAX_ATTEMPTS = 3
_client: OpenAI | None = None


def load_client() -> OpenAI:
    """Load the OpenAI client with the API key from the environment."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.open_router_api_key, base_url=OPENROUTER_BASE_URL
        )
    return _client


# T defines an object that heridate from BaseModel so the return type follows the schema passed in.
# messages is a Sequence to comply with the type hint.
def request_structured[T: BaseModel](
    messages: Sequence[ChatCompletionMessageParam], schema: type[T]
) -> tuple[T, int, int]:
    """Call the LLM with a schema-constrained response, retrying on validation errors.

    Retries feed the validation error back as a user turn so the model can correct
    itself. ``messages`` is copied, so those correction turns do not leak into the
    caller's list.

    Args:
        messages: Conversation to send, typically a system and a user turn.
        schema: Pydantic model the response must conform to.

    Returns:
        The parsed instance and the accumulated (input_tokens, output_tokens)
        across attempts.
    """
    client = load_client()
    conversation = list(messages)
    response_format: ResponseFormatJSONSchema = {
        "type": "json_schema",
        "json_schema": {
            "name": schema.__name__,
            "schema": schema.model_json_schema(),
        },
    }
    total_input_tokens = 0
    total_output_tokens = 0

    for attempt in range(MAX_ATTEMPTS):
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=conversation,
            response_format=response_format,
        )
        if response.usage:
            total_input_tokens += response.usage.prompt_tokens
            total_output_tokens += response.usage.completion_tokens

        raw_content = response.choices[0].message.content
        if raw_content is None:
            raise ValueError("LLM response content was empty")
        try:
            return (
                schema.model_validate_json(raw_content),
                total_input_tokens,
                total_output_tokens,
            )
        except ValidationError as exc:
            if attempt == MAX_ATTEMPTS - 1:
                raise
            conversation.append({"role": "assistant", "content": raw_content})
            conversation.append(
                {
                    "role": "user",
                    "content": f"Your response did not match the required schema: {exc}. Please resend a corrected JSON object.",
                }
            )

    raise AssertionError("unreachable: loop always returns or raises")
