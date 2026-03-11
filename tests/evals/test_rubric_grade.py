from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.evals.graders.rubric_grade import RubricGrader


def _expected_rubric() -> dict[str, object]:
    return {
        "rubric": {
            "criteria": [
                {"name": "correctness", "required_terms": ["alpha"], "mode": "all"},
                {"name": "completeness", "required_terms": ["beta"], "mode": "all"},
            ]
        }
    }


def test_rubric_grader_returns_typed_result() -> None:
    grader = RubricGrader(criteria_weights={"correctness": 0.7, "completeness": 0.3})
    result = grader.evaluate("alpha beta", _expected_rubric())
    assert isinstance(result, EvaluationResult)
    assert result.metric_name == "rubric"
    assert result.score == 1.0
    assert result.labels == ["rubric:pass"]


def test_rubric_grader_weighted_partial_score() -> None:
    grader = RubricGrader(criteria_weights={"correctness": 0.7, "completeness": 0.3})
    result = grader.evaluate("alpha only", _expected_rubric())
    assert result.score == 0.7
    assert result.labels == ["rubric:pass"]


def test_rubric_grader_score_boundaries() -> None:
    grader = RubricGrader(criteria_weights={"correctness": 0.7, "completeness": 0.3})
    low = grader.evaluate("missing everything", _expected_rubric())
    high = grader.evaluate("alpha beta plus extra context", _expected_rubric())
    assert low.score == 0.0
    assert high.score == 1.0
    assert low.labels == ["rubric:fail"]
    assert high.labels == ["rubric:pass"]


def test_rubric_grader_honors_per_criterion_weight_override() -> None:
    grader = RubricGrader(criteria_weights={"correctness": 0.2, "completeness": 0.8})
    expected = {
        "rubric": {
            "criteria": [
                {"name": "correctness", "required_terms": ["alpha"], "weight": 9.0},
                {"name": "completeness", "required_terms": ["beta"], "weight": 1.0},
            ]
        }
    }
    result = grader.evaluate("alpha", expected)
    assert result.score == 0.9
