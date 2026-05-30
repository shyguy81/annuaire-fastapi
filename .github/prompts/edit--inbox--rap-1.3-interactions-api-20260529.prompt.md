---
name: rap-1.3-interactions-api
description: 2 endpoints pour Interactions (POST, GET avec pagination)
priority: P0
effort: 2j
ice_score: 40.0
depends_on: rap-1.1-database-models
---

# RAP-1.3: API Endpoints — Interactions (2 routes)

## Contexte

Endpoints pour créer et lister interactions (calls, emails, meetings) avec un contact.

## Routes à implémenter

### 1. POST /contacts/{contact_id}/interactions

**Input:** InteractionCreate
- interaction_type (enum: call, email, meeting, message, other)
- interaction_date (datetime, required)
- notes (text, optional)

**Output:** 201 Created + InteractionResponse

**Validation:**
- contact_id existe
- interaction_type in enum values

### 2. GET /contacts/{contact_id}/interactions

**Query Parameters:**
- `skip` (default 0)
- `limit` (default 100, max 1000)
- `type` (optional, filter by interaction_type)
- `since` (optional, filter by date YYYY-MM-DD, interaction_date >= since)

**Output:** 200 OK + { items: [InteractionResponse], total: int }

**Pagination:**
- Implémenter offset/limit pagination
- Retourner `total` count + `items` list

## Validation

- [ ] POST valide → 201 Created
- [ ] POST contact inexistant → 404
- [ ] GET valide → 200 + list
- [ ] GET avec skip/limit → pagination correcte
- [ ] GET avec type filter → filtre par interaction_type
- [ ] GET avec since filter → filtre par date (>=)
- [ ] Paramètres invalides → 400 Bad Request
- [ ] limit > 1000 → clampé à 1000

## Livrable

- 2 endpoints dans `main.py` (~40 lignes)
- Pagination logic
- Filtering logic
- Tests pagination + filters

## ✅ Fin du traitement

```bash
mv .github/prompts/edit--inbox--rap-1.3-interactions-api-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.3-interactions-api-20260529.prompt.md
```
