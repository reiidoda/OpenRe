"""OpenAI Responses adapter."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
import importlib
from pathlib import Path
from typing import Any

import yaml

from agent_workbench.adapters.local.config_loader import YamlAgentConfigLoader
from agent_workbench.adapters.local.loader_errors import LoaderValidationError
from agent_workbench.domain.entities.agent_config import AgentConfig
from agent_workbench.domain.entities.task import TaskSpec


@dataclass(slots=True)
class ResponsesAdapter:
    """Adapter that executes tasks through OpenAI Responses API."""

    client: Any | None = None
    config_loader: YamlAgentConfigLoader = field(default_factory=YamlAgentConfigLoader)
    tool_config_root: Path = Path("configs/tools")

    def __post_init__(self) -> None:
        if self.client is None:
            self.client = self._build_default_client()

    def run_task(self, task: TaskSpec, config_path: str) -> str:
        config = self.config_loader.load(config_path)
        if config.provider.lower() != "openai":
            raise LoaderValidationError(
                "Config validation failed: "
                f"OpenAI Responses adapter requires provider='openai', got '{config.provider}' "
                f"in '{config_path}'."
            )

        model_payload = self._load_model_payload(config=config, config_path=config_path)
        request_payload: dict[str, Any] = {
            "model": model_payload["model"],
            "input": task.instruction,
            "instructions": config.system_prompt,
            "metadata": {"task_id": task.task_id, "config_id": config.config_id},
        }
        request_payload.update(self._optional_request_fields(model_payload))

        tools = self._load_tool_payload(config.tools)
        if tools:
            request_payload["tools"] = tools

        client = self.client
        if client is None:  # pragma: no cover - defensive guard
            raise RuntimeError("OpenAI client is not initialized.")
        response = client.responses.create(**request_payload)
        return self._extract_output_text(response)

    def _load_model_payload(self, *, config: AgentConfig, config_path: str) -> dict[str, Any]:
        config_file = Path(config_path)
        model_path = Path(config.model_config)
        if not model_path.is_absolute():
            model_path = (config_file.parent / model_path).resolve()

        if not model_path.exists():
            # fallback to repo-relative path for existing configs
            alt_path = Path(config.model_config)
            if alt_path.exists():
                model_path = alt_path.resolve()
            else:
                raise LoaderValidationError(
                    "Config validation failed: "
                    f"model_config file does not exist '{config.model_config}' "
                    f"(resolved from '{config_path}')."
                )

        raw = self._read_yaml_mapping(model_path, "model_config")
        model = raw.get("model")
        if not isinstance(model, str) or not model.strip():
            raise LoaderValidationError(
                f"Config validation failed: field 'model' must be a non-empty string in '{model_path}'."
            )

        payload: dict[str, Any] = {"model": model.strip()}

        if "temperature" in raw:
            temperature = raw["temperature"]
            if not isinstance(temperature, (int, float)):
                raise LoaderValidationError(
                    f"Config validation failed: field 'temperature' must be numeric in '{model_path}'."
                )
            payload["temperature"] = float(temperature)

        if "max_output_tokens" in raw:
            max_output_tokens = raw["max_output_tokens"]
            if not isinstance(max_output_tokens, int) or max_output_tokens <= 0:
                raise LoaderValidationError(
                    "Config validation failed: "
                    f"field 'max_output_tokens' must be a positive integer in '{model_path}'."
                )
            payload["max_output_tokens"] = max_output_tokens

        if "reasoning_effort" in raw:
            reasoning_effort = raw["reasoning_effort"]
            if not isinstance(reasoning_effort, str) or not reasoning_effort.strip():
                raise LoaderValidationError(
                    "Config validation failed: "
                    f"field 'reasoning_effort' must be a non-empty string in '{model_path}'."
                )
            payload["reasoning"] = {"effort": reasoning_effort.strip()}

        return payload

    def _load_tool_payload(self, tool_ids: list[str]) -> list[dict[str, Any]]:
        tools: list[dict[str, Any]] = []
        for tool_id in tool_ids:
            path = self.tool_config_root / f"{tool_id}.yaml"
            if not path.exists():
                raise LoaderValidationError(
                    f"Config validation failed: tool config file not found for '{tool_id}' at '{path}'."
                )

            raw = self._read_yaml_mapping(path, "tool_config")
            description = raw.get("description")
            if not isinstance(description, str) or not description.strip():
                raise LoaderValidationError(
                    "Config validation failed: "
                    f"field 'description' must be a non-empty string in '{path}'."
                )

            tools.append(
                {
                    "type": "function",
                    "name": tool_id,
                    "description": description.strip(),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": True,
                    },
                }
            )
        return tools

    @staticmethod
    def _optional_request_fields(model_payload: dict[str, Any]) -> dict[str, Any]:
        optional: dict[str, Any] = {}
        for key in ("temperature", "max_output_tokens", "reasoning"):
            if key in model_payload:
                optional[key] = model_payload[key]
        return optional

    @staticmethod
    def _read_yaml_mapping(path: Path, source_type: str) -> dict[str, Any]:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise LoaderValidationError(
                f"Config validation failed: invalid YAML in {source_type} '{path}' ({exc})."
            ) from exc

        if not isinstance(raw, dict):
            raise LoaderValidationError(
                f"Config validation failed: expected mapping at root of {source_type} '{path}'."
            )
        return raw

    @staticmethod
    def _extract_output_text(response: Any) -> str:
        if isinstance(response, dict):
            output_text = response.get("output_text")
            if isinstance(output_text, str) and output_text.strip():
                return output_text.strip()

            output = response.get("output")
            extracted = ResponsesAdapter._extract_from_output_chunks(output)
            if extracted:
                return extracted
            raise ValueError("Responses API returned no text output in dictionary response.")

        output_text_attr = getattr(response, "output_text", None)
        if isinstance(output_text_attr, str) and output_text_attr.strip():
            return output_text_attr.strip()

        output_attr = getattr(response, "output", None)
        extracted = ResponsesAdapter._extract_from_output_chunks(output_attr)
        if extracted:
            return extracted

        raise ValueError("Responses API returned no text output.")

    @staticmethod
    def _extract_from_output_chunks(chunks: Any) -> str:
        if not isinstance(chunks, list):
            return ""

        parts: list[str] = []
        for chunk in chunks:
            if isinstance(chunk, dict):
                content = chunk.get("content")
            else:
                content = getattr(chunk, "content", None)
            if not isinstance(content, list):
                continue

            for item in content:
                if isinstance(item, dict):
                    text_value = item.get("text")
                else:
                    text_value = getattr(item, "text", None)
                if isinstance(text_value, str) and text_value.strip():
                    parts.append(text_value.strip())

        return "\n".join(parts).strip()

    @staticmethod
    def _build_default_client() -> Any:
        try:
            openai_module = importlib.import_module("openai")
        except ImportError as exc:  # pragma: no cover - exercised only without injected client
            raise RuntimeError(
                "OpenAI SDK is not installed. Install it with `pip install openai` "
                "or inject a client into ResponsesAdapter(client=...)."
            ) from exc
        openai_cls = getattr(openai_module, "OpenAI", None)
        if openai_cls is None:
            raise RuntimeError("OpenAI SDK is installed but does not expose OpenAI client class.")
        return openai_cls()
