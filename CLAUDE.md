# Technical Documentation - Apache Iceberg REST Catalog Implementation

## Overview

This document provides a deep technical dive into the custom Apache Iceberg REST Catalog implementation, covering architecture, implementation details, and lessons learned.

## Table of Contents

1. [Iceberg Architecture](#iceberg-architecture)
2. [REST Catalog Implementation](#rest-catalog-implementation)
3. [Type System & Schema Conversion](#type-system--schema-conversion)
4. [DuckDB Integration](#duckdb-integration)
5. [Troubleshooting](#troubleshooting)
6. [Production Considerations](#production-considerations)

---

## Iceberg Architecture

### Three-Level Hierarchy

```
Catalog
  └─ Namespace (database/schema)
       └─ Table
            ├─ Metadata (JSON files with versioning)
            ├─ Snapshots (point-in-time table state)
            ├─ Manifests (lists of data files)
            └─ Data Files (Parquet/ORC/Avro)
```

### Metadata Evolution

Iceberg maintains a complete history of all table changes:

```
warehouse/weather_data.db/observations/metadata/
├── 00000-{uuid}.metadata.json  # Initial table creation
├── 00001-{uuid}.metadata.json  # After first write
├── 00002-{uuid}.metadata.json  # After second write
├── snap-{id}-0-{uuid}.avro      # Snapshot manifest
└── {uuid}-m0.avro               # Data file manifest
```

Each metadata file contains:
- **table-uuid**: Unique identifier for the table
- **schemas**: Array of schema versions
- **current-schema-id**: Active schema
- **partition-specs**: Partitioning configuration
- **sort-orders**: Sort order specifications
- **snapshots**: Array of table snapshots
- **current-snapshot-id**: Latest snapshot (omit if none)

### Snapshot Structure

```json
{
  "snapshot-id": 8234101027069594364,
  "timestamp-ms": 1764964231317,
  "summary": {
    "operation": "append",
    "added-records": "5",
    "total-records": "5",
    "added-data-files": "1"
  },
  "manifest-list": "file://.../snap-*.avro"
}
```

---

## REST Catalog Implementation

### REST API Endpoints

Location: `src/catalog/rest_server.py`

#### Configuration

```python
@app.route('/v1/config', methods=['GET'])
def get_config():
    return jsonify({
        "defaults": {"authorization_type": "none"}
    })
```

**Critical**: DuckDB defaults to OAuth2, must explicitly set `authorization_type: none`

#### Namespace Operations

```python
GET    /v1/namespaces              # List all namespaces
GET    /v1/namespaces/{ns}         # Get namespace properties
POST   /v1/namespaces/{ns}         # Create namespace
DELETE /v1/namespaces/{ns}         # Drop namespace (must be empty)
```

#### Table Operations

```python
GET    /v1/namespaces/{ns}/tables           # List tables
POST   /v1/namespaces/{ns}/tables           # Create table
GET    /v1/namespaces/{ns}/tables/{table}   # Load table metadata
POST   /v1/namespaces/{ns}/tables/{table}   # Update table
DELETE /v1/namespaces/{ns}/tables/{table}   # Drop table
```

### Schema Conversion

The hardest part of implementing a REST catalog is converting between REST API format and PyIceberg internal representation.

#### REST → PyIceberg

```python
def _convert_schema(schema_data: dict) -> Schema:
    """Convert REST API schema to PyIceberg Schema."""
    fields = []
    for field in schema_data.get('fields', []):
        field_type = _convert_type(field['type'])
        fields.append(NestedField(
            field_id=field['id'],
            name=field['name'],
            field_type=field_type,
            required=field.get('required', False),
        ))
    return Schema(*fields, schema_id=schema_data.get('schema-id', 0))
```

#### PyIceberg → REST

```python
def _schema_to_dict(schema: Schema) -> dict:
    """Convert PyIceberg Schema to REST API format."""
    return {
        "type": "struct",
        "schema-id": schema.schema_id,
        "fields": [
            {
                "id": field.field_id,
                "name": field.name,
                "type": _type_to_dict(field.field_type),  # Recursive!
                "required": field.required,
            }
            for field in schema.fields
        ]
    }
```

---

## Type System & Schema Conversion

### Primitive Types

```python
type_map = {
    'string': StringType(),
    'int': IntegerType(),
    'long': LongType(),
    'float': FloatType(),
    'double': DoubleType(),
    'boolean': BooleanType(),
    'timestamptz': TimestamptzType(),
}
```

### Complex Types

#### List Type

REST API format:
```json
{
  "type": "list",
  "element-id": 6,
  "element": "string",
  "element-required": false
}
```

PyIceberg format:
```python
ListType(
    element_id=6,
    element_type=StringType(),
    element_required=False
)
```

Conversion logic:
```python
def _type_to_dict(field_type):
    if isinstance(field_type, ListType):
        return {
            "type": "list",
            "element-id": field_type.element_id,
            "element": _type_to_dict(field_type.element_type),  # Recursive!
            "element-required": field_type.element_required
        }
```

#### Struct Type

REST API format:
```json
{
  "type": "struct",
  "fields": [
    {"id": 1, "name": "city", "type": "string", "required": true},
    {"id": 2, "name": "temp", "type": "double", "required": false}
  ]
}
```

PyIceberg format:
```python
StructType(
    NestedField(1, "city", StringType(), required=True),
    NestedField(2, "temp", DoubleType(), required=False)
)
```

#### Map Type

```python
{
  "type": "map",
  "key-id": 10,
  "key": "string",
  "value-id": 11,
  "value": "int",
  "value-required": false
}
```

### Critical Issues Fixed

#### Issue 1: `current-snapshot-id` Must Be Omitted, Not Null

**Wrong:**
```python
metadata["current-snapshot-id"] = None  # DuckDB rejects this!
```

**Correct:**
```python
if table.metadata.current_snapshot_id is not None:
    metadata["current-snapshot-id"] = table.metadata.current_snapshot_id
```

**Why**: DuckDB validates types strictly. `null` is not a valid integer, so the field must be omitted entirely.

#### Issue 2: Type Serialization Requires Recursion

**Wrong:**
```python
"type": str(field.field_type)  # Produces "list<string>"
```

**Correct:**
```python
"type": _type_to_dict(field.field_type)  # Produces nested dict
```

**Why**: DuckDB needs the structured format to properly understand complex types.

---

## DuckDB Integration

Location: `src/ingestion/iceberg_manager.py`

### ATTACH Syntax

```python
# Correct DuckDB v1.4.2+ syntax
ATTACH 'warehouse/' AS iceberg_catalog (
    TYPE iceberg,
    ENDPOINT 'http://localhost:8181',
    AUTHORIZATION_TYPE 'none'  # Critical!
)
```

**Common mistakes:**
- Using `URI` instead of `ENDPOINT`
- Forgetting `AUTHORIZATION_TYPE 'none'`
- Trying to use SQL catalog (not supported by DuckDB ATTACH)

### Writing Data

DuckDB's Iceberg write support is experimental (v1.4.2). Prefer PyIceberg for stability:

```python
# Using PyIceberg (stable)
from pyiceberg.catalog.sql import SqlCatalog

catalog = SqlCatalog(...)
table = catalog.load_table("namespace.table")

# Convert pandas to PyArrow with correct nullable flags
arrow_table = pa.Table.from_pandas(df, schema=pa.schema([
    pa.field("id", pa.int32(), nullable=False),  # Required
    pa.field("name", pa.string(), nullable=True),  # Optional
]))

table.append(arrow_table)
```

**Why PyIceberg over DuckDB writes:**
- More stable (DuckDB Iceberg writes cause segfaults in some cases)
- Better error messages
- Proper validation

### Multi-Cloud Configuration

```python
def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    storage_backend = config.storage_backend

    if storage_backend == "s3":
        conn.execute("INSTALL httpfs")
        conn.execute("LOAD httpfs")
        conn.execute(f"SET s3_region='{region}'")

    elif storage_backend == "azure":
        conn.execute("INSTALL azure")
        conn.execute("LOAD azure")

    elif storage_backend == "gcs":
        conn.execute("INSTALL httpfs")
        conn.execute("LOAD httpfs")

    return conn
```

---

## Troubleshooting

### REST Catalog Won't Start

**Symptoms:**
```
Address already in use: 8181
```

**Solution:**
```bash
# Find and kill process on port 8181
lsof -ti:8181 | xargs kill -9

# Restart
poetry run catalog-server
```

### OAuth2 Authentication Errors

**Symptoms:**
```
AUTHORIZATION_TYPE is 'oauth2', yet no 'secret' was provided
```

**Solution:**
Add to ATTACH statement:
```sql
ATTACH '...' AS cat (..., AUTHORIZATION_TYPE 'none')
```

Also ensure `/v1/config` endpoint returns:
```json
{"defaults": {"authorization_type": "none"}}
```

### DuckDB Segfault on Write

**Symptoms:**
```
Exit code 139 (segmentation fault)
```

**Solution:**
Use PyIceberg for writes instead of DuckDB:
```python
# Instead of:
conn.execute(f"INSERT INTO iceberg_table ...")

# Use:
table = catalog.load_table("namespace.table")
table.append(arrow_data)
```

### Schema Mismatch Errors

**Symptoms:**
```
Mismatch in fields:
❌ │ 1: id: required int  │ 1: id: optional int
```

**Solution:**
Ensure PyArrow schema matches Iceberg schema:
```python
arrow_table = pa.Table.from_pandas(df, schema=pa.schema([
    pa.field("id", pa.int32(), nullable=False),  # Match required=True
]))
```

### Empty Parquet Files

**Symptoms:**
```
File too small to be a Parquet file (107 bytes)
```

**Solution:**
API data fetching failed. Use synthetic data for testing:
```bash
poetry run python examples/test_catalog.py
```

---

## Production Considerations

### Authentication & Authorization

Current implementation uses `authorization_type: none`. For production:

```python
from flask import request
import jwt

@app.before_request
def authenticate():
    token = request.headers.get('Authorization')
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        g.user = payload['user']
    except:
        return jsonify({"error": "Unauthorized"}), 401
```

### High Availability

**Replace SQLite with PostgreSQL:**

```python
catalog = SqlCatalog(
    "prod_catalog",
    **{
        "uri": "postgresql://user:pass@host:5432/iceberg",
        "warehouse": "s3://bucket/warehouse/",
    }
)
```

**Add connection pooling:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    db_uri,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### Caching

Add Redis for metadata caching:

```python
import redis

cache = redis.Redis(host='localhost', port=6379)

@app.route('/v1/namespaces/<namespace>/tables/<table_name>')
def load_table(namespace, table_name):
    cache_key = f"table:{namespace}.{table_name}"

    # Check cache
    cached = cache.get(cache_key)
    if cached:
        return jsonify(json.loads(cached))

    # Load from catalog
    table = catalog.load_table(f"{namespace}.{table_name}")
    response = build_response(table)

    # Cache for 5 minutes
    cache.setex(cache_key, 300, json.dumps(response))

    return jsonify(response)
```

### Monitoring

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

request_count = Counter('catalog_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('catalog_request_duration_seconds', 'Request duration')

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - g.start_time
    request_count.labels(request.method, request.endpoint).inc()
    request_duration.observe(duration)
    return response
```

### Cloud Storage

**S3 Configuration:**

```yaml
storage:
  backend: s3
  s3:
    bucket: my-iceberg-data
    region: us-east-1
    warehouse_path: s3://my-iceberg-data/warehouse/
```

**Credentials:** Use IAM roles instead of access keys:

```python
# DuckDB automatically uses AWS credentials from:
# - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
# - ~/.aws/credentials
# - EC2 instance profile (in production)
```

---

## Performance Optimizations

### 1. Partition Pruning

```python
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import DayTransform

spec = PartitionSpec(
    PartitionField(
        source_id=2,  # timestamp column
        field_id=1000,
        name="day",
        transform=DayTransform()
    )
)

table = catalog.create_table(
    identifier="namespace.table",
    schema=schema,
    partition_spec=spec
)
```

### 2. File Compaction

```python
from pyiceberg.table import Table

def compact_table(table: Table):
    """Compact small files into larger ones."""
    # Get all data files
    snapshot = table.current_snapshot()
    manifests = snapshot.manifests()

    # Group small files
    small_files = [f for f in files if f.file_size_in_bytes < 128 * 1024 * 1024]

    # Rewrite as larger files
    # (Implementation depends on compute engine)
```

### 3. Snapshot Expiration

```python
from datetime import datetime, timedelta

def expire_snapshots(table: Table, older_than_days: int = 7):
    """Remove old snapshots to save storage."""
    cutoff = datetime.now() - timedelta(days=older_than_days)
    cutoff_ms = int(cutoff.timestamp() * 1000)

    table.expire_snapshots(older_than_ms=cutoff_ms)
```

---

## Advanced Features

### Schema Evolution

```python
from pyiceberg.table import Table

table = catalog.load_table("namespace.table")

# Add column
table.update_schema().add_column("humidity", DoubleType()).commit()

# Rename column
table.update_schema().rename_column("temp", "temperature").commit()

# Delete column
table.update_schema().delete_column("old_field").commit()
```

### Time Travel

```python
# Query specific snapshot
snapshot_id = table.metadata.snapshots[0].snapshot_id
df = table.scan(snapshot_id=snapshot_id).to_pandas()

# Query as of timestamp
as_of_timestamp_ms = int(datetime(2024, 1, 1).timestamp() * 1000)
df = table.scan(as_of_timestamp_ms=as_of_timestamp_ms).to_pandas()
```

### Branching (Iceberg v2)

```python
# Create branch for experimentation
table.manage_snapshots().create_branch("experiment").commit()

# Switch to branch
table.manage_snapshots().set_ref_snapshot("experiment", snapshot_id).commit()

# Merge branch
table.manage_snapshots().fast_forward_branch("main", "experiment").commit()
```

---

## File Locations

### REST Catalog Server
`src/catalog/rest_server.py` - Complete Flask implementation of Iceberg REST API

### DuckDB Integration
`src/ingestion/iceberg_manager.py` - ATTACH catalog, create/write tables

### Configuration
`src/ingestion/config.py` - Multi-backend config management

### Example
`examples/test_catalog.py` - Working demo with synthetic data

---

## References

- [Apache Iceberg Spec](https://iceberg.apache.org/spec/)
- [REST Catalog API](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)
- [DuckDB Iceberg Extension](https://duckdb.org/docs/extensions/iceberg)
- [PyIceberg Documentation](https://py.iceberg.apache.org/)
- [DuckDB Iceberg Writes](https://duckdb.org/2025/11/28/iceberg-writes-in-duckdb)

---

Built with ❤️ for learning Apache Iceberg internals