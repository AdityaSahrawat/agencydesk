import asyncio
import datetime
import os
import uuid
from datetime import timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import engine, AsyncSessionLocal
from app.models import (
    Agency,
    User,
    AgencyMembership,
    RoleEnum,
    Client,
    Project,
    ProjectStatus,
    ProjectMember,
    Task,
    TaskStatus,
    TaskPriority,
    Comment,
    TaskFile,
    FileApprovalStatus,
    TimeEntry,
    Base
)


async def seed_data():
    print("🌱 Initializing Database Schema & Seeding Data...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Common Hashed Password for seed users
        password_hash = get_password_hash("Password123!")

        # ----------------------------------------------------
        # Users
        # ----------------------------------------------------
        user_alice = User(
            id=uuid.uuid4(),
            email="alice@agencyalpha.com",
            full_name="Alice Admin",
            hashed_password=password_hash
        )
        user_bob = User(
            id=uuid.uuid4(),
            email="bob@agencyalpha.com",
            full_name="Bob Member",
            hashed_password=password_hash
        )
        user_charlie = User(
            id=uuid.uuid4(),
            email="charlie@clientcorp.com",
            full_name="Charlie Client",
            hashed_password=password_hash
        )
        user_diana = User(
            id=uuid.uuid4(),
            email="diana@betaagency.com",
            full_name="Diana Beta Admin",
            hashed_password=password_hash
        )
        # Multi-agency user (John belongs to Alpha as client, Beta as admin)
        user_john = User(
            id=uuid.uuid4(),
            email="john@gmail.com",
            full_name="John MultiTenant",
            hashed_password=password_hash
        )

        session.add_all([user_alice, user_bob, user_charlie, user_diana, user_john])
        await session.flush()

        # ----------------------------------------------------
        # Agency 1: Alpha Creative
        # ----------------------------------------------------
        agency_alpha = Agency(
            id=uuid.uuid4(),
            name="Alpha Creative",
            slug="alpha-creative"
        )

        # Agency 2: Beta Solutions
        agency_beta = Agency(
            id=uuid.uuid4(),
            name="Beta Solutions",
            slug="beta-solutions"
        )

        session.add_all([agency_alpha, agency_beta])
        await session.flush()

        # ----------------------------------------------------
        # Clients in Agency Alpha
        # ----------------------------------------------------
        client_acme = Client(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            name="Acme Corp",
            company_name="Acme Corporation",
            email="contact@acme.com",
            phone="+1-555-0199"
        )
        client_stark = Client(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            name="Stark Industries",
            company_name="Stark Industries Inc.",
            email="info@stark.com"
        )

        # Clients in Agency Beta
        client_globex = Client(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            name="Globex",
            company_name="Globex Corp",
            email="info@globex.com"
        )

        session.add_all([client_acme, client_stark, client_globex])
        await session.flush()

        # ----------------------------------------------------
        # Agency Memberships
        # ----------------------------------------------------
        m_alice = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_alice.id,
            role=RoleEnum.AGENCY_ADMIN
        )
        m_bob = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_bob.id,
            role=RoleEnum.AGENCY_MEMBER
        )
        m_charlie = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_charlie.id,
            role=RoleEnum.CLIENT_USER,
            client_id=client_acme.id
        )
        m_john_alpha = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_john.id,
            role=RoleEnum.CLIENT_USER,
            client_id=client_stark.id
        )

        m_diana = AgencyMembership(
            agency_id=agency_beta.id,
            user_id=user_diana.id,
            role=RoleEnum.AGENCY_ADMIN
        )
        m_john_beta = AgencyMembership(
            agency_id=agency_beta.id,
            user_id=user_john.id,
            role=RoleEnum.AGENCY_ADMIN
        )

        session.add_all([m_alice, m_bob, m_charlie, m_john_alpha, m_diana, m_john_beta])
        await session.flush()

        # ----------------------------------------------------
        # Projects
        # ----------------------------------------------------
        proj_website = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_acme.id,
            name="Acme Website Redesign",
            description="Complete UX/UI redesign and FastAPI backend development",
            status=ProjectStatus.ACTIVE,
            created_by=user_alice.id
        )
        proj_branding = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_acme.id,
            name="Acme Brand Identity",
            description="New brand guidelines and logo vectorization",
            status=ProjectStatus.ACTIVE,
            created_by=user_bob.id
        )
        proj_stark_app = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_stark.id,
            name="Stark Mobile Portal",
            description="iOS and Android companion portal",
            status=ProjectStatus.ACTIVE,
            created_by=user_alice.id
        )
        proj_beta_erp = Project(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            client_id=client_globex.id,
            name="Globex ERP Migration",
            description="Legacy migration to cloud ERP platform",
            status=ProjectStatus.ACTIVE,
            created_by=user_diana.id
        )

        session.add_all([proj_website, proj_branding, proj_stark_app, proj_beta_erp])
        await session.flush()

        # Project Members
        pm1 = ProjectMember(agency_id=agency_alpha.id, project_id=proj_website.id, user_id=user_bob.id)
        pm2 = ProjectMember(agency_id=agency_alpha.id, project_id=proj_branding.id, user_id=user_bob.id)
        session.add_all([pm1, pm2])
        await session.flush()

        # ----------------------------------------------------
        # Tasks (Client Visible & Internal)
        # ----------------------------------------------------
        task_client_visible = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Design Homepage Wireframes",
            description="Figma mockup for desktop and mobile hero layout",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            assigned_to=user_bob.id,
            is_internal=False,  # Client Visible!
            created_by=user_alice.id
        )

        task_internal_only = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Internal Database Audit & Optimization",
            description="Optimize PostgreSQL query indices and secret keys rot",
            status=TaskStatus.TODO,
            priority=TaskPriority.URGENT,
            assigned_to=user_alice.id,
            is_internal=True,  # INTERNAL ONLY!
            created_by=user_alice.id
        )

        task_beta = Task(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            project_id=proj_beta_erp.id,
            title="Globex Data Import Script",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            assigned_to=user_john.id,
            is_internal=False,
            created_by=user_diana.id
        )

        session.add_all([task_client_visible, task_internal_only, task_beta])
        await session.flush()

        # ----------------------------------------------------
        # Comments (Client Visible & Internal)
        # ----------------------------------------------------
        comm1 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_client_visible.id,
            user_id=user_charlie.id,
            content="Looking great! Please increase the logo size by 15%.",
            is_internal=False
        )
        comm2 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_client_visible.id,
            user_id=user_bob.id,
            content="Will update wireframes in Figma shortly.",
            is_internal=False
        )
        comm_internal = Comment(
            agency_id=agency_alpha.id,
            task_id=task_internal_only.id,
            user_id=user_alice.id,
            content="Internal note: Make sure we check backup WAL logs.",
            is_internal=True
        )

        session.add_all([comm1, comm2, comm_internal])
        await session.flush()

        # ----------------------------------------------------
        # Files
        # ----------------------------------------------------
        task_file = TaskFile(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            task_id=task_client_visible.id,
            uploaded_by=user_bob.id,
            filename="homepage_v1_wireframe.pdf",
            file_path=os.path.join(settings.UPLOAD_DIR, "demo_wireframe.pdf"),
            file_size=1024500,
            content_type="application/pdf",
            is_internal=False,
            approval_status=FileApprovalStatus.APPROVED
        )
        session.add(task_file)
        await session.flush()

        # ----------------------------------------------------
        # Time Entries
        # ----------------------------------------------------
        te1 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_client_visible.id,
            user_id=user_bob.id,
            hours=4.5,
            date=datetime.date.today(),
            note="Worked on responsive breakpoints and layout design."
        )
        te2 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_internal_only.id,
            user_id=user_alice.id,
            hours=2.0,
            date=datetime.date.today(),
            note="Configured PostgreSQL indices."
        )
        session.add_all([te1, te2])
        await session.commit()

    print("✅ Seed Data successfully created!")


if __name__ == "__main__":
    asyncio.run(seed_data())
