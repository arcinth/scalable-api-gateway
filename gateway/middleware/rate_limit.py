from fastapi import Request
from fastapi.responses import JSONResponse
import time

request_log = {}

LIMIT = 5
WINDOW = 10

async def rate_limiter(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    if client_ip not in request_log:
        request_log[client_ip] = []

    request_log[client_ip] = [
        t for t in request_log[client_ip]
        if current_time - t < WINDOW
    ]

    if len(request_log[client_ip]) >= LIMIT:
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )

    request_log[client_ip].append(current_time)

    return await call_next(request)