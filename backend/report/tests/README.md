# Report Module Test Suite

This directory contains comprehensive unit and integration tests for the report module.

## Prerequisites

### Required Microservices
The integration tests require the following microservices to be running:
- **Users Service** (http://localhost:5003)
- **Tasks Service** (http://localhost:5002)
- **Projects Service** (http://localhost:5001)
- **Team Service** (http://localhost:5004)
- **Department Service** (http://localhost:5005)

### Test Data Requirements
Integration tests assume the following test data exists:
- User ID 101: Staff user with tasks and projects
- User ID 352: Manager user with a team
- User ID 399: Director user with a department
- User ID 999999: Non-existent user (for 404 tests)

## Running Tests

### Run all tests
```bash
coverage run -m unittest discover tests -q
```

### Run Only Unit Tests
```bash
cd backend/report
python -m unittest tests.test_report_model -v
```

### Run Only Integration Tests
```bash
cd backend/report
python -m unittest tests.test_report_controller_integration -v
```

### Run Specific Test Class
```bash
cd backend/report
python -m unittest tests.test_report_model.TestReportModel -v
python -m unittest tests.test_report_model.TestReportDataModel -v
python -m unittest tests.test_report_model.TestTeamReportDataModel -v
```

### Run Specific Test Method
```bash
cd backend/report
python -m unittest tests.test_report_model.TestReportModel.test_report_creation_with_required_fields -v
```
