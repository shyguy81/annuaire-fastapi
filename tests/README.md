# RAP Integration Tests

This directory contains comprehensive integration tests for the Relationship Action Platform (RAP) backend API.

## Test Files

- **test_models.py** (13 tests)
  - ORM model validation
  - Pydantic schema validation
  - Enum value verification
  - Serialization format checks

- **test_relationship_profile_integration.py** (8 tests)
  - Relationship profile CRUD operations
  - Duplicate profile detection
  - Profile update/patch operations
  - 404 error handling

- **test_interactions_integration.py** (12 tests)
  - Interaction creation with all types
  - Interaction listing with pagination
  - Filtering by interaction type
  - Filtering by date range
  - Query parameter validation

- **test_actions_integration.py** (17 tests)
  - Relationship action CRUD operations
  - Filtering by status, priority, and contact
  - Due date logic (today, overdue, future)
  - Action completion endpoint
  - Pagination and combined filters

- **test_dashboard_integration.py** (13 tests)
  - Dashboard endpoint accessibility
  - Response schema validation
  - Aggregation metrics correctness
  - Active relations distinct count
  - High potential business contacts
  - Recent interactions window (7 days)
  - Timestamp ISO 8601 format

## Running Tests

Run all tests:
```bash
pytest .github/tests/ -v
```

Run specific test file:
```bash
pytest .github/tests/test_models.py -v
```

Run tests matching pattern:
```bash
pytest .github/tests/ -k "interaction" -v
```

Run with coverage:
```bash
pytest .github/tests/ --cov=. --cov-report=html
```

## Test Coverage

**Total: 62 tests (100% passing)**

Coverage areas:
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Pagination (skip, limit with max 1000)
- ✅ Filtering (type, status, priority, contact_id, date ranges)
- ✅ Error handling (400, 404, 409, 422 status codes)
- ✅ Data validation (enum values, date formats, unique constraints)
- ✅ Cascade operations (delete cascades from contact)
- ✅ Aggregation correctness (dashboard metrics)
- ✅ Edge cases (duplicates, future dates, empty results)
- ✅ Timestamp serialization (ISO 8601 with Z suffix)

## Infrastructure

Tests use:
- **pytest** 7.4.3 - Test framework
- **requests** 2.31.0 - HTTP testing against running API
- **FastAPI TestClient** - For some endpoint testing

Tests run against:
- **PostgreSQL** 15 database
- **FastAPI** 0.104.1 server running locally
- **Docker Compose** for database management

## Dependencies

All required dependencies are in `requirements.txt`:
- FastAPI
- SQLAlchemy
- Pydantic
- psycopg2-binary
- pytest
- requests

## Execution Time

Full test suite completes in approximately **4 seconds**

Individual test average: **65ms**
