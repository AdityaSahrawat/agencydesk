import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # Register new user & agency
    reg_payload = {
        "email": "newuser@test.com",
        "password": "Password123!",
        "full_name": "Test User",
        "agency_name": "Test Agency"
    }
    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # Login
    login_payload = {
        "email": "newuser@test.com",
        "password": "Password123!"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()

@pytest.mark.asyncio
async def test_invalid_login(client: AsyncClient):
    login_payload = {
        "email": "nonexistent@test.com",
        "password": "WrongPassword"
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 401
