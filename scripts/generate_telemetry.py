from pathlib import Path
from datetime import datetime, timedelta
import random

import numpy as np
import pandas as pd


# Reproducible data
random.seed(42)
np.random.seed(42)

NUM_TESTS = 1000

ROBOTS = ["RBT-01", "RBT-02", "RBT-03", "RBT-04", "RBT-05"]

TASK_TYPES = [
    "TOTE_TRANSFER",
    "PALLET_MOVE",
    "OBJECT_PICK",
    "WAREHOUSE_WALK",
]

FAILURE_TYPES = [
    "GRIP_FAILURE",
    "NAVIGATION_FAILURE",
    "BALANCE_FAILURE",
    "THERMAL_WARNING",
]


def generate_test_run(test_number: int) -> dict:

    robot_id = random.choice(ROBOTS)
    task_type = random.choice(TASK_TYPES)

    battery_level = round(random.uniform(20, 100), 2)
    motor_temperature = round(np.random.normal(55, 7), 2)
    cpu_temperature = round(np.random.normal(62, 6), 2)

    walking_speed = round(max(0, np.random.normal(1.1, 0.15)), 2)
    joint_velocity = round(max(0, np.random.normal(1.5, 0.25)), 2)
    torso_angle = round(abs(np.random.normal(2.5, 1.2)), 2)

    object_weight = round(random.uniform(2, 15), 2)
    grip_force = round(np.random.normal(48, 7), 2)

    task_duration = round(max(1, np.random.normal(40, 8)), 2)

    collision_detected = random.random() < 0.02
    emergency_stop = random.random() < 0.01

    result = "PASSED"
    failure_type = None

    # Inject understandable failure patterns.
    if object_weight > 11 and grip_force < 43:
        result = "FAILED"
        failure_type = "GRIP_FAILURE"

    elif torso_angle > 5:
        result = "FAILED"
        failure_type = "BALANCE_FAILURE"

    elif collision_detected:
        result = "FAILED"
        failure_type = "NAVIGATION_FAILURE"

    elif motor_temperature > 70:
        result = "FAILED"
        failure_type = "THERMAL_WARNING"

    elif emergency_stop:
        result = "FAILED"
        failure_type = random.choice(FAILURE_TYPES)

    timestamp = datetime.now() - timedelta(
        minutes=random.randint(0, 60 * 24 * 30)
    )

    return {
        "test_id": f"TEST-{test_number:04d}",
        "robot_id": robot_id,
        "timestamp": timestamp.isoformat(),
        "task_type": task_type,
        "battery_level": battery_level,
        "motor_temperature": motor_temperature,
        "cpu_temperature": cpu_temperature,
        "walking_speed": walking_speed,
        "joint_velocity": joint_velocity,
        "torso_angle": torso_angle,
        "grip_force": grip_force,
        "object_weight": object_weight,
        "task_duration": task_duration,
        "collision_detected": collision_detected,
        "emergency_stop": emergency_stop,
        "result": result,
        "failure_type": failure_type,
    }


def main():

    test_runs = [
        generate_test_run(test_number)
        for test_number in range(1, NUM_TESTS + 1)
    ]

    df = pd.DataFrame(test_runs)

    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "raw" / "robot_test_runs.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(output_path, index=False)

    passed = (df["result"] == "PASSED").sum()
    failed = (df["result"] == "FAILED").sum()

    print(f"Generated {len(df)} robot test runs.")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success rate: {passed / len(df) * 100:.2f}%")
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()