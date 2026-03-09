from agent_workbench.evals.graders.exact_match import ExactMatchGrader


def test_exact_match() -> None:
    grader = ExactMatchGrader()
    result = grader.evaluate("hello", {"target": "hello"})
    assert result.score == 1.0
