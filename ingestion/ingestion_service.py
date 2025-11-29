import fetch_zones
import fetch_stations
import fetch_observations
from datetime import datetime

def main_menu():
    print("Ingestion Service")
    print("1. Fetch Zones")
    print("2. Fetch Stations")
    print("3. Fetch Observations")
    print("4. Schedule Observations Fetcher")
    print("Q. Quit")

    choice = input("Select an option (1-4): ")

    if choice == '1':
        fetch_zones.write_zones(fetch_zones.fetch_zones())
    elif choice == '2':
        fetch_stations.fetch_station_groups(page_limit=10)
    elif choice == '3':
        fetch_observations.fetch_observations(station_limit=50)
    elif choice == '4':
        # Ask for cadence (supports suffixes s, m, h or plain seconds)
        cadence_input = input("Enter cadence (e.g. '10s', '5m', '1h' or number of seconds): ").strip().lower()

        def _parse_cadence(s):
            try:
                if s.endswith('s'):
                    return int(s[:-1])
                if s.endswith('m'):
                    return int(s[:-1]) * 60
                if s.endswith('h'):
                    return int(s[:-1]) * 3600
                return int(s)
            except Exception:
                return None

        cadence_seconds = _parse_cadence(cadence_input)
        if cadence_seconds is None or cadence_seconds <= 0:
            print("Invalid cadence. Please enter a positive number (or e.g. 10s, 5m, 1h).")
            main_menu()
            return

        station_limit = input("Enter station limit per fetch (default 50): ").strip()
        if station_limit == '':
            station_limit = 50
        else:
            try:
                station_limit = int(station_limit)
            except Exception:
                print("Invalid station limit. Please enter a positive integer.")
                main_menu()
                return

        print(f"Running fetch_observations starting now with cadence {cadence_seconds} seconds...")
        
        while True:
            start_time = datetime.now()
            print(f"Fetching observations at {start_time}...")
            fetch_observations.fetch_observations(station_limit)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            sleep_time = max(0, cadence_seconds - duration)
            if sleep_time > 0:
                print(f"Fetch completed in {duration:.2f} seconds. Sleeping for {sleep_time:.2f} seconds...")
                import time
                time.sleep(sleep_time)
                
    elif choice.lower() == 'q':
        print("Exiting...")
        return
    else:
        print("Invalid choice. Please try again.")

    main_menu()

if __name__ == "__main__":
    main_menu()