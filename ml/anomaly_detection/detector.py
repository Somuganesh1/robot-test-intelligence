from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "robot_test_runs.csv"
)


TELEMETRY_FEATURES = [
    "battery_level",
    "motor_temperature",
    "cpu_temperature",
    "walking_speed",
    "joint_velocity",
    "torso_angle",
    "grip_force",
    "object_weight",
    "task_duration",
]


def load_data() -> pd.DataFrame:
    """Load historical robot test telemetry."""
    return pd.read_csv(DATA_PATH)


def calculate_baseline(
    df: pd.DataFrame,
    task_type: str,
) -> pd.DataFrame:
    """
    Calculate the normal telemetry baseline for a specific task.

    Only PASSED tests are used so failed behavior does not
    influence the definition of normal robot operation.
    """

    normal_tests = df[
        (df["task_type"] == task_type)
        & (df["result"] == "PASSED")
    ]

    if normal_tests.empty:
        raise ValueError(
            f"No passed tests found for task: {task_type}"
        )

    baseline = normal_tests[TELEMETRY_FEATURES].agg(
        ["mean", "std"]
    )

    return baseline

def analyze_test(
    df: pd.DataFrame,
    test_id: str,
    threshold: float = 2.0,
) -> pd.DataFrame:
    """
    Compare a test run against successful runs of the same task.

    A feature is marked as anomalous when its absolute
    Z-score is greater than or equal to the threshold.
    """

    test_rows = df[df["test_id"] == test_id]

    if test_rows.empty:
        raise ValueError(
            f"Test not found: {test_id}"
        )

    test = test_rows.iloc[0]

    task_type = test["task_type"]

    baseline = calculate_baseline(
        df,
        task_type,
    )

    results = []

    for feature in TELEMETRY_FEATURES:
        value = float(test[feature])
        mean = float(baseline.loc["mean", feature])
        std = float(baseline.loc["std", feature])

        if pd.isna(std) or std == 0:
            z_score = 0.0
        else:
            z_score = (value - mean) / std

        is_anomaly = abs(z_score) >= threshold

        results.append(
            {
                "feature": feature,
                "value": round(value, 2),
                "baseline_mean": round(mean, 2),
                "z_score": round(z_score, 2),
                "status": (
                    "ANOMALY"
                    if is_anomaly
                    else "NORMAL"
                ),
            }
        )

    return pd.DataFrame(results)

def analyze_safety_events(
    df: pd.DataFrame,
    test_id: str,
) -> list[dict]:
    """
    Detect discrete safety events associated with a test run.
    """

    test_rows = df[df["test_id"] == test_id]

    if test_rows.empty:
        raise ValueError(
            f"Test not found: {test_id}"
        )

    test = test_rows.iloc[0]

    events = []

    if bool(test["collision_detected"]):
        events.append(
            {
                "event": "COLLISION_DETECTED",
                "severity": "CRITICAL",
            }
        )

    if bool(test["emergency_stop"]):
        events.append(
            {
                "event": "EMERGENCY_STOP",
                "severity": "HIGH",
            }
        )

    return events

if __name__ == "__main__":
    data = load_data()

    test_id = "TEST-0419"

    analysis = analyze_test(
        data,
        test_id,
    )

    safety_events = analyze_safety_events(
        data,
        test_id,
    )

    print(f"\nAnomaly Analysis — {test_id}\n")

    print(
        analysis.to_string(index=False)
    )

    print("\nSafety Event Analysis\n")

    if safety_events:
        for event in safety_events:
            print(
                f"{event['event']} "
                f"— {event['severity']}"
            )
    else:
        print("No safety events detected.")