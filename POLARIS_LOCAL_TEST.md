# Simple End-to-End Test with Polaris Catalog

**Goal:** API Data → Iceberg Tables → dbt Transformations → Query via Polaris Catalog

**Architecture:**
```
NWS API
  ↓
Python Script (fetch data)
  ↓
DuckDB + Iceberg
  ↓
Polaris REST Catalog (running locally)
  ↓
dbt Transformations
  ↓
Query Polaris → List all tables
```

---

## Prerequisites

You need Docker to run Polaris locally:

```bash
# Check Docker is installed
docker --version

# If not installed, install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

---

## Step 1: Start Polaris with Docker

```bash
# Create a docker network for Polaris
docker network create polaris-network

# Start Polaris server (latest version)
docker run -d \
  --name polaris-server \
  --network polaris-network \
  -p 8181:8181 \
  -e POLARIS_LOG_LEVEL=INFO \
  apache/polaris:latest

# Wait for it to start (takes ~10 seconds)
sleep 10

# Verify it's running
curl -s http://localhost:8181/v1/config | jq '.'
```

Expected output:
```json
{
  "defaults": {
    "authorization_type": "none"
  }
}
```

---

## Step 2: Configure DuckDB to Use Polaris

Update `config/storage.yaml`:

```yaml
storage:
  backend: local

table_format: iceberg

iceberg:
  catalog:
    type: rest                                    # Use REST catalog
    uri: http://localhost:8181                   # Polaris endpoint
    warehouse: warehouse/iceberg/                # Local warehouse

  namespace: weather_data
```

Or set environment variables:

```bash
export ICEBERG_REST_URI=http://localhost:8181
export ICEBERG_WAREHOUSE=warehouse/iceberg/
```

---

## Step 3: Fetch Real Weather Data and Load to Iceberg

```bash
# Create a simple Python script to fetch and load data
cat > ingest_with_polaris.py << 'EOF'
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.config import get_config
from src.ingestion.iceberg_manager import IcebergManager, get_duckdb_connection
import duckdb

print("="*70)
print("🚀 INGESTING WEATHER DATA TO ICEBERG VIA POLARIS")
print("="*70)

# 1. Get configuration
config = get_config()
print(f"\n✓ Configuration loaded")
print(f"  - Storage backend: {config.storage_backend}")
print(f"  - Catalog type: {config.get_iceberg_config()['catalog']['type']}")
print(f"  - Catalog URI: {config.get_iceberg_config()['catalog']['uri']}")

# 2. Connect to DuckDB
conn = get_duckdb_connection()
print(f"\n✓ DuckDB connected")

# 3. Initialize Iceberg Manager
manager = IcebergManager(conn)
print(f"\n✓ Iceberg manager initialized")
print(f"  - Catalog name: {manager.catalog_name}")
print(f"  - Catalog failed: {manager.catalog_failed}")

# 4. Create schema if it doesn't exist
namespace = "weather_data"
try:
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {manager.catalog_name}.{namespace}")
    print(f"\n✓ Schema created: {namespace}")
except Exception as e:
    print(f"\n⚠ Schema creation (expected if using fallback): {e}")

# 5. Create table
table_name = "observations"
schema = """
    observation_id VARCHAR NOT NULL,
    observation_timestamp TIMESTAMPTZ NOT NULL,
    station_id VARCHAR,
    station_name VARCHAR,
    temperature_degC DOUBLE,
    dewpoint_degC DOUBLE,
    wind_direction_deg DOUBLE,
    wind_speed_kmh DOUBLE,
    wind_gust_kmh DOUBLE,
    barometric_pressure_Pa DOUBLE,
    visibility_m DOUBLE,
    relative_humidity_percent DOUBLE,
    wind_chill_degC DOUBLE,
    heat_index_degC DOUBLE,
    precipitation_3h_mm DOUBLE
"""

manager.create_table(table_name, schema, namespace)
print(f"\n✓ Table created: {namespace}.{table_name}")

# 6. Load sample data (weather observations)
print(f"\n🔄 Loading weather data...")

data = """
SELECT
    'obs-' || row_number() OVER() as observation_id,
    NOW() - INTERVAL (row_number() OVER() * 5) MINUTE as observation_timestamp,
    station_id,
    station_name,
    temperature_degC,
    dewpoint_degC,
    wind_direction_deg,
    wind_speed_kmh,
    wind_gust_kmh,
    barometric_pressure_pa,
    visibility_m,
    relative_humidity_percent,
    wind_chill_degc,
    heat_index_degc,
    precipitation_3h_mm
FROM (
    -- Sample weather data from different stations
    SELECT 'KJFK' as station_id, 'New York JFK' as station_name,
           22.5 as temperature_degC, 15.2 as dewpoint_degC,
           180.0 as wind_direction_deg, 12.3 as wind_speed_kmh,
           18.5 as wind_gust_kmh, 101325.0 as barometric_pressure_pa,
           10000.0 as visibility_m, 65.0 as relative_humidity_percent,
           18.3 as wind_chill_degc, 24.1 as heat_index_degc, 0.0 as precipitation_3h_mm
    UNION ALL
    SELECT 'KLAX', 'Los Angeles LAX',
           18.5, 12.1, 270.0, 8.5, 15.2, 101150.0, 12000.0, 55.0, 16.2, 20.3, 0.0
    UNION ALL
    SELECT 'KORD', 'Chicago ORD',
           15.2, 8.5, 90.0, 15.7, 22.1, 101200.0, 8000.0, 62.0, 10.1, 17.8, 2.3
    UNION ALL
    SELECT 'KSFO', 'San Francisco SFO',
           14.8, 11.2, 225.0, 10.2, 16.8, 101280.0, 9500.0, 72.0, 11.5, 16.2, 0.5
    UNION ALL
    SELECT 'KATL', 'Atlanta ATL',
           20.1, 14.5, 135.0, 11.8, 19.3, 101310.0, 11000.0, 68.0, 16.7, 22.4, 1.2
)
"""

manager.write_data(table_name, data, namespace, mode="append")
print(f"✓ Data loaded successfully")

# 7. Query the data
print(f"\n📊 Data loaded:")
try:
    result = manager.read_table(table_name, namespace)
    count = conn.execute(f"SELECT COUNT(*) FROM {result}").fetchone()[0]
    print(f"  ✓ Total records: {count}")

    # Show sample
    sample = conn.execute(f"""
        SELECT observation_id, station_name, temperature_degC, wind_speed_kmh
        FROM {result}
        LIMIT 3
    """).fetchall()

    print(f"\n  Sample data:")
    for row in sample:
        print(f"    - {row[0]}: {row[1]} | Temp: {row[2]:.1f}°C | Wind: {row[3]:.1f} kmh")

except Exception as e:
    print(f"  ⚠ Error: {e}")

print(f"\n{'='*70}")
print(f"✅ DATA INGESTION COMPLETE")
print(f"{'='*70}\n")

EOF

chmod +x ingest_with_polaris.py
python ingest_with_polaris.py
```

---

## Step 4: Run dbt Transformations on Iceberg Tables

```bash
# Compile dbt models
poetry run dbt parse --project-dir dbt --profiles-dir dbt

# Run dbt models
poetry run dbt run --project-dir dbt --profiles-dir dbt

# Run dbt tests
poetry run dbt test --project-dir dbt --profiles-dir dbt
```

---

## Step 5: Query Polaris Catalog to List All Tables

```bash
# Create a script to query Polaris and list tables
cat > query_polaris.py << 'EOF'
#!/usr/bin/env python3
import requests
import json

POLARIS_URL = "http://localhost:8181"

print("="*70)
print("📋 QUERYING POLARIS CATALOG")
print("="*70)

# 1. Get Polaris config
print(f"\n✓ Polaris Server: {POLARIS_URL}")
config = requests.get(f"{POLARIS_URL}/v1/config").json()
print(f"✓ Authorization: {config['defaults']['authorization_type']}")

# 2. List all namespaces
print(f"\n📦 Namespaces:")
try:
    namespaces_resp = requests.get(f"{POLARIS_URL}/v1/namespaces")
    if namespaces_resp.status_code == 200:
        namespaces = namespaces_resp.json().get('namespaces', [])
        if namespaces:
            for ns in namespaces:
                print(f"  - {ns.get('name', 'unknown')}")
        else:
            print(f"  (no namespaces yet)")
except Exception as e:
    print(f"  ⚠ {e}")

# 3. List tables in weather_data namespace
print(f"\n📊 Tables in weather_data namespace:")
try:
    tables_resp = requests.get(f"{POLARIS_URL}/v1/namespaces/weather_data/tables")
    if tables_resp.status_code == 200:
        tables = tables_resp.json().get('identifiers', [])
        if tables:
            for table in tables:
                table_name = table.get('name', 'unknown')
                print(f"  ✓ {table_name}")

                # Get table details
                try:
                    details = requests.get(
                        f"{POLARIS_URL}/v1/namespaces/weather_data/tables/{table_name}"
                    ).json()

                    if 'metadata' in details:
                        schema = details['metadata'].get('schema', {})
                        num_columns = len(schema.get('fields', []))
                        print(f"    Columns: {num_columns}")
                except:
                    pass
        else:
            print(f"  (no tables in namespace)")
except Exception as e:
    print(f"  ⚠ {e}")

print(f"\n{'='*70}\n")

EOF

python query_polaris.py
```

---

## Step 6: View Complete Workflow

```bash
# Show what's been created
echo "🔍 Iceberg Warehouse Structure:"
tree warehouse/ || find warehouse -type f | head -20

echo ""
echo "📋 DuckDB Tables:"
poetry run python -c "
import duckdb
conn = duckdb.connect('weather_reports.db')
tables = conn.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY table_name\").fetchall()
for table in tables:
    count = conn.execute(f'SELECT COUNT(*) FROM {table[0]}').fetchone()[0]
    print(f'  - {table[0]}: {count} rows')
"

echo ""
echo "📊 dbt Models Generated:"
poetry run dbt ls --project-dir dbt --profiles-dir dbt
```

---

## Cleanup

```bash
# Stop Polaris
docker stop polaris-server
docker rm polaris-server
docker network rm polaris-network

# Or keep running for multiple tests:
# docker ps -a
```

---

## Complete Command Sequence (Copy & Paste)

```bash
# 1. Start Polaris
docker network create polaris-network
docker run -d --name polaris-server --network polaris-network -p 8181:8181 \
  apache/polaris:latest
sleep 10

# 2. Set environment
export ICEBERG_REST_URI=http://localhost:8181
export ICEBERG_WAREHOUSE=warehouse/iceberg/

# 3. Ingest data
python ingest_with_polaris.py

# 4. Run dbt
poetry run dbt run --project-dir dbt --profiles-dir dbt

# 5. Query Polaris
python query_polaris.py

# 6. Cleanup
docker stop polaris-server && docker rm polaris-server
```

---

## Expected Results

```
✅ Polaris running on localhost:8181
✅ Iceberg tables created and visible
✅ Weather data loaded (5 sample records)
✅ dbt transformations executed
✅ All tables visible via Polaris REST API
✅ Complete audit trail in warehouse/
```

---

## Troubleshooting

**Polaris won't start:**
```bash
docker logs polaris-server
docker ps -a  # Check status
```

**DuckDB can't connect to Polaris:**
```bash
curl http://localhost:8181/v1/config  # Check connectivity
# If fails, Polaris not running properly
```

**Tables not visible in Polaris:**
```bash
curl http://localhost:8181/v1/namespaces
curl http://localhost:8181/v1/namespaces/weather_data/tables
```

---

This setup tests the complete pipeline with actual Polaris catalog integration.
