"""Regression gate orchestration for CI workflows."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Literal
from typing import Protocol

import yaml

from agent_workbench.orchestration.runner import Runner

ThresholdMode = Literal["max_drop", "max_increase"]


@dataclass(slots=True)
class MetricThreshold:
    mode: ThresholdMode
    value: float


@dataclass(slots=True)
class RegressionGateConfig:
    dataset: str
    baseline_config_id: str
    baseline_config_path: str
    candidate_config_id: str
    candidate_config_path: str
    thresholds: dict[str, MetricThreshold]


@dataclass(slots=True)
class MetricComparison:
    metric: str
    baseline: float
    candidate: float
    delta: float
    mode: ThresholdMode
    threshold: float
    violated: bool


@dataclass(slots=True)
class RegressionGateResult:
    run_id: str
    dataset: str
    baseline_config_id: str
    candidate_config_id: str
    baseline_metrics: dict[str, float] = field(default_factory=dict)
    candidate_metrics: dict[str, float] = field(default_factory=dict)
    comparisons: list[MetricComparison] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(comparison.violated for comparison in self.comparisons)

    @property
    def violations(self) -> list[str]:
        return [comparison.metric for comparison in self.comparisons if comparison.violated]


class RunnerLike(Protocol):
    def run(self, dataset: str, config_paths: list[str]) -> dict[str, object]:
        """Execute benchmark run and return summary payload."""


def _as_mapping(value: object, *, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping.")
    clean: dict[str, object] = {}
    for key, val in value.items():
        if isinstance(key, str):
            clean[key] = val
    return clean


def _parse_threshold(metric: str, raw: object) -> MetricThreshold:
    if isinstance(raw, (int, float)):
        value = float(raw)
        if value < 0:
            raise ValueError(f"threshold for '{metric}' must be >= 0.")
        return MetricThreshold(mode="max_drop", value=value)

    mapping = _as_mapping(raw, field_name=f"thresholds.{metric}")
    if "mode" in mapping or "value" in mapping:
        mode_raw = mapping.get("mode", "max_drop")
        if mode_raw == "max_drop":
            mode: ThresholdMode = "max_drop"
        elif mode_raw == "max_increase":
            mode = "max_increase"
        else:
            raise ValueError(f"thresholds.{metric}.mode must be 'max_drop' or 'max_increase'.")
        value_raw = mapping.get("value", 0.0)
        if not isinstance(value_raw, (int, float)):
            raise ValueError(f"thresholds.{metric}.value must be numeric.")
        value = float(value_raw)
        if value < 0:
            raise ValueError(f"thresholds.{metric}.value must be >= 0.")
        return MetricThreshold(mode=mode, value=value)

    if "max_drop" in mapping:
        max_drop_raw = mapping["max_drop"]
        if not isinstance(max_drop_raw, (int, float)):
            raise ValueError(f"thresholds.{metric}.max_drop must be numeric.")
        max_drop = float(max_drop_raw)
        if max_drop < 0:
            raise ValueError(f"thresholds.{metric}.max_drop must be >= 0.")
        return MetricThreshold(mode="max_drop", value=max_drop)

    if "max_increase" in mapping:
        max_increase_raw = mapping["max_increase"]
        if not isinstance(max_increase_raw, (int, float)):
            raise ValueError(f"thresholds.{metric}.max_increase must be numeric.")
        max_increase = float(max_increase_raw)
        if max_increase < 0:
            raise ValueError(f"thresholds.{metric}.max_increase must be >= 0.")
        return MetricThreshold(mode="max_increase", value=max_increase)

    raise ValueError(
        f"thresholds.{metric} must be numeric or include mode/value, max_drop, or max_increase."
    )


def load_regression_gate_config(path: Path) -> RegressionGateConfig:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    root = _as_mapping(loaded, field_name=str(path))

    dataset_raw = root.get("dataset")
    if not isinstance(dataset_raw, str) or not dataset_raw.strip():
        raise ValueError("dataset must be a non-empty string.")
    dataset = dataset_raw.strip()

    baseline = _as_mapping(root.get("baseline"), field_name="baseline")
    candidate = _as_mapping(root.get("candidate"), field_name="candidate")

    baseline_id_raw = baseline.get("id")
    baseline_path_raw = baseline.get("config_path")
    candidate_id_raw = candidate.get("id")
    candidate_path_raw = candidate.get("config_path")

    if not isinstance(baseline_id_raw, str) or not baseline_id_raw.strip():
        raise ValueError("baseline.id must be a non-empty string.")
    if not isinstance(baseline_path_raw, str) or not baseline_path_raw.strip():
        raise ValueError("baseline.config_path must be a non-empty string.")
    if not isinstance(candidate_id_raw, str) or not candidate_id_raw.strip():
        raise ValueError("candidate.id must be a non-empty string.")
    if not isinstance(candidate_path_raw, str) or not candidate_path_raw.strip():
        raise ValueError("candidate.config_path must be a non-empty string.")

    raw_thresholds = _as_mapping(root.get("thresholds"), field_name="thresholds")
    if not raw_thresholds:
        raise ValueError("thresholds must define at least one metric gate.")

    thresholds: dict[str, MetricThreshold] = {}
    for metric, raw_threshold in raw_thresholds.items():
        metric_name = metric.strip()
        if not metric_name:
            raise ValueError("threshold metric names must be non-empty.")
        thresholds[metric_name] = _parse_threshold(metric_name, raw_threshold)

    return RegressionGateConfig(
        dataset=dataset,
        baseline_config_id=baseline_id_raw.strip(),
        baseline_config_path=baseline_path_raw.strip(),
        candidate_config_id=candidate_id_raw.strip(),
        candidate_config_path=candidate_path_raw.strip(),
        thresholds=thresholds,
    )


def _as_summary_map(summary: object) -> dict[str, dict[str, object]]:
    if not isinstance(summary, dict):
        raise ValueError("Runner result summary is missing or invalid.")

    raw = summary.get("config_summaries")
    if not isinstance(raw, list):
        raise ValueError("summary.config_summaries is missing or invalid.")

    indexed: dict[str, dict[str, object]] = {}
    for item in raw:
        if not isinstance(item, dict):
            continue
        config_id = item.get("config_id")
        if isinstance(config_id, str) and config_id.strip():
            indexed[config_id.strip()] = item
    return indexed


def _coerce_metric(
    summary: dict[str, object],
    *,
    config_id: str,
    metric: str,
) -> float:
    value = summary.get(metric)
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(
        f"Metric '{metric}' missing or non-numeric in summary for config '{config_id}'."
    )


def _evaluate_metric(
    *,
    metric: str,
    baseline: float,
    candidate: float,
    threshold: MetricThreshold,
) -> MetricComparison:
    delta = candidate - baseline
    if threshold.mode == "max_drop":
        violated = delta < -threshold.value
    else:
        violated = delta > threshold.value
    return MetricComparison(
        metric=metric,
        baseline=baseline,
        candidate=candidate,
        delta=delta,
        mode=threshold.mode,
        threshold=threshold.value,
        violated=violated,
    )


def run_regression_gate(
    config: RegressionGateConfig,
    *,
    artifact_root: Path,
    runner: RunnerLike | None = None,
) -> RegressionGateResult:
    active_runner = runner or Runner(artifact_root=artifact_root)
    run_result = active_runner.run(
        dataset=config.dataset,
        config_paths=[
            config.baseline_config_path,
            config.candidate_config_path,
        ],
    )

    run_id = str(run_result.get("run_id", ""))
    summary_map = _as_summary_map(run_result.get("summary"))
    if config.baseline_config_id not in summary_map:
        raise ValueError(
            f"Baseline config id '{config.baseline_config_id}' not found in run summary."
        )
    if config.candidate_config_id not in summary_map:
        raise ValueError(
            f"Candidate config id '{config.candidate_config_id}' not found in run summary."
        )

    baseline_summary = summary_map[config.baseline_config_id]
    candidate_summary = summary_map[config.candidate_config_id]
    comparisons: list[MetricComparison] = []
    baseline_metrics: dict[str, float] = {}
    candidate_metrics: dict[str, float] = {}

    for metric, threshold in config.thresholds.items():
        baseline_value = _coerce_metric(
            baseline_summary,
            config_id=config.baseline_config_id,
            metric=metric,
        )
        candidate_value = _coerce_metric(
            candidate_summary,
            config_id=config.candidate_config_id,
            metric=metric,
        )
        baseline_metrics[metric] = baseline_value
        candidate_metrics[metric] = candidate_value
        comparisons.append(
            _evaluate_metric(
                metric=metric,
                baseline=baseline_value,
                candidate=candidate_value,
                threshold=threshold,
            )
        )

    return RegressionGateResult(
        run_id=run_id,
        dataset=config.dataset,
        baseline_config_id=config.baseline_config_id,
        candidate_config_id=config.candidate_config_id,
        baseline_metrics=baseline_metrics,
        candidate_metrics=candidate_metrics,
        comparisons=comparisons,
    )


def format_regression_gate_markdown(result: RegressionGateResult) -> str:
    lines = [
        "## Regression Gate",
        "",
        f"- Run ID: `{result.run_id}`",
        f"- Dataset: `{result.dataset}`",
        f"- Baseline: `{result.baseline_config_id}`",
        f"- Candidate: `{result.candidate_config_id}`",
        f"- Status: `{'passed' if result.passed else 'failed'}`",
        "",
        "| Metric | Baseline | Candidate | Delta | Rule | Status |",
        "|---|---:|---:|---:|---|---|",
    ]
    for comparison in result.comparisons:
        rule = (
            f"candidate >= baseline - {comparison.threshold:.4f}"
            if comparison.mode == "max_drop"
            else f"candidate <= baseline + {comparison.threshold:.4f}"
        )
        status = "PASS" if not comparison.violated else "FAIL"
        lines.append(
            "| "
            f"{comparison.metric} | "
            f"{comparison.baseline:.4f} | "
            f"{comparison.candidate:.4f} | "
            f"{comparison.delta:+.4f} | "
            f"{rule} | "
            f"{status} |"
        )
    return "\n".join(lines)


def regression_gate_payload(result: RegressionGateResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "dataset": result.dataset,
        "baseline_config_id": result.baseline_config_id,
        "candidate_config_id": result.candidate_config_id,
        "passed": result.passed,
        "violations": result.violations,
        "comparisons": [
            {
                "metric": comparison.metric,
                "baseline": round(comparison.baseline, 6),
                "candidate": round(comparison.candidate, 6),
                "delta": round(comparison.delta, 6),
                "mode": comparison.mode,
                "threshold": round(comparison.threshold, 6),
                "violated": comparison.violated,
            }
            for comparison in result.comparisons
        ],
    }
