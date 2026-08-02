import time

from fastapi import Request
from fastapi.responses import JSONResponse

from gateway.config import settings

request_log = {}


async def rate_limiter(request: Request, call_next):
    # Exempt health, login, docs, and monitoring routes from rate limiting
    if request.url.path in [
        "/",
        "/docs",
        "/openapi.json",
        "/login",
        "/admin/stats",
        "/dashboard",
        "/admin/reset-stats",
    ]:
        return await call_next(request)

    client_ip = request.client.host
    current_time = time.time()

    if client_ip not in request_log:
        request_log[client_ip] = []

    request_log[client_ip] = [
        t
        for t in request_log[client_ip]
        if current_time - t < settings.rate_limit_window_seconds
    ]

    if len(request_log[client_ip]) >= settings.rate_limit_max_requests:
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})

    request_log[client_ip].append(current_time)

    return await call_next(request)
