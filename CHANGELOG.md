# Changelog

Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Security
- `POST /login` now validates credentials against an in-memory,
  bcrypt-hashed credential store (`gateway/auth_store.py`) instead of
  issuing a token unconditionally. Invalid credentials return `401`; a
  malformed request body returns `422`. JWT issuance/validation logic is
  unchanged (same secret, algorithm, expiry, and downstream middleware).
- Added `tests/test_auth.py` covering the credential store, `/login`,
  and `jwt_auth` middleware (9 tests).

### Added
- `gateway/auth_store.py` — in-memory demo credential store (no
  database; see README "Local login").
- `bcrypt` runtime dependency (`requirements.txt`).
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
Routing, middleware order, caching, and load balancing are unchanged.
Known unfixed issues: the JWT signing secret is still hardcoded in
source (env-based config is a separate, not-yet-started pass), and the
cache middleware still runs before `jwt_auth`, so a cached response can
still be served without a valid token. See `SECURITY.md`.

## [0.0.0] — Initial

FastAPI gateway with JWT auth, Redis caching, rate limiting, and a
circuit breaker routing to mock `user` and `order` services.
