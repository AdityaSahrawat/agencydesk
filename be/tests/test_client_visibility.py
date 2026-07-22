import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_client_user_sees_no_internal_tasks(client: AsyncClient, seed_test_data: dict):
    client_token = seed_test_data["client_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)

    headers = {
        "Authorization": f"Bearer {client_token}",
        "X-Agency-ID": agency_a_id
    }

    response = await client.get("/api/v1/tasks/", headers=headers)
    assert response.status_code == 200
    tasks = response.json()

    # None of the tasks returned to client should be internal!
    for t in tasks:
        assert t["is_internal"] is False

@pytest.mark.asyncio
async def test_client_user_access_internal_task_detail_fails(client: AsyncClient, seed_test_data: dict):
    client_token = seed_test_data["client_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)
    task_internal_id = str(seed_test_data["task_internal"].id)

    headers = {
        "Authorization": f"Bearer {client_token}",
        "X-Agency-ID": agency_a_id
    }

    response = await client.get(f"/api/v1/tasks/{task_internal_id}", headers=headers)
    assert response.status_code in (403, 404)

@pytest.mark.asyncio
async def test_client_user_sees_no_internal_comments(client: AsyncClient, seed_test_data: dict):
    client_token = seed_test_data["client_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)
    task_public_id = str(seed_test_data["task_public"].id)

    headers = {
        "Authorization": f"Bearer {client_token}",
        "X-Agency-ID": agency_a_id
    }

    response = await client.get(f"/api/v1/comments/task/{task_public_id}", headers=headers)
    assert response.status_code == 200
    comments = response.json()

    for c in comments:
        assert c["is_internal"] is False
