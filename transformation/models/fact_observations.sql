{{ config(materialized='table') }}

WITH cleaned_observations AS (
    SELECT
        observation_timestamp,
        observation_id,
        station_id,
        station_name,
        coordinates,
        
        -- Temperature metrics (convert to Celsius if needed, remove invalid values)
        CASE 
            WHEN temperature_degC BETWEEN -100 AND 60 THEN temperature_degC 
            ELSE NULL 
        END AS temperature_degC,
        
        CASE 
            WHEN dewpoint_degC BETWEEN -100 AND 50 THEN dewpoint_degC 
            ELSE NULL 
        END AS dewpoint_degC,
        
        -- Wind metrics (remove invalid values)
        CASE 
            WHEN wind_speed_kmh >= 0 AND wind_speed_kmh <= 500 THEN wind_speed_kmh 
            ELSE NULL 
        END AS wind_speed_kmh,
        
        CASE 
            WHEN wind_gust_kmh >= 0 AND wind_gust_kmh <= 500 THEN wind_gust_kmh 
            ELSE NULL 
        END AS wind_gust_kmh,
        
        CASE 
            WHEN wind_direction_deg >= 0 AND wind_direction_deg <= 360 THEN wind_direction_deg 
            ELSE NULL 
        END AS wind_direction_deg,
        
        -- Pressure metrics
        CASE 
            WHEN barometric_pressure_Pa > 0 THEN barometric_pressure_Pa 
            ELSE NULL 
        END AS barometric_pressure_Pa,
        
        CASE 
            WHEN sea_level_pressure_Pa > 0 THEN sea_level_pressure_Pa 
            ELSE NULL 
        END AS sea_level_pressure_Pa,
        
        -- Other metrics
        CASE 
            WHEN visibility_m >= 0 THEN visibility_m 
            ELSE NULL 
        END AS visibility_m,
        
        CASE 
            WHEN relative_humidity_percent >= 0 AND relative_humidity_percent <= 100 
            THEN relative_humidity_percent 
            ELSE NULL 
        END AS relative_humidity_percent,
        
        CASE 
            WHEN precipitation_3h_mm >= 0 THEN precipitation_3h_mm 
            ELSE NULL 
        END AS precipitation_3h_mm,
        
        elevation_m,
        wind_chill_degC,
        heat_index_degC,
        
        -- Extract date parts for easier analysis
        DATE_TRUNC('day', observation_timestamp) AS observation_date,
        EXTRACT(YEAR FROM observation_timestamp) AS observation_year,
        EXTRACT(MONTH FROM observation_timestamp) AS observation_month,
        EXTRACT(DAY FROM observation_timestamp) AS observation_day,
        EXTRACT(HOUR FROM observation_timestamp) AS observation_hour
        
    FROM read_parquet('../ingestion_data/observations/*/*/observation_*.parquet')
    WHERE observation_timestamp IS NOT NULL
        AND station_id IS NOT NULL
)

SELECT * 
FROM cleaned_observations
WHERE temperature_degC IS NOT NULL  -- At least have temperature data
    OR wind_speed_kmh IS NOT NULL
    OR precipitation_3h_mm IS NOT NULL