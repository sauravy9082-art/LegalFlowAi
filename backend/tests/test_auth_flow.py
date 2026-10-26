import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import Base, engine
from app.core.security import verify_password, get_password_hash

@pytest_asyncio.fixture
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_full_auth_flow_and_dashboard_isolation(setup_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register new user with Organization
        reg_payload = {
            "email": "corp_counsel@acmelegal.com",
            "password": "SecurePassword123!",
            "full_name": "Sarah Connor",
            "organization": "Acme Legal Corp"
        }
        res_reg = await ac.post("/api/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        user_data = res_reg.json()
        assert user_data["email"] == "corp_counsel@acmelegal.com"
        assert user_data["full_name"] == "Sarah Connor"
        assert user_data["organization"] == "Acme Legal Corp"

        # 2. Duplicate registration should return "Email already in use."
        res_dup = await ac.post("/api/auth/register", json=reg_payload)
        assert res_dup.status_code == 400
        assert "Email already in use." in res_dup.json()["detail"]

        # 3. Invalid login: Incorrect password
        bad_login = {
            "email": "corp_counsel@acmelegal.com",
            "password": "WrongPassword999!"
        }
        res_bad_pw = await ac.post("/api/auth/login", json=bad_login)
        assert res_bad_pw.status_code == 401
        assert "Incorrect password." in res_bad_pw.json()["detail"]

        # 4. Successful Login
        valid_login = {
            "email": "corp_counsel@acmelegal.com",
            "password": "SecurePassword123!"
        }
        res_login = await ac.post("/api/auth/login", json=valid_login)
        assert res_login.status_code == 200
        token_data = res_login.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        assert token_data["user"]["organization"] == "Acme Legal Corp"

        # 5. Access protected /auth/me
        headers = {"Authorization": f"Bearer {token}"}
        res_me = await ac.get("/api/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["organization"] == "Acme Legal Corp"

        # 6. Check user dashboard documents -> should be empty (0 active contracts onboarding state)
        res_docs = await ac.get("/api/documents", headers=headers)
        assert res_docs.status_code == 200
        assert len(res_docs.json()) == 0
