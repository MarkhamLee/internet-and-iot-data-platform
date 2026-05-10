import json
from time import perf_counter
from typing import Type

import requests
from pydantic import BaseModel, ValidationError
from requests.exceptions import RequestException

from logging_util import console_logging

logger = console_logging("Qwen client")


class QwenClient:
    def __init__(
        self,
        ollama_url: str,
        model: str,
        timeout: tuple[int, int] = (10, 180),
        temperature: float = 0.1,
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.temperature = temperature

    def generate_structured_response(
        self,
        prompt: str,
        payload: dict,
        response_model: Type[BaseModel],
    ) -> BaseModel:
        full_url = f"{self.ollama_url}/api/generate"

        request_body = {
            "model": self.model,
            "prompt": f"{prompt}\n\nPayload:\n{json.dumps(payload, indent=2)}",
            "stream": False,
            "format": response_model.model_json_schema(),
            "options": {
                "temperature": self.temperature
            }
        }

        start = perf_counter()

        try:
            response = requests.post(
                full_url,
                json=request_body,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except RequestException as exc:
            raise RuntimeError(f"Qwen request failed for model {self.model}: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Ollama returned invalid JSON. status={response.status_code}, "
                f"body={response.text[:500]}"
            ) from exc

        if "response" not in data:
            raise RuntimeError(
                f"Ollama response missing 'response' field: {json.dumps(data)[:500]}"
            )

        try:
            validated = response_model.model_validate_json(data["response"])
        except ValidationError as exc:
            raise RuntimeError(
                f"Model output failed Pydantic validation: {exc}"
            ) from exc
        except ValueError as exc:
            raise RuntimeError(
                f"Model returned invalid JSON in response field: {str(data['response'])[:500]}"
            ) from exc

        duration = round(perf_counter() - start, 2)
        logger.info(
            "Qwen query completed in %s seconds; model=%s; prompt_eval_count=%s; eval_count=%s; done=%s; done_reason=%s",
            duration,
            self.model,
            data.get("prompt_eval_count"),
            data.get("eval_count"),
            data.get("done"),
            data.get("done_reason"),
        )

        return validated
