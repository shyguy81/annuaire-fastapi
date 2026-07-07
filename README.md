# Annuaire Contacts — API FastAPI

Backend FastAPI pour "Annuaire Contacts", une Relationship Action Platform (RAP) : gestion de contacts, profils relationnels, interactions et actions de suivi.

## Stack

- FastAPI
- PostgreSQL via SQLAlchemy
- Pydantic v2 (schémas)
- Alembic (migrations)

## Lancer manuellement (sans Docker)

```bash
python3 -m virtualenv --always-copy .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker

```bash
docker compose up -d          # postgres + backend
docker compose up -d postgres # db seule, pour uvicorn local contre elle
```

## Tests

Tests d'intégration (pas de mocks) : nécessitent l'API lancée contre un Postgres réel (voir `tests/README.md`).

```bash
pytest tests/ -v
pytest tests/test_actions_integration.py -v
pytest tests/ -k "interaction" -v
pytest tests/ --cov=. --cov-report=html
```

## Migrations Alembic

```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Versioning

```bash
scripts/version_manager.sh show|major|minor|patch|set <x.y.z>|tag create
```

## Architecture

`main.py` est une factory d'app minimale : crée l'app FastAPI, définit les métadonnées Swagger, appelle `init_db()` au démarrage, expose `/health`, et délègue l'enregistrement des routes à `routes.register_all_routes(app)`.

Les routes n'utilisent pas `APIRouter` : chaque module de `routes/` définit une fonction `register_<domain>_routes(app: FastAPI)` qui attache directement les décorateurs `@app.get/post/...` à l'instance `app` reçue. `routes/__init__.py` est le point d'agrégation qui appelle chaque `register_*`.

Modules de domaine :

| Module | Endpoints |
|---|---|
| `routes/contacts.py` | Contact CRUD + recherche (`/contacts`, `/contacts/search/{query}`) |
| `routes/relationship_profiles.py` | Un profil par contact (`/contacts/{id}/relationship-profile`) |
| `routes/interactions.py` | Journal d'interactions par contact (`/contacts/{id}/interactions`) |
| `routes/actions.py` | Tâches de suivi/rappels (`/contacts/{id}/relationship-actions`, `/relationship-actions`, `/relationship-actions/due`, complétion) |
| `routes/dashboard.py` | `/rap/dashboard`, métriques SQL agrégées |

`models.py` regroupe modèles ORM SQLAlchemy (`ContactDB`, `RelationshipProfileDB`, `InteractionDB`, `RelationshipActionDB`) et schémas Pydantic `*Create`/`*Update`/`*Response` correspondants. `ContactDB` cascade les suppressions vers profils/interactions/actions.

`database.py` gère le moteur/session SQLAlchemy (`DATABASE_URL` env var) ; `get_db()` est la dépendance FastAPI utilisée par toutes les routes.

Les handlers de routes interrogent `Session` directement (pas de couche repository/service) — la logique métier vit dans la fonction de route elle-même.
