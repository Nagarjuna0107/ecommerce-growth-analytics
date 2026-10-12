-- 02_cohort_retention.sql
-- Computes the Monthly Customer Cohort Retention Matrix

WITH customer_first_purchase AS (
    SELECT 
        customer_id,
        MIN(DATE(order_date)) AS first_order_date,
        STRFTIME('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    WHERE status = 'Delivered'
    GROUP BY customer_id
),

customer_activities AS (
    SELECT 
        o.customer_id,
        fp.cohort_month,
        STRFTIME('%Y-%m', o.order_date) AS activity_month,
        (
            (CAST(STRFTIME('%Y', o.order_date) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 1, 4) AS INTEGER)) * 12 +
            (CAST(STRFTIME('%m', o.order_date) AS INTEGER) - CAST(SUBSTR(fp.cohort_month, 6, 2) AS INTEGER))
        ) AS month_index
    FROM orders o
    JOIN customer_first_purchase fp ON o.customer_id = fp.customer_id
    WHERE o.status = 'Delivered'
    GROUP BY o.customer_id, fp.cohort_month, activity_month, month_index
),

cohort_size AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_cohort_customers
    FROM customer_first_purchase
    GROUP BY cohort_month
),

retention_counts AS (
    SELECT 
        ca.cohort_month,
        ca.month_index,
        COUNT(DISTINCT ca.customer_id) AS active_customers
    FROM customer_activities ca
    GROUP BY ca.cohort_month, ca.month_index
)

SELECT 
    rc.cohort_month,
    cs.total_cohort_customers,
    rc.month_index,
    rc.active_customers,
    ROUND((CAST(rc.active_customers AS FLOAT) / cs.total_cohort_customers) * 100.0, 2) AS retention_rate_pct
FROM retention_counts rc
JOIN cohort_size cs ON rc.cohort_month = cs.cohort_month
ORDER BY rc.cohort_month ASC, rc.month_index ASC;
