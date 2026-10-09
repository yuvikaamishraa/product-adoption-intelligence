from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
EVENTS_PATH = DATA_DIR / "product_events.csv"


def generate_demo_data(n_users: int = 6000, seed: int = 42) -> pd.DataFrame:
    """Generate clearly synthetic product experiment data for local demonstration."""
    rng = np.random.default_rng(seed)
    user_ids = np.array([f"U{i:06d}" for i in range(1, n_users + 1)])
    groups = rng.choice(["control", "treatment"], size=n_users, p=[0.5, 0.5])
    regions = rng.choice(["North America", "Europe", "Asia Pacific", "Other"], n_users,
                         p=[0.38, 0.27, 0.25, 0.10])
    platforms = rng.choice(["Web", "iOS", "Android"], n_users, p=[0.48, 0.25, 0.27])
    user_types = rng.choice(["New", "Returning"], n_users, p=[0.42, 0.58])
    dates = pd.to_datetime("2026-08-01") + pd.to_timedelta(
        rng.integers(0, 28, size=n_users), unit="D"
    )

    # Synthetic assignment and conversion probabilities, used only for demo/testing.
    base_prob = np.where(user_types == "New", 0.105, 0.165)
    platform_effect = np.select(
        [platforms == "Web", platforms == "iOS", platforms == "Android"],
        [0.010, 0.018, -0.008],
        default=0.0,
    )
    region_effect = np.select(
        [regions == "North America", regions == "Europe", regions == "Asia Pacific"],
        [0.012, 0.004, -0.004],
        default=-0.01,
    )
    treatment_effect = np.where(groups == "treatment", 0.025, 0.0)
    probabilities = np.clip(base_prob + platform_effect + region_effect + treatment_effect, 0.02, 0.70)
    exposed = rng.random(n_users) < 0.94
    converted = (rng.random(n_users) < probabilities) & exposed
    feature_used = exposed & (rng.random(n_users) < (
        np.where(groups == "treatment", 0.47, 0.39)
        + np.where(user_types == "Returning", 0.06, 0.0)
    ))
    sessions = np.maximum(1, rng.poisson(lam=np.where(user_types == "Returning", 5.0, 2.8)))
    sessions = sessions + feature_used.astype(int)
    session_duration = np.round(rng.gamma(shape=2.2, scale=4.5, size=n_users), 2)
    support_contact = (rng.random(n_users) < np.where(converted, 0.035, 0.075))

    df = pd.DataFrame({
        "user_id": user_ids,
        "assigned_at": dates,
        "experiment_group": groups,
        "region": regions,
        "platform": platforms,
        "user_type": user_types,
        "exposed": exposed.astype(int),
        "feature_used": feature_used.astype(int),
        "converted": converted.astype(int),
        "sessions_7d": sessions.astype(int),
        "session_duration_min": session_duration,
        "support_contact": support_contact.astype(int),
    })
    df["assigned_at"] = pd.to_datetime(df["assigned_at"]).dt.strftime("%Y-%m-%d")
    return df


def load_or_create_data(force_regenerate: bool = False) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if force_regenerate or not EVENTS_PATH.exists():
        df = generate_demo_data()
        df.to_csv(EVENTS_PATH, index=False)
    else:
        df = pd.read_csv(EVENTS_PATH)
    df["assigned_at"] = pd.to_datetime(df["assigned_at"], errors="coerce")
    return df
