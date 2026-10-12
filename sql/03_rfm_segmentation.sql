-- 03_rfm_segmentation.sql
-- Performs RFM segmentation using NTILE(5) scoring across Recency, Frequency, and Monetary parameters

WITH base_rfm AS (
    SELECT 
        c.customer_id,
        c.city,
        c.acquisition_channel,
        -- Reference benchmark date is latest date in dataset (e.g. 2026-10-01)
        CAST(JULIANDAY('2026-10-01') - JULIANDAY(MAX(o.order_date)) AS INTEGER) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency_orders,
        ROUND(SUM(oi.total_item_revenue), 2) AS monetary_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id, c.city, c.acquisition_channel
),

rfm_scoring AS (
    SELECT 
        customer_id,
        city,
        acquisition_channel,
        recency_days,
        frequency_orders,
        monetary_spend,
        -- Higher score is better: Lowest recency days gets 5, highest frequency gets 5, highest spend gets 5
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency_orders ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary_spend ASC) AS m_score
    FROM base_rfm
),

rfm_composite AS (
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
        (r_score || f_score || m_score) AS rfm_cell,
        ROUND((r_score + f_score + m_score) / 3.0, 2) AS avg_rfm_score
    FROM rfm_scoring
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
    rfm_cell,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN f_score >= 3 AND m_score >= 3 AND r_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Recent Promising Buyers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk (High Spenders)'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score >= 3 THEN 'Hibernating Big Spenders'
        ELSE 'Casual / Lost'
    END AS customer_segment
FROM rfm_composite;
