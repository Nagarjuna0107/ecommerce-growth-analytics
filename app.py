import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="E-Commerce Growth and Customer Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database Connection
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "ecommerce.db")

@st.cache_data
def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 14px;
        text-align: center;
    }
    .metric-title {
        font-size: 0.8rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 1.5rem;
        color: #0F172A;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.title("E-Commerce Growth and Customer Analytics Platform")
st.caption("Customer Lifecycle, Cohort Retention, and RFM Segmentation Analytics Engine")

# Sidebar Filters
st.sidebar.header("Analytical Filters")
channel_df = run_query("SELECT DISTINCT acquisition_channel FROM customers")
channels = ["All Channels"] + channel_df["acquisition_channel"].tolist()
selected_channel = st.sidebar.selectbox("Acquisition Channel", channels)

city_df = run_query("SELECT DISTINCT city FROM customers")
cities = ["All Cities"] + city_df["city"].tolist()
selected_city = st.sidebar.selectbox("Customer Geography / City", cities)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Executive KPIs",
    "Cohort Retention Matrix",
    "RFM Customer Segmentation",
    "Category and Channel Insights"
])

# ----------------- TAB 1: EXECUTIVE KPIS -----------------
with tab1:
    st.subheader("Executive Performance Scorecard")

    where_clauses = ["o.status = 'Delivered'"]
    if selected_channel != "All Channels":
        where_clauses.append(f"c.acquisition_channel = '{selected_channel}'")
    if selected_city != "All Cities":
        where_clauses.append(f"c.city = '{selected_city}'")
    where_str = " AND ".join(where_clauses)

    kpi_query = f"""
    SELECT 
        COUNT(DISTINCT o.order_id) AS total_orders,
        COUNT(DISTINCT o.customer_id) AS active_customers,
        ROUND(SUM(oi.total_item_revenue), 2) AS total_revenue,
        ROUND(SUM(oi.quantity * oi.unit_cost), 2) AS total_cogs,
        ROUND(SUM(oi.total_item_revenue) - SUM(oi.quantity * oi.unit_cost), 2) AS gross_profit,
        ROUND(SUM(oi.total_item_revenue) / COUNT(DISTINCT o.order_id), 2) AS aov
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE {where_str};
    """
    kpis = run_query(kpi_query).iloc[0]

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Revenue", f"INR {kpis['total_revenue']:,.0f}")
    with col2:
        st.metric("Gross Profit", f"INR {kpis['gross_profit']:,.0f}")
    with col3:
        st.metric("Delivered Orders", f"{kpis['total_orders']:,}")
    with col4:
        st.metric("Active Buyers", f"{kpis['active_customers']:,}")
    with col5:
        st.metric("Avg Order Value (AOV)", f"INR {kpis['aov']:,.0f}")

    st.markdown("---")

    trend_query = f"""
    SELECT 
        STRFTIME('%Y-%m', o.order_date) AS month,
        ROUND(SUM(oi.total_item_revenue), 2) AS revenue,
        COUNT(DISTINCT o.order_id) AS orders_count
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE {where_str}
    GROUP BY month
    ORDER BY month ASC;
    """
    trend_df = run_query(trend_query)
    fig_rev = px.line(
        trend_df, x="month", y="revenue",
        title="Monthly Revenue Trend (Delivered Orders)",
        markers=True,
        color_discrete_sequence=["#1E3A8A"]
    )
    fig_rev.update_layout(xaxis_title="Month", yaxis_title="Revenue (INR)", hovermode="x unified")
    st.plotly_chart(fig_rev, use_container_width=True)

# ----------------- TAB 2: COHORT RETENTION MATRIX -----------------
with tab2:
    st.subheader("Monthly Customer Cohort Retention Heatmap")
    st.write("Tracking repeat purchase percentage from initial acquisition month (M+0) across subsequent active months (M+1 to M+12).")

    cohort_raw_query = """
    WITH first_purchase AS (
        SELECT 
            customer_id,
            STRFTIME('%Y-%m', MIN(order_date)) AS cohort_month
        FROM orders
        WHERE status = 'Delivered'
        GROUP BY customer_id
    ),
    activities AS (
        SELECT 
            o.customer_id,
            fp.cohort_month,
            (
                (CAST(STRFTIME('%Y', o.order_date) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12 +
                (CAST(STRFTIME('%m', o.order_date) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER))
            ) AS month_index
        FROM orders o
        JOIN first_purchase fp ON o.customer_id = fp.customer_id
        WHERE o.status = 'Delivered'
        GROUP BY o.customer_id, fp.cohort_month, month_index
    ),
    cohort_size AS (
        SELECT cohort_month, COUNT(DISTINCT customer_id) AS total_users
        FROM first_purchase
        GROUP BY cohort_month
    ),
    retention AS (
        SELECT 
            a.cohort_month,
            a.month_index,
            COUNT(DISTINCT a.customer_id) AS active_users
        FROM activities a
        GROUP BY a.cohort_month, a.month_index
    )
    SELECT 
        r.cohort_month,
        cs.total_users AS cohort_size,
        r.month_index,
        ROUND((CAST(r.active_users AS FLOAT) / cs.total_users) * 100.0, 1) AS retention_pct
    FROM retention r
    JOIN cohort_size cs ON r.cohort_month = cs.cohort_month
    ORDER BY r.cohort_month ASC, r.month_index ASC;
    """
    cohort_df = run_query(cohort_raw_query)

    pivot_df = cohort_df.pivot(index="cohort_month", columns="month_index", values="retention_pct")
    pivot_df.columns = [f"M+{col}" for col in pivot_df.columns]

    fig_heat = px.imshow(
        pivot_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Cohort Retention Rate (%) Heatmap",
        labels=dict(x="Months Since First Purchase", y="Acquisition Cohort", color="Retention %")
    )
    fig_heat.update_layout(height=480)
    st.plotly_chart(fig_heat, use_container_width=True)

    with st.expander("Key Strategic Insights from Retention Analysis"):
        st.markdown("""
        - **Month 1 Drop-off:** Average retention drops from 100% in M+0 to 20-30% in M+1, standard in D2C e-commerce.
        - **Long-tail Plateau:** Users remaining active by M+3 exhibit sustained retention rates above 15%.
        - **Action Plan:** Introduce automated post-delivery engagement sequences within 14 days of the initial order.
        """)

# ----------------- TAB 3: RFM SEGMENTATION -----------------
with tab3:
    st.subheader("Customer Segmentation via RFM (Recency, Frequency, Monetary)")
    st.write("Customers are evaluated on a 1 to 5 scale across Recency, Purchase Frequency, and Monetary Value.")

    rfm_sql = """
    WITH base_rfm AS (
        SELECT 
            c.customer_id,
            c.city,
            c.acquisition_channel,
            CAST(JULIANDAY('2026-10-01') - JULIANDAY(MAX(o.order_date)) AS INTEGER) AS recency_days,
            COUNT(DISTINCT o.order_id) AS frequency_orders,
            ROUND(SUM(oi.total_item_revenue), 2) AS monetary_spend
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Delivered'
        GROUP BY c.customer_id, c.city, c.acquisition_channel
    ),
    scored AS (
        SELECT 
            *,
            NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
            NTILE(5) OVER (ORDER BY frequency_orders ASC) AS f_score,
            NTILE(5) OVER (ORDER BY monetary_spend ASC) AS m_score
        FROM base_rfm
    )
    SELECT 
        customer_id,
        city,
        acquisition_channel,
        recency_days,
        frequency_orders,
        monetary_spend,
        r_score,
        f_score,
        m_score,
        CASE 
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 3 AND m_score >= 3 AND r_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Promising'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk (High Spenders)'
            WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Hibernating Big Spenders'
            ELSE 'Casual / Lost'
        END AS segment
    FROM scored;
    """
    rfm_data = run_query(rfm_sql)

    seg_summary = rfm_data.groupby("segment").agg(
        customer_count=("customer_id", "count"),
        total_revenue=("monetary_spend", "sum"),
        avg_spend=("monetary_spend", "mean"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency_orders", "mean")
    ).reset_index().sort_values(by="total_revenue", ascending=False)

    colA, colB = st.columns([1, 1])
    with colA:
        fig_pie = px.pie(
            seg_summary,
            names="segment",
            values="total_revenue",
            title="Revenue Contribution by Customer Segment",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with colB:
        fig_bar = px.bar(
            seg_summary,
            x="segment",
            y="customer_count",
            title="Customer Count by Segment",
            color="segment",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    fig_scatter = px.scatter(
        rfm_data,
        x="recency_days",
        y="monetary_spend",
        color="segment",
        size="frequency_orders",
        hover_data=["customer_id", "city", "acquisition_channel"],
        title="RFM Distribution: Monetary Spend vs. Recency Days (Bubble Size = Order Frequency)",
        labels={"recency_days": "Recency (Days Since Last Order)", "monetary_spend": "Total Spend (INR)"}
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Export Segment Cohorts")
    csv_bytes = rfm_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Segmented Customer Base (CSV)",
        data=csv_bytes,
        file_name="rfm_customer_segments.csv",
        mime="text/csv"
    )

# ----------------- TAB 4: CATEGORY & CHANNELS -----------------
with tab4:
    st.subheader("Product Categories and Marketing Channels")

    col_cat, col_chan = st.columns(2)

    with col_cat:
        cat_query = """
        SELECT 
            p.category,
            ROUND(SUM(oi.total_item_revenue), 2) AS revenue,
            ROUND(SUM(oi.total_item_revenue) - SUM(oi.quantity * oi.unit_cost), 2) AS profit,
            SUM(oi.quantity) AS units_sold
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.status = 'Delivered'
        GROUP BY p.category
        ORDER BY revenue DESC;
        """
        cat_df = run_query(cat_query)
        fig_cat = px.bar(
            cat_df,
            x="category",
            y=["profit", "revenue"],
            barmode="group",
            title="Revenue and Gross Profit by Product Category",
            labels={"value": "Amount (INR)", "category": "Category"},
            color_discrete_map={"revenue": "#1E3A8A", "profit": "#0284C7"}
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_chan:
        chan_query = """
        SELECT 
            c.acquisition_channel,
            COUNT(DISTINCT c.customer_id) AS acquired_users,
            ROUND(SUM(oi.total_item_revenue), 2) AS total_revenue,
            ROUND(SUM(oi.total_item_revenue) / COUNT(DISTINCT c.customer_id), 2) AS ltv_per_user
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Delivered'
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        GROUP BY c.acquisition_channel
        ORDER BY total_revenue DESC;
        """
        chan_df = run_query(chan_query)
        fig_chan = px.bar(
            chan_df,
            x="acquisition_channel",
            y="ltv_per_user",
            title="Customer Lifetime Value (LTV) by Acquisition Channel",
            labels={"ltv_per_user": "Average Revenue / User (INR)", "acquisition_channel": "Channel"},
            color="acquisition_channel",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_chan, use_container_width=True)
