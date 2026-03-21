from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt, JWTError

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

async def jwt_auth(request: Request, call_next):
    # Allow health + docs + login
    if request.url.path in ["/", "/docs", "/openapi.json", "/login"]:
        return await call_next(request)

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"error": "Missing token"}
        )

    try:
        scheme, token = auth_header.split()

        if scheme.lower() != "bearer":
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid auth scheme"}
            )

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        request.state.user = payload

    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid or expired token"}
        )

    return await call_next(request)