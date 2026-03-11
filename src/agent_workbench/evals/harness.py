"""Evaluation harness."""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_workbench.domain.entities.evaluation import EvaluationResult
from agent_workbench.domain.interfaces.evaluator import Evaluator
from agent_workbench.evals.metrics import average, weighted_score


@dataclass(slots=True)
class TaskRunEvaluation:
    task_id: str
    config_id: str
    score: float
    output_quality_score: float
    trace_quality_score: float
    latency_ms: float = 0.0
    cost_usd: float = 0.0
    failure_labels: list[str] = field(default_factory=list)
    evaluator_scores: dict[str, float] = field(default_factory=dict)
    evaluator_results: list[EvaluationResult] = field(default_factory=list)


@dataclass(slots=True)
class BenchmarkMetrics:
    task_runs: int
    success_rate: float
    avg_score: float
    avg_latency_ms: float
    avg_cost_usd: float


@dataclass(slots=True)
class EvalHarness:
    evaluators: list[Evaluator]

    def run(self, output: str, expected: dict[str, object]) -> list[EvaluationResult]:
        return [e.evaluate(output, expected) for e in self.evaluators]

    def evaluate_task_run(
        self,
        *,
        task_id: str,
        config_id: str,
        output: str,
        expected: dict[str, object],
        latency_ms: float = 0.0,
        cost_usd: float = 0.0,
    ) -> TaskRunEvaluation:
        results = self.run(output, expected)
        evaluator_scores = {result.metric_name: round(result.score, 4) for result in results}

        output_scores = [
            result.score
            for result in results
            if result.metric_name in {"exact_match", "rubric"}
        ]
        trace_scores = [result.score for result in results if result.metric_name == "trace_quality"]

        if output_scores:
            output_quality_score = average(output_scores)
        else:
            output_quality_score = average([result.score for result in results])
        trace_quality_score = average(trace_scores) if trace_scores else output_quality_score
        total_score = weighted_score(
            output_quality=output_quality_score,
            trace_quality=trace_quality_score,
        )

        failure_labels = sorted(
            {
                label.removeprefix("failure:")
                for result in results
                for label in result.labels
                if label.startswith("failure:")
            }
        )
        return TaskRunEvaluation(
            task_id=task_id,
            config_id=config_id,
            score=round(total_score, 4),
            output_quality_score=round(output_quality_score, 4),
            trace_quality_score=round(trace_quality_score, 4),
            latency_ms=round(latency_ms, 4),
            cost_usd=round(cost_usd, 6),
            failure_labels=failure_labels,
            evaluator_scores=evaluator_scores,
            evaluator_results=results,
        )

    @staticmethod
    def aggregate_metrics(task_evaluations: list[TaskRunEvaluation]) -> BenchmarkMetrics:
        task_runs = len(task_evaluations)
        if task_runs == 0:
            return BenchmarkMetrics(
                task_runs=0,
                success_rate=0.0,
                avg_score=0.0,
                avg_latency_ms=0.0,
                avg_cost_usd=0.0,
            )

        successful = sum(
            1
            for evaluation in task_evaluations
            if evaluation.score >= 0.5 and not evaluation.failure_labels
        )
        return BenchmarkMetrics(
            task_runs=task_runs,
            success_rate=successful / task_runs,
            avg_score=average([evaluation.score for evaluation in task_evaluations]),
            avg_latency_ms=average([evaluation.latency_ms for evaluation in task_evaluations]),
            avg_cost_usd=average([evaluation.cost_usd for evaluation in task_evaluations]),
        )
