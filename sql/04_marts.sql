CREATE OR REPLACE TABLE mart_daily_zone_performance AS
SELECT
    f.date_key,
    p.zone_name AS pickup_zone,
    p.borough,
    COUNT(*) AS trips,
    ROUND(SUM(f.total_amount), 2) AS revenue,
    ROUND(AVG(f.trip_distance), 2) AS avg_distance_miles,
    ROUND(AVG(f.trip_duration_minutes), 2) AS avg_duration_minutes,
    ROUND(AVG(f.tip_amount), 2) AS avg_tip_amount
FROM fact_trip f
JOIN dim_zone p ON f.pickup_zone_key = p.zone_key
GROUP BY 1, 2, 3;

CREATE OR REPLACE TABLE mart_hourly_demand AS
WITH hourly AS (
    SELECT
        date_key,
        EXTRACT(HOUR FROM pickup_time)::INTEGER AS pickup_hour,
        COUNT(*) AS trips,
        SUM(total_amount) AS revenue
    FROM fact_trip
    GROUP BY 1, 2
)
SELECT
    *,
    RANK() OVER (PARTITION BY date_key ORDER BY trips DESC) AS demand_rank_for_day
FROM hourly;

CREATE OR REPLACE TABLE mart_payment_mix AS
SELECT
    p.payment_type_name,
    COUNT(*) AS trips,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS trip_share_pct,
    ROUND(AVG(f.total_amount), 2) AS avg_total_amount
FROM fact_trip f
LEFT JOIN dim_payment_type p ON f.payment_type_key = p.payment_type_key
GROUP BY 1
ORDER BY trips DESC;