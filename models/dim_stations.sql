-- models/dim_stations.sql
{{ config(materialized='table') }}

SELECT
    DISTINCT
        station_id,
        station_name,
        geometry_coordinates,
        geometry_coordinates[1] AS location_lat,
        geometry_coordinates[2] AS location_lon
FROM {{ source('main', 'observations') }}
WHERE station_id IS NOT NULL