{{ config(materialized='table') }}

SELECT
    observation_id,
    observation_timestamp,
    station_id,
    temperature_degC,
    dewpoint_degC,
    wind_speed_mps,
    DATE_TRUNC('day', observation_timestamp) as observation_date,
    EXTRACT(HOUR FROM observation_timestamp) as observation_hour,
    EXTRACT(DOW FROM observation_timestamp) as day_of_week
FROM {{ ref('stg_observations') }}