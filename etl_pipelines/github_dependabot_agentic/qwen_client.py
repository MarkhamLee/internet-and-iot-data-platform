import json
import requests
from pydantic import BaseModel, ValidationError
from requests.exceptions import RequestException
from time import perf_counter
from typing import Type
from logging_util import console_logging


logger = console_logging("Qwen client")


class QwenClient:
    def __init__(
        self,
        ollama_url: str,
        model: str,
        approved_models: set[str],
        timeout: tuple[int, int] | int = (10, 180),
        temperature: float = 0
    ):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model
        self.model_list = approved_models

        if isinstance(timeout, (int, float)):
            self.timeout = (timeout, timeout)
        else:
            self.timeout = timeout

        self.temperature = temperature

        logger.info("Validating Ollama server connection and retrieving model list")
        response = self.verify_ollama_server(
            f"{self.ollama_url}/api/tags",
            self.timeout,
        )

        self.available_models = self.get_model_list(response, self.model_list)
        logger.info(f"The available approved models are: {self.available_models}")

        if self.model not in self.available_models:
            raise RuntimeError(
                f"Configured model '{self.model}' is not available. "
                f"Available approved models: {self.available_models}"
            )

    def verify_ollama_server(self, url: str, timeout):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except RequestException as exc:
            raise RuntimeError(f"Ollama URL is not available: {exc}") from exc

    def get_model_list(self, response, model_list):
        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError("Ollama returned invalid JSON") from exc

        approved_available = [
            model["name"]
            for model in data.get("models", [])
            if model.get("name") in model_list
        ]

        if not approved_available:
            raise RuntimeError("No approved models available")

        return approved_available

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
            "think": False,
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
            raise RuntimeError(
                f"Qwen request failed for model {self.model}: {exc}"
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Ollama returned invalid JSON. "
                f"status={response.status_code}, body={response.text[:500]}"
            ) from exc

        if "response" not in data:
            raise RuntimeError(
                f"Ollama response missing 'response' field: {json.dumps(data)[:500]}"
            )

        response_text = data.get("response", "")

        if not isinstance(response_text, str) or not response_text.strip():
            raise RuntimeError(
                "Ollama returned an empty response field. "
                f"done={data.get('done')}, done_reason={data.get('done_reason')}, "
                f"prompt_eval_count={data.get('prompt_eval_count')}, "
                f"eval_count={data.get('eval_count')}, "
                f"full_response={json.dumps(data)[:1000]}"
            )

        try:
            validated = response_model.model_validate_json(response_text)
        except ValidationError as exc:
            raise RuntimeError(
                f"Model output failed Pydantic validation: {exc}"
            ) from exc
        except ValueError as exc:
            raise RuntimeError(
                f"Model returned invalid JSON in response field: {response_text[:500]}"
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
