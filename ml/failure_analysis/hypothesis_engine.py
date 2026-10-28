from typing import Any


def generate_hypotheses(
    investigation: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate explainable root-cause hypotheses from an
    investigation report.

    These are contributing-factor hypotheses, not claims
    of proven physical causation.
    """

    hypotheses = []

    historical_signals = investigation.get(
        "historical_signals",
        []
    )

    safety_events = investigation.get(
        "safety_events",
        []
    )

    anomalies = investigation.get(
        "telemetry_anomalies",
        []
    )

    # -----------------------------------------------------
    # Historical failure signals
    # -----------------------------------------------------

    for signal in historical_signals:

        feature = signal.get("feature")
        percent_change = signal.get("percent_change", 0)
        normal_mean = signal.get("normal_mean")
        failure_mean = signal.get("failure_mean")

        absolute_change = abs(percent_change)

        # Ignore weak historical differences
        if absolute_change < 10:
            continue

        if absolute_change >= 50:
            confidence = "HIGH"
        elif absolute_change >= 20:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # -------------------------------------------------
        # Human-readable hypotheses
        # -------------------------------------------------

        if feature == "torso_angle":
            title = "POSTURAL INSTABILITY"

            explanation = (
                f"Historical failure runs show torso angle "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        elif feature == "battery_level":
            title = "REDUCED BATTERY STATE"

            explanation = (
                f"Historical failure runs show battery level "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        elif feature == "walking_speed":
            title = "MOVEMENT SPEED DEVIATION"

            explanation = (
                f"Historical failure runs show walking speed "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        elif feature == "grip_force":
            title = "GRIP FORCE DEVIATION"

            explanation = (
                f"Historical failure runs show grip force "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        elif feature == "motor_temperature":
            title = "MOTOR THERMAL DEVIATION"

            explanation = (
                f"Historical failure runs show motor temperature "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        elif feature == "cpu_temperature":
            title = "COMPUTE THERMAL DEVIATION"

            explanation = (
                f"Historical failure runs show CPU temperature "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        elif feature == "joint_velocity":
            title = "JOINT MOTION DEVIATION"

            explanation = (
                f"Historical failure runs show joint velocity "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        else:
            title = feature.replace("_", " ").upper()

            explanation = (
                f"Historical failure runs show {feature.replace('_', ' ')} "
                f"changing by {percent_change:+.2f}% compared "
                f"with successful runs."
            )

        hypotheses.append(
            {
                "feature": feature,
                "title": title,
                "confidence": confidence,
                "percent_change": round(percent_change, 2),
                "normal_mean": normal_mean,
                "failure_mean": failure_mean,
                "explanation": explanation,
            }
        )

    # -----------------------------------------------------
    # Sort strongest historical signal first
    # -----------------------------------------------------

    hypotheses.sort(
        key=lambda item: abs(item["percent_change"]),
        reverse=True,
    )

    # -----------------------------------------------------
    # Safety escalation
    # -----------------------------------------------------

    safety_escalation = None

    if safety_events:
        safety_escalation = {
            "level": "HIGH",
            "events": safety_events,
            "message": (
                "A safety event occurred during this test and "
                "should be prioritized during investigation."
            ),
        }

    # -----------------------------------------------------
    # Overall investigation confidence
    # -----------------------------------------------------

    high_confidence_count = sum(
        1
        for hypothesis in hypotheses
        if hypothesis["confidence"] == "HIGH"
    )

    if safety_events and high_confidence_count >= 1:
        overall_confidence = "HIGH"

    elif hypotheses or anomalies:
        overall_confidence = "MEDIUM"

    else:
        overall_confidence = "LOW"

    return {
        "hypotheses": hypotheses,
        "safety_escalation": safety_escalation,
        "investigation_confidence": overall_confidence,
        "disclaimer": (
            "Generated factors are investigation hypotheses "
            "based on telemetry and historical associations; "
            "they do not establish physical causation."
        ),
    }


# ---------------------------------------------------------
# Simple local test
# ---------------------------------------------------------

if __name__ == "__main__":

    sample_investigation = {
        "historical_failure_signals": [
            {
                "feature": "torso_angle",
                "normal_mean": 2.33,
                "failure_mean": 4.25,
                "percent_change": 82.17,
            },
            {
                "feature": "battery_level",
                "normal_mean": 61.86,
                "failure_mean": 49.93,
                "percent_change": -19.30,
            },
            {
                "feature": "walking_speed",
                "normal_mean": 1.12,
                "failure_mean": 1.30,
                "percent_change": 16.00,
            },
        ],
        "telemetry_anomalies": [],
        "safety_events": [
            {
                "event": "EMERGENCY_STOP",
                "severity": "HIGH",
            }
        ],
    }

    result = generate_hypotheses(sample_investigation)

    print("\nRoot-Cause Hypothesis Engine\n")

    for index, hypothesis in enumerate(
        result["hypotheses"],
        start=1,
    ):
        print(
            f"{index}. {hypothesis['title']} "
            f"({hypothesis['confidence']})"
        )

        print(
            f"   {hypothesis['explanation']}"
        )

    print(
        "\nInvestigation Confidence:",
        result["investigation_confidence"],
    )