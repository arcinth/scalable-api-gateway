import os
import time

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from jose import jwt
from pydantic import BaseModel

from gateway.auth_store import verify_credentials
from gateway.config import settings
from gateway.middleware.auth import jwt_auth
from gateway.middleware.cache import cache_middleware
from gateway.middleware.logging import log_requests
from gateway.middleware.rate_limit import rate_limiter
from gateway.monitoring import metrics
from gateway.router import router

# Exposed as module attributes because tests import them by name; both
# delegate to the single source of truth in gateway.config.settings.
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm

app = FastAPI()

# Starlette executes middleware in the reverse of registration order.
# Registered bottom-up so execution is top-down:
#   log_requests → rate_limiter → jwt_auth → cache_middleware → router
app.middleware("http")(cache_middleware)
app.middleware("http")(jwt_auth)
app.middleware("http")(rate_limiter)
app.middleware("http")(log_requests)


@app.get("/admin/stats")
def get_stats():
    return metrics.get_stats()


@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard():
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "dashboard.html"
    )
    with open(template_path, encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.post("/admin/reset-stats")
def reset_stats():
    metrics.reset_counters()
    return {"status": "stats reset successful"}


app.include_router(router)


@app.get("/")
def health_check():
    return {"status": "API Gateway Running"}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/login")
def login(credentials: LoginRequest):
    if not verify_credentials(credentials.username, credentials.password):
        return JSONResponse(
            status_code=401, content={"error": "Invalid username or password"}
        )

    payload = {
        "user": credentials.username,
        "exp": time.time() + settings.jwt_expiry_seconds,
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}
