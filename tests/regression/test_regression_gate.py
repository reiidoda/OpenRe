from agent_workbench.evals.regression import violates_threshold


def test_regression_gate_detects_drop() -> None:
    assert violates_threshold(current=0.70, baseline=0.80, max_drop=0.05)
