{{ config(materialized='table') }}

SELECT DISTINCT
    station_id,
    MIN(observation_timestamp) as first_observation,
    MAX(observation_timestamp) as last_observation,
    COUNT(*) as total_observations
FROM {{ ref('stg_observations') }}
WHERE station_id IS NOT NULL
GROUP BY station_id