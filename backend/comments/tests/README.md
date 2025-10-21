# Comments Module Tests

This directory contains comprehensive tests for the comments module.

## Test Files

- `test_comment_model.py` - Unit tests for the Comment model class
- `test_comment_controller_integration.py` - Integration tests for comment API endpoints

## Running Tests

### Run All Tests
```bash
cd backend/comments
python run_tests.py
```

### Run Individual Test Files
```bash
# Model tests only (no environment variables needed)
cd backend/comments/tests
python -m unittest test_comment_model -v

# Controller tests (requires Supabase environment variables)
cd backend/comments/tests
python -m unittest test_comment_controller_integration -v
```

## Environment Variables

For integration tests, you need to set these environment variables:

```bash
set SUPABASE_URL=https://your-project.supabase.co
set SUPABASE_SERVICE_KEY=your-service-key
```

## Test Coverage

### Model Tests (`test_comment_model.py`)
- Comment creation with defaults and specific values
- Dictionary conversion (to_dict/from_dict)
- Roundtrip conversion testing
- Special character and unicode handling
- Long content handling
- Edge cases and error conditions

### Controller Tests (`test_comment_controller_integration.py`)
- Comment creation (success and failure cases)
- Retrieving comments by task
- Getting individual comments
- Updating comments
- Deleting comments
- Health check endpoint
- Multiple comments scenarios
- Cross-task isolation

## Test Data Cleanup

The integration tests automatically clean up test data after each test run to prevent database pollution.
