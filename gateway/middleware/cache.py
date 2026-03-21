from fastapi import Request
from fastapi.responses import JSONResponse
from gateway.utils.redis_client import redis_client
import json

CACHE_TTL = 10  # seconds


async def cache_middleware(request: Request, call_next):

    if request.url.path in ["/", "/docs", "/openapi.json", "/login"]:
        return await call_next(request)

    key = f"{request.method}:{request.url}"


    cached_data = redis_client.get(key)

    if cached_data:

        return JSONResponse(content=json.loads(cached_data))

    print(" REDIS CACHE MISS")

    # Call actual service
    response = await call_next(request)

    if request.method == "GET":
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            body = b""
            async for chunk in response.body_iterator:
                body += chunk

            try:
                data = json.loads(body.decode())

                redis_client.setex(
                    key,
                    CACHE_TTL,
                    json.dumps(data)
                )

                return JSONResponse(content=data)

            except Exception:
                return response  # fallback safely

    return response