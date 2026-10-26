import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine
from app.services.risk_engine import DeterministicRiskEngine
from app.services.translation_service import MultilingualExplanationService
from app.models.schemas import ClauseSchema, RiskLevelEnum

client = TestClient(app)

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "LegalFlow AI" in data["app"]
    assert "informational document analysis" in data["privacy_notice"]


def test_user_registration_and_login():
    email = "testuser@legalflow.ai"
    password = "secretpassword123"

    # Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test User"
    })
    assert reg_res.status_code in [201, 400]

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data

    # Profile lookup
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email


def test_risk_scoring_engine_determinism():
    clauses = [
        ClauseSchema(
            category="Security Deposit Forfeiture",
            original_text="The tenant shall forfeit deposit.",
            risk_level=RiskLevelEnum.CRITICAL,
            explanation="Critical risk",
            reason="Unilateral forfeiture",
            suggested_action="Remove forfeiture clause"
        ),
        ClauseSchema(
            category="Uncapped Liability",
            original_text="Tenant agrees to uncapped liability.",
            risk_level=RiskLevelEnum.CRITICAL,
            explanation="Critical liability risk",
            reason="Uncapped liability",
            suggested_action="Cap liability"
        )
    ]
    res = DeterministicRiskEngine().calculate_score(clauses)
    
    assert res["score"] <= 60
    assert res["classification"] in ["ORANGE", "RED"]


def test_multilingual_translations():
    category = "Security Deposit Forfeiture"
    hi_exp = MultilingualExplanationService.get_explanation(category, "English text", "hindi")
    mr_exp = MultilingualExplanationService.get_explanation(category, "English text", "marathi")
    
    assert "सुरक्षा जमा" in hi_exp
    assert "सुरक्षा ठेव" in mr_exp


def test_system_ollama_status():
    res = client.get("/api/system/ollama-status")
    assert res.status_code == 200
    assert "ollama_connected" in res.json()
