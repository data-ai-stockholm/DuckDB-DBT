# Fetch weather observations for each station and store them in Parquet files.

import duckdb

conn = duckdb.connect()

station_urls = conn.execute("""
    SELECT station_url
    FROM read_parquet('ingestion_data/stations/weather_stations_*.parquet')
""").df()['station_url'].tolist()

for url in station_urls:
    observations = conn.execute(f"""
        COPY (
            SELECT
                UNNEST(features) AS observation
            FROM read_json_auto('{url}/observations')
        ) TO 'ingestion_data/observations/observations_station_{url.split('/')[-1]}.parquet' (FORMAT PARQUET)
    """)
    print(f"Fetched observations for station: {url}")