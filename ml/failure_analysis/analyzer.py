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


def analyze_failure_pattern(
    df: pd.DataFrame,
    failure_type: str,
) -> dict:
    """
    Analyze historical runs associated with a specific failure type.
    """

    failures = df[
        (df["result"] == "FAILED")
        & (df["failure_type"] == failure_type)
    ]

    if failures.empty:
        raise ValueError(
            f"No failures found for: {failure_type}"
        )

    total_failures = len(failures)

    emergency_stops = int(
        failures["emergency_stop"].sum()
    )

    collisions = int(
        failures["collision_detected"].sum()
    )

    telemetry_averages = (
        failures[TELEMETRY_FEATURES]
        .mean()
        .round(2)
        .to_dict()
    )

    return {
        "failure_type": failure_type,
        "total_failures": total_failures,
        "emergency_stops": emergency_stops,
        "collisions": collisions,
        "emergency_stop_rate": round(
            emergency_stops / total_failures * 100,
            2,
        ),
        "collision_rate": round(
            collisions / total_failures * 100,
            2,
        ),
        "telemetry_averages": telemetry_averages,
    }


def compare_failure_to_normal(
    df: pd.DataFrame,
    failure_type: str,
    task_type: str,
) -> pd.DataFrame:
    """
    Compare telemetry from a specific failure type against
    successful runs of the same task.
    """

    failures = df[
        (df["result"] == "FAILED")
        & (df["failure_type"] == failure_type)
        & (df["task_type"] == task_type)
    ]

    normal = df[
        (df["result"] == "PASSED")
        & (df["task_type"] == task_type)
    ]

    if failures.empty:
        raise ValueError(
            f"No {failure_type} failures found "
            f"for task {task_type}"
        )

    if normal.empty:
        raise ValueError(
            f"No successful tests found "
            f"for task {task_type}"
        )

    results = []

    for feature in TELEMETRY_FEATURES:
        failure_mean = float(
            failures[feature].mean()
        )

        normal_mean = float(
            normal[feature].mean()
        )

        difference = failure_mean - normal_mean

        if normal_mean != 0:
            percent_change = (
                difference / normal_mean
            ) * 100
        else:
            percent_change = 0.0

        results.append(
            {
                "feature": feature,
                "normal_mean": round(normal_mean, 2),
                "failure_mean": round(failure_mean, 2),
                "difference": round(difference, 2),
                "percent_change": round(
                    percent_change,
                    2,
                ),
            }
        )

    return pd.DataFrame(results)

if __name__ == "__main__":
    data = load_data()

    failure_type = "BALANCE_FAILURE"
    task_type = "PALLET_MOVE"

    analysis = analyze_failure_pattern(
        data,
        failure_type,
    )

    print(
        f"\nFailure Pattern Analysis — "
        f"{analysis['failure_type']}\n"
    )

    print(
        f"Total failures: "
        f"{analysis['total_failures']}"
    )

    print(
        f"Emergency stops: "
        f"{analysis['emergency_stops']} "
        f"({analysis['emergency_stop_rate']}%)"
    )

    print(
        f"Collisions: "
        f"{analysis['collisions']} "
        f"({analysis['collision_rate']}%)"
    )

    comparison = compare_failure_to_normal(
        data,
        failure_type,
        task_type,
    )

    print(
        f"\n{failure_type} vs Normal "
        f"{task_type}\n"
    )

    print(
        comparison.to_string(index=False)
    )