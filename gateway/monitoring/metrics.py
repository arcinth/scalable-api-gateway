import time
from collections import defaultdict
from threading import Lock

from gateway.config import settings
from services.circuit_breaker import get_circuit_breaker_state


def _format_uptime(seconds: float) -> str:
    secs = int(seconds)
    days = secs // 86400
    hours = (secs % 86400) // 3600
    minutes = (secs % 3600) // 60
    remaining = secs % 60

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0 or days > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or hours > 0 or days > 0:
        parts.append(f"{minutes}m")
    parts.append(f"{remaining}s")

    return " ".join(parts)


def _service_breaker_state(service_name: str) -> str:
    """Return the worst circuit breaker state across all URLs for a service."""
    urls = settings.routes.get(service_name, [])
    if not urls:
        return "CLOSED"
    states = [get_circuit_breaker_state(url) for url in urls]
    if "OPEN" in states:
        return "OPEN"
    if "HALF-OPEN" in states:
        return "HALF-OPEN"
    return "CLOSED"


class GatewayMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.blocked_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.per_service_request_counts: defaultdict[str, int] = defaultdict(int)

    def increment_total_requests(self) -> None:
        with self._lock:
            self.total_requests += 1

    def increment_successful_requests(self) -> None:
        with self._lock:
            self.successful_requests += 1

    def increment_failed_requests(self) -> None:
        with self._lock:
            self.failed_requests += 1

    def increment_blocked_requests(self) -> None:
        with self._lock:
            self.blocked_requests += 1

    def increment_cache_hits(self) -> None:
        with self._lock:
            self.cache_hits += 1

    def increment_cache_misses(self) -> None:
        with self._lock:
            self.cache_misses += 1

    def increment_service_request(self, service_name: str) -> None:
        with self._lock:
            self.per_service_request_counts[service_name] += 1

    def reset_counters(self) -> None:
        with self._lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.blocked_requests = 0
            self.cache_hits = 0
            self.cache_misses = 0
            self.per_service_request_counts.clear()

    def get_stats(self) -> dict:
        with self._lock:
            uptime_str = _format_uptime(time.time() - self.start_time)

            total_cache = self.cache_hits + self.cache_misses
            hit_ratio = self.cache_hits / total_cache if total_cache > 0 else 0.0

            services_data: dict[str, int] = {
                f"{k}-service": v for k, v in self.per_service_request_counts.items()
            }
            services_data.setdefault("user-service", 0)
            services_data.setdefault("order-service", 0)

            return {
                "gateway": {
                    "status": "healthy",
                    "version": "2.0.0",
                    "uptime": uptime_str,
                },
                "requests": {
                    "total": self.total_requests,
                    "successful": self.successful_requests,
                    "failed": self.failed_requests,
                    "blocked": self.blocked_requests,
                },
                "cache": {
                    "hits": self.cache_hits,
                    "misses": self.cache_misses,
                    "hitRate": hit_ratio,
                },
                "services": services_data,
                "circuitBreaker": {
                    "user-service": _service_breaker_state("user"),
                    "order-service": _service_breaker_state("order"),
                },
            }
