# Security Policy

Pre-1.0, single active branch (`main`) — no maintained release versions yet.

## Reporting a vulnerability

Do not open a public GitHub issue. Report privately via [TODO: add a
security contact email or enable GitHub Security Advisories].

Include a description of the issue, its impact, and steps to reproduce
(a minimal curl example is usually enough for this API).

## Current state

This is a demo/learning-stage gateway with known, unfixed security gaps —
most notably a hardcoded JWT secret, a `/login` endpoint that issues
tokens without checking any credentials, and a middleware ordering bug
that lets cached responses bypass auth. None of these have been patched
yet; do not deploy this gateway with real data or credentials behind it.
Fixes are tracked separately from repository/tooling changes — see
`CHANGELOG.md`.
