from __future__ import annotations

from pathlib import Path

import pytest

from agent_workbench.adapters.local.loader_errors import LoaderValidationError
from agent_workbench.adapters.openai.responses_adapter import ResponsesAdapter
from agent_workbench.domain.entities.task import TaskModality, TaskSpec
from agent_workbench.domain.value_objects.risk_level import RiskLevel


class _FakeResponses:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> dict[str, object]:
        self.calls.append(kwargs)
        return self.response


class _FakeClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.responses = _FakeResponses(response)


def _task() -> TaskSpec:
    return TaskSpec(
        task_id="ra_test",
        instruction="Summarize this file.",
        modality=TaskModality.TEXT,
        risk_profile=RiskLevel.LOW,
    )


def test_responses_adapter_uses_model_and_tools_from_config() -> None:
    fake_client = _FakeClient({"output_text": "Done."})
    adapter = ResponsesAdapter(client=fake_client)

    output = adapter.run_task(_task(), "configs/agents/research_basic.yaml")

    assert output == "Done."
    assert len(fake_client.responses.calls) == 1

    call = fake_client.responses.calls[0]
    assert call["model"] == "gpt-5"
    assert call["temperature"] == 0.2
    assert call["max_output_tokens"] == 2500
    assert call["reasoning"] == {"effort": "medium"}
    assert call["instructions"].startswith("You are a research assistant")
    assert call["input"] == "Summarize this file."

    tools = call["tools"]
    assert isinstance(tools, list)
    tool_names = [tool["name"] for tool in tools if isinstance(tool, dict)]
    assert tool_names == ["file_search", "web_search"]


def test_responses_adapter_supports_output_chunk_fallback() -> None:
    fake_client = _FakeClient(
        {
            "output": [
                {
                    "content": [
                        {"type": "output_text", "text": "Alpha"},
                        {"type": "output_text", "text": "Beta"},
                    ]
                }
            ]
        }
    )
    adapter = ResponsesAdapter(client=fake_client)

    output = adapter.run_task(_task(), "configs/agents/research_basic.yaml")

    assert output == "Alpha\nBeta"


def test_responses_adapter_rejects_non_openai_provider(tmp_path: Path) -> None:
    config = tmp_path / "bad_provider.yaml"
    config.write_text(
        """
id: bad
provider: local
model_config: configs/models/openai_gpt5.yaml
system_prompt: test
tools: [file_search]
safety_policy_id: low_risk
budgets:
  max_steps: 1
  max_cost_usd: 1.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    fake_client = _FakeClient({"output_text": "x"})
    adapter = ResponsesAdapter(client=fake_client)

    with pytest.raises(LoaderValidationError, match="requires provider='openai'"):
        adapter.run_task(_task(), str(config))
