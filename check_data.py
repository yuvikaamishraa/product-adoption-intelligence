import pandas as pd

df = pd.read_csv("data/product_events.csv")

print("DATASET OVERVIEW")
print("Rows:", len(df))
print("Columns:", len(df.columns))
print("Unique users:", df["user_id"].nunique())

print("\nMISSING VALUES")
print(df.isnull().sum())

print("\nDUPLICATE USER IDs")
print(df["user_id"].duplicated().sum())

print("\nEXPERIMENT GROUP COUNTS")
print(df["experiment_group"].value_counts())

print("\nCONVERSION RATE (%)")
print(df.groupby("experiment_group")["converted"].mean() * 100)

print("\nDATA QUALITY CHECK COMPLETE")


print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATE USER IDs ---")
print(df["user_id"].duplicated().sum())

print("\n--- INVALID BINARY VALUES ---")
for col in ["exposed", "feature_used", "converted", "support_contact"]:
    invalid = ~df[col].isin([0, 1])
    print(f"{col}: {invalid.sum()}")

print("\n--- EXPOSURE BY GROUP (%) ---")
print(df.groupby("experiment_group")["exposed"].mean() * 100)

print("\n--- FEATURE ADOPTION BY GROUP (%) ---")
print(df.groupby("experiment_group")["feature_used"].mean() * 100)


from math import sqrt
from scipy.stats import norm

groups = df.groupby("experiment_group")["converted"].agg(["sum", "count"])

c = groups.loc["control"]
t = groups.loc["treatment"]

p_c = c["sum"] / c["count"]
p_t = t["sum"] / t["count"]

# Treatment minus control
lift = p_t - p_c

# Two-proportion z-test
pooled = (c["sum"] + t["sum"]) / (c["count"] + t["count"])

se_test = sqrt(pooled * (1 - pooled) * (1 / c["count"] + 1 / t["count"]))

z = lift / se_test
p_value = 2 * norm.sf(abs(z))

# 95% confidence interval for absolute lift
se_ci = sqrt(p_c * (1 - p_c) / c["count"] + p_t * (1 - p_t) / t["count"])

ci_low = lift - 1.96 * se_ci
ci_high = lift + 1.96 * se_ci

print("\n--- INDEPENDENT A/B TEST ---")
print(f"Control conversion: {p_c:.4%}")
print(f"Treatment conversion: {p_t:.4%}")
print(f"Absolute lift: {lift:.4%}")
print(f"Relative lift: {lift / p_c:.2%}")
print(f"Z statistic: {z:.4f}")
print(f"Two-sided p-value: {p_value:.6f}")
print(f"95% CI: [{ci_low:.4%}, {ci_high:.4%}]")
