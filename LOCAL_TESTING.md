# Local Testing Guide (No AWS/Azure/GCS/Polaris Required)

## Overview

You can fully test the weather data pipeline locally using only:
- **Local filesystem** for data storage
- **DuckDB** (v1.4.2+) with native Iceberg extension
- **Python 3.10+** with Poetry

No external services required!

## What Works Locally

✅ **Data Pipeline**
- Weather data ingestion and transformation
- Iceberg table creation and data operations
- dbt model execution
- Prefect workflow orchestration

✅ **Testing Capabilities**
- Configuration validation
- DuckDB connection and Iceberg operations
- Table creation and schema evolution
- Data write/read operations
- Complete end-to-end pipeline execution

✅ **No Dependencies Needed**
- No AWS account required
- No Azure subscription required
- No GCS setup required
- No Polaris catalog service required
- No Docker or external services required

## Quick Start

### 1. Install Dependencies
```bash
poetry install
```

### 2. Validate Local Setup
```bash
# Run comprehensive local validation
python test_local_setup.py
```

Expected output:
```
✅ All critical tests PASSED
Your local Iceberg setup is working!
```

### 3. Run Demo Flow
```bash
poetry run python src/flows/demo_flow.py
```

Creates synthetic weather data and demonstrates the pipeline.

### 4. Fetch Real Weather Data (Optional)
```bash
# Fetch weather stations
poetry run fetch-stations

# Fetch observations
poetry run fetch-observations

# Load to Iceberg
poetry run load-observations
```

### 5. Run Full Pipeline
```bash
poetry run python src/flows/main_pipeline.py
```

Ingestion + dbt transformations + documentation generation.

### 6. Using Makefile Commands
```bash
make demo              # Quick demo with synthetic data
make run-weather       # Ingestion flow
make run-pipeline      # Full end-to-end
make dbt-run          # Transform data with dbt
make dbt-test         # Run dbt tests
make clean-data       # Clean up test artifacts
```

## Configuration Files

### For Local Testing

**Primary config (REST catalog - will fallback to DuckDB):**
```bash
config/storage.yaml          # Uses REST catalog (falls back gracefully)
```

**Alternative config (Direct local access):**
```bash
config/storage.local.yaml    # Uses local filesystem directly
```

**Environment setup:**
```bash
# Use local configuration
export CONFIG_PATH="config/storage.local.yaml"

# Or set environment variables
export STORAGE_BACKEND=local
export TABLE_FORMAT=iceberg
export ICEBERG_CATALOG_TYPE=local
export ICEBERG_WAREHOUSE=warehouse/
```

## What Gets Created

When you run tests, the following directories are created:

```
warehouse/               # Iceberg warehouse (data + metadata)
  ├── catalog.db        # SQLite catalog metadata
  └── test/             # Example tables
      ├── weather_samples/
      │   ├── data/     # Parquet data files
      │   └── metadata/ # Iceberg metadata (versioning)
      └── ...

ingestion_data/         # Downloaded weather data (if fetching real data)

weather_reports.db      # DuckDB local database file
```

All files are local - you control them completely.

## Warehouse Structure

The Iceberg warehouse follows this structure:

```
warehouse/
└── namespace/
    └── table/
        ├── metadata/
        │   ├── 00000-{uuid}.metadata.json      # Metadata v1
        │   ├── 00001-{uuid}.metadata.json      # Metadata v2
        │   ├── snap-{id}-0-{uuid}.avro         # Snapshots
        │   └── {uuid}-m0.avro                  # Manifest lists
        └── data/
            └── 00000-0-{uuid}.parquet          # Parquet data files
```

This provides:
- ✅ **ACID Transactions** - All-or-nothing writes
- ✅ **Schema Evolution** - Add/modify/remove columns
- ✅ **Time Travel** - Query historical snapshots
- ✅ **Versioning** - Complete metadata history

## Testing Examples

### Test Configuration Loading
```python
from src.ingestion.config import get_config
config = get_config()
print(config.storage_backend)  # "local"
print(config.table_format)     # "iceberg"
```

### Test DuckDB Connection
```python
from src.ingestion.iceberg_manager import get_duckdb_connection
conn = get_duckdb_connection()
result = conn.execute("SELECT 1").fetchall()
print(result)  # [(1,)]
```

### Test Iceberg Manager
```python
from src.ingestion.iceberg_manager import IcebergManager, get_duckdb_connection
conn = get_duckdb_connection()
manager = IcebergManager(conn)

# Create table
manager.create_table(
    "test",
    "id INT, name VARCHAR",
    namespace="default"
)

# Write data
manager.write_data(
    "test",
    "SELECT 1 as id, 'Alice' as name",
    namespace="default"
)

# Read data
table = manager.read_table("test", namespace="default")
result = conn.execute(f"SELECT * FROM {table}").fetchall()
print(result)  # [(1, 'Alice')]
```

## Data Flow

```
┌─────────────────────────────────────────────┐
│  Local Filesystem Tests                     │
│  (No external services required)            │
└─────────────────────────────────────────────┘
                    │
                    ▼
        ┌─────────────────────┐
        │   DuckDB 1.4.2+     │
        │  (Iceberg + httpfs) │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │ Iceberg Manager     │
        │ (Config + Tables)   │
        └──────────┬──────────┘
                   │
    ┌──────────────▼──────────────┐
    │   Data Operations           │
    │  ✓ Create tables            │
    │  ✓ Write data               │
    │  ✓ Read data                │
    │  ✓ Schema evolution         │
    └──────────────┬──────────────┘
                   │
    ┌──────────────▼──────────────┐
    │   Local Warehouse           │
    │  warehouse/                 │
    │  ├── catalog.db             │
    │  └── namespaces/tables/     │
    └─────────────────────────────┘
```

## Cleanup

### Remove Test Data
```bash
# Remove warehouse (Iceberg tables)
rm -rf warehouse/

# Remove downloaded data
rm -rf ingestion_data/

# Remove DuckDB database
rm -f weather_reports.db*

# Using Make
make clean-data
```

## Next Steps

### After Local Testing Works

1. **Try with Real Data**
   ```bash
   make fetch-all
   make run-pipeline
   ```

2. **Use Polaris for Production**
   - See `docs/POLARIS_SETUP.md`
   - Configure AWS managed Polaris
   - Update environment variables
   - Switch to REST catalog

3. **Deploy to Cloud**
   - Use S3, Azure, or GCS backend
   - Use managed Polaris service
   - Set up Prefect Cloud
   - Enable GitHub Actions CI/CD

## Troubleshooting

### Configuration Issues
```bash
# Check config loads
python -c "from src.ingestion.config import get_config; print(get_config().storage_backend)"

# Check with local config
export CONFIG_PATH="config/storage.local.yaml"
python -c "from src.ingestion.config import get_config; print(get_config().get_iceberg_config()['catalog'])"
```

### DuckDB Issues
```bash
# Check version
poetry run python -c "import duckdb; print(duckdb.__version__)"

# Check extensions
poetry run python -c "import duckdb; conn = duckdb.connect(); print(conn.execute('SELECT * FROM duckdb_extensions()').fetchall())"
```

### Test Failures
```bash
# Run with debug output
python -u test_local_setup.py

# Check warehouse structure
ls -la warehouse/
find warehouse/ -type f | head -20
```

## FAQ

**Q: Do I need AWS credentials?**
A: No! Everything works locally on your machine.

**Q: Can I use real weather data?**
A: Yes! The pipeline fetches from NOAA Weather API (free, no auth required).

**Q: Is this production-ready?**
A: Locally, yes. For production, add Polaris (see POLARIS_SETUP.md).

**Q: What about scale?**
A: DuckDB handles millions of rows. For petabyte-scale, use cloud storage + Polaris.

**Q: Can I switch to cloud later?**
A: Absolutely! Just:
1. Export local Iceberg tables
2. Set up Polaris on cloud
3. Update config with S3/Azure/GCS paths
4. Switch to REST catalog

## Resources

- [DuckDB Iceberg Extension](https://duckdb.org/docs/extensions/iceberg)
- [Apache Iceberg Spec](https://iceberg.apache.org/spec/)
- [Production Deployment](docs/POLARIS_SETUP.md)
- [Complete Documentation](docs/CLAUDE.md)

---

**Status:** ✅ Local setup validated and working!

Everything you need to test the weather pipeline is on your local machine.
