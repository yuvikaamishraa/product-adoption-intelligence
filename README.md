# Product Adoption & A/B Testing Intelligence

A portfolio project that investigates whether a product onboarding experiment changes feature adoption and conversion.

## 🚀 Live Demo

[Open Product Adoption & A/B Testing Intelligence Dashboard](https://appuct-adoption-intelligence-3g45kvagev3t52kyuyqq3c.streamlit.app/)

An interactive dashboard for analyzing feature adoption, onboarding experiments, conversion rates, statistical uncertainty, audience segments, and data quality using synthetic demonstration data.

---

## Important data note
The app generates **synthetic demonstration data locally** on first run. It is not Microsoft data, not real customer data, and not evidence of a real product experiment. The project is designed to demonstrate an end-to-end analytical workflow. Replace the generated CSV with a properly documented public dataset when you are ready, and update the README to describe that dataset accurately.

## Features
- Executive dashboard for experiment health and product adoption
- Control vs treatment analysis
- Two-proportion z-test and confidence interval for conversion difference
- Segment-level exploratory analysis
- Data-quality checks and caveats
- SQL examples for common product analytics questions
- CSV export of generated events

## Run in VS Code (Windows)
1. Install Python 3.10+ and VS Code.
2. Download and unzip this project.
3. In VS Code, select **File → Open Folder** and open `product-adoption-intelligence`.
4. Open **Terminal → New Terminal**.
5. Create a virtual environment:
   ```powershell
   py -m venv .venv
   ```
6. Activate it:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```
7. Install dependencies:
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
8. Start the app:
   ```powershell
   streamlit run app.py
   ```
9. Your browser should open automatically. If it doesn't, open the local URL printed in the terminal, usually `http://localhost:8501`.

## Project structure
```text
product-adoption-intelligence/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── .gitkeep
├── sql/
│   └── product_analytics_queries.sql
└── src/
    ├── __init__.py
    ├── analytics.py
    └── data.py
```

## Methodology
- The synthetic dataset assigns users to control or treatment groups.
- The primary metric is user-level conversion rate: converted users / assigned users.
- The experiment result uses a two-sided two-proportion z-test and a 95% confidence interval for the absolute difference (treatment minus control).
- Segment comparisons are exploratory and should not be interpreted as causal proof without a pre-registered design, sufficient sample size, and multiple-comparison controls.
- The dashboard reports effect size and uncertainty, not just a p-value.

## Next steps to make this stronger
- Replace synthetic data with a documented public event-level dataset.
- Add a pre-analysis plan defining the primary metric and guardrail metrics.
- Add unit tests for metric calculations.
- Add a proper database (SQLite/PostgreSQL) and run SQL queries against it.
- Ask a peer to review the analysis and document changes made from feedback.
## Tech Stack

* **Python** — data processing and statistical analysis
* **Streamlit** — interactive analytics dashboard
* **Pandas** — data manipulation
* **Statistical testing** — two-proportion z-test and 95% confidence intervals
* **SQL** — product analytics queries

## Dashboard Preview

Screenshots of the dashboard will be added here.

Planned views:

* Executive Overview
* Experiment Lab
* Audience Insights
* Data Quality
* SQL Playbook

## Limitations

* The current results use synthetic demonstration data and do not represent a real product experiment.
* Statistical significance in simulated data does not establish a real-world business impact.
* Segment-level comparisons are exploratory.
* A production-ready version should include experiment assignment validation, guardrail metrics, and automated tests.
