import json

from fastapi import Request
from fastapi.responses import JSONResponse

from gateway.config import settings
from gateway.monitoring import metrics
from gateway.utils.redis_client import redis_client

# Paths that bypass the cache entirely.
_EXCLUDED_PATHS = frozenset(
    {
        "/",
        "/docs",
        "/openapi.json",
        "/login",
        "/admin/stats",
        "/dashboard",
        "/admin/reset-stats",
    }
)


async def cache_middleware(request: Request, call_next):
    if request.url.path in _EXCLUDED_PATHS:
        return await call_next(request)

    # Cache key is scoped to the authenticated identity (set by jwt_auth,
    # which runs before this middleware) so different users never share entries.
    identity = getattr(request.state, "user", None)
    subject = identity.get("user", "anonymous") if identity else "anonymous"
    key = f"{subject}:{request.method}:{request.url}"

    cached_data = redis_client.get(key)

    if cached_data:
        metrics.increment_cache_hits()
        return JSONResponse(content=json.loads(cached_data))

    metrics.increment_cache_misses()

    response = await call_next(request)

    if request.method == "GET" and response.status_code == 200:
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            try:
                data = json.loads(body.decode())
                redis_client.setex(key, settings.cache_ttl_seconds, json.dumps(data))
                return JSONResponse(content=data)
            except Exception:
                return response  # fallback if body cannot be parsed

    return response
