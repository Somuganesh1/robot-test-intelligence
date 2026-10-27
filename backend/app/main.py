from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException


app = FastAPI(
    title="Robot Test Intelligence API",
    description="API for robot test analytics and failure investigation.",
    version="0.1.0",
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "robot_test_runs.csv"


def load_test_data() -> pd.DataFrame:
    """Load robot test telemetry from the synthetic dataset."""
    return pd.read_csv(DATA_PATH)


@app.get("/")
def root():
    return {
        "service": "Robot Test Intelligence API",
        "status": "running",
    }


@app.get("/api/tests")
def get_tests(limit: int = 100):
    df = load_test_data()

    records = df.head(limit).copy()

    # Convert NaN values (such as empty failure_type) to None
    records = records.where(pd.notnull(records), None)

    return records.to_dict(orient="records")


@app.get("/api/tests/{test_id}")
def get_test(test_id: str):
    df = load_test_data()

    test = df[df["test_id"] == test_id]

    if test.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Test {test_id} not found",
        )

    record = test.iloc[0].where(pd.notnull(test.iloc[0]), None)

    return record.to_dict()


@app.get("/api/summary")
def get_summary():
    df = load_test_data()

    total_tests = len(df)
    passed = int((df["result"] == "PASSED").sum())
    failed = int((df["result"] == "FAILED").sum())

    success_rate = (
        round((passed / total_tests) * 100, 2)
        if total_tests > 0
        else 0
    )

    failure_counts = (
        df.loc[df["result"] == "FAILED", "failure_type"]
        .value_counts()
        .to_dict()
    )

    return {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "success_rate": success_rate,
        "failure_breakdown": failure_counts,
    }