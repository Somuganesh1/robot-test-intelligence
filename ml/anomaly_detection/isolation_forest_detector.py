from pathlib import Path

import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


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
    """
    Load the robot telemetry dataset.
    """

    return pd.read_csv(DATA_PATH)


def get_training_data(
    df: pd.DataFrame,
    task_type: str,
    exclude_test_id: str | None = None,
) -> pd.DataFrame:
    """
    Build a task-specific training dataset using only
    successful validation runs.

    A selected passed test can be excluded so the model
    does not evaluate a test that it already trained on.
    """

    training_data = df[
        (df["task_type"] == task_type)
        & (df["result"] == "PASSED")
    ].copy()

    if exclude_test_id:
        training_data = training_data[
            training_data["test_id"]
            != exclude_test_id
        ]

    if training_data.empty:
        raise ValueError(
            f"No successful training data found "
            f"for task: {task_type}"
        )

    return training_data


def analyze_test_with_isolation_forest(
    df: pd.DataFrame,
    test_id: str,
) -> dict:
    """
    Analyze one robot test using a task-specific
    Isolation Forest model.

    The model is trained only on successful runs of the
    same task type.
    """

    rows = df[
        df["test_id"] == test_id
    ]

    if rows.empty:
        raise ValueError(
            f"Test not found: {test_id}"
        )

    test = rows.iloc[0]

    task_type = test["task_type"]

    training_data = get_training_data(
        df,
        task_type,
        exclude_test_id=test_id,
    )

    # -----------------------------------------------------
    # Prepare feature matrices
    # -----------------------------------------------------

    x_train = training_data[
        TELEMETRY_FEATURES
    ].copy()

    x_test = pd.DataFrame(
        [test[TELEMETRY_FEATURES]]
    )

    # -----------------------------------------------------
    # Standardize telemetry features
    # -----------------------------------------------------

    scaler = StandardScaler()

    x_train_scaled = scaler.fit_transform(
        x_train
    )

    x_test_scaled = scaler.transform(
        x_test
    )

    # -----------------------------------------------------
    # Train Isolation Forest
    # -----------------------------------------------------

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
    )

    model.fit(
        x_train_scaled
    )

    # -----------------------------------------------------
    # Predict selected test
    #
    #  1 = normal
    # -1 = anomaly
    # -----------------------------------------------------

    prediction = int(
        model.predict(
            x_test_scaled
        )[0]
    )

    decision_score = float(
        model.decision_function(
            x_test_scaled
        )[0]
    )

    is_anomaly = (
        prediction == -1
    )

    return {
        "test_id": test_id,
        "task_type": task_type,
        "model": "Isolation Forest",
        "training_runs": len(training_data),
        "prediction": (
            "ANOMALY"
            if is_anomaly
            else "NORMAL"
        ),
        "is_anomaly": is_anomaly,
        "decision_score": round(
            decision_score,
            4,
        ),
        "features_used": TELEMETRY_FEATURES,
    }


if __name__ == "__main__":

    data = load_data()

    print(
        "\nSearching for Isolation Forest anomalies...\n"
    )

    anomaly_count = 0

    for test_id in data["test_id"]:

        result = (
            analyze_test_with_isolation_forest(
                data,
                test_id,
            )
        )

        if result["is_anomaly"]:

            anomaly_count += 1

            row = data[
                data["test_id"] == test_id
            ].iloc[0]

            print(
                f"{anomaly_count}. "
                f"{test_id} | "
                f"{row['task_type']} | "
                f"{row['result']} | "
                f"score={result['decision_score']}"
            )

            if anomaly_count >= 10:
                break

    if anomaly_count == 0:
        print(
            "No Isolation Forest anomalies found."
        )

    