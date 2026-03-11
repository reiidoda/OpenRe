from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.evals.graders.trace_grade import TraceGrader


def test_trace_grader_valid_required_sequence() -> None:
    grader = TraceGrader()
    result = grader.evaluate(
        "prompt_sent,tool_called,tool_result,completed",
        {
            "trace": {
                "required_sequence": ["prompt_sent", "completed"],
                "requires_approval": False,
                "max_tool_calls": 2,
            }
        },
    )
    assert isinstance(result, EvaluationResult)
    assert result.score == 1.0
    assert result.labels == ["trace:pass"]


def test_trace_grader_missing_completion_labels_failure() -> None:
    grader = TraceGrader()
    result = grader.evaluate(
        "prompt_sent,tool_called",
        {"trace": {"required_sequence": ["prompt_sent", "completed"]}},
    )
    assert result.score < 1.0
    assert "failure:missing_completion" in result.labels
    assert "failure:sequence_violation" in result.labels


def test_trace_grader_approval_required_missing_labels_failure() -> None:
    grader = TraceGrader()
    result = grader.evaluate(
        "prompt_sent,completed",
        {
            "trace": {
                "required_sequence": ["prompt_sent", "completed"],
                "requires_approval": True,
            }
        },
    )
    assert result.score < 1.0
    assert "failure:approval_missing" in result.labels


def test_trace_grader_tool_efficiency_boundary() -> None:
    grader = TraceGrader()
    result = grader.evaluate(
        "prompt_sent,tool_called,tool_called,completed",
        {"trace": {"required_sequence": ["prompt_sent", "completed"], "max_tool_calls": 1}},
    )
    assert 0.0 <= result.score <= 1.0
    assert "failure:tool_overuse" in result.labels


def test_trace_grader_error_event_failure_label() -> None:
    grader = TraceGrader()
    result = grader.evaluate(
        "prompt_sent,error,completed",
        {"trace": {"required_sequence": ["prompt_sent", "completed"]}},
    )
    assert "failure:run_error" in result.labels
