import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_cross_tenant_isolation(client: AsyncClient, seed_test_data: dict):
    admin_token = seed_test_data["admin_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)
    proj_b_id = str(seed_test_data["proj_b"].id)

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Agency-ID": agency_a_id
    }

    # Attempt to fetch Agency B's project using Agency A tenant header
    response = await client.get(f"/api/v1/projects/{proj_b_id}", headers=headers)
    assert response.status_code in (403, 404)

@pytest.mark.asyncio
async def test_invalid_agency_header_denied(client: AsyncClient, seed_test_data: dict):
    admin_token = seed_test_data["admin_token"]
    agency_b_id = str(seed_test_data["agency_b"].id)

    # Admin of Agency A tries sending Agency B ID header
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Agency-ID": agency_b_id
    }

    response = await client.get("/api/v1/projects/", headers=headers)
    assert response.status_code == 403
