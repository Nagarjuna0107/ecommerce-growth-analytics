-- 04_kpi_metrics.sql
-- Computes executive business KPIs: AOV, Repeat Purchase Rate, Channel Economics, Gross Margins

-- 1. Executive Summary
SELECT 
    COUNT(DISTINCT o.order_id) AS total_delivered_orders,
    COUNT(DISTINCT o.customer_id) AS total_purchasing_customers,
    ROUND(SUM(oi.total_item_revenue), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * oi.unit_cost), 2) AS total_cogs,
    ROUND(SUM(oi.total_item_revenue) - SUM(oi.quantity * oi.unit_cost), 2) AS gross_profit,
    ROUND(((SUM(oi.total_item_revenue) - SUM(oi.quantity * oi.unit_cost)) / SUM(oi.total_item_revenue)) * 100.0, 2) AS gross_margin_pct,
    ROUND(SUM(oi.total_item_revenue) / COUNT(DISTINCT o.order_id), 2) AS average_order_value_aov
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered';

-- 2. Acquisition Channel Efficiency
SELECT 
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) AS acquired_customers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.total_item_revenue), 2) AS channel_revenue,
    ROUND(SUM(oi.total_item_revenue) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_acquired_user,
    ROUND(CAST(COUNT(DISTINCT o.order_id) AS FLOAT) / COUNT(DISTINCT c.customer_id), 2) AS orders_per_customer
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'Delivered'
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.acquisition_channel
ORDER BY channel_revenue DESC;
