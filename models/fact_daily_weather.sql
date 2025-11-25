{{ config(materialized='table') }}

SELECT
    observation_date,
    observation_year,
    observation_month,
    station_id,
    station_name,
    geometry_coordinates,
    
    -- Temperature aggregates
    ROUND(AVG(temperature_degC), 2) AS avg_temp_degC,
    ROUND(MIN(temperature_degC), 2) AS min_temp_degC,
    ROUND(MAX(temperature_degC), 2) AS max_temp_degC,
    
    -- Wind aggregates
    ROUND(AVG(wind_speed_kmh), 2) AS avg_wind_speed_kmh,
    ROUND(MAX(wind_speed_kmh), 2) AS max_wind_speed_kmh,
    ROUND(MAX(wind_gust_kmh), 2) AS max_wind_gust_kmh,
    
    -- Precipitation
    ROUND(SUM(precipitation_3h_mm), 2) AS total_precipitation_mm,
    
    -- Humidity
    ROUND(AVG(relative_humidity_percent), 2) AS avg_humidity_percent,
    
    -- Pressure
    ROUND(AVG(barometric_pressure_Pa), 2) AS avg_pressure_Pa,
    
FROM {{ ref('fact_observations') }}
GROUP BY 
    observation_date,
    observation_year,
    observation_month,
    station_id,
    station_name,
    geometry_coordinates