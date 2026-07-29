import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from jose import jwt
from pydantic import BaseModel

from gateway.auth_store import verify_credentials
from gateway.middleware.auth import jwt_auth
from gateway.middleware.cache import cache_middleware
from gateway.middleware.logging import log_requests
from gateway.middleware.rate_limit import rate_limiter
from gateway.router import router

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

app = FastAPI()


app.middleware("http")(rate_limiter)
app.middleware("http")(jwt_auth)
app.middleware("http")(cache_middleware)
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

    payload = {"user": credentials.username, "exp": time.time() + 3600}

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}
