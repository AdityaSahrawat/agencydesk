import datetime
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_crud_clients_and_projects(client: AsyncClient, seed_test_data: dict):
    admin_token = seed_test_data["admin_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Agency-ID": agency_a_id
    }

    # Create Client
    c_res = await client.post("/api/v1/clients/", json={
        "name": "New Client",
        "company_name": "New Corp",
        "email": "new@client.com"
    }, headers=headers)
    assert c_res.status_code == 201
    client_id = c_res.json()["id"]

    # List Clients
    list_c = await client.get("/api/v1/clients/", headers=headers)
    assert list_c.status_code == 200
    assert len(list_c.json()) >= 2

    # Create Project
    p_res = await client.post("/api/v1/projects/", json={
        "client_id": client_id,
        "name": "New Web App",
        "status": "active"
    }, headers=headers)
    assert p_res.status_code == 201
    project_id = p_res.json()["id"]

    # Log Time Entry
    t_res = await client.post("/api/v1/time-entries/", json={
        "project_id": project_id,
        "hours": 3.5,
        "date": str(datetime.date.today()),
        "note": "Initial architectural setup"
    }, headers=headers)
    assert t_res.status_code == 201

    # Check Total Hours for Project
    h_res = await client.get(f"/api/v1/time-entries/project/{project_id}/total-hours", headers=headers)
    assert h_res.status_code == 200
    assert h_res.json()["total_hours"] == 3.5

    # Get Dashboard Summary
    dash_res = await client.get("/api/v1/dashboard/summary", headers=headers)
    assert dash_res.status_code == 200
    assert dash_res.json()["total_projects"] >= 2
