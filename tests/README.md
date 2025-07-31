# Tests

This directory contains test files for the SDOH Dashboard application.

## Test Files

- `test_api.py` - Tests for Census API integration
- `final_test.py` - End-to-end application tests

## Running Tests

From the project root directory:

```bash
# Activate virtual environment
source venv/bin/activate

# Run API tests
python tests/test_api.py

# Run final tests
python tests/final_test.py
```

## Test Coverage

- ✅ Census API connectivity
- ✅ Data processing and caching
- ✅ Map visualization generation
- ✅ Export functionality