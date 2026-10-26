import pytest
from app.services.risk_engine import RiskEngineService
from app.models.schemas import ClauseSchema, RiskLevelEnum, RiskClassificationEnum

def test_risk_engine_zero_findings():
    svc = RiskEngineService()
    res = svc.calculate_score([])
    assert res["score"] == 100
    assert res["classification"] == RiskClassificationEnum.GREEN.value
    assert res["total_penalty"] == 0

def test_risk_engine_single_low_finding():
    svc = RiskEngineService()
    clause = ClauseSchema(
        category="Privacy",
        page=1,
        original_text="Standard cookie policy notice.",
        risk_level=RiskLevelEnum.LOW,
        explanation="Low risk informative notice.",
        reason="Informative",
        suggested_action="Accept",
        evidence="Standard notice"
    )
    res = svc.calculate_score([clause])
    assert res["score"] == 98
    assert res["classification"] == RiskClassificationEnum.GREEN.value
    assert res["total_penalty"] == 2

def test_risk_engine_multiple_findings_classification():
    svc = RiskEngineService()
    clauses = [
        ClauseSchema(category="Liability", page=1, original_text="Text 1", risk_level=RiskLevelEnum.CRITICAL, explanation="E", reason="R", suggested_action="A", evidence="Ev"), # 25
        ClauseSchema(category="Termination", page=1, original_text="Text 2", risk_level=RiskLevelEnum.HIGH, explanation="E", reason="R", suggested_action="A", evidence="Ev"),    # 15
    ]
    # Total penalty: 40. Score: 60. Classification: YELLOW
    res = svc.calculate_score(clauses)
    assert res["score"] == 60
    assert res["classification"] == RiskClassificationEnum.YELLOW.value
    assert res["total_penalty"] == 40

def test_risk_engine_score_floor_zero():
    svc = RiskEngineService()
    # 5 CRITICAL findings = 5 * 25 = 125 penalty -> max(0, 100 - 125) = 0 score
    clauses = [
        ClauseSchema(category=f"Cat {i}", page=1, original_text="Text", risk_level=RiskLevelEnum.CRITICAL, explanation="E", reason="R", suggested_action="A", evidence="Ev")
        for i in range(5)
    ]
    res = svc.calculate_score(clauses)
    assert res["score"] == 0
    assert res["classification"] == RiskClassificationEnum.RED.value
    assert res["total_penalty"] == 125

def test_risk_engine_deduplicates_same_category_once():
    svc = RiskEngineService()
    # 2 findings under the SAME category ("Unilateral Liability & Indemnity") must deduct score strictly ONCE
    clauses = [
        ClauseSchema(
            category="Unilateral Liability & Indemnity",
            page_number=1,
            original_text="2. Unlimited Liability ...",
            risk_level=RiskLevelEnum.CRITICAL, # 25
            explanation="E",
            reason="R",
            suggested_action="A",
            evidence="2. Unlimited Liability ...",
            occurrence_count=2,
            evidence_occurrences=["2. Unlimited Liability ...", "3. Indemnity ..."]
        ),
        ClauseSchema(
            category="Unilateral Liability & Indemnity",
            page_number=1,
            original_text="3. Indemnity ...",
            risk_level=RiskLevelEnum.CRITICAL, # Duplicate category
            explanation="E",
            reason="R",
            suggested_action="A",
            evidence="3. Indemnity ..."
        )
    ]
    res = svc.calculate_score(clauses)
    # Score must be 100 - 25 = 75, NOT 100 - 50 = 50
    assert res["score"] == 75
    assert res["total_penalty"] == 25
    assert res["finding_counts"]["CRITICAL"] == 1

def test_risk_engine_separate_categories_scored_separately():
    svc = RiskEngineService()
    # PDF 07 case: Termination Imbalance (HIGH) and Automatic Renewal (MEDIUM) are different categories / legal effects
    clauses = [
        ClauseSchema(
            category="Immediate Termination & Notice Period",
            page_number=1,
            original_text="Termination text",
            risk_level=RiskLevelEnum.HIGH, # 15
            explanation="E",
            reason="R",
            suggested_action="A",
            evidence="Termination text"
        ),
        ClauseSchema(
            category="Onerous Automatic Renewal Trap",
            page_number=1,
            original_text="Renewal text",
            risk_level=RiskLevelEnum.MEDIUM, # 8
            explanation="E",
            reason="R",
            suggested_action="A",
            evidence="Renewal text"
        )
    ]
    res = svc.calculate_score(clauses)
    # Score must be 100 - 15 - 8 = 77
    assert res["score"] == 77
    assert res["total_penalty"] == 23
    assert res["finding_counts"]["HIGH"] == 1
    assert res["finding_counts"]["MEDIUM"] == 1
