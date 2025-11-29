# Fetch weather observations for each station and store them in Parquet files.

import duckdb
import os

conn = duckdb.connect()

def fetch_observations(station_limit=50):
    station_urls = conn.execute(f"""
        SELECT DISTINCT station_url
        FROM read_parquet('ingestion_data/stations/station_group_*.parquet')
        ORDER BY station_url
        LIMIT {station_limit}
    """).df()['station_url'].tolist()

    stations_searched = 0
    for url in station_urls:
        station_id = url.split('/')[-1]

        try:
            observations = conn.execute(f"""
                SELECT
                    properties.timestamp AS observation_timestamp,
                    id AS observation_id,
                    type AS observation_type,
                    geometry.type AS geometry_type,
                    geometry.coordinates AS geometry_coordinates,
                    properties.elevation.value AS elevation_m,
                    properties.stationId AS station_id,
                    properties.stationName AS station_name,
                    properties.temperature.value AS temperature_degC,
                    properties.dewpoint.value AS dewpoint_degC,
                    properties.windDirection.value AS wind_direction_deg,
                    properties.windSpeed.value AS wind_speed_kmh,
                    properties.windGust.value AS wind_gust_kmh,
                    properties.barometricPressure.value AS barometric_pressure_Pa,
                    properties.seaLevelPressure.value AS sea_level_pressure_Pa,
                    properties.visibility.value AS visibility_m,
                    properties.maxTemperatureLast24Hours.value AS max_temp_24h_degC,
                    properties.minTemperatureLast24Hours.value AS min_temp_24h_degC,
                    properties.precipitationLast3Hours.value AS precipitation_3h_mm,
                    properties.relativeHumidity.value AS relative_humidity_percent,
                    properties.windChill.value AS wind_chill_degC,
                    properties.heatIndex.value AS heat_index_degC
                FROM read_json_auto('{url}/observations/latest')
            """).df()
        except duckdb.HTTPException as e:
            stations_searched += 1
            print(f"{stations_searched} out of {station_limit} - Did NOT save observations for station: {station_id} due to HTTP Error")
            continue
        except duckdb.BinderException as e:
            stations_searched += 1
            print(f"{stations_searched} out of {station_limit} - Did NOT save observations for station: {station_id} due to Binder Error")
            continue

        fetch_date = conn.execute(f"""
            SELECT
                SPLIT(observation_timestamp, 'T')[1] AS latest_time
            FROM observations
        """).fetchone()[0]

        latest_timestamp = conn.execute(f"""
            SELECT
                SPLIT(observation_timestamp, 'T')[2] AS latest_time
            FROM observations
        """).fetchone()[0]

        if not os.path.exists(f"ingestion_data/observations/{station_id}/{fetch_date}"):
            os.makedirs(f"ingestion_data/observations/{station_id}/{fetch_date}")

        conn.execute(f"""
            COPY (
                SELECT
                    *
                FROM observations
            ) TO 'ingestion_data/observations/{station_id}/{fetch_date}/observation_{latest_timestamp}.parquet' (FORMAT PARQUET)
        """)

        stations_searched += 1
        print(f"{stations_searched} out of {station_limit} - Saved observations for station: {station_id} at {latest_timestamp}")

if __name__ == "__main__":
    fetch_observations()