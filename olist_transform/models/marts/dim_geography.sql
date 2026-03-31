{{ config(materialized='table') }}

WITH base_geography AS (
    -- Clean up the raw geolocation data (keep it distinct by city/state)
    SELECT DISTINCT
        geolocation_zip_code_prefix AS zip_code_prefix,
        geolocation_city AS city,
        geolocation_state AS state_code
    FROM {{ source('raw', 'raw_olist_geolocation') }}
)

SELECT
    zip_code_prefix,
    city,
    state_code,
    -- Clustering into Macro-Regions (Independent Research Flex)
    CASE 
        WHEN state_code IN ('AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO') THEN 'North'
        WHEN state_code IN ('AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE') THEN 'Northeast'
        WHEN state_code IN ('DF', 'GO', 'MT', 'MS') THEN 'Central-West'
        WHEN state_code IN ('ES', 'MG', 'RJ', 'SP') THEN 'Southeast'
        WHEN state_code IN ('PR', 'RS', 'SC') THEN 'South'
        ELSE 'Unknown'
    END AS macro_region
FROM base_geography
