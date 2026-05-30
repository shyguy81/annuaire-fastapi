---
name: rap-1.6-1.7-tests-docs
description: Tests pytest + Documentation OpenAPI pour RAP endpoints
priority: P1
effort: 6j
ice_score: 48.0
depends_on: rap-1.2-1.5-endpoints-api
---

# RAP-1.6: Tests d'Intégration
## Test Coverage
- CRUD RelationshipProfile (201, 404, 409, 200 PATCH)
- CRUD Interactions (201, 404, 200 list, pagination, filters)
- CRUD RelationshipActions (201, 404, 200, PATCH complete)
- DELETE Contact → cascade (profile, interactions, actions deleted)
- Dashboard aggregations (counts correct)

## Structure
- tests/test_rap.py (~50 test cases)
- tests/conftest.py (fixtures: db_session, test_contact, test_profile, etc)
- Fixtures pour test data

## Validation
- All tests pass
- Coverage >= 85% RAP endpoints
- Tests rapides (< 1s each)

# RAP-1.7: Documentation OpenAPI
## Docstrings
- Ajouter docstring complet pour chaque endpoint
- Décrire parameters, inputs, outputs, error codes
- Exemples JSON pour Request/Response

## Pydantic Examples
```python
model_config = ConfigDict(
    json_schema_extra={
        "example": {...}
    }
)
```

## Enums Documentation
- Description pour chaque enum value
- Exemple: class RelationshipType(str, Enum) avec descriptions

## Validation
- GET /docs charge sans error
- Swagger UI affiche tous endpoints + examples
- GET /openapi.json valide

## Livrable
- Docstrings complets dans main.py
- Examples dans Pydantic schemas
- Enum descriptions
- Swagger auto-generated OK

## ✅ Fin
```bash
mv .github/prompts/edit--inbox--rap-1.6-1.7-tests-docs-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.6-1.7-tests-docs-20260529.prompt.md
```
