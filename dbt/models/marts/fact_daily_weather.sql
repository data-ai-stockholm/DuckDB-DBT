{{ config(materialized='table') }}

SELECT
    station_id,
    observation_date,
    COUNT(*) as observation_count,
    AVG(temperature_degC) as avg_temperature_degC,
    MIN(temperature_degC) as min_temperature_degC,
    MAX(temperature_degC) as max_temperature_degC,
    AVG(dewpoint_degC) as avg_dewpoint_degC,
    AVG(wind_speed_mps) as avg_wind_speed_mps,
    MAX(wind_speed_mps) as max_wind_speed_mps
FROM {{ ref('fact_observations') }}
GROUP BY
    station_id,
    observation_date
