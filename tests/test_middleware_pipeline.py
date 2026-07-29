"""Regression tests for the middleware pipeline's security properties.

These exercise the real, fully-assembled `app` (real registered
middleware, real ordering) rather than testing jwt_auth or
cache_middleware in isolation — the vulnerability this file guards
against is specifically about how they interact when composed, which
isolated unit tests (see tests/test_auth.py) cannot see.

Redis and the upstream HTTP call are faked so these tests are hermetic
(no live Redis/backend services required) and deterministic — genuinely
different from mocking-to-hide-a-missing-dependency, since redis is
already a real, installed dependency elsewhere in this suite.
"""

import time

import pytest
from fastapi.testclient import TestClient
from jose import jwt

import gateway.middleware.cache as cache_module
import gateway.router as router_module
from gateway.config import settings
from gateway.main import app

client = TestClient(app)


class _FakeRedis:
    """In-memory stand-in for redis_client.get/.setex."""

    def __init__(self):
        self._store = {}

    def get(self, key):
        return self._store.get(key)

    def setex(self, key, _ttl, value):
        self._store[key] = value


class _FakeUpstreamResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class _FakeAsyncClient:
    """Stands in for httpx.AsyncClient so no real backend service is hit.

    Tracks how many times the upstream was actually called, which is
    what lets these tests prove whether a second request was served
    from cache or genuinely re-executed.
    """

    call_count = 0

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def request(self, method, url, headers=None, content=None, timeout=None):
        _FakeAsyncClient.call_count += 1
        return _FakeUpstreamResponse({"call": _FakeAsyncClient.call_count})


@pytest.fixture
def fake_infra(monkeypatch):
    fake_redis = _FakeRedis()
    monkeypatch.setattr(cache_module, "redis_client", fake_redis)

    _FakeAsyncClient.call_count = 0
    monkeypatch.setattr(router_module.httpx, "AsyncClient", _FakeAsyncClient)

    return fake_redis


def _login(username="admin", password="ChangeMe123!"):
    response = client.post("/login", json={"username": username, "password": password})
    return response.json()["access_token"]


def _forged_token(username):
    """A validly-signed token for a user who never called /login — simulates
    a second, different authenticated caller without needing a second seeded
    account in the (single-user) demo credential store."""
    payload = {"user": username, "exp": time.time() + 3600}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def test_protected_route_requires_auth_when_nothing_is_cached(fake_infra):
    response = client.get("/user/profile")

    assert response.status_code == 401


def test_cache_hit_does_not_bypass_authentication(fake_infra):
    token = _login()
    primed = client.get("/user/profile", headers={"Authorization": f"Bearer {token}"})
    assert primed.status_code == 200

    unauthenticated = client.get("/user/profile")

    assert unauthenticated.status_code == 401


def test_cached_response_is_not_shared_across_different_users(fake_infra):
    token_a = _login()
    token_b = _forged_token("someone-else")

    response_a = client.get(
        "/user/profile", headers={"Authorization": f"Bearer {token_a}"}
    )
    response_b = client.get(
        "/user/profile", headers={"Authorization": f"Bearer {token_b}"}
    )

    assert response_a.status_code == 200
    assert response_b.status_code == 200
    # Each identity must reach the real upstream at least once — if this is
    # 1, user B silently received user A's cached response.
    assert _FakeAsyncClient.call_count == 2


def test_cache_hit_does_not_bypass_rate_limiting(fake_infra):
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    responses = [client.get("/user/profile", headers=headers) for _ in range(10)]
    statuses = {r.status_code for r in responses}

    assert 429 in statuses


def test_caching_still_works_for_repeat_requests_from_the_same_user(fake_infra):
    token = _login()
    headers = {"Authorization": f"Bearer {token}"}

    first = client.get("/user/profile", headers=headers)
    second = client.get("/user/profile", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    # The second identical request from the same user should be served
    # from cache, not re-hit the upstream.
    assert _FakeAsyncClient.call_count == 1
