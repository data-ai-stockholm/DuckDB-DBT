# Fetch weather station data from the API and store it in Parquet files.

import requests
import duckdb
import os

conn = duckdb.connect()

def fetch_station_groups(page_limit=10):
    next_page = "https://api.weather.gov/stations"

    if not os.path.exists('ingestion_data/stations/'):
        os.makedirs('ingestion_data/stations/')

    for _ in range(10):  # Limit to 10 pages for demo --> 5000 stations
        conn.execute(f"""
            CREATE OR REPLACE TABLE weather_stations AS
            
            SELECT
                UNNEST(features)['properties']['stationIdentifier'] AS station_id,
                UNNEST(features)['id'] AS station_url,
                CAST(UNNEST(features)['geometry']['coordinates'] AS VARCHAR[]) AS coordinates,
                UNNEST(features)['properties']['elevation']['value']::DECIMAL AS elevation_m,
                UNNEST(features)['properties']['name'] AS station_name,
                UNNEST(features)['properties']['timeZone'] AS time_zone,
                UNNEST(features)['properties']['forecast'] AS forecast_url,
                UNNEST(features)['properties']['county'] AS county,
                pagination.next AS next_page
            FROM read_json_auto('{next_page}')
        """)

        next_page = conn.execute("""
            SELECT
                DISTINCT next_page
            FROM weather_stations
        """).fetchone()[0]

        cursor = next_page.split("cursor=")[-1]

        conn.execute(f"""
            COPY (FROM weather_stations) TO 'ingestion_data/stations/station_group_{cursor}.parquet' (FORMAT PARQUET)
        """).df()

        print(f"Saved Page: {next_page}")

if __name__ == "__main__":
    fetch_station_groups()