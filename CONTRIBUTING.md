# Contributing to DuckDB-dbt Weather Pipeline

Thank you for your interest in contributing! This guide will help you get started.

## Repository Structure

```
duckdb-dbt/
├── config/          # Application configuration
├── dbt/             # dbt project (models, profiles)
├── docs/            # Documentation (README, technical guides)
├── scripts/         # Deployment and utility scripts
├── src/             # Source code
│   ├── catalog/     # Iceberg REST catalog implementation
│   ├── flows/       # Prefect orchestration flows
│   └── ingestion/   # Data ingestion modules
└── examples/        # Demo scripts and examples
```

## Development Setup

### Prerequisites
- Python 3.10+
- Poetry for dependency management
- Git

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/duckdb-dbt.git
cd duckdb-dbt

# 2. Install dependencies
make setup

# 3. Start services
make start

# 4. Run tests
make test
```

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

**Adding a new data source:**
- Add fetcher to `src/ingestion/`
- Create Prefect flow in `src/flows/`
- Add dbt model to `dbt/models/`

**Modifying dbt models:**
- Edit models in `dbt/models/staging/` or `dbt/models/marts/`
- Run `make dbt-run` to test
- Add tests in `dbt/models/schema.yml`

**Updating documentation:**
- User guides → `docs/README.md`
- Technical details → `docs/CLAUDE.md`

### 3. Code Quality

Run these before committing:

```bash
make lint      # Check code style
make format    # Auto-format code
make test      # Run tests
```

### 4. Commit Guidelines

Follow conventional commits:

```bash
git commit -m "feat: add new weather station source"
git commit -m "fix: resolve dbt model schema issue"
git commit -m "docs: update README with new feature"
git commit -m "refactor: simplify data ingestion logic"
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 5. Testing

```bash
# Run all tests
make test

# Run dbt tests
make dbt-test

# Test specific flow
poetry run python src/flows/weather_ingestion.py
```

### 6. Create Pull Request

1. Push your branch: `git push origin feature/your-feature-name`
2. Create PR on GitHub
3. Ensure CI passes
4. Wait for review

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Ruff for linting/formatting

### SQL (dbt)
- Use lowercase keywords
- Indent with 4 spaces
- Use CTEs for readability
- Add comments for complex logic

### Documentation
- Keep README.md user-focused
- Put technical details in CLAUDE.md
- Use code examples
- Include diagrams where helpful

## Adding New Features

### New Data Source

1. Create fetcher in `src/ingestion/fetch_*.py`
2. Add configuration to `config/storage.yaml`
3. Create Prefect flow in `src/flows/`
4. Add dbt staging model in `dbt/models/staging/`
5. Update documentation

### New dbt Model

1. Create SQL file in `dbt/models/staging/` or `dbt/models/marts/`
2. Add schema tests in `schema.yml`
3. Run `make dbt-run` and `make dbt-test`
4. Document in model docstring

### New Prefect Flow

1. Create flow file in `src/flows/`
2. Add to `scripts/deploy_flows.py`
3. Update `prefect.yaml` if scheduled
4. Add documentation

## Project Standards

### File Organization
- One class/module per file
- Group related functionality
- Use `__init__.py` for clean imports

### Configuration
- Use `config/storage.yaml` for app config
- Use environment variables for secrets
- Never commit `.env` files

### Testing
- Write tests for new features
- Maintain >80% coverage
- Test edge cases

## Getting Help

- Check existing issues
- Read documentation in `docs/`
- Ask questions in discussions
- Reference `docs/CLAUDE.md` for technical details

## Resources

- [Prefect Documentation](https://docs.prefect.io/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Apache Iceberg](https://iceberg.apache.org/)
- [DuckDB Docs](https://duckdb.org/docs/)

---

Thank you for contributing! 🎉
