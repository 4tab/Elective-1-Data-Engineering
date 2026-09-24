-- 1) Top pickup zones by revenue with a window-function ranking.
WITH zone_revenue AS (
    SELECT pickup_zone, borough, SUM(revenue) AS revenue
    FROM mart_daily_zone_performance
    GROUP BY 1, 2
)
SELECT
    *,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
FROM zone_revenue
ORDER BY revenue_rank
LIMIT 10;

-- 2) Peak demand hour for each day using a CTE + window function.
WITH ranked AS (
    SELECT
        date_key,
        pickup_hour,
        trips,
        ROW_NUMBER() OVER (PARTITION BY date_key ORDER BY trips DESC) AS rn
    FROM mart_hourly_demand
)
SELECT date_key, pickup_hour, trips
FROM ranked
WHERE rn = 1
ORDER BY date_key;

-- 3) Join fact data to both pickup and dropoff zones.
SELECT
    p.zone_name AS pickup_zone,
    d.zone_name AS dropoff_zone,
    COUNT(*) AS trips,
    ROUND(AVG(f.total_amount), 2) AS avg_fare
FROM fact_trip f
JOIN dim_zone p ON f.pickup_zone_key = p.zone_key
JOIN dim_zone d ON f.dropoff_zone_key = d.zone_key
GROUP BY 1, 2
ORDER BY trips DESC
LIMIT 20;
