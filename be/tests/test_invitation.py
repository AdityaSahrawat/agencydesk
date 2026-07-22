import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_invitation_flow_and_resend(client: AsyncClient, seed_test_data: dict):
    admin_token = seed_test_data["admin_token"]
    agency_a_id = str(seed_test_data["agency_a"].id)

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "X-Agency-ID": agency_a_id
    }

    # 1. Create invitation
    invite_payload = {
        "email": "invited_person@test.com",
        "role": "agency_member"
    }

    res = await client.post("/api/v1/invitations/", json=invite_payload, headers=headers)
    assert res.status_code == 201
    invite_1 = res.json()
    token_1 = invite_1["token"]

    # 2. Resend invitation (race & duplicate edge case test)
    resend = await client.post("/api/v1/invitations/", json=invite_payload, headers=headers)
    assert resend.status_code == 201
    invite_2 = resend.json()
    token_2 = invite_2["token"]

    # Same invitation ID updated with new token
    assert invite_1["id"] == invite_2["id"]

    # 3. Accept invitation
    accept_payload = {
        "token": token_2,
        "password": "Password123!",
        "full_name": "Invited Person"
    }

    accept_res = await client.post("/api/v1/invitations/accept", json=accept_payload)
    assert accept_res.status_code == 200
    assert accept_res.json()["role"] == "agency_member"

    # 4. Accept twice idempotency check
    accept_twice = await client.post("/api/v1/invitations/accept", json=accept_payload)
    assert accept_twice.status_code == 200
