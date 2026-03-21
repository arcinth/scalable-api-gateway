from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import httpx

from gateway.config import ROUTES
from services.circuit_breaker import (
    is_service_available,
    record_failure,
    record_success
)

router = APIRouter()

# Round Robin index
load_balancer_index = {}


@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway_handler(service: str, path: str, request: Request):

    # 🔹 Check if service exists
    if service not in ROUTES:
        return JSONResponse(status_code=404, content={"error": "Service not found"})

    service_list = ROUTES[service]

    # 🔹 Initialize index
    if service not in load_balancer_index:
        load_balancer_index[service] = 0

    # 🔹 Select service (Round Robin)
    index = load_balancer_index[service]
    target_base_url = service_list[index]

    # 🔹 Update index
    load_balancer_index[service] = (index + 1) % len(service_list)

    # 🔥 DEBUG: which service is being called
    print(f"➡️ Calling: {target_base_url}")

    # 🔥 Circuit Breaker Check
    if not is_service_available(target_base_url):
        return JSONResponse(
            status_code=503,
            content={"error": "Service temporarily unavailable"}
        )

    target_url = f"{target_base_url}/{path}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=request.headers.raw,
                content=await request.body(),
                timeout=2.0
            )

        # ✅ Success → reset failure count
        record_success(target_base_url)

        return JSONResponse(content=response.json())

    except Exception as e:
        print(f"❌ FAILED: {target_base_url}")

        # ❌ Record failure
        record_failure(target_base_url)

        return JSONResponse(
            status_code=500,
            content={"error": "Service failed"}
        )