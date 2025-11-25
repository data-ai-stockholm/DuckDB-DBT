# Writes the observations data from Parquet files into a DuckDB database table.

import duckdb

conn = duckdb.connect("weather_reports.db")

conn.execute("""
    CREATE OR REPLACE TABLE observations AS
    SELECT
        CAST(observation.properties.timestamp AS TIMESTAMPTZ) AS observation_timestamp,
        json_extract_string(observation, '$.id') AS observation_id,
        json_extract_string(observation, '$.type') AS observation_type,
        json_extract_string(observation.geometry, '$.type') AS geometry_type,
        CAST(json_extract(observation.geometry, '$.coordinates') AS VARCHAR[]) AS geometry_coordinates,
        observation.properties.elevation.value::DECIMAL AS elevation_m,
        json_extract_string(observation.properties, '$.stationId') AS station_id,
        json_extract_string(observation.properties, '$.stationName') AS station_name,
        observation.properties.temperature.value::DECIMAL AS temperature_degC,
        observation.properties.dewpoint.value::DECIMAL AS dewpoint_degC,
        observation.properties.windDirection.value::DECIMAL AS wind_direction_deg,
        observation.properties.windSpeed.value::DECIMAL AS wind_speed_kmh,
        observation.properties.windGust.value::DECIMAL AS wind_gust_kmh,
        observation.properties.barometricPressure.value::DECIMAL AS barometric_pressure_Pa,
        observation.properties.seaLevelPressure.value::DECIMAL AS sea_level_pressure_Pa,
        observation.properties.visibility.value::DECIMAL AS visibility_m,
        observation.properties.maxTemperatureLast24Hours.value::DECIMAL AS max_temp_24h_degC,
        observation.properties.minTemperatureLast24Hours.value::DECIMAL AS min_temp_24h_degC,
        observation.properties.precipitationLast3Hours.value::DECIMAL AS precipitation_3h_mm,
        observation.properties.relativeHumidity.value::DECIMAL AS relative_humidity_percent,
        observation.properties.windChill.value::DECIMAL AS wind_chill_degC,
        observation.properties.heatIndex.value::DECIMAL AS heat_index_degC
    FROM read_parquet('ingestion/ingestion_data/observations/observations_station_*.parquet')
""")