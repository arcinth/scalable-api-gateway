import time

from gateway.config import settings

failure_count = {}
last_failure_time = {}


def is_service_available(service_url):
    if service_url not in failure_count:
        return True

    if failure_count[service_url] < settings.circuit_breaker_failure_threshold:
        return True

    elapsed = time.time() - last_failure_time[service_url]

    if elapsed > settings.circuit_breaker_recovery_seconds:
        print("HALF-OPEN: Retrying service...")
        failure_count[service_url] = 0
        return True

    print(" CIRCUIT OPEN: Blocking service")
    return False


def record_failure(service_url):
    failure_count[service_url] = failure_count.get(service_url, 0) + 1
    last_failure_time[service_url] = time.time()


def record_success(service_url):
    failure_count[service_url] = 0
