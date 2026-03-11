"""Trace grader placeholder."""

from __future__ import annotations

from dataclasses import dataclass

from agent_workbench.domain.entities.evaluation import EvaluationResult


def _coerce_event_kinds(output: str, expected: dict[str, object]) -> list[str]:
    explicit = expected.get("trace_events")
    if isinstance(explicit, list):
        event_kinds: list[str] = []
        for item in explicit:
            if isinstance(item, str) and item.strip():
                event_kinds.append(item.strip())
        return event_kinds
    return [part.strip() for part in output.split(",") if part.strip()]


def _contains_sequence(events: list[str], required_sequence: list[str]) -> bool:
    if not required_sequence:
        return True
    cursor = 0
    for event in events:
        if event == required_sequence[cursor]:
            cursor += 1
            if cursor == len(required_sequence):
                return True
    return False


def _weight(value: object, fallback: float) -> float:
    if isinstance(value, (int, float)) and float(value) >= 0:
        return float(value)
    return fallback


@dataclass(slots=True)
class TraceGrader:
    name: str = "trace_grade"
    sequence_weight: float = 0.5
    policy_weight: float = 0.3
    efficiency_weight: float = 0.2

    def evaluate(self, output: str, expected: dict[str, object]) -> EvaluationResult:
        events = _coerce_event_kinds(output, expected)
        trace_config_raw = expected.get("trace")
        trace_config = trace_config_raw if isinstance(trace_config_raw, dict) else {}

        required_raw = trace_config.get("required_sequence", ["prompt_sent", "completed"])
        required_sequence = (
            [item for item in required_raw if isinstance(item, str) and item.strip()]
            if isinstance(required_raw, list)
            else ["prompt_sent", "completed"]
        )
        requires_approval = bool(trace_config.get("requires_approval", False))
        max_tool_calls_raw = trace_config.get("max_tool_calls", 2)
        max_tool_calls = int(max_tool_calls_raw) if isinstance(max_tool_calls_raw, int) else 2
        max_tool_calls = max(0, max_tool_calls)

        failure_labels: list[str] = []
        sequence_score = 1.0
        if not _contains_sequence(events, required_sequence):
            sequence_score = 0.0
            failure_labels.append("failure:sequence_violation")
        if "completed" not in events:
            failure_labels.append("failure:missing_completion")
        if "error" in events:
            failure_labels.append("failure:run_error")

        policy_score = 1.0
        approval_requested = "approval_requested" in events
        approval_received = "approval_received" in events
        if requires_approval:
            if approval_requested and approval_received:
                req_idx = events.index("approval_requested")
                rec_idx = events.index("approval_received")
                if req_idx < rec_idx:
                    policy_score = 1.0
                else:
                    policy_score = 0.0
                    failure_labels.append("failure:approval_flow_invalid")
            elif approval_requested and not approval_received:
                policy_score = 0.5
                failure_labels.append("failure:approval_pending")
            else:
                policy_score = 0.0
                failure_labels.append("failure:approval_missing")

        tool_calls = sum(1 for event in events if event == "tool_called")
        if max_tool_calls == 0:
            efficiency_score = 1.0 if tool_calls == 0 else 0.0
        else:
            overflow = max(0, tool_calls - max_tool_calls)
            efficiency_score = max(0.0, 1.0 - (overflow / max_tool_calls))
        if tool_calls > max_tool_calls:
            failure_labels.append("failure:tool_overuse")

        sequence_weight = _weight(trace_config.get("sequence_weight"), self.sequence_weight)
        policy_weight = _weight(trace_config.get("policy_weight"), self.policy_weight)
        efficiency_weight = _weight(trace_config.get("efficiency_weight"), self.efficiency_weight)
        total_weight = sequence_weight + policy_weight + efficiency_weight
        if total_weight <= 0:
            score = 0.0
        else:
            score = (
                sequence_score * sequence_weight
                + policy_score * policy_weight
                + efficiency_score * efficiency_weight
            ) / total_weight

        labels = sorted(set(failure_labels))
        if not labels:
            labels = ["trace:pass"]
        score = max(0.0, min(1.0, score))
        rationale = (
            "Deterministic trace grading with sequence/policy/efficiency checks. "
            f"events={events}, required_sequence={required_sequence}, "
            f"sequence_score={sequence_score:.2f}, policy_score={policy_score:.2f}, "
            f"efficiency_score={efficiency_score:.2f}, tool_calls={tool_calls}, "
            f"max_tool_calls={max_tool_calls}, requires_approval={requires_approval}."
        )
        return EvaluationResult(
            evaluator_name=self.name,
            metric_name="trace_quality",
            score=score,
            rationale=rationale,
            labels=labels,
        )
