from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm


def overall_metrics(df: pd.DataFrame) -> dict:
    users = int(df["user_id"].nunique())
    exposed_users = int(df.loc[df["exposed"] == 1, "user_id"].nunique())
    converters = int(df.loc[df["converted"] == 1, "user_id"].nunique())
    feature_users = int(df.loc[df["feature_used"] == 1, "user_id"].nunique())
    return {
        "users": users,
        "exposed": exposed_users,
        "conversions": converters,
        "feature_users": feature_users,
        "exposure_rate": exposed_users / users if users else 0.0,
        "conversion_rate": converters / users if users else 0.0,
        "adoption_rate_assigned": feature_users / users if users else 0.0,
        "adoption_rate_exposed": feature_users / exposed_users if exposed_users else 0.0,
        "support_rate": float(df["support_contact"].mean()) if users else 0.0,
        "avg_sessions": float(df["sessions_7d"].mean()) if users else 0.0,
    }


def group_metrics(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("experiment_group", observed=False).agg(
        users=("user_id", "nunique"),
        exposed_users=("exposed", "sum"),
        feature_users=("feature_used", "sum"),
        converters=("converted", "sum"),
        avg_sessions=("sessions_7d", "mean"),
        support_contact_rate=("support_contact", "mean"),
    ).reset_index()
    out["adoption_rate"] = out["feature_users"] / out["users"]
    out["conversion_rate"] = out["converters"] / out["users"]
    out["exposure_rate"] = out["exposed_users"] / out["users"]
    return out


def two_proportion_test(df: pd.DataFrame, outcome: str = "converted") -> dict:
    """Pooled two-proportion z-test and Wald CI for treatment - control."""
    grouped = df.groupby("experiment_group")[outcome].agg(["sum", "count"])
    if not {"control", "treatment"}.issubset(set(grouped.index)):
        raise ValueError("Both control and treatment groups are required.")
    x0, n0 = int(grouped.loc["control", "sum"]), int(grouped.loc["control", "count"])
    x1, n1 = int(grouped.loc["treatment", "sum"]), int(grouped.loc["treatment", "count"])
    p0, p1 = x0 / n0 if n0 else 0.0, x1 / n1 if n1 else 0.0
    diff = p1 - p0
    pooled = (x0 + x1) / (n0 + n1) if n0 + n1 else 0.0
    se_null = np.sqrt(pooled * (1 - pooled) * ((1 / n0) + (1 / n1))) if n0 and n1 else 0.0
    z_score = diff / se_null if se_null > 0 else 0.0
    p_value = float(2 * norm.sf(abs(z_score)))
    se_ci = np.sqrt((p0 * (1 - p0) / n0) + (p1 * (1 - p1) / n1)) if n0 and n1 else 0.0
    ci_low, ci_high = diff - 1.96 * se_ci, diff + 1.96 * se_ci
    relative_lift = diff / p0 if p0 else np.nan
    return {
        "control_n": n0, "treatment_n": n1,
        "control_conversions": x0, "treatment_conversions": x1,
        "control_rate": p0, "treatment_rate": p1,
        "absolute_lift": diff, "relative_lift": relative_lift,
        "z_score": z_score, "p_value": p_value,
        "ci_low": ci_low, "ci_high": ci_high,
        "significant_05": bool(p_value < 0.05),
    }


def segment_summary(df: pd.DataFrame, segment: str, outcome: str = "converted") -> pd.DataFrame:
    return (df.groupby([segment, "experiment_group"], observed=False)
            .agg(users=("user_id", "nunique"), outcome_count=(outcome, "sum"))
            .reset_index()
            .assign(rate=lambda x: x["outcome_count"] / x["users"]))


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    rows = [
        ("Rows", len(df), "Expected one row per assigned user in this demo"),
        ("Unique users", df["user_id"].nunique(), "Should equal rows for this one-row-per-user schema"),
        ("Duplicate user IDs", int(df["user_id"].duplicated().sum()), "Investigate duplicates before analysis"),
        ("Missing cells", int(df.isna().sum().sum()), "Review missingness before modelling"),
        ("Invalid experiment groups", int((~df["experiment_group"].isin(["control", "treatment"])).sum()), "Only control/treatment are expected"),
        ("Invalid binary values", int(sum((~df[c].isin([0, 1])).sum() for c in ["exposed", "feature_used", "converted", "support_contact"])), "Binary columns should contain 0 or 1"),
        ("Treatment users", int((df["experiment_group"] == "treatment").sum()), "Compare allocation with control"),
        ("Control users", int((df["experiment_group"] == "control").sum()), "Compare allocation with treatment"),
    ]
    return pd.DataFrame(rows, columns=["Check", "Result", "Interpretation"])
