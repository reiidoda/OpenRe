from agent_workbench.reporting.benchmark_report import BenchmarkReportBuilder


def test_report_builder_builds_per_task_scores_and_failure_clusters() -> None:
    builder = BenchmarkReportBuilder(
        dataset_id="research_assistant_v1",
        configs=["cfg_a", "cfg_b"],
    )
    report = builder.build(
        [
            {
                "task_id": "ra_001",
                "config_id": "cfg_a",
                "task_run_id": "taskrun_a1",
                "trace_path": "/tmp/trace.jsonl",
                "score": 0.8,
                "failure_labels": ["sequence_violation"],
            },
            {
                "task_id": "ra_001",
                "config_id": "cfg_b",
                "score": 1.0,
                "failure_labels": [],
            },
            {
                "task_id": "ra_002",
                "config_id": "cfg_a",
                "task_run_id": "taskrun_a2",
                "trace_path": "/tmp/trace.jsonl",
                "score": 0.9,
                "failure_labels": ["approval_missing"],
            },
        ]
    )

    assert report.per_task_scores == {
        "ra_001": {"cfg_a": 0.8, "cfg_b": 1.0},
        "ra_002": {"cfg_a": 0.9},
    }
    assert report.failure_clusters == {
        "sequence_violation": 1,
        "approval_missing": 1,
    }
    assert report.failure_cluster_details == [
        {
            "label": "approval_missing",
            "count": 1,
            "representative": {
                "task_id": "ra_002",
                "config_id": "cfg_a",
                "task_run_id": "taskrun_a2",
                "trace_path": "/tmp/trace.jsonl",
            },
        },
        {
            "label": "sequence_violation",
            "count": 1,
            "representative": {
                "task_id": "ra_001",
                "config_id": "cfg_a",
                "task_run_id": "taskrun_a1",
                "trace_path": "/tmp/trace.jsonl",
            },
        },
    ]
    assert report.best_config == "cfg_b"
