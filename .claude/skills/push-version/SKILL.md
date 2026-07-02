---
name: push-version
description: Automate version bump, git tagging, and trigger GitHub Actions workflow for Annuaire Contacts FastAPI backend
type: skill
---

# Version Bump & Release Skill

Automatise la montée de version, création de tags git, et trigger du workflow GitHub Actions.

## Usage

```bash
scripts/version_manager.sh show           # Version actuelle
scripts/version_manager.sh patch           # Bump patch (bugfix)
scripts/version_manager.sh minor           # Bump minor (feature)
scripts/version_manager.sh major           # Bump major (breaking)
scripts/version_manager.sh set 1.2.3       # Version spécifique
scripts/version_manager.sh tag create      # Crée + push le tag git
```

## Workflow

### Pré-requis

- Aucun changement non-committé (`git status` doit être clean)
- Tous les commits doivent être pushés (aucun commit en attente de push)
- Workflow GitHub Actions actif: `.github/workflows/*.yml` (déclenché sur tags `v*`)

### Étapes

1. **Vérification** : `git status` clean + pas de commits en attente de push
2. **Bump version** : `scripts/version_manager.sh <major|minor|patch>` — met à jour `VERSION`
3. **Sync `main.py`** : mettre à jour manuellement `version="X.Y.Z"` dans l'init `FastAPI` (main.py:39) — le script ne le fait pas automatiquement
4. **Git commit** : `git commit -m "chore: bump version to X.Y.Z"`
5. **Git push** : `git push origin master`
6. **Tag + push** : `scripts/version_manager.sh tag create` (crée `vX.Y.Z` et push sur origin)
7. **Trigger workflow** : GitHub Actions déclenché automatiquement sur le push du tag

### Workflow GitHub Actions (automatique après tag push)

`.github/workflows/*.yml` s'exécute sur les tags `v*`:

1. Checkout code
2. Lint/typecheck (pylint, mypy — non bloquants)
3. Build Docker image
4. Push vers `ghcr.io/${{ github.repository }}/backend-api` avec tags semver

Monitor: `gh run list` / `gh run watch` ou https://github.com/shyguy81/annuaire-fastapi/actions

## Fichiers modifiés

- `VERSION` : source de vérité de la version courante
- `main.py` : `version="X.Y.Z"` dans l'init FastAPI (ligne ~39) — à mettre à jour à la main

## Rollback

Si erreur avant push:

```bash
git reset --soft HEAD~1
git checkout VERSION main.py
```

Si tag déjà créé mais pas encore pushé:

```bash
git tag -d vX.Y.Z
```

Si déjà pushé:

```bash
git revert HEAD
git push origin :refs/tags/vX.Y.Z
```

## Vérification

```bash
git log --oneline -5
git tag -l | tail -5
gh run list --limit 5
```

## Troubleshooting

### Uncommitted changes

```bash
git status
git add <fichiers>
git commit -m "..."
```

### Unpushed commits

```bash
git log --oneline -5
git push origin master
```

### Workflow GitHub Actions fail

```bash
gh run list --limit 5
gh run view <run-id> --log-failed
```

Causes fréquentes:
- `GITHUB_TOKEN` insuffisant pour push ghcr.io (permissions `packages: write` requis, déjà configuré)
- Erreur build Docker
- Échec pylint/mypy (non bloquant normalement)

## Related

- `scripts/version_manager.sh` : script de version (show/major/minor/patch/set/sync/tag create)
- `.github/workflows/*.yml` : CI/CD GitHub Actions
- `VERSION` : fichier source de vérité
