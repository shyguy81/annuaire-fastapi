---
name: rap-1.7-documentation-api
description: Documentation OpenAPI + docstrings pour tous endpoints RAP
priority: P1
effort: 2j
ice_score: 30.0
depends_on: rap-1.1-database-models, rap-1.2-profile-api, rap-1.3-interactions-api, rap-1.4-actions-api, rap-1.5-dashboard-api
---

# RAP-1.7: Documentation API (OpenAPI + Exemples)

## Contexte

FastAPI auto-génère Swagger via `/docs`. Enrichir avec docstrings + examples.

## Tâche

### Pour chaque endpoint (RAP-1.2 à RAP-1.5)

#### 1. Docstring endpoint

```python
@app.post("/contacts/{contact_id}/relationship-profile")
def create_profile(contact_id: int, profile: RelationshipProfileCreate):
    """
    Créer un profil relationnel pour un contact.
    
    - **contact_id**: ID du contact (doit exister)
    - **profile**: Données profil (relationship_type, trust_level, etc.)
    
    Returns:
    - 201: Profile créé
    - 404: Contact introuvable
    - 409: Profile existe déjà
    """
```

#### 2. Exemple Request/Response

Ajouter au schema Pydantic:

```python
class RelationshipProfileCreate(BaseModel):
    relationship_type: str
    proximity_level: str
    trust_level: int
    business_potential: str = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "relationship_type": "business",
                "proximity_level": "warm",
                "trust_level": 4,
                "business_potential": "high"
            }
        }
    )
```

#### 3. Documenter Enums

Ajouter description à chaque enum:

```python
class RelationshipType(str, Enum):
    """Types de relations: spouse, family, business, mentor, friend, acquaintance"""
    spouse = "spouse"
    family = "family"
    business = "business"
    mentor = "mentor"
    friend = "friend"
    acquaintance = "acquaintance"
```

### À ajouter

- [ ] Docstrings complets pour tous endpoints RAP
- [ ] Examples JSON pour chaque route (request + response)
- [ ] Description des enums
- [ ] Description des paramètres query (skip, limit, type, since, status, priority)
- [ ] Documentation codes erreur (400, 404, 409, etc.)

## Validation

- [ ] `GET /docs` charge sans erreur
- [ ] Swagger UI affiche tous endpoints
- [ ] Exemples JSON visibles dans Swagger
- [ ] Descriptions lisibles + utiles
- [ ] `GET /openapi.json` valide schema OpenAPI

## Livrable

- Docstrings dans tous endpoints
- Examples dans Pydantic schemas
- Enum descriptions
- Swagger auto-generated OK

## ✅ Fin du traitement

```bash
mv .github/prompts/edit--inbox--rap-1.7-documentation-api-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.7-documentation-api-20260529.prompt.md
```
