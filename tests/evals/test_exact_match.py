from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.evals.graders.exact_match import ExactMatchGrader


def test_exact_match() -> None:
    grader = ExactMatchGrader()
    result = grader.evaluate("hello", {"target": "hello"})
    assert isinstance(result, EvaluationResult)
    assert result.score == 1.0


def test_exact_match_mismatch_boundary() -> None:
    grader = ExactMatchGrader()
    result = grader.evaluate("hello", {"target": "world"})
    assert result.score == 0.0
