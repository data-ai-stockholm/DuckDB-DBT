-- models/dim_stations.sql
{{ config(materialized='table') }}

SELECT
    DISTINCT
        station_id,
        station_name,
        coordinates[1]::DECIMAL AS location_lat,
        coordinates[2]::DECIMAL AS location_lon,
        elevation_m,
        time_zone,
        SPLIT(county, '/')[-1] AS county_id
FROM read_parquet('../ingestion_data/stations/station_group_*.parquet')
ORDER BY station_id