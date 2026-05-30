---
name: rap-1.2-1.5-endpoints-api
description: 11 endpoints RAP-1.2 à 1.5 (Profile, Interactions, Actions, Dashboard)
priority: P0
effort: 9j
ice_score: 166.75
depends_on: rap-1.1-database-models
---

# RAP-1.2 à RAP-1.5: API Endpoints (11 routes)

## RAP-1.2: Relationship Profile (3 endpoints)
- POST /contacts/{contact_id}/relationship-profile → 201
- GET /contacts/{contact_id}/relationship-profile → 200/404
- PATCH /contacts/{contact_id}/relationship-profile → 200/404

## RAP-1.3: Interactions (2 endpoints)
- POST /contacts/{contact_id}/interactions → 201
- GET /contacts/{contact_id}/interactions?skip=0&limit=100&type=&since= → 200

## RAP-1.4: Actions (5 endpoints)
- POST /contacts/{contact_id}/relationship-actions → 201
- GET /relationship-actions?status=&priority=&contact_id= → 200 paginated
- GET /relationship-actions/due → 200 (due_today + overdue)
- PATCH /relationship-actions/{action_id} → 200
- PATCH /relationship-actions/{action_id}/complete → 200 (status=completed, completed_at=NOW)

## RAP-1.5: Dashboard (1 endpoint)
- GET /rap/dashboard → 200 (due_today, overdue, active_relations, high_potential, recent_interactions, timestamp)

## Validation
- All endpoints 201/200 Created/OK
- 404 Not Found for missing resources
- 409 Conflict for duplicates (Profile)
- 400 Bad Request for invalid data
- Pagination works (skip, limit)
- Filters work (type, since, status, priority, contact_id)
- Dashboard aggregations correct

## Livrable
- ~90 lignes endpoints dans main.py
- Query filtering + pagination logic
- Validation complète
- Tests pytest pour tous cases

## ✅ Fin
```bash
mv .github/prompts/edit--inbox--rap-1.2-1.5-endpoints-api-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.2-1.5-endpoints-api-20260529.prompt.md
```
