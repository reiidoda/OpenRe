from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.orchestration.runner import Runner


@dataclass(slots=True)
class FixedLowTraceGrader:
    name: str = "trace_grade"

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        _ = (output, expected)
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="trace_quality",
            score=0.0,
            rationale="forced low trace quality",
            labels=["failure:sequence_violation"],
        )


def test_trace_quality_contributes_to_overall_score(tmp_path: Path) -> None:
    runner = Runner(
        artifact_root=tmp_path / "artifacts",
        trace_grader=FixedLowTraceGrader(),
    )
    result = runner.run(
        dataset="datasets/research_assistant_v1",
        config_paths=["configs/agents/research_basic.yaml"],
    )

    first_row = result["result_table"][0]
    assert first_row["output_quality_score"] == 1.0
    assert first_row["trace_quality_score"] == 0.0
    assert first_row["score"] == 0.8
    assert first_row["failure_labels"] == ["sequence_violation"]
