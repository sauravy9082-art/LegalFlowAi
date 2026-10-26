from typing import List, Dict, Any
from app.models.schemas import ClauseSchema, RiskLevelEnum, RiskClassificationEnum

PENALTY_WEIGHTS = {
    RiskLevelEnum.CRITICAL: 25,
    RiskLevelEnum.HIGH: 15,
    RiskLevelEnum.MEDIUM: 8,
    RiskLevelEnum.LOW: 2,
    "CRITICAL": 25,
    "HIGH": 15,
    "MEDIUM": 8,
    "LOW": 2
}

class RiskEngineService:
    """
    Deterministic Mathematical Risk Scoring Engine (Rule 21).
    Calculates safety score starting at 100 with weighted deductions.
    The LLM MUST NOT non-deterministically invent the score.
    """

    def calculate_score(self, clauses: List[ClauseSchema]) -> Dict[str, Any]:
        total_penalty = 0
        finding_counts = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        # Score only UNIQUE risks. Evidence occurrences must NOT affect score.
        seen_categories = set()
        for clause in clauses:
            cat = clause.category
            if cat in seen_categories:
                continue
            seen_categories.add(cat)

            level = clause.risk_level
            level_str = level.value if isinstance(level, RiskLevelEnum) else str(level).upper()
            penalty = PENALTY_WEIGHTS.get(level_str, 0)
            total_penalty += penalty
            if level_str in finding_counts:
                finding_counts[level_str] += 1

        final_score = max(0, 100 - total_penalty)
        classification = self.get_classification(final_score)

        return {
            "score": final_score,
            "total_penalty": total_penalty,
            "classification": classification.value,
            "finding_counts": finding_counts
        }

    @staticmethod
    def get_classification(score: int) -> RiskClassificationEnum:
        if score >= 80:
            return RiskClassificationEnum.GREEN
        elif score >= 60:
            return RiskClassificationEnum.YELLOW
        elif score >= 40:
            return RiskClassificationEnum.ORANGE
        else:
            return RiskClassificationEnum.RED

DeterministicRiskEngine = RiskEngineService
