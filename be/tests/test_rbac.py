import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_client_user_cannot_create_task(client: AsyncClient, seed_test_data: dict):
    client_token = seed_test_data["client_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)
    proj_a_id = str(seed_test_data["proj_a"].id)

    headers = {
        "Authorization": f"Bearer {client_token}",
        "X-Agency-ID": agency_a_id
    }

    payload = {
        "project_id": proj_a_id,
        "title": "Client Unauthorized Task Creation",
        "description": "Should fail with 403"
    }

    response = await client.post("/api/v1/tasks/", json=payload, headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_client_user_cannot_update_task_status(client: AsyncClient, seed_test_data: dict):
    client_token = seed_test_data["client_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)
    task_public_id = str(seed_test_data["task_public"].id)

    headers = {
        "Authorization": f"Bearer {client_token}",
        "X-Agency-ID": agency_a_id
    }

    payload = {"status": "done"}
    response = await client.patch(f"/api/v1/tasks/{task_public_id}/status", json=payload, headers=headers)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_admin_can_create_task(client: AsyncClient, seed_test_data: dict):
    admin_token = seed_test_data["admin_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)
    proj_a_id = str(seed_test_data["proj_a"].id)

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Agency-ID": agency_a_id
    }

    payload = {
        "project_id": proj_a_id,
        "title": "Admin Created Task",
        "is_internal": False
    }

    response = await client.post("/api/v1/tasks/", json=payload, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Admin Created Task"
