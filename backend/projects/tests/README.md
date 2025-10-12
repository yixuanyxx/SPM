# Project Model Tests

This directory contains unit tests for the Project module.

## Test Files

- `test_project_model.py` - Unit tests for the Project model class

## Running Tests

### Run all tests
```bash
python run_tests.py
```

### Run specific test file
```bash
python -m unittest tests.test_project_model -v
```

### Run specific test class
```bash
python -m unittest tests.test_project_model.TestProjectModel -v
```

### Run specific test method
```bash
python -m unittest tests.test_project_model.TestProjectModel.test_project_creation_with_defaults -v
```

## Test Coverage

The test suite covers:
- Project creation with default values
- Project creation with specific values
- Conversion to dictionary (to_dict)
- Conversion from dictionary (from_dict)
- Handling of collaborators (both string and list formats)
- Handling of tasks (both string and list formats)
- Roundtrip conversion (to_dict -> from_dict)
- Edge cases (None values, empty strings, type conversions)

## Requirements

Install test dependencies:
```bash
pip install -r test_requirements.txt
```

## Notes

- Tests use Python's built-in `unittest` framework
- No external database connection required for model tests
- Tests validate data type conversions and edge cases

