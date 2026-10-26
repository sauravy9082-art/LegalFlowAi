import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os
from app.main import app
from app.core.database import Base, engine

FICTIONAL_LEASE_TEXT = """
FICTIONAL DEMONSTRATION DOCUMENT - NOT A REAL LEGAL AGREEMENT
RESIDENTIAL LEASE AGREEMENT

This Lease Agreement is made on 2026-09-01 between Landlord Alpha and Tenant Beta.
1. Payment & Deposit: Rent shall be $2,000 per month. Non-refundable penalty fee of $500 for late payment.
2. Liability & Indemnity: Tenant shall indemnify Landlord against unlimited liability for any property damages.
3. Termination: Landlord may terminate immediately without notice and without cause.
4. Renewal: Lease shall automatically renew for additional 12-month periods unless notice is given 90 days prior.
"""

@pytest_asyncio.fixture
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_full_end_to_end_legalflow_pipeline(setup_test_db, tmp_path):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Register & Login User
        await ac.post("/api/auth/register", json={"email": "e2e_lawyer@legalflow.ai", "password": "SecurePassword123"})
        res_login = await ac.post("/api/auth/login", json={"email": "e2e_lawyer@legalflow.ai", "password": "SecurePassword123"})
        assert res_login.status_code == 200
        token = res_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Check System Ollama Status
        res_status = await ac.get("/api/system/ollama-status")
        assert res_status.status_code == 200
        status_data = res_status.json()
        assert "ollama_connected" in status_data

        # 3. Upload Fictional Lease Document
        files = {"file": ("sample_lease.txt", FICTIONAL_LEASE_TEXT.encode("utf-8"), "text/plain")}
        res_upload = await ac.post("/api/upload", headers=headers, files=files)
        assert res_upload.status_code == 201
        doc_id = res_upload.json()["id"]

        # 4. Trigger Document Analysis
        res_analyze = await ac.post(f"/api/analyze/{doc_id}", headers=headers)
        assert res_analyze.status_code == 200
        analysis_data = res_analyze.json()
        assert "deterministic_risk_score" in analysis_data
        assert "risk_classification" in analysis_data
        assert len(analysis_data["clauses"]) > 0

        # 5. Fetch Analysis Report & Risks
        res_report = await ac.get(f"/api/analysis/{doc_id}", headers=headers)
        assert res_report.status_code == 200

        res_risks = await ac.get(f"/api/documents/{doc_id}/risks", headers=headers)
        assert res_risks.status_code == 200

        # 6. Export OpenXML Redlined DOCX
        res_export = await ac.get(f"/api/export/docx/{doc_id}", headers=headers)
        assert res_export.status_code == 200
        assert res_export.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        # 7. Extract Timeline
        res_timeline = await ac.get(f"/api/timeline/{doc_id}", headers=headers)
        assert res_timeline.status_code == 200
        timeline_data = res_timeline.json()
        assert "events" in timeline_data

        # 8. Generate Contract Template (.docx)
        template_req = {
            "template_type": "NDA",
            "party_a": "Acme Corp",
            "party_b": "Beta LLC",
            "effective_date": "2026-09-01",
            "governing_law": "State of Delaware",
            "duration_months": 24
        }
        res_tmpl = await ac.post("/api/templates/generate", headers=headers, json=template_req)
        assert res_tmpl.status_code == 200

        # 9. Compare Document against itself
        res_cmp = await ac.post("/api/compare", headers=headers, json={"document_id_a": doc_id, "document_id_b": doc_id})
        assert res_cmp.status_code == 200
