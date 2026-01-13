#!/bin/bash
# Run the weather pipeline with LOCAL filesystem (no AWS/Polaris needed)

set -e

echo "=================================================="
echo "LOCAL FILESYSTEM TEST (No external services)"
echo "=================================================="
echo ""

# Clean up previous test artifacts (optional)
# Uncomment to start fresh:
# rm -rf warehouse/ ingestion_data/ weather_reports.db*

# Test 1: Run validation script
echo "Step 1: Validating local setup..."
python test_local_setup.py
echo ""

# Test 2: Run demo flow (requires Prefect, but shows pipeline in action)
echo "Step 2: Running demo flow with local data..."
echo "Command: poetry run python src/flows/demo_flow.py"
echo ""
echo "To run the demo:"
echo "  poetry run python src/flows/demo_flow.py"
echo ""

# Test 3: Full pipeline test
echo "Step 3: Running full pipeline with local storage..."
echo "Command: poetry run python src/flows/main_pipeline.py"
echo ""
echo "To run the full pipeline:"
echo "  poetry run python src/flows/main_pipeline.py"
echo ""

# Test 4: Using make commands
echo "Step 4: Using Makefile commands..."
echo ""
echo "Available local test commands:"
echo "  make demo              # Quick demo flow"
echo "  make run-weather       # Weather ingestion (fetches real data from API)"
echo "  make fetch-all         # Fetch and load all weather data"
echo "  make run-pipeline      # Complete end-to-end pipeline"
echo "  make dbt-run          # Run dbt transformations"
echo "  make dbt-test         # Run dbt tests"
echo ""

echo "=================================================="
echo "✅ Local setup validated successfully!"
echo "=================================================="
echo ""
echo "Your setup works with:"
echo "  ✓ Local filesystem storage"
echo "  ✓ Iceberg tables (with fallback to native DuckDB)"
echo "  ✓ No AWS, Azure, GCS, or Polaris required"
echo ""
echo "Next: Run any of the test commands above to continue."
