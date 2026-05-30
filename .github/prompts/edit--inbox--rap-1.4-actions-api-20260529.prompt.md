---
name: rap-1.4-actions-api
description: 5 endpoints pour Relationship Actions (POST, GET global, GET due, PATCH, complete)
priority: P0
effort: 3j
ice_score: 33.3
depends_on: rap-1.1-database-models
---

# RAP-1.4: API Endpoints — Relationship Actions (5 routes)

## Contexte

Endpoints pour créer, lister, filtrer et compléter les actions de suivi avec contacts.

## Routes à implémenter

### 1. POST /contacts/{contact_id}/relationship-actions

**Input:** RelationshipActionCreate
- action_type (enum: followup, relance, candidature, email, call, meeting)
- priority (enum: low, medium, high)
- due_date (date)
- notes (text, optional)

**Output:** 201 Created + RelationshipActionResponse

### 2. GET /relationship-actions

**Query Parameters:**
- `skip` (default 0)
- `limit` (default 100)
- `status` (optional: todo, in_progress, completed, cancelled)
- `priority` (optional: low, medium, high)
- `contact_id` (optional: filter by specific contact)

**Output:** 200 OK + { items: [RelationshipActionResponse], total: int }

### 3. GET /relationship-actions/due

Liste actions dues aujourd'hui + overdue.

**Query Parameters:**
- `skip`, `limit` (pagination)

**Output:** 200 OK + { items, total, due_today: int, overdue: int }

Contient actions WHERE due_date <= TODAY AND status IN [todo, in_progress]

### 4. PATCH /relationship-actions/{action_id}

Mettre à jour n'importe quel champ.

**Input:** RelationshipActionUpdate (tous fields optionnels)
**Output:** 200 OK + RelationshipActionResponse
**Error:** 404 si action inexistante

### 5. PATCH /relationship-actions/{action_id}/complete

Marquer action comme terminée.

**Input:** (empty ou optionnel notes)
**Output:** 200 OK + RelationshipActionResponse

**Action:**
- Set status = "completed"
- Set completed_at = NOW()

## Validation

- [ ] POST valide → 201 Created
- [ ] GET global avec filters (status, priority, contact_id) → filtre correctement
- [ ] GET /due retourne actions due + overdue
- [ ] PATCH met à jour champs
- [ ] PATCH complete marque action done + set completed_at
- [ ] Action inexistante → 404
- [ ] Enum invalides → 400
- [ ] Pagination marche

## Livrable

- 5 endpoints dans `main.py` (~80 lignes)
- Query filtering logic
- Complete action logic
- Tests pour tous les filters

## ✅ Fin du traitement

```bash
mv .github/prompts/edit--inbox--rap-1.4-actions-api-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.4-actions-api-20260529.prompt.md
```
