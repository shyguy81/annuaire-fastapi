---
name: rap-1.2-profile-api
description: 3 endpoints pour Relationship Profile (POST, GET, PATCH)
priority: P0
effort: 2j
ice_score: 45.0
depends_on: rap-1.1-database-models
---

# RAP-1.2: API Endpoints — Relationship Profile (3 routes)

## Contexte

Endpoints CRUD pour gérer profil relationnel d'un contact.

## Routes à implémenter

### 1. POST /contacts/{contact_id}/relationship-profile

**Input:** RelationshipProfileCreate
- relationship_type (enum, required)
- proximity_level (enum, required)
- trust_level (1-5, required)
- business_potential (enum, optional)

**Output:** 201 Created + RelationshipProfileResponse

**Validation:**
- contact_id existe dans BD
- Un seul profil par contact (409 Conflict si existe déjà)
- relationship_type in enum values
- trust_level in [1, 5]

### 2. GET /contacts/{contact_id}/relationship-profile

**Output:** 200 OK + RelationshipProfileResponse
**Error:** 404 Not Found si pas de profil

### 3. PATCH /contacts/{contact_id}/relationship-profile

**Input:** RelationshipProfileUpdate (tous les champs optionnels)
**Output:** 200 OK + RelationshipProfileResponse
**Error:** 404 Not Found si pas de profil

## Validation

- [ ] POST avec données valides → 201 Created + data retourné
- [ ] POST duplicate contact_id → 409 Conflict
- [ ] GET contact existant → 200 + profil
- [ ] GET contact sans profil → 404
- [ ] PATCH met à jour champs fournis uniquement
- [ ] PATCH contact inexistant → 404
- [ ] trust_level < 1 ou > 5 → 400 Bad Request
- [ ] relationship_type invalide → 400 Bad Request

## Livrable

- 3 endpoints dans `main.py` (~50 lignes)
- Validation complète
- Tests pytest couvrant happy path + error cases

## ✅ Fin du traitement

```bash
mv .github/prompts/edit--inbox--rap-1.2-profile-api-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.2-profile-api-20260529.prompt.md
```
