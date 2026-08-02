# Security Policy

Pre-1.0, single active branch (`main`) — no maintained release versions yet.

## Reporting a vulnerability

Do not open a public GitHub issue. Report privately via [TODO: add a
security contact email or enable GitHub Security Advisories].

Include a description of the issue, its impact, and steps to reproduce
(a minimal curl example is usually enough for this API).

## Current state

This is a demo/learning-stage gateway. Do not deploy it with real data or
credentials behind it. Known, unfixed gaps:

- **JWT signing secret is hardcoded in source** (`gateway/main.py`,
  `gateway/middleware/auth.py`). Environment-based config is planned but
  not yet implemented.
- **Cache middleware runs before auth** — a cached response for a given
  URL can be served to a request with no valid token, since the cache
  key doesn't include the caller's identity. Not yet fixed.
- **No real user store** — `/login` now validates credentials (see
  `CHANGELOG.md`), but against a single hardcoded in-memory demo user,
  not a real user base.

Fixes are tracked incrementally rather than all at once — see
`CHANGELOG.md` for what's been addressed.
