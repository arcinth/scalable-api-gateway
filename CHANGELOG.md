# Changelog

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `.gitignore` (Python bytecode, `venv/`, `.env`).
- `docs/`, `tests/`, `docker/`, `assets/` folders.
- `.editorconfig`.
- `.env.example` — documents every value currently hardcoded in the app;
  not yet read by the app itself.
- Black, Ruff, isort, pre-commit, configured in `pyproject.toml` and
  `.pre-commit-config.yaml`; `requirements-dev.txt`.
- GitHub Actions CI (`.github/workflows/ci.yml`): Ruff, Black check,
  isort check, pytest.
- `Dockerfile`, `docker-compose.yml`, `.dockerignore`.
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` (MIT).
- `tests/test_placeholder.py` — one passing test so CI has something to
  collect until real coverage exists.

### Removed
- 18 committed `__pycache__/*.pyc` files (now git-ignored).

### Not changed
No application code changed: authentication, routing, middleware order,
caching, and load balancing are all as before, including known issues
(hardcoded JWT secret, unauthenticated `/login`, cache middleware running
before auth). Those are tracked as follow-up work.

## [0.0.0] — Initial

FastAPI gateway with JWT auth, Redis caching, rate limiting, and a
circuit breaker routing to mock `user` and `order` services.
