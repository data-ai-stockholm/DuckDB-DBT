# Changelog

All notable changes to this project will be documented in this file.

## [0.2.0] - 2025-01-13

### Added
- **Apache Iceberg Polaris Support** - Full integration with Polaris REST catalog for production deployments
  - Support for AWS managed Polaris service
  - Support for self-hosted Polaris deployments
  - Support for Nessie (alternative REST catalog)
  - OAuth 2.0 authentication support for Polaris
  - Comprehensive setup guide with multiple deployment options

- **Enhanced Configuration Management**
  - Environment variable support for Polaris authentication (ICEBERG_CLIENT_ID, ICEBERG_CLIENT_SECRET)
  - Support for catalog type configuration via ICEBERG_CATALOG_TYPE
  - Multi-cloud warehouse path configuration

- **Updated REST Catalog Support in DuckDB**
  - Improved ATTACH statement handling for REST catalogs
  - OAuth 2.0 authentication handling in iceberg_manager.py
  - Better error messages for catalog connection failures

- **Documentation**
  - New `docs/POLARIS_SETUP.md` with detailed Polaris setup instructions
  - Cloud provider deployment options (AWS, self-hosted, Nessie)
  - Troubleshooting guide for common Polaris issues
  - Production configuration examples

### Changed
- **Default Catalog Configuration** - REST catalog now primary configuration (was local)
- **dbt/profiles.yml** - Simplified development profile, enhanced production profiles with REST catalog support
- **storage.yaml** - Updated comments and examples to reference Polaris
- **README** - Updated to highlight Polaris as production catalog option
- **Version** - Bumped to 0.2.0 to reflect production-ready Polaris support

### Improved
- Enhanced `config.py` with Polaris authentication configuration options
- Improved `iceberg_manager.py` with better OAuth 2.0 support
- Better error handling for REST catalog connections
- More comprehensive environment variable support

## [0.1.0] - 2024-12-08

### Initial Release
- Core data ingestion from US National Weather Service API
- Apache Iceberg support with local filesystem catalog
- dbt data transformation models
- Prefect workflow orchestration
- GitHub Actions CI/CD
- Multi-cloud storage support (S3, Azure Blob, GCS)
- Custom Iceberg REST catalog implementation
- Comprehensive documentation and examples
