from agent_workbench.evals.graders.exact_match import ExactMatchGrader
from agent_workbench.evals.graders.rubric_grade import RubricGrader
from agent_workbench.evals.graders.trace_grade import TraceGrader
from agent_workbench.evals.harness import EvalHarness, TaskRunEvaluation


def _expected_payload(output: str) -> dict[str, object]:
    return {
        "target": output,
        "rubric": {
            "criteria": [
                {"name": "correctness", "required_terms": ["alpha"], "mode": "all"},
                {"name": "completeness", "required_terms": ["beta"], "mode": "all"},
            ]
        },
        "trace_events": ["prompt_sent", "completed"],
        "trace": {"required_sequence": ["prompt_sent", "completed"], "requires_approval": False},
    }


def test_harness_executes_configured_evaluators_per_task_run() -> None:
    harness = EvalHarness(
        evaluators=[
            ExactMatchGrader(),
            RubricGrader(),
            TraceGrader(),
        ]
    )
    output = "task ra_001 alpha beta completed"
    task_eval = harness.evaluate_task_run(
        task_id="ra_001",
        config_id="research_basic",
        output=output,
        expected=_expected_payload(output),
    )

    assert task_eval.task_id == "ra_001"
    assert task_eval.config_id == "research_basic"
    assert task_eval.evaluator_scores["exact_match"] == 1.0
    assert task_eval.evaluator_scores["rubric"] == 1.0
    assert task_eval.evaluator_scores["trace_quality"] == 1.0
    assert task_eval.score == 1.0
    assert task_eval.failure_labels == []


def test_harness_aggregate_includes_success_rate_and_placeholders() -> None:
    task_evaluations = [
        TaskRunEvaluation(
            task_id="ra_001",
            config_id="cfg",
            score=1.0,
            output_quality_score=1.0,
            trace_quality_score=1.0,
            latency_ms=0.0,
            cost_usd=0.0,
            failure_labels=[],
        ),
        TaskRunEvaluation(
            task_id="ra_002",
            config_id="cfg",
            score=0.8,
            output_quality_score=1.0,
            trace_quality_score=0.0,
            latency_ms=0.0,
            cost_usd=0.0,
            failure_labels=["sequence_violation"],
        ),
    ]
    metrics = EvalHarness.aggregate_metrics(task_evaluations)

    assert metrics.task_runs == 2
    assert metrics.success_rate == 0.5
    assert metrics.avg_score == 0.9
    assert metrics.avg_latency_ms == 0.0
    assert metrics.avg_cost_usd == 0.0
