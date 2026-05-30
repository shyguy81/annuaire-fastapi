"""
RAP Integration Tests Module

Contains comprehensive integration tests for all RAP (Relationship Action Platform)
endpoints and database models.

Test Files:
- test_models.py: ORM model and Pydantic schema validation
- test_relationship_profile_integration.py: Relationship profile CRUD tests
- test_interactions_integration.py: Interaction creation and listing tests
- test_actions_integration.py: Relationship action CRUD and special endpoints
- test_dashboard_integration.py: Dashboard aggregation metrics tests

To run tests:
    pytest .github/tests/ -v
    pytest .github/tests/test_models.py -v
    pytest .github/tests/ -k "integration" -v
"""
