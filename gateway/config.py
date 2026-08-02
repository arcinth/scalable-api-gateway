"""Centralized application configuration.

Single source of truth for values that used to be hardcoded and
duplicated across gateway/main.py, gateway/middleware/*,
gateway/utils/redis_client.py, gateway/auth_store.py, and
services/circuit_breaker.py.

Every setting is read from an environment variable with a default that
reproduces today's previously-hardcoded behavior exactly — see
.env.example for the full list and README "Configuration". Settings are
read once, at process start (when this module is first imported); the
app does not hot-reload environment changes.
"""

import os


def _split_urls(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    def __init__(self) -> None:
        # --- Auth (gateway/main.py, gateway/middleware/auth.py) ---
        self.secret_key = os.environ.get("SECRET_KEY", "mysecretkey")
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        self.jwt_expiry_seconds = int(os.environ.get("JWT_EXPIRY_SECONDS", "3600"))

        # --- Demo credential store (gateway/auth_store.py) ---
        self.demo_admin_username = os.environ.get("DEMO_ADMIN_USERNAME", "admin")
        self.demo_admin_password = os.environ.get("DEMO_ADMIN_PASSWORD", "ChangeMe123!")

        # --- Redis (gateway/utils/redis_client.py) ---
        self.redis_host = os.environ.get("REDIS_HOST", "localhost")
        self.redis_port = int(os.environ.get("REDIS_PORT", "6379"))
        self.redis_db = int(os.environ.get("REDIS_DB", "0"))

        # --- Response cache (gateway/middleware/cache.py) ---
        self.cache_ttl_seconds = int(os.environ.get("CACHE_TTL_SECONDS", "10"))

        # --- Rate limiting (gateway/middleware/rate_limit.py) ---
        self.rate_limit_max_requests = int(
            os.environ.get("RATE_LIMIT_MAX_REQUESTS", "5")
        )
        self.rate_limit_window_seconds = int(
            os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "10")
        )

        # --- Circuit breaker (services/circuit_breaker.py) ---
        self.circuit_breaker_failure_threshold = int(
            os.environ.get("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "3")
        )
        self.circuit_breaker_recovery_seconds = int(
            os.environ.get("CIRCUIT_BREAKER_RECOVERY_SECONDS", "10")
        )

        # --- Backend service routing (gateway/router.py) ---
        self.user_service_urls = _split_urls(
            os.environ.get(
                "USER_SERVICE_URLS", "http://localhost:8001,http://localhost:8003"
            )
        )
        self.order_service_urls = _split_urls(
            os.environ.get("ORDER_SERVICE_URLS", "http://localhost:8002")
        )
        self.routes = {
            "user": self.user_service_urls,
            "order": self.order_service_urls,
        }


settings = Settings()
