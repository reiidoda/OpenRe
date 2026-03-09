from __future__ import annotations

from pathlib import Path

import pytest

from agent_workbench.adapters.local.config_loader import YamlAgentConfigLoader
from agent_workbench.adapters.local.loader_errors import LoaderValidationError


def test_config_loader_returns_typed_config() -> None:
    loader = YamlAgentConfigLoader()

    config = loader.load("configs/agents/research_basic.yaml")

    assert config.config_id == "research_basic"
    assert config.provider == "openai"
    assert config.budgets is not None
    assert config.budgets.max_steps > 0
    assert config.tools == ["file_search", "web_search"]


def test_config_loader_rejects_missing_required_field(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text(
        """
id: test
provider: openai
model_config: configs/models/openai_gpt5.yaml
system_prompt: hello
tools: [file_search]
budgets:
  max_steps: 1
  max_cost_usd: 1.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    loader = YamlAgentConfigLoader()
    with pytest.raises(LoaderValidationError, match="missing required field 'safety_policy_id'"):
        loader.load(str(path))


def test_config_loader_rejects_invalid_budget(tmp_path: Path) -> None:
    path = tmp_path / "bad_budget.yaml"
    path.write_text(
        """
id: test
provider: openai
model_config: configs/models/openai_gpt5.yaml
system_prompt: hello
tools: [file_search]
safety_policy_id: medium_risk
budgets:
  max_steps: 0
  max_cost_usd: 1.0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    loader = YamlAgentConfigLoader()
    with pytest.raises(LoaderValidationError, match="budgets.max_steps"):
        loader.load(str(path))
