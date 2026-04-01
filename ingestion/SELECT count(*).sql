SELECT count(*) 
FROM analytics.fact_sales 
WHERE price <= 0 OR order_id IS NULL;
