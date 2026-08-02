"""Shared test fixtures.

The rate limiter (gateway/middleware/rate_limit.py) keeps its counters in
a module-level dict shared by every request in-process, including
requests made by TestClient. Clearing it between tests keeps the auth
tests independent of test ordering/count without touching the limiter's
actual behavior.
"""

import pytest

from gateway.middleware.rate_limit import request_log


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    request_log.clear()
    yield
    request_log.clear()
