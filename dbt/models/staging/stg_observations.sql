{{ config(materialized='view') }}

SELECT
    observation_timestamp,
    observation_id,
    station_id,
    temperature_degC,
    dewpoint_degC,
    wind_speed_mps
FROM {{ source('weather', 'observations') }}
WHERE observation_timestamp IS NOT NULL
