import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import Base, engine, AsyncSessionLocal
from app.core.security import verify_password, get_password_hash

@pytest_asyncio.fixture
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_password_hashing_and_verification():
    raw_pass = "LegalFlowSecuredPassword2026!"
    hashed = get_password_hash(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

@pytest.mark.asyncio
async def test_auth_register_and_login(setup_test_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register User A
        reg_payload = {
            "email": "user_a@legalflow.ai",
            "password": "PasswordUserA123",
            "full_name": "Alice Partner"
        }
        res_reg = await ac.post("/api/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        data_reg = res_reg.json()
        assert data_reg["email"] == "user_a@legalflow.ai"

        # 2. Login User A
        login_payload = {
            "email": "user_a@legalflow.ai",
            "password": "PasswordUserA123"
        }
        res_login = await ac.post("/api/auth/login", json=login_payload)
        assert res_login.status_code == 200
        token_data = res_login.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # 3. Get /auth/me with Token
        headers = {"Authorization": f"Bearer {token}"}
        res_me = await ac.get("/api/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == "user_a@legalflow.ai"

@pytest.mark.asyncio
async def test_document_ownership_security(setup_test_db):
    """
    Test Rule 12: User A cannot access User B's documents.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Register User A & B
        await ac.post("/api/auth/register", json={"email": "usera@legalflow.ai", "password": "PassUserA123"})
        await ac.post("/api/auth/register", json={"email": "userb@legalflow.ai", "password": "PassUserB123"})

        # Login User A & B
        res_a = await ac.post("/api/auth/login", json={"email": "usera@legalflow.ai", "password": "PassUserA123"})
        token_a = res_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}

        res_b = await ac.post("/api/auth/login", json={"email": "userb@legalflow.ai", "password": "PassUserB123"})
        token_b = res_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # User A uploads fictional document
        files = {"file": ("fictional_contract_a.txt", b"FICTIONAL DEMONSTRATION DOCUMENT\nNOT A REAL LEGAL AGREEMENT", "text/plain")}
        res_upload = await ac.post("/api/upload", headers=headers_a, files=files)
        assert res_upload.status_code == 201
        doc_id = res_upload.json()["id"]

        # User A can fetch document
        res_fetch_a = await ac.get(f"/api/documents/{doc_id}", headers=headers_a)
        assert res_fetch_a.status_code == 200

        # User B attempts to fetch User A's document -> Must fail with 403 Forbidden
        res_fetch_b = await ac.get(f"/api/documents/{doc_id}", headers=headers_b)
        assert res_fetch_b.status_code == 403
