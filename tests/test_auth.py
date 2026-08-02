from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from gateway.auth_store import verify_credentials
from gateway.main import ALGORITHM, SECRET_KEY, app
from gateway.middleware.auth import jwt_auth

client = TestClient(app)

VALID_USERNAME = "admin"
VALID_PASSWORD = "ChangeMe123!"


def _isolated_auth_app():
    """A minimal app with only jwt_auth attached, to unit-test the
    middleware without going through caching/rate-limiting/the proxy
    (none of which are in scope for this change)."""
    mini_app = FastAPI()
    mini_app.middleware("http")(jwt_auth)

    @mini_app.get("/protected")
    def protected():
        return {"ok": True}

    return TestClient(mini_app)


def test_verify_credentials_accepts_correct_password():
    assert verify_credentials(VALID_USERNAME, VALID_PASSWORD) is True


def test_verify_credentials_rejects_wrong_password():
    assert verify_credentials(VALID_USERNAME, "wrong-password") is False


def test_verify_credentials_rejects_unknown_user():
    assert verify_credentials("nobody", VALID_PASSWORD) is False


def test_login_with_valid_credentials_returns_jwt():
    response = client.post(
        "/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD}
    )

    assert response.status_code == 200

    token = response.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["user"] == VALID_USERNAME
    assert "exp" in payload


def test_login_with_wrong_password_returns_401():
    response = client.post(
        "/login", json={"username": VALID_USERNAME, "password": "wrong-password"}
    )

    assert response.status_code == 401
    assert response.json() == {"error": "Invalid username or password"}


def test_login_with_unknown_username_returns_401():
    response = client.post(
        "/login", json={"username": "nobody", "password": VALID_PASSWORD}
    )

    assert response.status_code == 401
    assert response.json() == {"error": "Invalid username or password"}


def test_login_missing_password_returns_422():
    response = client.post("/login", json={"username": VALID_USERNAME})

    assert response.status_code == 422


def test_jwt_auth_rejects_request_with_no_token():
    auth_client = _isolated_auth_app()

    response = auth_client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {"error": "Missing token"}


def test_jwt_auth_accepts_token_issued_by_login():
    login_response = client.post(
        "/login", json={"username": VALID_USERNAME, "password": VALID_PASSWORD}
    )
    token = login_response.json()["access_token"]

    auth_client = _isolated_auth_app()
    response = auth_client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
