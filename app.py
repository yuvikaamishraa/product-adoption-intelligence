from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data import load_or_create_data, generate_demo_data
from src.analytics import overall_metrics, group_metrics, two_proportion_test, segment_summary, data_quality_report

st.set_page_config(
    page_title="Pulse | Product Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Visual system ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#172033; --muted:#64748b; --line:#e7eaf1; --panel:#ffffff; --accent:#5b5ce2; --teal:#0e9f9a; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(180deg, #f7f8fc 0%, #f3f5fb 100%); color:var(--ink); }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1500px; }
[data-testid="stSidebar"] { background: #10182c; }
[data-testid="stSidebar"] * { color: #eef2ff !important; }
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color:#c7d2fe !important; }
.hero { padding: 28px 30px; border-radius: 22px; background: radial-gradient(circle at 85% 10%, #7677f8 0, transparent 32%), linear-gradient(115deg,#151e3c,#343b79 65%,#4f46e5); color:white; margin-bottom: 20px; box-shadow: 0 14px 35px rgba(45,54,120,.15); }
.hero h1 { font-family:'Manrope',sans-serif; font-size:2.1rem; font-weight:800; margin:0; color:white; letter-spacing:-.04em; }
.hero p { color:#e0e7ff; margin:.55rem 0 0; font-size:1rem; max-width:800px; }
.eyebrow { color:#c4b5fd; font-size:.75rem; letter-spacing:.16em; text-transform:uppercase; font-weight:700; margin-bottom:8px; }
.section-title { font-family:'Manrope',sans-serif; font-size:1.15rem; font-weight:800; color:#172033; margin:.25rem 0 .15rem; }
.section-sub { color:#64748b; font-size:.9rem; margin-bottom:.7rem; }
.metric-card { background:rgba(255,255,255,.92); border:1px solid #e7eaf1; border-radius:17px; padding:17px 18px; min-height:118px; box-shadow:0 5px 18px rgba(31,41,55,.035); }
.metric-label { color:#64748b; font-size:.79rem; font-weight:600; }
.metric-value { color:#172033; font-family:'Manrope',sans-serif; font-size:1.75rem; font-weight:800; margin-top:7px; letter-spacing:-.04em; }
.metric-foot { color:#7c86a0; font-size:.75rem; margin-top:3px; }
.panel { background:white; border:1px solid #e7eaf1; border-radius:17px; padding:18px 20px; }
.status-pill { display:inline-block; background:#e0f2fe; color:#075985; border-radius:999px; padding:5px 10px; font-size:.74rem; font-weight:700; }
div[data-testid="stMetric"] { background:white; border:1px solid #e7eaf1; padding:17px 18px; border-radius:16px; box-shadow:0 5px 18px rgba(31,41,55,.035); }
div[data-testid="stMetricLabel"] { color:#64748b; }
div[data-testid="stMetricValue"] { font-family:'Manrope',sans-serif; }
.stTabs [data-baseweb="tab-list"] { gap:8px; }
.stTabs [data-baseweb="tab"] { border-radius:10px 10px 0 0; padding:10px 16px; }
div.stButton > button { border-radius:10px; font-weight:700; }
.small-note { color:#64748b; font-size:.82rem; }
div[data-testid="stAlert"] { border-radius:12px; }
</style>
""", unsafe_allow_html=True)

def metric_card(label: str, value: str, foot: str = ""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div><div class="metric-foot">{foot}</div></div>',
        unsafe_allow_html=True,
    )

def section(title: str, subtitle: str = ""):
    st.markdown(f'<div class="section-title">{title}</div><div class="section-sub">{subtitle}</div>',
                unsafe_allow_html=True)

def fmt_pct(x):
    return f"{x:.1%}" if pd.notna(x) else "—"

@st.cache_data
def get_data():
    return load_or_create_data()

df_original = get_data()
df = df_original.copy()

# Sidebar
with st.sidebar:
    st.markdown("## ◈ PULSE")
    st.markdown("**PRODUCT INTELLIGENCE**")
    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        ["Overview", "Experiment Lab", "Audience Insights", "Data Quality", "SQL Playbook"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("**DATA ENVIRONMENT**")
    st.markdown('<span class="status-pill">DEMO DATA · SYNTHETIC</span>', unsafe_allow_html=True)
    st.caption("This portfolio app does not use Microsoft internal data.")
    if st.button("↻ Regenerate demo data", use_container_width=True):
        new_df = generate_demo_data(seed=int(pd.Timestamp.now().timestamp()) % 100000)
        new_df.to_csv(ROOT / "data" / "product_events.csv", index=False)
        st.cache_data.clear()
        st.rerun()
    st.markdown("---")
    st.caption("Pulse Analytics · Portfolio project")

# Header
st.markdown("""
<div class="hero">
  <div class="eyebrow">PRODUCT ANALYTICS / EXPERIMENTATION</div>
  <h1>Understand what moves your product.</h1>
  <p>Explore feature adoption, evaluate an experiment, and translate user behaviour into decisions — with metrics, uncertainty, and data quality in view.</p>
</div>
""", unsafe_allow_html=True)

# Global filters
f1, f2, f3 = st.columns([1, 1, 1.3])
with f1:
    regions = ["All regions"] + sorted(df["region"].dropna().unique().tolist())
    selected_region = st.selectbox("Region", regions)
with f2:
    platforms = ["All platforms"] + sorted(df["platform"].dropna().unique().tolist())
    selected_platform = st.selectbox("Platform", platforms)
with f3:
    user_types = ["All user types"] + sorted(df["user_type"].dropna().unique().tolist())
    selected_user_type = st.selectbox("User type", user_types)

if selected_region != "All regions":
    df = df[df["region"] == selected_region]
if selected_platform != "All platforms":
    df = df[df["platform"] == selected_platform]
if selected_user_type != "All user types":
    df = df[df["user_type"] == selected_user_type]

if df.empty:
    st.warning("No users match the selected filters. Change one or more filters.")
    st.stop()

metrics = overall_metrics(df)
groups = group_metrics(df)
group_map = groups.set_index("experiment_group")
control = group_map.loc["control"] if "control" in group_map.index else None
treatment = group_map.loc["treatment"] if "treatment" in group_map.index else None
test = two_proportion_test(df)

if page == "Overview":
    section("Experiment at a glance", "A decision-ready snapshot of user adoption and conversion.")
    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("ASSIGNED USERS", f'{metrics["users"]:,}', "Unique users in selected view")
    with c2: metric_card("FEATURE ADOPTION", fmt_pct(metrics["adoption_rate_assigned"]), "Feature users / assigned users")
    with c3: metric_card("CONVERSION RATE", fmt_pct(metrics["conversion_rate"]), "Converted users / assigned users")
    with c4: metric_card("EXPOSURE RATE", fmt_pct(metrics["exposure_rate"]), "Users recorded as exposed")

    st.write("")
    left, right = st.columns([1.25, 1])
    with left:
        section("Adoption & conversion by experiment", "Compare control and treatment using the same user-level definitions.")
        chart_df = groups.melt(id_vars="experiment_group", value_vars=["adoption_rate", "conversion_rate"],
                               var_name="metric", value_name="rate")
        chart_df["metric"] = chart_df["metric"].map({"adoption_rate":"Feature adoption", "conversion_rate":"Conversion"})
        fig = px.bar(chart_df, x="experiment_group", y="rate", color="metric", barmode="group",
                     text=chart_df["rate"].map(lambda x: f"{x:.1%}"),
                     color_discrete_sequence=["#6366f1", "#14b8a6"])
        fig.update_layout(height=360, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="white",
                          plot_bgcolor="white", yaxis_tickformat=".0%", legend_title_text="",
                          xaxis_title="", yaxis_title="Rate", font=dict(family="DM Sans", color="#475569"))
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(fig, use_container_width=True)
    with right:
        section("Experiment readout", "Treatment minus control; statistical significance is not the same as business importance.")
        st.metric("Absolute conversion lift", f'{test["absolute_lift"]:+.2%}')
        st.metric("Relative conversion lift", f'{test["relative_lift"]:+.1%}' if pd.notna(test["relative_lift"]) else "—")
        st.metric("Two-sided p-value", f'{test["p_value"]:.4f}')
        st.caption(f'95% CI for absolute lift: [{test["ci_low"]:+.2%}, {test["ci_high"]:+.2%}]')
        if test["significant_05"]:
            st.success("The observed difference is statistically significant at the 5% level in this demo.")
        else:
            st.info("The observed difference is not statistically significant at the 5% level in this demo.")
    st.write("")
    section("Audience snapshot", "Use these breakdowns to identify follow-up questions, not to overclaim causality.")
    g1, g2 = st.columns(2)
    with g1:
        seg = segment_summary(df, "platform")
        fig2 = px.bar(seg, x="platform", y="rate", color="experiment_group", barmode="group",
                      color_discrete_sequence=["#6366f1", "#14b8a6"], labels={"rate":"Conversion rate","platform":"Platform","experiment_group":"Group"})
        fig2.update_layout(height=300, margin=dict(l=5,r=5,t=15,b=5), paper_bgcolor="white", plot_bgcolor="white", yaxis_tickformat=".0%")
        st.plotly_chart(fig2, use_container_width=True)
    with g2:
        daily = df.groupby(["assigned_at", "experiment_group"], observed=False)["converted"].mean().reset_index()
        fig3 = px.line(daily, x="assigned_at", y="converted", color="experiment_group", markers=True,
                       color_discrete_sequence=["#6366f1", "#14b8a6"], labels={"converted":"Conversion rate","assigned_at":"Assignment date","experiment_group":"Group"})
        fig3.update_layout(height=300, margin=dict(l=5,r=5,t=15,b=5), paper_bgcolor="white", plot_bgcolor="white", yaxis_tickformat=".0%")
        st.plotly_chart(fig3, use_container_width=True)
    st.info("Interpretation rule: check experiment assignment, exposure tracking, sample size, guardrails and segment balance before recommending a rollout.")

elif page == "Experiment Lab":
    section("Experiment lab", "Inspect the primary metric, effect size, uncertainty, and key assumptions.")
    outcome_label = st.selectbox("Primary outcome", ["Conversion", "Feature adoption", "Exposure"], index=0)
    outcome_col = {"Conversion":"converted", "Feature adoption":"feature_used", "Exposure":"exposed"}[outcome_label]
    test = two_proportion_test(df, outcome_col)
    a, b, c = st.columns(3)
    with a: st.metric("Control rate", fmt_pct(test["control_rate"]), f'{test["control_conversions"]:,} / {test["control_n"]:,}')
    with b: st.metric("Treatment rate", fmt_pct(test["treatment_rate"]), f'{test["treatment_conversions"]:,} / {test["treatment_n"]:,}')
    with c: st.metric("Absolute difference", f'{test["absolute_lift"]:+.2%}', "Treatment − control")
    st.write("")
    # Confidence interval plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[test["ci_low"], test["ci_high"]], y=[0,0], mode="lines",
                             line=dict(color="#6366f1", width=8), name="95% confidence interval"))
    fig.add_trace(go.Scatter(x=[test["absolute_lift"]], y=[0], mode="markers",
                             marker=dict(color="#0f172a", size=15), name="Observed difference"))
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8")
    fig.update_layout(height=240, margin=dict(l=15,r=15,t=25,b=20), paper_bgcolor="white",
                      plot_bgcolor="white", xaxis_title="Absolute rate difference", yaxis=dict(visible=False),
                      xaxis_tickformat=".1%", legend=dict(orientation="h", y=1.15), title="Effect size and 95% confidence interval")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("### Statistical readout")
    st.write(f'- **Test:** two-sided two-proportion z-test')
    st.write(f'- **z-score:** `{test["z_score"]:.3f}`')
    st.write(f'- **p-value:** `{test["p_value"]:.4f}`')
    st.write(f'- **95% CI:** `[{test["ci_low"]:+.2%}, {test["ci_high"]:+.2%}]`')
    if test["significant_05"]:
        st.success("At α = 0.05, the observed difference is statistically significant under this test's assumptions.")
    else:
        st.warning("At α = 0.05, this test does not provide sufficient evidence of a difference.")
    st.markdown("### Before making a product decision")
    st.checkbox("The primary metric was chosen before looking at results", key="pre_registered")
    st.checkbox("Random assignment and exposure logging were checked", key="randomization_checked")
    st.checkbox("Guardrail metrics and sample-ratio mismatch were reviewed", key="guardrails_checked")
    st.checkbox("Segment cuts are exploratory and multiple comparisons are considered", key="segments_checked")
    st.caption("The checkboxes are a review checklist only; checking them does not verify the assumptions automatically.")

elif page == "Audience Insights":
    section("Audience insights", "Explore differences by user type, platform, and region.")
    dimension = st.selectbox("Break down by", ["platform", "user_type", "region"])
    outcome = st.selectbox("Measure", ["converted", "feature_used", "support_contact"], format_func=lambda x: {
        "converted":"Conversion rate", "feature_used":"Feature adoption rate", "support_contact":"Support contact rate"
    }[x])
    seg = segment_summary(df, dimension, outcome)
    fig = px.bar(seg, x=dimension, y="rate", color="experiment_group", barmode="group",
                 text=seg["rate"].map(lambda x: f"{x:.1%}"),
                 color_discrete_sequence=["#6366f1", "#14b8a6"],
                 labels={"rate":"Rate", "experiment_group":"Experiment group"})
    fig.update_layout(height=390, margin=dict(l=10,r=10,t=20,b=10), paper_bgcolor="white", plot_bgcolor="white",
                      yaxis_tickformat=".0%", legend_title_text="")
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(seg.rename(columns={"outcome_count":"events_or_users", "rate":"rate"}), use_container_width=True, hide_index=True)
    st.markdown("### Questions to investigate")
    st.markdown("- Is the pattern consistent across major segments?\n- Are segment sizes large enough for reliable conclusions?\n- Could differences be explained by traffic mix or exposure logging?\n- Is this breakdown pre-planned or one of many exploratory comparisons?")
    st.warning("Segment-level differences are exploratory. Avoid declaring a segment-specific treatment effect without an appropriate statistical test and multiplicity plan.")

elif page == "Data Quality":
    section("Data quality & assumptions", "A good analysis makes data limitations visible before drawing conclusions.")
    quality = data_quality_report(df)
    st.dataframe(quality, use_container_width=True, hide_index=True)
    st.markdown("### Experiment balance")
    balance = df.groupby("experiment_group", observed=False).agg(
        users=("user_id","nunique"),
        new_user_share=("user_type", lambda s: (s == "New").mean()),
        web_share=("platform", lambda s: (s == "Web").mean()),
        exposure_rate=("exposed","mean"),
    ).reset_index()
    st.dataframe(balance.style.format({"new_user_share":"{:.1%}","web_share":"{:.1%}","exposure_rate":"{:.1%}"}), use_container_width=True, hide_index=True)
    st.markdown("### Limitations")
    st.markdown("""
    - This is synthetic demonstration data, not real user behaviour.
    - One row represents one assigned user; it is not a raw clickstream.
    - The primary conversion metric uses all assigned users as the denominator.
    - A simple Wald confidence interval and two-proportion z-test are used for demonstration; other methods may be preferable for some designs.
    - Segment findings are exploratory and can be affected by multiple comparisons.
    - The dashboard does not establish real business impact or revenue ROI.
    """)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, file_name="product_events_filtered.csv", mime="text/csv")

elif page == "SQL Playbook":
    section("SQL playbook", "Copy-ready queries for the core product analytics questions.")
    st.markdown("Queries below use a table named `product_events`. Adjust date functions to match your SQL engine.")
    queries = {
        "Group conversion rate": """SELECT experiment_group,
       COUNT(DISTINCT user_id) AS users,
       SUM(converted) AS conversions,
       1.0 * SUM(converted) / COUNT(DISTINCT user_id) AS conversion_rate
FROM product_events
GROUP BY experiment_group;""",
        "Feature adoption by platform": """SELECT platform, experiment_group,
       COUNT(DISTINCT user_id) AS users,
       SUM(feature_used) AS feature_users,
       1.0 * SUM(feature_used) / COUNT(DISTINCT user_id) AS adoption_rate
FROM product_events
GROUP BY platform, experiment_group
ORDER BY platform, experiment_group;""",
        "Rank segments by adoption": """WITH adoption AS (
    SELECT user_type, platform,
           COUNT(DISTINCT user_id) AS users,
           1.0 * SUM(feature_used) / COUNT(DISTINCT user_id) AS adoption_rate
    FROM product_events
    GROUP BY user_type, platform
)
SELECT *,
       DENSE_RANK() OVER (ORDER BY adoption_rate DESC) AS adoption_rank
FROM adoption;""",
        "Exposure tracking health": """SELECT experiment_group,
       COUNT(*) AS assigned_users,
       SUM(exposed) AS exposed_users,
       1.0 * SUM(exposed) / COUNT(*) AS exposure_rate
FROM product_events
GROUP BY experiment_group;"""
    }
    chosen = st.selectbox("Choose a query", list(queries.keys()))
    st.code(queries[chosen], language="sql")
    st.download_button("Download SQL playbook", data=(ROOT / "sql" / "product_analytics_queries.sql").read_text(),
                       file_name="product_analytics_queries.sql", mime="text/plain")
    st.caption("These are examples to practise SQL reasoning. To execute them, load the CSV into a database table named product_events.")

st.markdown("---")
st.markdown('<div class="small-note">PULSE Product Intelligence · Portfolio demo · Synthetic data · Interpret results with care</div>', unsafe_allow_html=True)
