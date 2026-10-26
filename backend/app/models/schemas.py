from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from enum import Enum

class RiskLevelEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class RiskClassificationEnum(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ORANGE = "ORANGE"
    RED = "RED"

# --- User & Auth Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    organization: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    full_name: Optional[str] = None
    organization: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# --- Document Schemas ---
class BoundingBox(BaseModel):
    xmin: float
    ymin: float
    xmax: float
    ymax: float

class DocumentPageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: int
    text_content: str
    width: Optional[float] = None
    height: Optional[float] = None

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    filename: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
    status: str
    ocr_applied: bool = False
    created_at: datetime
    pages: List[DocumentPageResponse] = []

# --- Risk Finding & Clause Schemas ---
class ClauseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: Optional[str] = None
    category: str
    page_number: int = Field(alias="page", default=1)
    original_text: str
    risk_level: RiskLevelEnum
    explanation: str
    reason: str
    suggested_action: str
    bounding_box: Optional[BoundingBox] = None
    evidence: Optional[str] = ""
    evidence_occurrences: List[str] = Field(default_factory=list)
    occurrence_count: int = 1
    confidence: float = 1.0
    section: Optional[str] = None
    multilingual_explanations: Optional[Dict[str, str]] = None

class RiskFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    analysis_id: Optional[str] = None
    category: str
    risk_level: RiskLevelEnum
    explanation: str
    reason: str
    suggested_action: str

class FullAnalysisReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    deterministic_risk_score: int
    risk_classification: RiskClassificationEnum
    summary: str
    clauses: List[ClauseSchema] = []
    financial_obligations: List[Dict[str, Any]] = []
    important_dates: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    ai_model_used: str
    created_at: datetime
    document: Optional[DocumentResponse] = None

AnalysisReportSchema = FullAnalysisReportResponse

# --- Template Schemas ---
class TemplateGenerateRequest(BaseModel):
    template_id: Optional[str] = "nda-mutual"
    template_type: str = "CONFIDENTIALITY"
    title: Optional[str] = None
    party_a_name: Optional[str] = None
    party_b_name: Optional[str] = None
    effective_date: Optional[str] = "2026-08-29"
    duration_months: Optional[int] = 24
    payment_terms: Optional[str] = None
    governing_law: Optional[str] = "Laws of India"
    custom_terms: Optional[str] = None
    form_data: Optional[Dict[str, Any]] = None

    @property
    def party_a(self) -> str:
        if self.party_a_name:
            return self.party_a_name
        if self.form_data:
            return self.form_data.get("party_a_name") or self.form_data.get("disclosing_party") or self.form_data.get("landlord_name") or self.form_data.get("client_name") or "Party A"
        return "Party A"

    @property
    def party_b(self) -> str:
        if self.party_b_name:
            return self.party_b_name
        if self.form_data:
            return self.form_data.get("party_b_name") or self.form_data.get("receiving_party") or self.form_data.get("tenant_name") or self.form_data.get("freelancer_name") or "Party B"
        return "Party B"

# --- Comparison Schemas ---
class ClauseDiff(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    change_type: str
    category: str
    text_a: Optional[str] = None
    text_b: Optional[str] = None
    semantic_impact: str
    reason: Optional[str] = None
    confidence: float = 1.0
    status: Optional[str] = None
    version_a: Optional[str] = None
    version_b: Optional[str] = None

class DocumentCompareRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    document_id_a: str = Field(alias="doc_a_id")
    document_id_b: str = Field(alias="doc_b_id")

class DocumentCompareResponse(BaseModel):
    document_a: DocumentResponse
    document_b: DocumentResponse
    similarity_score: float
    added_clauses: List[str] = []
    removed_clauses: List[str] = []
    modified_clauses: List[Dict[str, str]] = []
    unchanged_clauses: List[str] = []
    summary_counts: Optional[Dict[str, int]] = None
    diff_html: str

# --- Timeline Schema ---
class TimelineEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    date: str = Field(alias="date_str", default="")
    event_type: str = "MILESTONE"
    description: str = ""
    source_evidence: Optional[str] = None
    page_number: Optional[int] = None

class TimelineResponse(BaseModel):
    document_id: str
    events: List[TimelineEvent] = []

# --- System Status Schema ---
class SystemStatusResponse(BaseModel):
    ollama_active: bool = False
    ollama_connected: bool = False
    ollama_url: Optional[str] = None
    ollama_model: str = "qwen2:latest"
    configured_model: Optional[str] = "qwen2:latest"
    model_available: bool = False
    tesseract_installed: bool = False
    tesseract_available: bool = False
    tesseract_version: Optional[str] = None
    database_connected: bool = True
    vector_db_connected: bool = True
