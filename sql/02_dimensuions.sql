CREATE OR REPLACE TABLE dim_zone AS
SELECT
    CAST(LocationID AS INTEGER) AS zone_key,
    CAST(Borough AS VARCHAR) AS borough,
    CAST(zone AS VARCHAR) AS zone_name,
    CAST(service_zone AS VARCHAR) AS service_zone
FROM zones;