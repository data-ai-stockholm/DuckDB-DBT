import fetch_zones
import fetch_stations
import fetch_observations
from datetime import datetime
import os

cadence_seconds = 300  # 5 minutes

if __name__ == "__main__":
    if not os.path.exists("ingestion_data/zones/"):
        fetch_zones.write_zones(fetch_zones.fetch_zones())

    if not os.path.exists("ingestion_data/stations/"):
        fetch_stations.fetch_station_groups(page_limit=10)
        
    while True:
        start_time = datetime.now()
        print(f"Fetching observations at {start_time}...")
        fetch_observations.fetch_observations(station_limit=100)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        sleep_time = max(0, cadence_seconds - duration)
        if sleep_time > 0:
            print(f"Fetch completed in {duration:.2f} seconds. Sleeping for {sleep_time:.2f} seconds...")
            import time
            time.sleep(sleep_time)