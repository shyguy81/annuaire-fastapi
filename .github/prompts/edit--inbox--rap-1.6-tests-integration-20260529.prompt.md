---
name: rap-1.6-tests-integration
description: Tests d'intégration pytest pour RAP (CRUD, cascades, aggregations)
priority: P1
effort: 4j
ice_score: 18.0
depends_on: rap-1.1-database-models, rap-1.2-profile-api, rap-1.3-interactions-api, rap-1.4-actions-api, rap-1.5-dashboard-api
---

# RAP-1.6: Tests d'Intégration (pytest)

## Contexte

Tests complets pour valider tous les endpoints RAP 1.1-1.5 + cascades + aggregations.

## Structure Tests

Créer `tests/test_rap.py` avec fixtures conftest.

### Fixtures (conftest.py ou début test_rap.py)

- `db_session`: Session SQLAlchemy PostgreSQL test
- `test_contact`: Contact fixture (pour FK)
- `test_profile`: RelationshipProfile fixture
- `test_interactions`: List[Interaction] fixtures
- `test_actions`: List[RelationshipAction] fixtures

### Test Cases

#### RelationshipProfile (CRUD)

- [ ] POST profile valide → 201 + data retourné
- [ ] POST duplicate contact → 409 Conflict
- [ ] GET profile existant → 200
- [ ] GET contact sans profile → 404
- [ ] PATCH update fields → 200 + changes appliqués
- [ ] PATCH contact inexistant → 404

#### Interactions (CREATE, LIST)

- [ ] POST interaction valide → 201
- [ ] POST contact inexistant → 404
- [ ] GET interactions contact → 200 + list
- [ ] GET avec skip/limit → pagination correcte
- [ ] GET avec type filter → filtre works
- [ ] GET avec since filter → filtre works

#### RelationshipActions (CRUD + special)

- [ ] POST action valide → 201
- [ ] GET /relationship-actions → 200 + all actions
- [ ] GET /relationship-actions?status=todo → filtre works
- [ ] GET /relationship-actions?priority=high → filtre works
- [ ] GET /relationship-actions?contact_id=X → filtre works
- [ ] GET /relationship-actions/due → due_today + overdue corrects
- [ ] PATCH action → 200 + update
- [ ] PATCH /complete → 200 + status=completed + completed_at set

#### Cascades

- [ ] DELETE contact → cascade delete profile, interactions, actions
- [ ] Vérifier BD après delete: tout clean

#### Dashboard Aggregations

- [ ] GET /rap/dashboard → 200 + JSON valide
- [ ] due_today count correct
- [ ] overdue count correct
- [ ] active_relations count correct
- [ ] high_potential count correct
- [ ] recent_interactions count correct
- [ ] timestamp ISO 8601

## Validation

- [ ] Tous tests passent
- [ ] Fixtures complètes pour test data
- [ ] Coverage >= 85% pour RAP endpoints
- [ ] Tests rapides (< 1s par test)

## Livrable

- `tests/test_rap.py` (~50 test cases)
- `tests/conftest.py` (fixtures)

## ✅ Fin du traitement

```bash
mv .github/prompts/edit--inbox--rap-1.6-tests-integration-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.6-tests-integration-20260529.prompt.md
```
