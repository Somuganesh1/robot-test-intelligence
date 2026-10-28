from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ml.failure_analysis.investigator import investigate_failure


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Robot Test Intelligence API",
    description="API for robot test analytics and failure investigation.",
    version="0.1.0",
)


# ---------------------------------------------------------
# CORS configuration
# Allows the React frontend to communicate with FastAPI
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Dataset configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "robot_test_runs.csv"
)


# ---------------------------------------------------------
# Data loader
# ---------------------------------------------------------

def load_test_data() -> pd.DataFrame:
    """Load robot test telemetry from the synthetic dataset."""
    return pd.read_csv(DATA_PATH)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": "Robot Test Intelligence API",
        "status": "running",
    }


# ---------------------------------------------------------
# Get robot test runs
# Example:
# /api/tests
# /api/tests?limit=10
# ---------------------------------------------------------

@app.get("/api/tests")
def get_tests(limit: int = 100):
    df = load_test_data()

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    records = (
    df.sort_values("timestamp", ascending=False)
    .head(limit)
    .copy()
    )

    # Convert Pandas NaN values into JSON-safe Python None.
    # astype(object) is important because some Pandas columns
    # otherwise preserve NaN even when we try replacing it.
    records = records.astype(object).where(
        pd.notnull(records),
        None,
    )

    return records.to_dict(orient="records")


# ---------------------------------------------------------
# Get one specific test
# Example:
# /api/tests/TEST-0004
# ---------------------------------------------------------

@app.get("/api/tests/{test_id}")
def get_test(test_id: str):
    df = load_test_data()

    test = df[df["test_id"] == test_id]

    if test.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Test {test_id} not found",
        )

    record = test.iloc[0].astype(object)

    record = record.where(
        pd.notnull(record),
        None,
    )

    return record.to_dict()

@app.get("/api/investigate/{test_id}")
def investigate_test(test_id: str):
    df = load_test_data()

    try:
        report = investigate_failure(
            df,
            test_id,
        )

        return report

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )
        
# ---------------------------------------------------------
# Fleet summary
# ---------------------------------------------------------

@app.get("/api/summary")
def get_summary():
    df = load_test_data()

    total_tests = len(df)

    passed = int(
        (df["result"] == "PASSED").sum()
    )

    failed = int(
        (df["result"] == "FAILED").sum()
    )

    success_rate = (
        round((passed / total_tests) * 100, 2)
        if total_tests > 0
        else 0
    )

    failure_counts = (
        df.loc[
            df["result"] == "FAILED",
            "failure_type",
        ]
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