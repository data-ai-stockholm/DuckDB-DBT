# Weather Data Pipeline with DuckDB & dbt

A data pipeline for fetching, storing, and transforming weather observation data using DuckDB and dbt.

## Prerequisites

- Python 3.12+
- DuckDB CLI
- dbt-duckdb

## Setup

### 1. Install Dependencies

```bash
pip install duckdb dbt-duckdb --break-system-packages
```

### 2. Install DuckDB CLI

```bash
# Extract the DuckDB CLI binary
unzip duckdb_cli-linux-amd64.zip
chmod +x duckdb
```

### 3. Set up dbt Profile

Ensure `profiles.yml` exists in your project root with:

```yaml
weather:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "weather_reports.db"
      threads: 4
```

## Data Ingestion

### Fetch Weather Stations

Downloads weather station metadata from the API:

```bash
python3 ingestion/fetch_stations.py
```

Data is saved to: `ingestion/ingestion_data/stations/*.parquet`

### Fetch Observations

Downloads weather observations for each station:

```bash
python3 ingestion/fetch_observations.py
```

Data is saved to: `ingestion/ingestion_data/observations/*.parquet`

**Note:** This can take several hours as it fetches data for each station individually.

### Load Data into DuckDB

Load the Parquet files into the DuckDB database:

```bash
# Load stations
python3 ingestion/write_stations.py

# Load observations
python3 ingestion/write_observations.py
```

This creates the `stations` and `observations` tables in `weather_reports.db`.

## Data Transformation with dbt

Run dbt models to transform raw data:

```bash
dbt run
```

This creates the following tables:

### Dimension Tables
- **`dim_stations`** - Unique weather stations with location information

### Fact Tables
- **`fact_observations`** - Cleaned observations with data quality checks applied
  - Removes invalid temperature readings (< -100°C or > 60°C)
  - Validates wind speeds, humidity percentages
  - Adds date/time components for easier analysis
  
- **`fact_daily_weather`** - Daily aggregated weather metrics by station
  - Average, min, max temperatures
  - Maximum wind speeds and gusts
  - Total daily precipitation
  - Data quality counts

### Analytics Tables
- **`extreme_weather_events`** - Identified extreme weather events
  - Extreme Heat: ≥ 40°C
  - Extreme Cold: ≤ -30°C
  - High Winds: ≥ 75 km/h
  - Extreme Gusts: ≥ 100 km/h
  - Heavy Precipitation: ≥ 50mm per day
  - Large Temperature Swings: ≥ 30°C daily range

## Querying Data

Open the DuckDB CLI:

```bash
./duckdb weather_reports.db
```

Example queries:

```sql
-- Show all tables
SHOW TABLES;

-- View stations
SELECT * FROM dim_stations LIMIT 10;

-- Count observations
SELECT COUNT(*) FROM observations;
SELECT COUNT(*) FROM fact_observations;

-- Check daily weather aggregates
SELECT * FROM fact_daily_weather 
ORDER BY observation_date DESC 
LIMIT 10;

-- Find extreme weather events
SELECT 
    observation_date,
    station_name,
    event_types,
    max_temp_degC,
    max_wind_speed_kmh
FROM extreme_weather_events 
ORDER BY observation_date DESC 
LIMIT 20;

-- Exit
.exit
```

## Troubleshooting

### Empty Parquet Files

If you encounter errors about files being too small, remove empty Parquet files:

```bash
find ingestion/ingestion_data/observations/ -name "*.parquet" -size 0 -delete
```

### dbt Command Not Found

If `dbt` is not in your PATH after installation, add it:

```bash
export PATH="/home/codespace/.local/bin:$PATH"
```

Or run dbt commands with the full path:

```bash
/home/codespace/.local/bin/dbt run
```

### Running Specific Models

```bash
# Run only one model
dbt run --select fact_observations

# Run a model and its downstream dependencies
dbt run --select fact_observations+

# Run all models in a specific folder
dbt run --select models/facts/
```

## Future Enhancements

- Add geographic dimension tables (regions, states, counties)
- Create time-series analysis models
- Add data quality tests
- Implement incremental models for large datasets
- Add visualization layer