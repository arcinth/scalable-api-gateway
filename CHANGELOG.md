# Changelog

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Security
- `POST /login` now validates credentials against an in-memory,
  bcrypt-hashed credential store (`gateway/auth_store.py`) instead of
  issuing a token unconditionally. Invalid credentials return `401`; a
  malformed request body returns `422`.
- Fixed: cache middleware previously executed *before* authentication,
  so a cached response could be served to a request with no valid
  token, and the cache key didn't include the caller's identity, so two
  different authenticated users could receive each other's cached
  response. `gateway/main.py` middleware registration now results in
  `jwt_auth` running before `cache_middleware`, and the cache key
  (`gateway/middleware/cache.py`) is scoped to the authenticated
  caller's identity. See `SECURITY.md` for details.
- JWT secret/algorithm/expiry were hardcoded in source with no way to
  override them; they're now read from the environment (see
  "Configuration" below). The default values are still insecure
  placeholders and must be overridden outside local development — see
  `SECURITY.md`.
- Added `tests/test_auth.py` (credential store, `/login`, `jwt_auth`
  middleware) and `tests/test_middleware_pipeline.py` (regression tests
  proving the cache/auth ordering fix).

### Added
- `gateway/config.py` — centralized, environment-driven settings
  (`Settings`/`settings`); every previously-hardcoded value (JWT config,
  Redis host/port/db, cache TTL, rate limits, circuit breaker
  thresholds, demo credentials, backend service URLs) now has a single
  source of truth. See README "Configuration" and `.env.example`.
- `gateway/monitoring/` — request/cache/circuit-breaker counters,
  exposed via `GET /admin/stats`. `GET /dashboard` — an HTML dashboard
  (`gateway/templates/dashboard.html`) polling `/admin/stats` every 5s.
  `POST /admin/reset-stats` — resets counters. All three are
  intentionally unauthenticated development/observability endpoints;
  see README "Monitoring & Dashboard" and `SECURITY.md`.
- `gateway/auth_store.py` — in-memory demo credential store (no
  database; see README "Local login").
- `bcrypt` and `redis` runtime dependencies (`requirements.txt`) — the
  latter was previously imported by `gateway/utils/redis_client.py` but
  missing from the manifest.
- `.gitignore` (Python bytecode, `venv/`, `.env`).
- `docs/`, `tests/`, `docker/`, `assets/` folders.
- `.editorconfig`.
- `.env.example` — documents every configurable value and its default.
- Black, Ruff, isort, pre-commit, configured in `pyproject.toml` and
  `.pre-commit-config.yaml`; `requirements-dev.txt`.
- GitHub Actions CI (`.github/workflows/ci.yml`): Ruff, Black check,
  isort check, pytest.
- `Dockerfile`, `docker-compose.yml`, `.dockerignore`.
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `LICENSE` (MIT).
- `tests/test_placeholder.py`, `tests/test_config.py`,
  `tests/test_monitoring_v2.py`.

### Removed
- 18 committed `__pycache__/*.pyc` files (now git-ignored).

### Known limitations (not changed)
- No real user store — `/login` validates against a single hardcoded
  demo user, not a database.
- `SECRET_KEY`/`DEMO_ADMIN_PASSWORD` default to well-known placeholder
  values; nothing enforces overriding them for a real deployment.
- `/admin/stats`, `/dashboard`, and `/admin/reset-stats` are public by
  design in this project and would need auth/network controls before a
  production deployment.

See `SECURITY.md` for the full, current security posture.

## [0.0.0] — Initial

FastAPI gateway with JWT auth, Redis caching, rate limiting, and a
circuit breaker routing to mock `user` and `order` services.
