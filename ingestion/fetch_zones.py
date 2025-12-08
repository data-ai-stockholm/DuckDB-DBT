# Fetch weather station data from the API and store it in Parquet files.

import duckdb
import os

conn = duckdb.connect()

def fetch_zones():
    URL = "https://api.weather.gov/zones"

    zones = conn.execute(f"""
        CREATE OR REPLACE TABLE zones AS
        
        SELECT
            UNNEST(features)['id'] AS zone_id,
            UNNEST(features)['properties']['@id'] AS zone_url,
            UNNEST(features)['properties']['type'] AS zone_type,
            UNNEST(features)['properties']['name'] AS zone_name,
            UNNEST(features)['properties']['state'] AS state,
            UNNEST(features)['properties']['forecastOffice'] AS office_url
        FROM read_json_auto('{URL}')
    """).df()

    return zones

def write_zones(zones_df):
    if not os.path.exists('ingestion_data/zones/'):
        os.makedirs('ingestion_data/zones/')

    conn.execute(f"""
        COPY (FROM zones_df) TO 'ingestion_data/zones/zones.parquet' (FORMAT PARQUET)
    """).df()

    print(f"Saved zones data to ingestion_data/zones/zones.parquet")
    
if __name__ == "__main__":
    zones_df = fetch_zones()
    write_zones(zones_df)