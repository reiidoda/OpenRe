"""Agent config loader for local YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from agent_workbench.adapters.local.loader_errors import LoaderValidationError
from agent_workbench.domain.entities.agent_config import AgentBudget, AgentConfig


class YamlAgentConfigLoader:
    """Loads and validates agent configuration YAML into typed `AgentConfig`."""

    REQUIRED_FIELDS = (
        "id",
        "provider",
        "model_config",
        "system_prompt",
        "tools",
        "safety_policy_id",
        "budgets",
    )

    def load(self, config_path: str) -> AgentConfig:
        path = Path(config_path)

        if not path.exists():
            raise LoaderValidationError(
                f"Config validation failed: file does not exist '{path}'."
            )

        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise LoaderValidationError(
                f"Config validation failed: invalid YAML in '{path}' ({exc})."
            ) from exc

        if not isinstance(raw, dict):
            raise LoaderValidationError(
                f"Config validation failed: expected mapping at root of '{path}'."
            )

        for field in self.REQUIRED_FIELDS:
            if field not in raw:
                raise LoaderValidationError(
                    f"Config validation failed: missing required field '{field}' in '{path}'."
                )

        config_id = self._require_str(raw, "id", path)
        provider = self._require_str(raw, "provider", path)
        model_config = self._require_str(raw, "model_config", path)
        system_prompt = self._require_str(raw, "system_prompt", path)
        safety_policy_id = self._require_str(raw, "safety_policy_id", path)

        tools = raw.get("tools")
        if not isinstance(tools, list) or not tools or any(not isinstance(tool, str) for tool in tools):
            raise LoaderValidationError(
                f"Config validation failed: field 'tools' must be a non-empty list[str] in '{path}'."
            )

        budgets_raw = raw.get("budgets")
        if not isinstance(budgets_raw, dict):
            raise LoaderValidationError(
                f"Config validation failed: field 'budgets' must be an object in '{path}'."
            )

        max_steps = budgets_raw.get("max_steps")
        max_cost = budgets_raw.get("max_cost_usd")

        if not isinstance(max_steps, int) or max_steps <= 0:
            raise LoaderValidationError(
                f"Config validation failed: 'budgets.max_steps' must be a positive integer in '{path}'."
            )

        if not isinstance(max_cost, (int, float)) or float(max_cost) <= 0:
            raise LoaderValidationError(
                f"Config validation failed: 'budgets.max_cost_usd' must be a positive number in '{path}'."
            )

        return AgentConfig(
            config_id=config_id,
            provider=provider,
            model_config=model_config,
            system_prompt=system_prompt,
            tools=list(tools),
            safety_policy_id=safety_policy_id,
            budgets=AgentBudget(max_steps=max_steps, max_cost_usd=float(max_cost)),
        )

    @staticmethod
    def _require_str(payload: dict[str, Any], field: str, path: Path) -> str:
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            raise LoaderValidationError(
                f"Config validation failed: field '{field}' must be a non-empty string in '{path}'."
            )
        return value.strip()
