from pathlib import Path
from ml.failure_analysis.hypothesis_engine import generate_hypotheses
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

sys.path.append(str(PROJECT_ROOT))


from ml.anomaly_detection.detector import (
    analyze_test,
    analyze_safety_events,
)

from ml.failure_analysis.analyzer import (
    compare_failure_to_normal,
)


DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "robot_test_runs.csv"
)


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH)


def investigate_failure(
    df: pd.DataFrame,
    test_id: str,
) -> dict:
    """
    Generate a combined failure investigation report
    for a robot test run.
    """

    rows = df[df["test_id"] == test_id]

    if rows.empty:
        raise ValueError(
            f"Test not found: {test_id}"
        )

    test = rows.iloc[0]

    telemetry_analysis = analyze_test(
        df,
        test_id,
    )

    safety_events = analyze_safety_events(
        df,
        test_id,
    )

    report = {
        "test_id": test_id,
        "robot_id": test["robot_id"],
        "task_type": test["task_type"],
        "result": test["result"],
        "failure_type": (
            None
            if pd.isna(test["failure_type"])
            else test["failure_type"]
        ),
        "telemetry_anomalies": [],
        "safety_events": safety_events,
        "historical_signals": [],
    }

    anomalies = telemetry_analysis[
        telemetry_analysis["status"] == "ANOMALY"
    ]

    for _, row in anomalies.iterrows():
        report["telemetry_anomalies"].append(
            {
                "feature": row["feature"],
                "value": row["value"],
                "z_score": row["z_score"],
            }
        )

    if (
        test["result"] == "FAILED"
        and pd.notna(test["failure_type"])
    ):
        comparison = compare_failure_to_normal(
            df,
            test["failure_type"],
            test["task_type"],
        )

        significant = comparison[
            comparison["percent_change"].abs() >= 15
        ].copy()

        significant["abs_change"] = (
            significant["percent_change"].abs()
        )

        significant = significant.sort_values(
            "abs_change",
            ascending=False,
        )

        for _, row in significant.iterrows():
            report["historical_signals"].append(
                {
                    "feature": row["feature"],
                    "normal_mean": row["normal_mean"],
                    "failure_mean": row["failure_mean"],
                    "percent_change": row[
                        "percent_change"
                    ],
                }
            )

    hypothesis_report = generate_hypotheses(report)

    report["root_cause_analysis"] = hypothesis_report

    return report


if __name__ == "__main__":
    data = load_data()

    test_id = "TEST-0419"

    report = investigate_failure(
        data,
        test_id,
    )

    print(
        f"\nFailure Investigation — "
        f"{report['test_id']}\n"
    )

    print(f"Robot: {report['robot_id']}")
    print(f"Task: {report['task_type']}")
    print(f"Result: {report['result']}")
    print(
        f"Failure Type: "
        f"{report['failure_type']}"
    )

    print("\nTelemetry Anomalies")

    if report["telemetry_anomalies"]:
        for anomaly in report[
            "telemetry_anomalies"
        ]:
            print(
                f"- {anomaly['feature']}: "
                f"value={anomaly['value']}, "
                f"z={anomaly['z_score']}"
            )
    else:
        print("- No >= 2σ telemetry anomalies.")

    print("\nSafety Events")

    if report["safety_events"]:
        for event in report["safety_events"]:
            print(
                f"- {event['event']} "
                f"({event['severity']})"
            )
    else:
        print("- None")

    print("\nHistorical Failure Signals")

    if report["historical_signals"]:
        for signal in report[
            "historical_signals"
        ]:
            print(
                f"- {signal['feature']}: "
                f"{signal['percent_change']}% "
                f"vs successful runs"
            )
    else:
        print("- No strong historical signals.")