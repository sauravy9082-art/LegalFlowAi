import pytest
from app.models.db_models import Document, AnalysisReport, Clause, RiskFinding, DocumentPage
from app.api.chat import build_rule_based_fallback_response


def test_chat_fallback_risk_query():
    doc = Document(id="doc-test-1", original_filename="commercial_lease.pdf")
    report = AnalysisReport(
        deterministic_risk_score=68,
        risk_classification="ORANGE",
        summary="Commercial lease with landlord unilateral termination and indemnity.",
        recommendations=["Limit indemnification liability", "Add mutual notice period"]
    )
    flagged = [
        {
            "category": "Unilateral Modification Right",
            "level": "HIGH",
            "page": 2,
            "text": "Landlord may modify common rules without notice.",
            "explanation": "Allows landlord to change obligations unilaterally.",
            "suggested_action": "Require 30-day written notice."
        },
        {
            "category": "Indemnification & Hold Harmless",
            "level": "CRITICAL",
            "page": 5,
            "text": "Tenant indemnifies landlord against all liabilities whatsoever.",
            "explanation": "One-sided unlimited indemnity exposure.",
            "suggested_action": "Carve out landlord gross negligence."
        }
    ]
    pages = [
        DocumentPage(page_number=1, text_content="Lease agreement preamble"),
        DocumentPage(page_number=2, text_content="Landlord rights"),
        DocumentPage(page_number=5, text_content="Indemnification section")
    ]

    # Test "how much risk detected in my project"
    reply, ref_pages = build_rule_based_fallback_response(
        query="how much risk detected in my project",
        doc=doc,
        report=report,
        flagged_risks=flagged,
        pages=pages,
        language="English"
    )

    assert "68/100" in reply
    assert "ORANGE" in reply
    assert "Unilateral Modification Right" in reply
    assert "Indemnification & Hold Harmless" in reply
    assert 2 in ref_pages or 5 in ref_pages


def test_chat_fallback_summary_query():
    doc = Document(id="doc-test-2", original_filename="freelance_contract.pdf")
    report = AnalysisReport(
        deterministic_risk_score=20,
        risk_classification="GREEN",
        summary="Standard freelance agreement for software development.",
        recommendations=["Ensure payment milestone verification"]
    )

    reply, ref_pages = build_rule_based_fallback_response(
        query="give me summary about my project",
        doc=doc,
        report=report,
        flagged_risks=[],
        pages=[],
        language="English"
    )

    assert "20/100" in reply
    assert "GREEN" in reply
    assert "Standard freelance agreement" in reply


def test_chat_fallback_clause_search():
    doc = Document(id="doc-test-3", original_filename="nda.pdf")
    flagged = [
        {
            "category": "Immediate Termination & Notice Period",
            "level": "HIGH",
            "page": 3,
            "text": "Party A may terminate immediately without cause.",
            "explanation": "No cure period provided.",
            "suggested_action": "Require 14-day cure notice."
        }
    ]

    reply, ref_pages = build_rule_based_fallback_response(
        query="what is the termination clause?",
        doc=doc,
        report=None,
        flagged_risks=flagged,
        pages=[],
        language="English"
    )

    assert "Termination" in reply
    assert "Immediate Termination & Notice Period" in reply
    assert 3 in ref_pages
