# Weather Data Pipeline with DuckDB, dbt & Apache Iceberg

Modern data pipeline demonstrating **DuckDB**, **dbt**, and **Apache Iceberg** integration with a custom REST catalog implementation.

## Features

- ✅ **Custom Iceberg REST Catalog** - Educational implementation of Apache Iceberg REST spec
- ✅ **DuckDB Integration** - Native Iceberg support with DuckDB v1.4.2+
- ✅ **dbt Transformations** - Data modeling and transformations
- ✅ **Multi-Cloud Ready** - Supports local, S3, Azure Blob Storage, GCS
- ✅ **Poetry** - Modern Python dependency management

## Quick Start

### 1. Install Dependencies

```bash
poetry install
```

### 2. Start REST Catalog Server

```bash
poetry run catalog-server
```

### 3. Run Demo

```bash
poetry run python examples/test_catalog.py
```

This creates an Iceberg table, writes synthetic data, and queries it with DuckDB.

### 4. Fetch Real Weather Data (Optional)

```bash
poetry run fetch-stations
poetry run fetch-observations
poetry run load-observations
```

### 5. Run dbt Transformations

```bash
poetry run dbt run --profiles-dir .
poetry run dbt test --profiles-dir .
```

## Project Structure

```
duckdb-dbt/
├── src/
│   ├── catalog/
│   │   └── rest_server.py       # Custom Iceberg REST catalog
│   └── ingestion/
│       ├── config.py            # Configuration management
│       ├── iceberg_manager.py   # DuckDB Iceberg integration
│       ├── fetch_stations.py    # Weather station fetcher
│       ├── fetch_observations.py # Weather data fetcher
│       └── write_observations.py # Data loader
├── examples/
│   └── test_catalog.py          # Demo script
├── models/                      # dbt transformations
│   ├── staging/                 # Staging models
│   └── marts/                   # Business logic models
├── config.yaml                  # Multi-backend configuration
├── dbt_project.yml              # dbt configuration
├── profiles.yml                 # dbt profiles
├── pyproject.toml               # Poetry dependencies
└── warehouse/                   # Iceberg data lake
```

## Configuration

Edit `config.yaml` to configure storage backends and catalog settings:

```yaml
# Storage: local, s3, azure, gcs
storage:
  backend: local

# Table format: duckdb or iceberg
table_format: iceberg

# Iceberg REST catalog
iceberg:
  catalog:
    type: rest
    uri: http://localhost:8181
```

## Commands

```bash
# Start catalog server
poetry run catalog-server

# Fetch weather data
poetry run fetch-stations
poetry run fetch-observations

# Load data to Iceberg
poetry run load-observations

# Run dbt
poetry run dbt run --profiles-dir .
poetry run dbt test --profiles-dir .
```

## What's Inside

### Custom REST Catalog

A complete implementation of the Apache Iceberg REST Catalog specification:
- Namespace management (create, list, delete)
- Table operations (create, read, update, delete)
- Proper schema conversion (REST ↔ PyIceberg)
- Complex type handling (lists, structs, maps)
- Snapshot and metadata management

### Iceberg Table Format

Real Iceberg tables with proper structure:
```
warehouse/
└── weather_data.db/
    └── observations/
        ├── data/
        │   └── *.parquet          # Data files
        └── metadata/
            ├── *.metadata.json    # Schema + snapshots
            └── *.avro             # Manifests
```

### dbt Models

**Staging Layer:**
- **stg_observations** - Cleaned weather observations from source

**Marts Layer:**
- **fact_observations** - Enriched observations with temporal attributes
- **fact_daily_weather** - Daily weather aggregates by station
- **dim_stations** - Station dimension table
- **extreme_weather_events** - Statistical anomaly detection (Z-score based)

## Architecture

```
┌─────────────┐
│   DuckDB    │ ──────┐
└─────────────┘       │
                       ├──→ ┌──────────────────┐
┌─────────────┐       │    │  REST Catalog    │
│     dbt     │ ──────┘    │  (Port 8181)     │
└─────────────┘            └──────────────────┘
                                     │
                                     ↓
                           ┌──────────────────┐
                           │  PyIceberg +     │
                           │  SQLite Catalog  │
                           └──────────────────┘
                                     │
                                     ↓
                           ┌──────────────────┐
                           │   Warehouse      │
                           │   (Iceberg)      │
                           └──────────────────┘
```

## Learn More

See [CLAUDE.md](CLAUDE.md) for detailed technical documentation including:
- Iceberg architecture deep-dive
- REST catalog protocol details
- Schema conversion internals
- Troubleshooting guide
- Production deployment considerations

## Resources

- [Apache Iceberg](https://iceberg.apache.org/)
- [DuckDB Iceberg Extension](https://duckdb.org/docs/extensions/iceberg)
- [dbt Documentation](https://docs.getdbt.com/)
- [PyIceberg](https://py.iceberg.apache.org/)

---

Built with ❤️ for learning modern data engineering