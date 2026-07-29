import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from jose import jwt
from pydantic import BaseModel

from gateway.auth_store import verify_credentials
from gateway.config import settings
from gateway.middleware.auth import jwt_auth
from gateway.middleware.cache import cache_middleware
from gateway.middleware.logging import log_requests
from gateway.middleware.rate_limit import rate_limiter
from gateway.router import router

# Kept as module attributes (not inlined) because they're part of this
# module's public surface — e.g. tests import them by name. Both read
# through to the single source of truth in gateway.config.settings.
SECRET_KEY = settings.secret_key
ALGORITHM = settings.jwt_algorithm

app = FastAPI()


# Starlette executes decorator-registered middleware in the REVERSE of
# registration order (each app.middleware() call is inserted at the
# front of the internal stack). Registered here bottom-up so it executes
# top-down: log_requests -> rate_limiter -> jwt_auth -> cache_middleware
# -> router. Auth and rate limiting must run before the cache so neither
# can be bypassed by a cache hit, and jwt_auth must run before the cache
# so request.state.user exists when cache_middleware keys its lookup.
app.middleware("http")(cache_middleware)
app.middleware("http")(jwt_auth)
app.middleware("http")(rate_limiter)
app.middleware("http")(log_requests)

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
