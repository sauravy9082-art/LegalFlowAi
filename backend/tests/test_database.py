import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.core.database import Base
from app.models.db_models import User, Document, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_user_creation_and_query(test_db: AsyncSession):
    new_user = User(
        email="testlawyer@legalflow.ai",
        hashed_password="secret_hashed_password_123",
        full_name="Jane Doe, Esq.",
        role=UserRole.USER.value
    )
    test_db.add(new_user)
    await test_db.commit()

    stmt = select(User).where(User.email == "testlawyer@legalflow.ai")
    result = await test_db.execute(stmt)
    user = result.scalar_one_or_none()

    assert user is not None
    assert user.email == "testlawyer@legalflow.ai"
    assert user.full_name == "Jane Doe, Esq."
    assert user.role == "USER"

@pytest.mark.asyncio
async def test_document_user_relationship(test_db: AsyncSession):
    user = User(
        email="owner@legalflow.ai",
        hashed_password="hashed_pass_456"
    )
    test_db.add(user)
    await test_db.commit()

    doc = Document(
        user_id=user.id,
        filename="lease_agreement.pdf",
        original_filename="sample_lease.pdf",
        file_path="/storage/documents/sample_lease.pdf",
        mime_type="application/pdf",
        file_size_bytes=102450
    )
    test_db.add(doc)
    await test_db.commit()

    stmt = select(Document).where(Document.user_id == user.id)
    result = await test_db.execute(stmt)
    fetched_doc = result.scalar_one_or_none()

    assert fetched_doc is not None
    assert fetched_doc.filename == "lease_agreement.pdf"
    assert fetched_doc.user_id == user.id
