# Fetch weather station data from the API and store it in Parquet files.

import requests
import duckdb

conn = duckdb.connect()

next_page = "https://api.weather.gov/stations"

while True:
    conn.execute(f"""
        CREATE OR REPLACE TABLE weather_stations AS
        SELECT
            UNNEST(observationStations) AS station_url,
            pagination.next AS next_page
        FROM read_json_auto('{next_page}');
    """)

    next_page = conn.execute("""
        SELECT
            DISTINCT next_page
        FROM weather_stations
    """).fetchone()[0]

    cursor = next_page.split("cursor=")[-1]

    conn.execute(f"""
        COPY (FROM weather_stations) TO 'ingestion_data/stations/weather_stations_{cursor}.parquet' (FORMAT PARQUET)
    """).df()

    print(f"Saved Page: {next_page}")