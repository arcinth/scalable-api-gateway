"""Tests for gateway/config.py.

Each Settings() constructed here is a fresh instance, not the shared
gateway.config.settings singleton — the singleton is built once at
import time (before any test's monkeypatch takes effect), so overrides
must be verified against a new instance instead.
"""

from gateway.config import Settings


def test_defaults_reproduce_original_hardcoded_values():
    """Every default must match the value that used to be hardcoded,
    so introducing this module doesn't change behavior for anyone who
    sets no environment variables."""
    s = Settings()

    assert s.secret_key == "mysecretkey"
    assert s.jwt_algorithm == "HS256"
    assert s.jwt_expiry_seconds == 3600

    assert s.demo_admin_username == "admin"
    assert s.demo_admin_password == "ChangeMe123!"

    assert s.redis_host == "localhost"
    assert s.redis_port == 6379
    assert s.redis_db == 0

    assert s.cache_ttl_seconds == 10

    assert s.rate_limit_max_requests == 5
    assert s.rate_limit_window_seconds == 10

    assert s.circuit_breaker_failure_threshold == 3
    assert s.circuit_breaker_recovery_seconds == 10

    assert s.user_service_urls == [
        "http://localhost:8001",
        "http://localhost:8003",
    ]
    assert s.order_service_urls == ["http://localhost:8002"]
    assert s.routes == {
        "user": ["http://localhost:8001", "http://localhost:8003"],
        "order": ["http://localhost:8002"],
    }


def test_string_setting_reads_env_override(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "a-different-secret")
    s = Settings()

    assert s.secret_key == "a-different-secret"


def test_integer_setting_reads_env_override(monkeypatch):
    monkeypatch.setenv("CACHE_TTL_SECONDS", "42")
    s = Settings()

    assert s.cache_ttl_seconds == 42
    assert isinstance(s.cache_ttl_seconds, int)


def test_service_urls_are_split_and_trimmed(monkeypatch):
    monkeypatch.setenv("USER_SERVICE_URLS", " http://svc-a:9001 , http://svc-b:9002 ")
    s = Settings()

    assert s.user_service_urls == ["http://svc-a:9001", "http://svc-b:9002"]
    assert s.routes["user"] == ["http://svc-a:9001", "http://svc-b:9002"]


def test_unset_variables_fall_back_to_defaults(monkeypatch):
    monkeypatch.delenv("REDIS_HOST", raising=False)
    s = Settings()

    assert s.redis_host == "localhost"
