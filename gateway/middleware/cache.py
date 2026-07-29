import json

from fastapi import Request
from fastapi.responses import JSONResponse

from gateway.config import settings
from gateway.utils.redis_client import redis_client


async def cache_middleware(request: Request, call_next):

    if request.url.path in ["/", "/docs", "/openapi.json", "/login"]:
        return await call_next(request)

    # Scoped by caller identity (set by jwt_auth, which runs before this
    # middleware) so two different authenticated users never share a
    # cache entry. "anonymous" only occurs for exempted paths above,
    # which never reach here.
    identity = getattr(request.state, "user", None)
    subject = identity.get("user", "anonymous") if identity else "anonymous"
    key = f"{subject}:{request.method}:{request.url}"

    cached_data = redis_client.get(key)

    if cached_data:

        return JSONResponse(content=json.loads(cached_data))

    print(" REDIS CACHE MISS")

    # Call actual service
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
                return response  # fallback safely

    return response
