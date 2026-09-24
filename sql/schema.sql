CREATE OR REPLACE TABLE dim_date AS
SELECT DISTINCT
    CAST(tpep_pickup_datetime AS DATE) AS date_key,
    EXTRACT(YEAR FROM tpep_pickup_datetime)::INTEGER AS year,
    EXTRACT(MONTH FROM tpep_pickup_datetime)::INTEGER AS month,
    EXTRACT(DAY FROM tpep_pickup_datetime)::INTEGER AS day,
    STRFTIME(tpep_pickup_datetime, '%A') AS day_name,
    EXTRACT(DOW FROM tpep_pickup_datetime)::INTEGER AS day_of_week,
    EXTRACT(ISODOW FROM tpep_pickup_datetime)::INTEGER AS iso_day_of_week,
    EXTRACT(WEEK FROM tpep_pickup_datetime)::INTEGER AS week_of_year
FROM curated_trips;

CREATE OR REPLACE TABLE dim_vendor AS
SELECT DISTINCT VendorID AS vendor_key FROM curated_trips WHERE VendorID IS NOT NULL;

CREATE OR REPLACE TABLE dim_payment_type AS
SELECT * FROM (VALUES
    (0, 'Flex Fare trip'),
    (1, 'Credit card'),
    (2, 'Cash'),
    (3, 'No charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided trip')
) AS t(payment_type_key, payment_type_name);

CREATE OR REPLACE TABLE dim_rate_code AS
SELECT * FROM (VALUES
    (1, 'Standard rate'),
    (2, 'JFK'),
    (3, 'Newark'),
    (4, 'Nassau or Westchester'),
    (5, 'Negotiated fare'),
    (6, 'Group ride'),
    (99, 'Null/unknown')
) AS t(rate_code_key, rate_code_name);