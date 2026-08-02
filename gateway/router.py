import logging

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from gateway.config import settings
from gateway.monitoring import metrics
from services.circuit_breaker import (
    is_service_available,
    record_failure,
    record_success,
)

logger = logging.getLogger(__name__)

router = APIRouter()

load_balancer_index: dict[str, int] = {}


@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_handler(service: str, path: str, request: Request):
    metrics.increment_service_request(service)

    if service not in settings.routes:
        return JSONResponse(status_code=404, content={"error": "Service not found"})

    service_list = settings.routes[service]

    if service not in load_balancer_index:
        load_balancer_index[service] = 0

    index = load_balancer_index[service]
    target_base_url = service_list[index]
    load_balancer_index[service] = (index + 1) % len(service_list)

    if not is_service_available(target_base_url):
        return JSONResponse(
            status_code=503, content={"error": "Service temporarily unavailable"}
        )

    target_url = f"{target_base_url}/{path}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body(),
                timeout=2.0,
            )

        record_success(target_base_url)
        return JSONResponse(content=response.json())

    except Exception:
        logger.error("Upstream request failed: %s", target_base_url)
        record_failure(target_base_url)
        return JSONResponse(status_code=500, content={"error": "Service failed"})
