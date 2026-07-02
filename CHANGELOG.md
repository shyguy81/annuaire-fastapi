# Changelog

Toutes les modifications notables de ce projet sont documentées dans ce fichier.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
versionnement selon [SemVer](https://semver.org/lang/fr/).

## [0.0.7] - 2026-07-02

### Fixed
- `scripts/version_manager.sh sync` ne mettait jamais à jour `version=` dans `main.py` malgré son message de succès ; ajoute la substitution réelle pour aligner `main.py` sur `VERSION`.

### Added
- Skill `.claude/skills/push-version` adaptée au projet (GitHub Actions + ghcr.io, au lieu de Gitea).
