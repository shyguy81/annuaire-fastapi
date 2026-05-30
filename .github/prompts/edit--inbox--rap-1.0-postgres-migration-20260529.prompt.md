---
name: rap-1.0-postgres-migration
description: Migrer base de données de MariaDB à PostgreSQL 15+
priority: P0
effort: 3j
ice_score: 31.67
agent: agent
---

# RAP-1.0: Database Migration (MariaDB → PostgreSQL)

## Contexte

Projet annuaire-contacts utilise actuellement MariaDB. Migration → PostgreSQL 15+ pour moderniser stack BD et meilleure compatibilité.

## Tâche

- [ ] Mettre à jour `requirements.txt` ou `pyproject.toml`: remplacer `mysqlclient` ou `mysql-connector` par `psycopg2` ou `psycopg2-binary`
- [ ] Modifier `database.py` (ou fichier config): changer dialecte SQLAlchemy de `mysql+pymysql://` ou `mysql+mysqlconnector://` à `postgresql+psycopg2://`
- [ ] Mettre à jour URL connexion BD (host, port 5432, user, password, dbname)
- [ ] Tester connexion PostgreSQL locale
- [ ] Vérifier Alembic migrations (si existant) compatible PostgreSQL
- [ ] Supprimer toutes références MariaDB du code (commentaires, docs inline)
- [ ] Mettre à jour `.env.example` ou config docs

## Validation

- [ ] `docker compose up` démarre sans erreur
- [ ] PostgreSQL container démarre et est healthy
- [ ] App se connecte à PostgreSQL sans error
- [ ] Connexion test valide la BD est accessible
- [ ] Zéro références "mariadb", "mysql", "mysql://" dans le code

## Livrable

- Connexion PostgreSQL fonctionnelle
- Driver psycopg2 configuré
- `.env` mis à jour pour PostgreSQL

## ✅ Fin du traitement

Après commit dans annuaire-fastapi:
```bash
mv .github/prompts/edit--inbox--rap-1.0-postgres-migration-20260529.prompt.md \
   .github/prompts/edit--done--rap-1.0-postgres-migration-20260529.prompt.md
```
