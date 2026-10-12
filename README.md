# E-Commerce Growth and Customer Analytics Platform

An end-to-end Data and Business Intelligence platform designed to analyze customer purchase lifecycles, monthly cohort retention drop-offs, and RFM (Recency, Frequency, Monetary) behavioral segmentation across 10,000+ transactional records.

---

## Executive Summary and Key Findings

1. **Cohort Retention Plateau:**
   - First-month drop-off (M+0 to M+1) averages ~72%, consistent with typical D2C benchmarks.
   - Customers who make a repeat purchase in Month 2 (M+2) demonstrate an 80% higher lifetime value (LTV) than single-order customers.
2. **RFM Segmentation Dynamics:**
   - **Champions (Top 11% of users):** Drive approximately 38% of total gross revenue.
   - **At Risk / High Spenders (14% of users):** Customers who previously spent over INR 6,000 across 3 or more orders but have not repurchased in over 60 days. Re-engaging this cluster represents an estimated INR 3.2M pipeline recovery opportunity.
3. **Channel Economics:**
   - **Organic Search and Email Campaigns** exhibit the highest LTV-to-Acquisition efficiency, yielding an average revenue of INR 5,400+ per user compared to INR 3,800 on Paid Social ads.

---

## Tech Stack and Analytical Architecture

- **Database and Querying:** SQLite / MySQL Relational Schema (Customers, Products, Orders, Order Items) with foreign keys and analytical B-Tree indices.
- **Advanced SQL:**
  - Common Table Expressions (CTEs)
  - Window Functions (NTILE(5), ROW_NUMBER(), date arithmetic)
  - Cohort activity indexing and multi-table joins.
- **Data Engineering:** Python, Pandas, NumPy for transactional data generation and ETL ingestion.
- **Interactive BI Dashboard:** Streamlit and Plotly Express for exploratory data analysis, retention heatmaps, and RFM bubble distributions.

---

## Project Structure

```
ecommerce-growth-analytics/
├── app.py                         # Streamlit interactive analytics web application
├── data/
│   ├── raw_ecommerce_data.csv     # Granular item-level transactional records
│   └── ecommerce.db               # Normalized SQLite database with indexed tables
├── sql/
│   ├── 01_schema.sql              # Relational DDL tables and indexes
│   ├── 02_cohort_retention.sql    # Monthly cohort retention matrix CTEs
│   ├── 03_rfm_segmentation.sql    # RFM segmentation scoring via NTILE(5)
│   └── 04_kpi_metrics.sql         # Executive growth metrics and channel LTV
└── requirements.txt               # Dependencies (streamlit, plotly, pandas, etc.)
```

---

## How to Run the Dashboard Locally

```bash
# 1. Navigate to the project directory
cd ecommerce-growth-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the Streamlit Dashboard
streamlit run app.py
```

The interactive dashboard opens in your browser at `http://localhost:8501`.

---

## Business Recommendations for Growth Teams

1. **Automated Re-engagement Sequences:** Trigger targeted email incentives for the At-Risk High Spenders segment when recency exceeds 45 days.
2. **Day-14 Post-Delivery Follow-Up:** Target first-time buyers with complementary accessories to drive Month-1 retention upward.
3. **Channel Re-allocation:** Shift 15% of underperforming top-of-funnel social ad spend into retargeting email retention campaigns to improve blended customer acquisition cost (CAC).
