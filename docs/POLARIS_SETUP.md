# Apache Iceberg Polaris Catalog Setup

This guide explains how to integrate Apache Iceberg Polaris with the weather data pipeline.

## What is Polaris?

**Apache Iceberg Polaris** is an open-source REST API server that manages Iceberg table metadata and catalog operations. It provides:

- **Multi-Warehouse Support**: Manage tables across multiple data warehouses
- **High Availability**: Reliable catalog service for production workloads
- **Standards-Based**: Implements Apache Iceberg REST Catalog specification
- **Storage Agnostic**: Works with S3, Azure Blob, GCS, and local storage
- **Authentication**: Built-in support for OAuth 2.0, API keys, and mutual TLS

## Deployment Options

### Option 1: AWS Managed Service (Recommended for Production)

**AWS Iceberg Polaris Catalog** (via AWS Glue or dedicated service):

1. **Create a Polaris Instance** in your AWS account
2. **Configure credentials**:
   ```bash
   export ICEBERG_REST_URI=https://your-polaris.us-east-1.amazonaws.com
   export ICEBERG_WAREHOUSE=s3://your-weather-bucket/warehouse/
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_DEFAULT_REGION=us-east-1
   ```

3. **Test connection**:
   ```bash
   make fetch-all  # Will use Polaris as catalog
   ```

### Option 2: Nessie (Alternative REST Catalog)

**Nessie** is another popular REST catalog implementation with git-like versioning:

1. **Deploy Nessie Server** (Docker/Kubernetes)
2. **Configure**:
   ```bash
   export ICEBERG_REST_URI=http://nessie-server:19120  # Nessie default port
   export ICEBERG_WAREHOUSE=s3://your-bucket/warehouse/
   ```

### Option 3: Self-Hosted Polaris (Development)

1. **Clone Polaris**: `git clone https://github.com/apache/iceberg-polaris.git`
2. **Build & Run**: Follow [Polaris documentation](https://iceberg.apache.org/polaris-install/)
3. **Configure**:
   ```bash
   export ICEBERG_REST_URI=http://localhost:8181  # Default Polaris port
   export ICEBERG_WAREHOUSE=s3://local-bucket/warehouse/
   ```

## Configuration Steps

### 1. Choose Storage Backend

Edit `config/storage.yaml`:

```yaml
storage:
  backend: s3  # Or 'local', 'azure', 'gcs'

  s3:
    bucket: your-weather-data-bucket
    region: us-east-1
    warehouse_path: s3://your-weather-data-bucket/warehouse/

table_format: iceberg

iceberg:
  catalog:
    type: rest  # Enable REST catalog (Polaris)
    uri: https://your-polaris-instance.com  # Override via ICEBERG_REST_URI
    warehouse: s3://your-weather-data-bucket/warehouse/
```

### 2. Set Environment Variables

Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your Polaris details:

```bash
# Storage Backend
STORAGE_BACKEND=s3
S3_BUCKET=your-weather-data-bucket
AWS_DEFAULT_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Iceberg Polaris Catalog
ICEBERG_REST_URI=https://your-polaris-instance.com
ICEBERG_WAREHOUSE=s3://your-weather-data-bucket/warehouse/

# Optional: Polaris Authentication
ICEBERG_CLIENT_ID=your_client_id
ICEBERG_CLIENT_SECRET=your_client_secret
```

### 3. Install Dependencies

```bash
poetry install
```

### 4. Test Polaris Connection

```bash
# Query Iceberg table structure
python list_catalog.py

# Test data operations
python query_iceberg.py

# Run the full pipeline
make run-pipeline
```

## Troubleshooting

### Connection Failed

**Error**: `Could not attach to Iceberg catalog`

**Solution**:
- Verify `ICEBERG_REST_URI` is correct and accessible
- Check network connectivity to Polaris server
- Verify credentials if using authentication
- Enable debug logging: `export DEBUG=1`

### Authentication Issues

**Error**: `401 Unauthorized`

**Solution**:
- Check `ICEBERG_CLIENT_ID` and `ICEBERG_CLIENT_SECRET`
- Ensure credentials have warehouse access in Polaris
- Verify token hasn't expired

### Storage Access Issues

**Error**: `S3 access denied`

**Solution**:
- Verify AWS credentials in `.env`
- Check S3 bucket policy allows your IAM user
- Ensure bucket region matches `AWS_DEFAULT_REGION`
- Check warehouse path permissions

## Advanced Configuration

### Using Polaris OAuth 2.0

For managed Polaris services with OAuth:

```bash
export ICEBERG_OAUTH_SERVER_URI=https://auth.your-domain.com
export ICEBERG_CLIENT_ID=your_client_id
export ICEBERG_CLIENT_SECRET=your_client_secret
```

### Multi-Warehouse Setup

Use Polaris to manage Iceberg tables across multiple warehouses:

```bash
# All tables visible through single Polaris endpoint
# Configure different warehouses:
# - Warehouse 1: s3://bucket-1/warehouse/
# - Warehouse 2: s3://bucket-2/warehouse/
# Polaris routes queries to appropriate warehouse
```

### Time Travel with Polaris

Query historical data using Polaris snapshots:

```python
# In dbt or Python:
SELECT * FROM iceberg_catalog.weather_data.observations
VERSION AS OF '2024-01-15 10:30:00'
```

## Performance Considerations

- **Metadata Caching**: Polaris caches table metadata for performance
- **REST Latency**: REST catalog adds network latency vs local catalogs
- **Partition Pruning**: Still effective with Polaris
- **Batch Operations**: Group operations for better performance

## Migration from Local Catalog

If moving from local filesystem catalog to Polaris:

1. **Export metadata** from local warehouse
2. **Set up Polaris** with same storage backend
3. **Register tables** in Polaris
4. **Update configuration** to use REST URI
5. **Validate data** before switching production traffic

## Next Steps

- [Iceberg Polaris Docs](https://iceberg.apache.org/polaris-install/)
- [DuckDB Iceberg Extension](https://duckdb.org/docs/extensions/iceberg.html)
- [Project README](./README.md)