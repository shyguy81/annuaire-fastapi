---
name: rap-1.5-dashboard-api
description: 1 endpoint Dashboard avec aggregations SQL
priority: P0
effort: 2j
ice_score: 42.75
depends_on: rap-1.2-profile-api, rap-1.3-interactions-api, rap-1.4-actions-api
---

# RAP-1.5: API Endpoint — RAP Dashboard

## Contexte

Endpoint d'agrégation pour afficher stats système RAP en un seul appel.

## Route à implémenter

### GET /rap/dashboard

**Output:** 200 OK + DashboardResponse

```json
{
  "due_today": 5,
  "overdue": 2,
  "active_relations": 12,
  "high_potential": 8,
  "recent_interactions": 23,
  "timestamp": "2026-05-29T14:30:00Z"
}
```

## Aggregations à implémenter

- **due_today**: COUNT(RelationshipActionDB) WHERE due_date = TODAY AND status IN [todo, in_progress]
- **overdue**: COUNT(RelationshipActionDB) WHERE due_date < TODAY AND status IN [todo, in_progress]
- **active_relations**: COUNT(DISTINCT contact_id) FROM RelationshipProfileDB WHERE proximity_level IN ['warm', 'active', 'close']
- **high_potential**: COUNT(DISTINCT contact_id) FROM RelationshipProfileDB WHERE business_potential = 'high'
- **recent_interactions**: COUNT(InteractionDB) WHERE interaction_date > TODAY - 7 days
- **timestamp**: NOW() in ISO 8601

## Validation

- [ ] Tous les counts corrects
- [ ] Timestamp valide
- [ ] Réponse JSON valide
- [ ] Aggregations optimisées (pas N+1 queries)
- [ ] Tester avec données de test (fixtures)

## Livrable

- 1 endpoint dans `main.py` (~40 lignes)
- SQL aggregations optimisées
- Tests pour vérifier counts corrects

## ✅ Fin du traitement

```bash
mv .github/prompts/edit--inbox--rap-1.5-dashboard-api-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.5-dashboard-api-20260529.prompt.md
```
