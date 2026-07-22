import asyncio
import os
import uuid
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.db.session import get_db
from app.main import app
from app.models import (
    Agency,
    AgencyMembership,
    Base,
    Client,
    Comment,
    FileApprovalStatus,
    Project,
    ProjectMember,
    ProjectStatus,
    RoleEnum,
    Task,
    TaskFile,
    TaskPriority,
    TaskStatus,
    TimeEntry,
    User
)

# Use SQLite in-memory for fast integration testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def seed_test_data(db_session: AsyncSession):
    pw_hash = get_password_hash("Password123!")

    # Users
    user_admin = User(id=uuid.uuid4(), email="admin@agencya.com", full_name="Alpha Admin", hashed_password=pw_hash)
    user_member = User(id=uuid.uuid4(), email="member@agencya.com", full_name="Alpha Member", hashed_password=pw_hash)
    user_client = User(id=uuid.uuid4(), email="client@clienta.com", full_name="Alpha Client", hashed_password=pw_hash)
    user_agency_b_admin = User(id=uuid.uuid4(), email="admin@agencyb.com", full_name="Beta Admin", hashed_password=pw_hash)

    db_session.add_all([user_admin, user_member, user_client, user_agency_b_admin])
    await db_session.flush()

    # Agencies
    agency_a = Agency(id=uuid.uuid4(), name="Agency A", slug="agency-a")
    agency_b = Agency(id=uuid.uuid4(), name="Agency B", slug="agency-b")
    db_session.add_all([agency_a, agency_b])
    await db_session.flush()

    # Client
    client_a = Client(id=uuid.uuid4(), agency_id=agency_a.id, name="Client A", company_name="Client A Inc", email="info@clienta.com")
    db_session.add(client_a)
    await db_session.flush()

    # Memberships
    m_admin = AgencyMembership(agency_id=agency_a.id, user_id=user_admin.id, role=RoleEnum.AGENCY_ADMIN)
    m_member = AgencyMembership(agency_id=agency_a.id, user_id=user_member.id, role=RoleEnum.AGENCY_MEMBER)
    m_client = AgencyMembership(agency_id=agency_a.id, user_id=user_client.id, role=RoleEnum.CLIENT_USER, client_id=client_a.id)
    m_b_admin = AgencyMembership(agency_id=agency_b.id, user_id=user_agency_b_admin.id, role=RoleEnum.AGENCY_ADMIN)

    db_session.add_all([m_admin, m_member, m_client, m_b_admin])
    await db_session.flush()

    # Project
    proj_a = Project(id=uuid.uuid4(), agency_id=agency_a.id, client_id=client_a.id, name="Project Alpha", created_by=user_admin.id)
    proj_b = Project(id=uuid.uuid4(), agency_id=agency_b.id, client_id=client_a.id, name="Project Beta", created_by=user_agency_b_admin.id)
    db_session.add_all([proj_a, proj_b])
    await db_session.flush()

    # Tasks
    task_public = Task(
        id=uuid.uuid4(),
        agency_id=agency_a.id,
        project_id=proj_a.id,
        title="Public Client Task",
        is_internal=False,
        created_by=user_admin.id
    )
    task_internal = Task(
        id=uuid.uuid4(),
        agency_id=agency_a.id,
        project_id=proj_a.id,
        title="Internal Agency Secret Task",
        is_internal=True,
        created_by=user_admin.id
    )
    db_session.add_all([task_public, task_internal])
    await db_session.flush()

    # Comments
    comm_public = Comment(agency_id=agency_a.id, task_id=task_public.id, user_id=user_admin.id, content="Public Comment", is_internal=False)
    comm_internal = Comment(agency_id=agency_a.id, task_id=task_public.id, user_id=user_admin.id, content="Internal Comment", is_internal=True)
    db_session.add_all([comm_public, comm_internal])
    await db_session.flush()

    await db_session.commit()

    return {
        "user_admin": user_admin,
        "user_member": user_member,
        "user_client": user_client,
        "user_agency_b_admin": user_agency_b_admin,
        "agency_a": agency_a,
        "agency_b": agency_b,
        "client_a": client_a,
        "proj_a": proj_a,
        "proj_b": proj_b,
        "task_public": task_public,
        "task_internal": task_internal,
        "admin_token": create_access_token(user_admin.id),
        "member_token": create_access_token(user_member.id),
        "client_token": create_access_token(user_client.id),
        "agency_b_admin_token": create_access_token(user_agency_b_admin.id)
    }
