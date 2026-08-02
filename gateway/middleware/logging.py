import logging
import time

from fastapi import Request

from gateway.monitoring import metrics

logger = logging.getLogger(__name__)

# Paths excluded from request metrics and logging.
_EXCLUDED_PATHS = frozenset({"/admin/stats", "/dashboard", "/admin/reset-stats"})


async def log_requests(request: Request, call_next):
    if request.url.path in _EXCLUDED_PATHS:
        return await call_next(request)

    metrics.increment_total_requests()
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception:
        metrics.increment_failed_requests()
        raise

    elapsed = time.time() - start_time
    logger.info("%s %s %.4fs", request.method, request.url, elapsed)

    if response.status_code < 400:
        metrics.increment_successful_requests()
    else:
        metrics.increment_failed_requests()
        if response.status_code in (401, 429, 503):
            metrics.increment_blocked_requests()

    return response
