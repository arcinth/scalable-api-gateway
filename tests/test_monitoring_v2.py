import time

import pytest
from fastapi.testclient import TestClient

from gateway.config import settings
from gateway.main import app
from gateway.monitoring import metrics
from services.circuit_breaker import failure_count, last_failure_time

client = TestClient(app)


@pytest.fixture(autouse=True)
def _reset_state():
    metrics.reset_counters()
    failure_count.clear()
    last_failure_time.clear()
    yield
    metrics.reset_counters()
    failure_count.clear()
    last_failure_time.clear()


def test_stats_initially_empty():
    response = client.get("/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["gateway"]["status"] == "healthy"
    assert data["requests"]["total"] == 0
    assert data["requests"]["successful"] == 0
    assert data["requests"]["failed"] == 0
    assert data["requests"]["blocked"] == 0
    assert data["cache"]["hits"] == 0
    assert data["cache"]["misses"] == 0
    assert data["cache"]["hitRate"] == 0.0
    assert data["services"]["user-service"] == 0
    assert data["services"]["order-service"] == 0
    assert data["circuitBreaker"]["user-service"] == "CLOSED"
    assert data["circuitBreaker"]["order-service"] == "CLOSED"


def test_stats_not_polluted_by_admin_or_dashboard():
    client.get("/admin/stats")
    client.get("/dashboard")
    client.post("/admin/reset-stats")

    assert metrics.total_requests == 0
    assert metrics.successful_requests == 0


def test_successful_request_increments_stats():
    response = client.get("/")
    assert response.status_code == 200

    data = client.get("/admin/stats").json()
    assert data["requests"]["total"] == 1
    assert data["requests"]["successful"] == 1
    assert data["requests"]["failed"] == 0
    assert data["requests"]["blocked"] == 0


def test_failed_request_increments_stats():
    # An invalid payload to /login returns 422 Unprocessable Entity.
    response = client.post("/login", json={})
    assert response.status_code == 422

    data = client.get("/admin/stats").json()
    assert data["requests"]["total"] == 1
    assert data["requests"]["successful"] == 0
    assert data["requests"]["failed"] == 1
    assert data["requests"]["blocked"] == 0


def test_blocked_requests_auth_error():
    response = client.get("/user/profile")
    assert response.status_code == 401

    data = client.get("/admin/stats").json()
    assert data["requests"]["total"] == 1
    assert data["requests"]["failed"] == 1
    assert data["requests"]["blocked"] == 1


def test_blocked_requests_rate_limiter():
    for _ in range(6):
        client.get("/invalid-route")

    data = client.get("/admin/stats").json()
    assert data["requests"]["blocked"] >= 1


def test_cache_metrics():
    metrics.increment_cache_hits()
    metrics.increment_cache_misses()
    metrics.increment_cache_hits()

    data = client.get("/admin/stats").json()
    assert data["cache"]["hits"] == 2
    assert data["cache"]["misses"] == 1
    assert data["cache"]["hitRate"] == 2.0 / 3.0


def test_service_counters_and_circuit_breakers():
    metrics.increment_service_request("user")
    metrics.increment_service_request("order")
    metrics.increment_service_request("user")

    order_url = settings.order_service_urls[0]
    failure_count[order_url] = 3
    last_failure_time[order_url] = time.time()

    data = client.get("/admin/stats").json()
    assert data["services"]["user-service"] == 2
    assert data["services"]["order-service"] == 1
    assert data["circuitBreaker"]["user-service"] == "CLOSED"
    assert data["circuitBreaker"]["order-service"] == "OPEN"


def test_reset_endpoint():
    metrics.increment_total_requests()
    metrics.increment_successful_requests()
    metrics.increment_service_request("user")

    response = client.post("/admin/reset-stats")
    assert response.status_code == 200
    assert response.json() == {"status": "stats reset successful"}

    data = client.get("/admin/stats").json()
    assert data["requests"]["total"] == 0
    assert data["requests"]["successful"] == 0
    assert data["services"]["user-service"] == 0


def test_dashboard_endpoint_returns_html():
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "API Gateway Dashboard" in response.text
