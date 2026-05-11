import sys
from qwen_client import QwenClient
from schemas import SimpleQuestionResponse

PROMPT = (
    "Answer the question using the provided JSON schema only. "
    "Do not include reasoning. "
    "Return only valid JSON for the schema."
)
PAYLOAD = {"question": "What is GitHub Dependabot?"}

APPROVED_MODELS = {"qwen3.5:9b", "llama3.2:3b"}

client = QwenClient(
    ollama_url="https://ollama.local.markhamslab.com",
    model="qwen3.5:9b",
    approved_models=APPROVED_MODELS
)

result = client.generate_structured_response(
    prompt=PROMPT,
    payload=PAYLOAD,
    response_model=SimpleQuestionResponse,
)

print(result.model_dump())