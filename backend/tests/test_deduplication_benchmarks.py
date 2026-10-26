import pytest
import os
from app.services.pdf_parser import PDFParserService
from app.services.agent_engine import AgentEngineService
from app.services.risk_engine import RiskEngineService
from app.models.schemas import RiskLevelEnum


@pytest.mark.asyncio
async def test_benchmark_pdf_08_uncapped_liability_deduplication():
    """
    Benchmark Test for PDF 08:
    Contains both Unlimited Liability (Section 2) and Indemnity (Section 3).
    Both fall under 'Unilateral Liability & Indemnity'.
    MUST produce:
    - 1 UNIQUE RISK
    - 2 EVIDENCE OCCURRENCES
    - Score deducted ONCE (100 - 25 = 75, YELLOW)
    """
    pdf_path = os.path.join("storage", "documents", "f861bb6e-7c34-458c-a58c-5951a468936b.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip(f"Test PDF {pdf_path} not found.")

    parser = PDFParserService()
    agent = AgentEngineService()
    risk = RiskEngineService()

    pages = await parser.extract_text_and_coords(pdf_path, "08_Critical_Uncapped_Liability.pdf")
    analysis_res = await agent.analyze_document_content(pages)
    score_res = risk.calculate_score(analysis_res.clauses)

    # 1. Must be exactly 1 unique risk
    assert len(analysis_res.clauses) == 1, f"Expected 1 unique risk, got {len(analysis_res.clauses)}"
    
    unique_clause = analysis_res.clauses[0]
    assert unique_clause.category == "Unilateral Liability & Indemnity"
    assert unique_clause.risk_level == RiskLevelEnum.CRITICAL

    # 2. Must have 2 evidence occurrences
    assert unique_clause.occurrence_count == 2, f"Expected 2 occurrences, got {unique_clause.occurrence_count}"
    assert len(unique_clause.evidence_occurrences) == 2

    # 3. Score must be deducted strictly ONCE (100 - 25 = 75)
    assert score_res["score"] == 75, f"Expected score 75, got {score_res['score']}"
    assert score_res["total_penalty"] == 25
    assert score_res["finding_counts"]["CRITICAL"] == 1


@pytest.mark.asyncio
async def test_benchmark_pdf_07_termination_and_renewal_different_legal_effects():
    """
    Benchmark Test for PDF 07:
    Contains Termination Imbalance (Section 2) and Automatic Renewal (Section 3).
    These represent different legal effects and MUST remain 2 separate unique risks:
    - Finding 1: 'Immediate Termination & Notice Period' (HIGH, -15)
    - Finding 2: 'Onerous Automatic Renewal Trap' (MEDIUM, -8)
    - Score: 100 - 15 - 8 = 77 (YELLOW)
    """
    pdf_path = os.path.join("storage", "documents", "e83b2814-bb64-4c1d-95de-d1d2fadc7bfb.pdf")
    if not os.path.exists(pdf_path):
        pytest.skip(f"Test PDF {pdf_path} not found.")

    parser = PDFParserService()
    agent = AgentEngineService()
    risk = RiskEngineService()

    pages = await parser.extract_text_and_coords(pdf_path, "07_High_Termination_Imbalance.pdf")
    analysis_res = await agent.analyze_document_content(pages)
    score_res = risk.calculate_score(analysis_res.clauses)

    # 1. Must remain 2 separate unique risks
    assert len(analysis_res.clauses) == 2, f"Expected 2 unique risks, got {len(analysis_res.clauses)}"

    categories = {c.category for c in analysis_res.clauses}
    assert "Immediate Termination & Notice Period" in categories
    assert "Onerous Automatic Renewal Trap" in categories

    # 2. Score must deduct both distinct legal risks
    assert score_res["score"] == 77, f"Expected score 77, got {score_res['score']}"
    assert score_res["total_penalty"] == 23
    assert score_res["finding_counts"]["HIGH"] == 1
    assert score_res["finding_counts"]["MEDIUM"] == 1
