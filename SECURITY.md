# Security Policy

Pre-1.0, single active branch (`main`) — no maintained release versions yet.

## Reporting a vulnerability

Do not open a public GitHub issue. Report privately via [TODO: add a
security contact email or enable GitHub Security Advisories].

Include a description of the issue, its impact, and steps to reproduce
(a minimal curl example is usually enough for this API).

## Current state

This is a demo/learning-stage gateway. Do not deploy it with real data or
credentials behind it.

### Fixed

- **`/login` previously issued a token with no credential check at all.**
  It now validates the request against `gateway/auth_store.py`'s
  bcrypt-hashed credential store, returning `401` on invalid credentials
  and `422` on a malformed request.
- **JWT secret/algorithm/expiry were hardcoded directly in source, with
  no way to override them.** This was a code-only configuration
  problem: the values are now read from the environment via
  `gateway/config.py` (`SECRET_KEY`, `JWT_ALGORITHM`,
  `JWT_EXPIRY_SECONDS`), with defaults that reproduce the original
  behavior. See "Remaining limitations" below — the *default* value is
  still insecure and must be overridden.
- **Cache middleware used to execute before authentication.** Middleware
  registration in `gateway/main.py` now results in `jwt_auth` running
  before `cache_middleware` (see README "Architecture"), so an
  unauthenticated or invalidly-authenticated request can no longer reach
  the cache at all.
- **Cache responses could be served to callers other than the one who
  triggered them.** As a direct consequence of the above, this is also
  fixed — but was additionally hardened by scoping the cache key to the
  authenticated caller's identity (`gateway/middleware/cache.py`), so
  two different authenticated users no longer share a cache entry for
  the same URL.

Regression tests for all four: `tests/test_auth.py`,
`tests/test_middleware_pipeline.py`.

### Remaining limitations (genuine, not yet addressed)

- **No real user store.** `/login` validates against a single hardcoded
  in-memory demo user (`gateway/auth_store.py`), not a real user base or
  database.
- **Insecure defaults ship in source.** `SECRET_KEY` and
  `DEMO_ADMIN_PASSWORD` are now configurable via environment variables,
  but their *default* values (`mysecretkey`, `ChangeMe123!`) are
  well-known placeholders. Nothing enforces overriding them — deploying
  with the defaults intact is exactly as insecure as the old hardcoded
  values were.
- **`/admin/stats`, `/dashboard`, and `/admin/reset-stats` are
  intentionally unauthenticated.** This is a deliberate choice for this
  development/demo project (see README "Monitoring & Dashboard"), not an
  oversight. It is **not appropriate for a production deployment**:
  anyone who can reach the gateway can read operational metrics or reset
  them via `POST /admin/reset-stats` with no credential. A production
  deployment must put these routes behind authentication and/or
  network-level access controls (internal-only network, reverse-proxy
  IP allowlist, etc.) before exposing the gateway publicly.

Fixes are tracked incrementally rather than all at once — see
`CHANGELOG.md` for what's been addressed.
