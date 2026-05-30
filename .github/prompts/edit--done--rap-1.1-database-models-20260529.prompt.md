---
name: rap-1.1-database-models
description: Ajouter 3 entités SQLAlchemy (RelationshipProfile, Interaction, RelationshipAction)
priority: P0
effort: 3j
ice_score: 33.3
depends_on: rap-1.0-postgres-migration
---

# RAP-1.1: Database Models + ORM

## Contexte
Fondation système RAP. 3 modèles BD + Pydantic schemas + Enums.

## Tâche - Models SQLAlchemy
- [ ] RelationshipProfileDB (id, contact_id FK, relationship_type/enum, proximity_level/enum, trust_level 1-5, business_potential/enum, unique constraint contact_id)
- [ ] InteractionDB (id, contact_id FK, interaction_type/enum, interaction_date, notes)
- [ ] RelationshipActionDB (id, contact_id FK, action_type/enum, priority/enum, status/enum, due_date, completed_at nullable)

## Enums
relationship_type: spouse, family, business, mentor, friend, acquaintance
proximity_level: cold, warm, active, close
business_potential: low, medium, high
interaction_type: call, email, meeting, message, other
action_type: followup, relance, candidature, email, call, meeting
action_status: todo, in_progress, completed, cancelled
priority: low, medium, high

## Pydantic Schemas
Pour chaque modèle: Create, Update, Response

## Configuration
- [ ] Cascades ondelete="CASCADE" sur ForeignKeys
- [ ] Tested avec PostgreSQL schema migration

## Validation
- [ ] alembic revision --autogenerate génère migration
- [ ] Migration applique tables dans PostgreSQL
- [ ] pytest test_models.py passe
- [ ] Enums valides PostgreSQL

## Livrable
- models.py étendus (~200 lignes)
- Migrations Alembic
- Tests models + FK + ENUM

## ✅ Fin
```bash
mv .github/prompts/edit--inbox--rap-1.1-database-models-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.1-database-models-20260529.prompt.md
```
