import logging
import time

from gateway.config import settings

logger = logging.getLogger(__name__)

failure_count: dict[str, int] = {}
last_failure_time: dict[str, float] = {}


def is_service_available(service_url: str) -> bool:
    if service_url not in failure_count:
        return True

    if failure_count[service_url] < settings.circuit_breaker_failure_threshold:
        return True

    elapsed = time.time() - last_failure_time[service_url]

    if elapsed > settings.circuit_breaker_recovery_seconds:
        logger.info("Circuit half-open, retrying %s", service_url)
        failure_count[service_url] = 0
        return True

    logger.warning("Circuit open, blocking %s", service_url)
    return False


def record_failure(service_url: str) -> None:
    failure_count[service_url] = failure_count.get(service_url, 0) + 1
    last_failure_time[service_url] = time.time()


def record_success(service_url: str) -> None:
    failure_count[service_url] = 0


def get_circuit_breaker_state(service_url: str) -> str:
    if service_url not in failure_count:
        return "CLOSED"

    if failure_count[service_url] < settings.circuit_breaker_failure_threshold:
        return "CLOSED"

    elapsed = time.time() - last_failure_time.get(service_url, 0)
    if elapsed > settings.circuit_breaker_recovery_seconds:
        return "HALF-OPEN"

    return "OPEN"
