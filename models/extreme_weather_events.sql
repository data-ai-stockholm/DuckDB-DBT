{{ config(materialized='table') }}

WITH daily_weather AS (
    SELECT *
    FROM {{ ref('fact_daily_weather') }}
),

extreme_events AS (
    SELECT
        observation_date,
        observation_year,
        observation_month,
        station_id,
        station_name,
        geometry_coordinates,
        geometry_coordinates[2] AS location_lat,
        geometry_coordinates[1] AS location_lon,
        
        -- Temperature extremes
        CASE WHEN max_temp_degC >= 40 THEN 'Extreme Heat' END AS heat_event,
        CASE WHEN min_temp_degC <= -30 THEN 'Extreme Cold' END AS cold_event,
        CASE WHEN (max_temp_degC - min_temp_degC) >= 30 THEN 'Large Temp Swing' END AS temp_swing_event,
        
        -- Wind extremes
        CASE WHEN max_wind_speed_kmh >= 75 THEN 'High Winds' END AS wind_event,
        CASE WHEN max_wind_gust_kmh >= 100 THEN 'Extreme Gusts' END AS gust_event,
        
        -- Precipitation extremes
        CASE WHEN total_precipitation_mm >= 50 THEN 'Heavy Precipitation' END AS precip_event,
        
        -- Actual values
        max_temp_degC,
        min_temp_degC,
        max_wind_speed_kmh,
        max_wind_gust_kmh,
        total_precipitation_mm
        
    FROM daily_weather
)

SELECT
    *,
    -- Create a combined event type field
    CONCAT_WS(', ', 
        heat_event, 
        cold_event, 
        temp_swing_event, 
        wind_event, 
        gust_event, 
        precip_event
    ) AS event_types
FROM extreme_events
WHERE heat_event IS NOT NULL
    OR cold_event IS NOT NULL
    OR temp_swing_event IS NOT NULL
    OR wind_event IS NOT NULL
    OR gust_event IS NOT NULL
    OR precip_event IS NOT NULL
ORDER BY observation_date DESC