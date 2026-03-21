from fastapi import FastAPI
from gateway.router import router
from gateway.middleware.logging import log_requests
from gateway.middleware.rate_limit import rate_limiter
from gateway.middleware.auth import jwt_auth
from jose import jwt
import time
from gateway.middleware.cache import cache_middleware



SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

app = FastAPI()

# Middleware order
app.middleware("http")(rate_limiter)
app.middleware("http")(jwt_auth)
app.middleware("http")(cache_middleware)
app.middleware("http")(log_requests)

app.include_router(router)

# Health check
@app.get("/")
def health_check():
    return {"status": "API Gateway Running"}


# 🔐 Login endpoint (dummy)
@app.post("/login")
def login():
    payload = {
        "user": "admin",
        "exp": time.time() + 3600  # 1 hour expiry
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token}