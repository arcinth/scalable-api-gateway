import time

failure_count = {}
last_failure_time = {}

FAILURE_THRESHOLD = 3
RECOVERY_TIME = 10  


def is_service_available(service_url):
    if service_url not in failure_count:
        return True

    if failure_count[service_url] < FAILURE_THRESHOLD:
        return True

    elapsed = time.time() - last_failure_time[service_url]

    if elapsed > RECOVERY_TIME:
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