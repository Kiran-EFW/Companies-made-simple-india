"""Tests for authentication endpoints."""


def test_signup_success(client):
    """Signing up with valid data returns a token."""
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "email": "new@example.com",
            "password": "Secure1pass",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_signup_duplicate_email(client):
    """Signing up with an already-registered email returns 400."""
    payload = {
        "email": "dup@example.com",
        "password": "Password1x",
        "full_name": "First User",
    }
    client.post("/api/v1/auth/signup", json=payload)
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 400


def test_login_success(client):
    """Logging in with correct credentials returns a token."""
    # First, create a user
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "login@example.com",
            "password": "Login1pass",
            "full_name": "Login User",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Login1pass"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client):
    """Logging in with wrong password returns 401."""
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "wrong@example.com",
            "password": "Correct1pass",
            "full_name": "Wrong Pass User",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "Wrong1pass"},
    )
    assert response.status_code == 401


def test_get_profile(client, test_user, auth_headers):
    """GET /auth/me returns the current user profile."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
