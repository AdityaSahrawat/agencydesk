import asyncio
import datetime
import os
import uuid
from datetime import timedelta, timezone
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
    Invitation,
    InvitationStatus,
    Base
)


async def seed_data():
    print("🌱 Initializing Database Schema & Seeding Data...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Ensure upload directory exists for physical files
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    async with AsyncSessionLocal() as session:
        # Common Hashed Password for seed users
        password_hash = get_password_hash("Password123!")
        now = datetime.datetime.now(timezone.utc)
        today = datetime.date.today()

        # ----------------------------------------------------
        # 1. Users
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
        user_carol = User(
            id=uuid.uuid4(),
            email="carol@agencyalpha.com",
            full_name="Carol Senior Dev",
            hashed_password=password_hash
        )
        user_charlie = User(
            id=uuid.uuid4(),
            email="charlie@clientcorp.com",
            full_name="Charlie Client",
            hashed_password=password_hash
        )
        user_david = User(
            id=uuid.uuid4(),
            email="david@stark.com",
            full_name="David Stark Client",
            hashed_password=password_hash
        )
        user_diana = User(
            id=uuid.uuid4(),
            email="diana@betaagency.com",
            full_name="Diana Beta Admin",
            hashed_password=password_hash
        )
        user_john = User(
            id=uuid.uuid4(),
            email="john@gmail.com",
            full_name="John MultiTenant",
            hashed_password=password_hash
        )

        session.add_all([
            user_alice, user_bob, user_carol, user_charlie,
            user_david, user_diana, user_john
        ])
        await session.flush()

        # ----------------------------------------------------
        # 2. Agencies
        # ----------------------------------------------------
        agency_alpha = Agency(
            id=uuid.uuid4(),
            name="Alpha Creative",
            slug="alpha-creative"
        )
        agency_beta = Agency(
            id=uuid.uuid4(),
            name="Beta Solutions",
            slug="beta-solutions"
        )

        session.add_all([agency_alpha, agency_beta])
        await session.flush()

        # ----------------------------------------------------
        # 3. Clients
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
            email="info@stark.com",
            phone="+1-555-0188"
        )
        client_cyberdyne = Client(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            name="Cyberdyne Systems",
            company_name="Cyberdyne AI Systems",
            email="support@cyberdyne.io",
            phone="+1-555-0177"
        )
        client_globex = Client(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            name="Globex",
            company_name="Globex Corporation",
            email="info@globex.com"
        )

        session.add_all([client_acme, client_stark, client_cyberdyne, client_globex])
        await session.flush()

        # ----------------------------------------------------
        # 4. Agency Memberships
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
        m_carol = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_carol.id,
            role=RoleEnum.AGENCY_MEMBER
        )
        m_charlie = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_charlie.id,
            role=RoleEnum.CLIENT_USER,
            client_id=client_acme.id
        )
        m_david = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_david.id,
            role=RoleEnum.CLIENT_USER,
            client_id=client_stark.id
        )
        m_john_alpha = AgencyMembership(
            agency_id=agency_alpha.id,
            user_id=user_john.id,
            role=RoleEnum.CLIENT_USER,
            client_id=client_acme.id
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

        session.add_all([
            m_alice, m_bob, m_carol, m_charlie, m_david, m_john_alpha,
            m_diana, m_john_beta
        ])
        await session.flush()

        # ----------------------------------------------------
        # 5. Projects
        # ----------------------------------------------------
        proj_website = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_acme.id,
            name="Acme Brand & Website Redesign",
            description="Comprehensive brand strategy, Figma UI design, Next.js frontend, and FastAPI backend development.",
            status=ProjectStatus.ACTIVE,
            created_by=user_alice.id
        )

        proj_stark_app = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_stark.id,
            name="Stark Mobile Portal",
            description="Cross-platform iOS and Android companion app with real-time telematics dashboard.",
            status=ProjectStatus.ACTIVE,
            created_by=user_alice.id
        )

        proj_cyberdyne_ai = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_cyberdyne.id,
            name="Cyberdyne AI Interface",
            description="Machine learning data visualization suite and analytics dashboard.",
            status=ProjectStatus.DRAFT,
            created_by=user_bob.id
        )

        proj_acme_growth = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_acme.id,
            name="Acme Q3 Growth & SEO Campaign",
            description="SEO audit, performance tuning, and landing page conversion rate optimization.",
            status=ProjectStatus.COMPLETED,
            created_by=user_carol.id
        )

        proj_acme_legacy = Project(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            client_id=client_acme.id,
            name="Acme Legacy Database Migration",
            description="Archived project for legacy Oracle cluster to cloud migration.",
            status=ProjectStatus.ARCHIVED,
            created_by=user_alice.id
        )

        proj_beta_erp = Project(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            client_id=client_globex.id,
            name="Globex ERP Cloud Migration",
            description="Enterprise resource planning migration to distributed cloud platform.",
            status=ProjectStatus.ACTIVE,
            created_by=user_diana.id
        )

        session.add_all([
            proj_website, proj_stark_app, proj_cyberdyne_ai,
            proj_acme_growth, proj_acme_legacy, proj_beta_erp
        ])
        await session.flush()

        # Project Members
        pm1 = ProjectMember(agency_id=agency_alpha.id, project_id=proj_website.id, user_id=user_bob.id)
        pm2 = ProjectMember(agency_id=agency_alpha.id, project_id=proj_website.id, user_id=user_carol.id)
        pm3 = ProjectMember(agency_id=agency_alpha.id, project_id=proj_stark_app.id, user_id=user_carol.id)
        pm4 = ProjectMember(agency_id=agency_alpha.id, project_id=proj_cyberdyne_ai.id, user_id=user_bob.id)
        session.add_all([pm1, pm2, pm3, pm4])
        await session.flush()

        # ----------------------------------------------------
        # 6. Tasks for ALL Projects (Mixed: DONE, IN_PROGRESS, REVIEW, TODO)
        # ----------------------------------------------------

        # --- Project 1: Acme Brand & Website Redesign ---
        task_w1 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Discovery & Sitemap Definition",
            description="Map primary user flows, content hierarchy, and SEO architecture.",
            status=TaskStatus.DONE,
            priority=TaskPriority.LOW,
            due_date=now - timedelta(days=10),
            assigned_to=user_bob.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_w2 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Figma Hero & Component UI Kit",
            description="Design modern dark-mode responsive hero layouts and interactive UI elements.",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=now - timedelta(days=3),
            assigned_to=user_bob.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_w3 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Develop Next.js 16 Frontend Pages",
            description="Build responsive dashboard views, authentication screens, and client portal layout.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=now + timedelta(days=4),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_w4 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Stripe Billing Integration",
            description="Connect subscription checkout, webhooks, and invoice generation.",
            status=TaskStatus.REVIEW,
            priority=TaskPriority.URGENT,
            due_date=now + timedelta(days=2),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_w5 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Internal Security & Vulnerability Audit",
            description="Rotate secrets, verify JWT expiration, and audit CORS origins.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.URGENT,
            due_date=now + timedelta(days=1),
            assigned_to=user_alice.id,
            is_internal=True,
            created_by=user_alice.id
        )
        task_w6 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            title="Database Query Optimization",
            description="Add database indices to improve multi-tenant query speeds.",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            due_date=now + timedelta(days=7),
            assigned_to=user_bob.id,
            is_internal=True,
            created_by=user_alice.id
        )

        # --- Project 2: Stark Mobile Portal ---
        task_s1 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_stark_app.id,
            title="Setup React Native Project Structure",
            description="Initialize boilerplate with TypeScript, Navigation, and Tailwind.",
            status=TaskStatus.DONE,
            priority=TaskPriority.MEDIUM,
            due_date=now - timedelta(days=5),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_s2 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_stark_app.id,
            title="Real-Time Telematics WebSocket Stream",
            description="Implement secure WebSocket handler for live sensor telemetry stream.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=now + timedelta(days=5),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_s3 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_stark_app.id,
            title="Biometric Authentication & Keychain Storage",
            description="Implement FaceID / Fingerprint auth flow for mobile app logins.",
            status=TaskStatus.DONE,
            priority=TaskPriority.URGENT,
            due_date=now - timedelta(days=1),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_alice.id
        )
        task_s4 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_stark_app.id,
            title="Push Notification Delivery Engine",
            description="Integrate Firebase Cloud Messaging for instant status alerts.",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            due_date=now + timedelta(days=10),
            assigned_to=user_bob.id,
            is_internal=False,
            created_by=user_alice.id
        )

        # --- Project 3: Cyberdyne AI Interface ---
        task_c1 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_cyberdyne_ai.id,
            title="Draft AI Model Architecture Specification",
            description="Outline GPU requirements, latency targets, and interface wireframes.",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=now - timedelta(days=2),
            assigned_to=user_bob.id,
            is_internal=False,
            created_by=user_bob.id
        )
        task_c2 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_cyberdyne_ai.id,
            title="Train Anomaly Detection Transformer Model",
            description="Fine-tune deep learning model on historical sensor telemetry data.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.URGENT,
            due_date=now + timedelta(days=6),
            assigned_to=user_bob.id,
            is_internal=True,
            created_by=user_alice.id
        )
        task_c3 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_cyberdyne_ai.id,
            title="Build WebGL Neural Network Visualizer",
            description="3D canvas renderer for real-time model activation node graphs.",
            status=TaskStatus.REVIEW,
            priority=TaskPriority.MEDIUM,
            due_date=now + timedelta(days=3),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_bob.id
        )
        task_c4 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_cyberdyne_ai.id,
            title="Client Demonstration & Sign-Off Session",
            description="Present interactive AI dashboard prototype to Cyberdyne stakeholders.",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            due_date=now + timedelta(days=14),
            assigned_to=user_alice.id,
            is_internal=False,
            created_by=user_alice.id
        )

        # --- Project 4: Acme Q3 Growth & SEO Campaign ---
        task_g1 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_acme_growth.id,
            title="Technical SEO & Schema Markup Audit",
            description="Audit structured data, canonical tags, and mobile usability scores.",
            status=TaskStatus.DONE,
            priority=TaskPriority.MEDIUM,
            due_date=now - timedelta(days=20),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_carol.id
        )
        task_g2 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_acme_growth.id,
            title="Core Web Vitals Optimization",
            description="Optimize LCP, CLS, and FID to achieve 100 Lighthouse performance rating.",
            status=TaskStatus.DONE,
            priority=TaskPriority.URGENT,
            due_date=now - timedelta(days=15),
            assigned_to=user_carol.id,
            is_internal=False,
            created_by=user_carol.id
        )
        task_g3 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_acme_growth.id,
            title="High-Converting Landing Page A/B Test",
            description="Deploy split test variant with dynamic headline copy and CTA.",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=now - timedelta(days=10),
            assigned_to=user_bob.id,
            is_internal=False,
            created_by=user_alice.id
        )

        # --- Project 5: Acme Legacy Database Migration ---
        task_l1 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_acme_legacy.id,
            title="Legacy Oracle Schema Extraction",
            description="Dump DDL definitions and generate PostgreSQL target mapping.",
            status=TaskStatus.DONE,
            priority=TaskPriority.MEDIUM,
            due_date=now - timedelta(days=30),
            assigned_to=user_alice.id,
            is_internal=True,
            created_by=user_alice.id
        )
        task_l2 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_acme_legacy.id,
            title="Data Sanitization & Type Coercion Pipeline",
            description="Convert legacy CHAR columns to UUID and text format.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            due_date=now + timedelta(days=5),
            assigned_to=user_bob.id,
            is_internal=True,
            created_by=user_alice.id
        )
        task_l3 = Task(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            project_id=proj_acme_legacy.id,
            title="Dual-Write Replication Verification",
            description="Verify zero-downtime replication between Oracle and Postgres.",
            status=TaskStatus.TODO,
            priority=TaskPriority.URGENT,
            due_date=now + timedelta(days=15),
            assigned_to=user_alice.id,
            is_internal=True,
            created_by=user_alice.id
        )

        # --- Project 6: Globex ERP Cloud Migration (Beta Agency) ---
        task_b1 = Task(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            project_id=proj_beta_erp.id,
            title="Globex ETL Data Migration Pipeline",
            description="Parse legacy XML exports and stream to PostgreSQL database.",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.URGENT,
            due_date=now + timedelta(days=3),
            assigned_to=user_john.id,
            is_internal=False,
            created_by=user_diana.id
        )
        task_b2 = Task(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            project_id=proj_beta_erp.id,
            title="Role-Based Access Control Configuration",
            description="Setup Globex department permissions and security roles.",
            status=TaskStatus.DONE,
            priority=TaskPriority.HIGH,
            due_date=now - timedelta(days=4),
            assigned_to=user_diana.id,
            is_internal=False,
            created_by=user_diana.id
        )
        task_b3 = Task(
            id=uuid.uuid4(),
            agency_id=agency_beta.id,
            project_id=proj_beta_erp.id,
            title="Automated Inventory Reconciliation Test",
            description="Validate real-time inventory balances against legacy ERP records.",
            status=TaskStatus.REVIEW,
            priority=TaskPriority.MEDIUM,
            due_date=now + timedelta(days=1),
            assigned_to=user_john.id,
            is_internal=False,
            created_by=user_diana.id
        )

        all_tasks = [
            task_w1, task_w2, task_w3, task_w4, task_w5, task_w6,
            task_s1, task_s2, task_s3, task_s4,
            task_c1, task_c2, task_c3, task_c4,
            task_g1, task_g2, task_g3,
            task_l1, task_l2, task_l3,
            task_b1, task_b2, task_b3
        ]
        session.add_all(all_tasks)
        await session.flush()

        # ----------------------------------------------------
        # 7. Comments
        # ----------------------------------------------------
        comm1 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_w2.id,
            user_id=user_charlie.id,
            content="The new Figma hero concept looks clean! Can we make the CTA button slightly larger?",
            is_internal=False
        )
        comm2 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_w2.id,
            user_id=user_bob.id,
            content="Updated in Figma file v2! Increased contrast and button padding.",
            is_internal=False
        )
        comm3 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_w4.id,
            user_id=user_carol.id,
            content="Stripe webhook endpoint is ready and tested in sandbox environment.",
            is_internal=False
        )
        comm_internal1 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_w5.id,
            user_id=user_alice.id,
            content="Internal note: Double check JWT secret key rotation procedures in production.",
            is_internal=True
        )
        comm_internal2 = Comment(
            agency_id=agency_alpha.id,
            task_id=task_w6.id,
            user_id=user_bob.id,
            content="Adding composite index on (agency_id, project_id) reduces query times by 80%.",
            is_internal=True
        )

        session.add_all([comm1, comm2, comm3, comm_internal1, comm_internal2])
        await session.flush()

        # ----------------------------------------------------
        # 8. Files
        # ----------------------------------------------------
        file_path_1 = os.path.join(settings.UPLOAD_DIR, "acme_homepage_wireframe_v2.pdf")
        file_path_2 = os.path.join(settings.UPLOAD_DIR, "stripe_integration_spec.pdf")
        file_path_3 = os.path.join(settings.UPLOAD_DIR, "security_vulnerability_scan.log")

        for fpath in [file_path_1, file_path_2, file_path_3]:
            if not os.path.exists(fpath):
                with open(fpath, "w") as f:
                    f.write("AgencyDesk Demo File Content")

        task_file1 = TaskFile(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            task_id=task_w2.id,
            uploaded_by=user_bob.id,
            filename="acme_homepage_wireframe_v2.pdf",
            file_path=file_path_1,
            file_size=2048500,
            content_type="application/pdf",
            is_internal=False,
            approval_status=FileApprovalStatus.APPROVED
        )

        task_file2 = TaskFile(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            task_id=task_w4.id,
            uploaded_by=user_carol.id,
            filename="stripe_integration_spec.pdf",
            file_path=file_path_2,
            file_size=1540200,
            content_type="application/pdf",
            is_internal=False,
            approval_status=FileApprovalStatus.PENDING
        )

        task_file3 = TaskFile(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            task_id=task_w5.id,
            uploaded_by=user_alice.id,
            filename="security_vulnerability_scan.log",
            file_path=file_path_3,
            file_size=40200,
            content_type="text/plain",
            is_internal=True,
            approval_status=FileApprovalStatus.APPROVED
        )

        session.add_all([task_file1, task_file2, task_file3])
        await session.flush()

        # ----------------------------------------------------
        # 9. Time Entries
        # ----------------------------------------------------
        te1 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_w1.id,
            user_id=user_bob.id,
            hours=6.0,
            date=today - timedelta(days=6),
            note="Conducted stakeholder discovery calls and mapped sitemap."
        )
        te2 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_w2.id,
            user_id=user_bob.id,
            hours=7.5,
            date=today - timedelta(days=3),
            note="Designed Figma responsive layouts and UI components."
        )
        te3 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_w3.id,
            user_id=user_carol.id,
            hours=8.0,
            date=today - timedelta(days=2),
            note="Developed Next.js pages and integrated TanStack Query."
        )
        te4 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_w4.id,
            user_id=user_carol.id,
            hours=4.5,
            date=today - timedelta(days=1),
            note="Implemented Stripe Checkout webhook handler."
        )
        te5 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_website.id,
            task_id=task_w5.id,
            user_id=user_alice.id,
            hours=3.0,
            date=today,
            note="Audited API authorization dependencies and security headers."
        )
        te6 = TimeEntry(
            agency_id=agency_alpha.id,
            project_id=proj_stark_app.id,
            task_id=task_s2.id,
            user_id=user_carol.id,
            hours=5.0,
            date=today,
            note="Configured WebSocket stream for vehicle telemetry."
        )

        session.add_all([te1, te2, te3, te4, te5, te6])
        await session.flush()

        # ----------------------------------------------------
        # 10. Invitations
        # ----------------------------------------------------
        inv1 = Invitation(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            email="devlead@agencyalpha.com",
            role=RoleEnum.AGENCY_MEMBER,
            token="inv_alpha_member_token_12345",
            status=InvitationStatus.PENDING,
            expires_at=now + timedelta(days=7),
            created_by=user_alice.id
        )

        inv2 = Invitation(
            id=uuid.uuid4(),
            agency_id=agency_alpha.id,
            email="vp@acme.com",
            role=RoleEnum.CLIENT_USER,
            client_id=client_acme.id,
            token="inv_acme_client_token_67890",
            status=InvitationStatus.PENDING,
            expires_at=now + timedelta(days=7),
            created_by=user_alice.id
        )

        session.add_all([inv1, inv2])
        await session.commit()

    print("✅ Seed Data successfully initialized!")
    print("📊 Summary:")
    print("   - Agencies: 2 (Alpha Creative, Beta Solutions)")
    print("   - Users: 7 (Admins, Members, Client Users)")
    print("   - Clients: 4 (Acme Corp, Stark Industries, Cyberdyne Systems, Globex)")
    print("   - Projects: 6 across Active, Draft, Completed, Archived statuses")
    print(f"   - Tasks: {len(all_tasks)} total tasks distributed across all 6 projects (DONE, IN_PROGRESS, REVIEW, TODO)")
    print("   - Task Files: 3 with Approval Statuses (Approved, Pending)")
    print("   - Comments: 5 (Client Visible & Internal Notes)")
    print("   - Time Logs: 34.0 Total Hours logged across tasks")
    print("   - Pending Invitations: 2")


if __name__ == "__main__":
    asyncio.run(seed_data())
