from __future__ import annotations

from pathlib import Path

import pytest

from agent_workbench.evals.regression_gate import (
    MetricThreshold,
    RegressionGateConfig,
    format_regression_gate_markdown,
    load_regression_gate_config,
    regression_gate_payload,
    run_regression_gate,
)


class _StubRunner:
    def __init__(self, result: dict[str, object]) -> None:
        self._result = result
        self.calls: list[tuple[str, list[str]]] = []

    def run(self, dataset: str, config_paths: list[str]) -> dict[str, object]:
        self.calls.append((dataset, config_paths))
        return self._result


def test_load_regression_gate_config_supports_mode_value_schema(tmp_path: Path) -> None:
    config_path = tmp_path / "regression_gate.yaml"
    config_path.write_text(
        "\n".join(
            [
                "dataset: datasets/research_assistant_v1",
                "baseline:",
                "  id: research_basic",
                "  config_path: configs/agents/research_basic.yaml",
                "candidate:",
                "  id: research_multimodal",
                "  config_path: configs/agents/research_multimodal.yaml",
                "thresholds:",
                "  avg_score:",
                "    mode: max_drop",
                "    value: 0.02",
                "  avg_latency_ms:",
                "    mode: max_increase",
                "    value: 10.0",
            ]
        ),
        encoding="utf-8",
    )

    config = load_regression_gate_config(config_path)

    assert config.dataset == "datasets/research_assistant_v1"
    assert config.baseline_config_id == "research_basic"
    assert config.candidate_config_id == "research_multimodal"
    assert config.thresholds["avg_score"].mode == "max_drop"
    assert config.thresholds["avg_score"].value == 0.02
    assert config.thresholds["avg_latency_ms"].mode == "max_increase"
    assert config.thresholds["avg_latency_ms"].value == 10.0


def test_run_regression_gate_computes_deltas_and_detects_violations() -> None:
    config = RegressionGateConfig(
        dataset="datasets/research_assistant_v1",
        baseline_config_id="research_basic",
        baseline_config_path="configs/agents/research_basic.yaml",
        candidate_config_id="research_multimodal",
        candidate_config_path="configs/agents/research_multimodal.yaml",
        thresholds={
            "avg_score": MetricThreshold(mode="max_drop", value=0.02),
            "avg_latency_ms": MetricThreshold(mode="max_increase", value=25.0),
        },
    )
    runner = _StubRunner(
        {
            "run_id": "run_123",
            "summary": {
                "config_summaries": [
                    {
                        "config_id": "research_basic",
                        "avg_score": 0.9,
                        "avg_latency_ms": 100.0,
                    },
                    {
                        "config_id": "research_multimodal",
                        "avg_score": 0.86,
                        "avg_latency_ms": 120.0,
                    },
                ]
            },
        }
    )

    result = run_regression_gate(config, artifact_root=Path(".artifacts"), runner=runner)

    assert runner.calls == [
        (
            "datasets/research_assistant_v1",
            [
                "configs/agents/research_basic.yaml",
                "configs/agents/research_multimodal.yaml",
            ],
        )
    ]
    assert result.run_id == "run_123"
    assert result.passed is False
    assert result.violations == ["avg_score"]
    avg_score = next(c for c in result.comparisons if c.metric == "avg_score")
    assert avg_score.delta == pytest.approx(-0.04)
    assert avg_score.violated is True
    latency = next(c for c in result.comparisons if c.metric == "avg_latency_ms")
    assert latency.delta == 20.0
    assert latency.violated is False

    markdown = format_regression_gate_markdown(result)
    assert "Baseline: `research_basic`" in markdown
    assert "Candidate: `research_multimodal`" in markdown
    assert "| avg_score | 0.9000 | 0.8600 | -0.0400 |" in markdown
    assert "| avg_latency_ms | 100.0000 | 120.0000 | +20.0000 |" in markdown

    payload = regression_gate_payload(result)
    assert payload["passed"] is False
    assert payload["violations"] == ["avg_score"]
