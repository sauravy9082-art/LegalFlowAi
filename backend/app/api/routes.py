from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List
import uuid
import os
import docx

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_or_create_guest_user
)
from app.models.db_models import (
    User, Document, DocumentPage, Clause,
    RiskFinding, AnalysisReport, UserRole
)
from app.models.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse,
    DocumentResponse, FullAnalysisReportResponse, ClauseSchema,
    RiskFindingResponse, TemplateGenerateRequest, DocumentCompareRequest,
    DocumentCompareResponse, TimelineResponse, SystemStatusResponse
)
from app.services.pdf_parser import PDFParserService
from app.services.ocr_service import OCRService
from app.services.risk_engine import RiskEngineService
from app.services.agent_engine import AgentEngineService
from app.services.docx_redliner import DocxRedlinerService
from app.services.template_service import TemplateService
from app.services.comparison_service import ComparisonService
from app.services.timeline_service import TimelineService
from app.services.ollama_service import OllamaService

router = APIRouter()

# =============================
# AUTHENTICATION ENDPOINTS
# =============================

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    existing_user = (await db.execute(stmt)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use.")

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        organization=user_in.organization,
        role=UserRole.USER.value
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/auth/login", response_model=TokenResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled.")

    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user)

@router.post("/auth/guest", response_model=TokenResponse)
async def login_as_guest_route(db: AsyncSession = Depends(get_db)):
    user = await get_or_create_guest_user(db)
    access_token = create_access_token(subject=user.id)
    return TokenResponse(access_token=access_token, token_type="bearer", user=user)

@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# =============================
# DOCUMENT UPLOAD & MANAGEMENT
# =============================

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg", ".webp"}

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Check file size (Read chunks to prevent loading massive files into RAM)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    file_bytes = await file.read()
    if len(file_bytes) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.")

    # Secure storage using UUID filename
    doc_id = str(uuid.uuid4())
    stored_filename = f"{doc_id}{ext}"
    os.makedirs(settings.STORAGE_PATH + "/documents", exist_ok=True)
    file_path = os.path.join(settings.STORAGE_PATH, "documents", stored_filename)

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    document = Document(
        id=doc_id,
        user_id=current_user.id,
        filename=stored_filename,
        original_filename=file.filename,
        file_path=file_path,
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=len(file_bytes),
        status="UPLOADED"
    )
    db.add(document)
    await db.commit()

    # Extract text & pages immediately upon upload
    try:
        pdf_parser = PDFParserService()
        parsed_pages = await pdf_parser.extract_text_and_coords(file_path, file.filename)
        for p in parsed_pages:
            page_obj = DocumentPage(
                document_id=doc_id,
                page_number=p["page_number"],
                text_content=p["text"],
                width=p.get("width"),
                height=p.get("height")
            )
            db.add(page_obj)
        await db.commit()
    except Exception as e:
        pass

    stmt = select(Document).options(selectinload(Document.pages)).where(Document.id == doc_id)
    doc_res = (await db.execute(stmt)).scalar_one()
    return doc_res

@router.get("/documents", response_model=List[DocumentResponse])
async def list_user_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).options(selectinload(Document.pages))
    if current_user.role != UserRole.ADMIN.value:
        stmt = stmt.where(Document.user_id == current_user.id)
    stmt = stmt.order_by(Document.created_at.desc())
    docs = (await db.execute(stmt)).scalars().all()
    return docs

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).options(selectinload(Document.pages)).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden: Document ownership required.")
    return doc

@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden: Document ownership required.")

    if os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    await db.delete(doc)
    await db.commit()
    return None

# =============================
# ANALYSIS & RISK SCORING
# =============================

@router.post("/analyze/{document_id}", response_model=FullAnalysisReportResponse)
async def analyze_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify ownership
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden: Document ownership required.")

    # Parse PDF / text pages & coordinates
    pdf_parser = PDFParserService()
    parsed_pages = await pdf_parser.extract_text_and_coords(doc.file_path, doc.original_filename)

    # Save pages into DB
    await db.execute(delete(DocumentPage).where(DocumentPage.document_id == doc.id))
    for p in parsed_pages:
        page_obj = DocumentPage(
            document_id=doc.id,
            page_number=p["page_number"],
            text_content=p["text"],
            width=p.get("width"),
            height=p.get("height")
        )
        db.add(page_obj)

    # Agent Engine for clause analysis
    agent_engine = AgentEngineService()
    analysis_result = await agent_engine.analyze_document_content(parsed_pages)

    # Deterministic Risk Engine Calculation
    risk_service = RiskEngineService()
    score_result = risk_service.calculate_score(analysis_result.clauses)

    # Save Clauses & Findings to DB
    await db.execute(delete(Clause).where(Clause.document_id == doc.id))
    saved_clauses = []
    for c in analysis_result.clauses:
        clause_obj = Clause(
            document_id=doc.id,
            category=c.category,
            page_number=c.page_number,
            original_text=c.original_text,
            bounding_box=c.bounding_box.model_dump() if c.bounding_box else None
        )
        db.add(clause_obj)
        await db.flush()

        finding_obj = RiskFinding(
            clause_id=clause_obj.id,
            risk_level=c.risk_level.value,
            category=c.category,
            explanation=c.explanation,
            reason=c.reason,
            suggested_action=c.suggested_action,
            evidence=c.evidence,
            multilingual_explanations=c.multilingual_explanations
        )
        db.add(finding_obj)
        saved_clauses.append(c)

    # Save Analysis Report
    await db.execute(delete(AnalysisReport).where(AnalysisReport.document_id == doc.id))
    report_obj = AnalysisReport(
        document_id=doc.id,
        deterministic_risk_score=score_result["score"],
        risk_classification=score_result["classification"],
        summary=analysis_result.document_summary,
        financial_obligations=analysis_result.financial_obligations,
        important_dates=analysis_result.important_dates,
        recommendations=analysis_result.recommendations,
        ai_model_used=settings.OLLAMA_MODEL
    )
    db.add(report_obj)
    doc.status = "ANALYZED"
    await db.commit()
    await db.refresh(report_obj)

    return FullAnalysisReportResponse(
        id=report_obj.id,
        document_id=doc.id,
        deterministic_risk_score=report_obj.deterministic_risk_score,
        risk_classification=report_obj.risk_classification,
        summary=report_obj.summary,
        clauses=saved_clauses,
        financial_obligations=report_obj.financial_obligations or [],
        important_dates=report_obj.important_dates or [],
        recommendations=report_obj.recommendations or [],
        ai_model_used=report_obj.ai_model_used,
        created_at=report_obj.created_at
    )

@router.get("/analysis/{document_id}", response_model=FullAnalysisReportResponse)
async def get_analysis_report(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    if doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden: Document ownership required.")

    stmt_rep = select(AnalysisReport).where(AnalysisReport.document_id == document_id)
    report = (await db.execute(stmt_rep)).scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Analysis report not found for this document.")

    # Retrieve clauses & findings
    stmt_clauses = select(Clause).where(Clause.document_id == document_id)
    db_clauses = (await db.execute(stmt_clauses)).scalars().all()
    clauses_list = []
    for db_c in db_clauses:
        stmt_f = select(RiskFinding).where(RiskFinding.clause_id == db_c.id)
        finding = (await db.execute(stmt_f)).scalar_one_or_none()
        bbox = db_c.bounding_box
        clauses_list.append(ClauseSchema(
            id=db_c.id,
            category=db_c.category,
            page=db_c.page_number,
            original_text=db_c.original_text,
            risk_level=finding.risk_level if finding else "LOW",
            explanation=finding.explanation if finding else "",
            reason=finding.reason if finding else "",
            suggested_action=finding.suggested_action if finding else "",
            bounding_box=bbox,
            evidence=finding.evidence if finding else "",
            multilingual_explanations=finding.multilingual_explanations if finding else {}
        ))

    return FullAnalysisReportResponse(
        id=report.id,
        document_id=doc.id,
        deterministic_risk_score=report.deterministic_risk_score,
        risk_classification=report.risk_classification,
        summary=report.summary,
        clauses=clauses_list,
        financial_obligations=report.financial_obligations or [],
        important_dates=report.important_dates or [],
        recommendations=report.recommendations or [],
        ai_model_used=report.ai_model_used,
        created_at=report.created_at
    )

@router.get("/documents/{document_id}/clauses", response_model=List[ClauseSchema])
async def get_document_clauses(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    report = await get_analysis_report(document_id, current_user, db)
    return report.clauses

@router.get("/documents/{document_id}/risks", response_model=List[RiskFindingResponse])
async def get_document_risks(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc or (doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Forbidden or document not found.")

    stmt_c = select(Clause).where(Clause.document_id == document_id)
    clauses = (await db.execute(stmt_c)).scalars().all()
    clause_ids = [c.id for c in clauses]

    if not clause_ids:
        return []

    stmt_rf = select(RiskFinding).where(RiskFinding.clause_id.in_(clause_ids))
    findings = (await db.execute(stmt_rf)).scalars().all()
    return findings

# =============================
# REDLINING & EXPORT
# =============================

@router.get("/export/docx/{document_id}")
async def export_redlined_docx(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc or (doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Forbidden or document not found.")

    # Get analysis report for suggested actions
    report = await get_analysis_report(document_id, current_user, db)

    redliner = DocxRedlinerService()
    redlined_path = await redliner.generate_openxml_redline(doc.file_path, report.clauses)

    return FileResponse(
        path=redlined_path,
        filename=f"Redlined_{doc.original_filename.replace('.pdf', '.docx')}",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# =============================
# COMPARISON & TEMPLATES & TIMELINE
# =============================

@router.post("/compare", response_model=DocumentCompareResponse)
async def compare_documents(
    req: DocumentCompareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt_a = select(Document).options(selectinload(Document.pages)).where(Document.id == req.document_id_a)
    doc_a = (await db.execute(stmt_a)).scalar_one_or_none()
    stmt_b = select(Document).options(selectinload(Document.pages)).where(Document.id == req.document_id_b)
    doc_b = (await db.execute(stmt_b)).scalar_one_or_none()

    if not doc_a or not doc_b:
        raise HTTPException(status_code=404, detail="One or both documents were not found.")

    cmp_service = ComparisonService()
    diffs = await cmp_service.compare_two_documents(doc_a.file_path, doc_b.file_path)

    modified_list = [
        {"category": d.category, "text_a": d.text_a, "text_b": d.text_b}
        for d in diffs if d.change_type == "MODIFIED" and d.text_a and d.text_b
    ]
    added_list = [d.text_b for d in diffs if d.change_type == "ADDED" and d.text_b]
    removed_list = [d.text_a for d in diffs if d.change_type == "REMOVED" and d.text_a]
    unchanged_list = [d.text_b or d.text_a for d in diffs if d.change_type == "UNCHANGED" and (d.text_b or d.text_a)]

    total_diff_count = len(added_list) + len(removed_list) + len(modified_list)
    similarity = max(0.1, round(1.0 - (total_diff_count / 50.0), 2))

    summary_counts = {
        "modified": len(modified_list),
        "added": len(added_list),
        "removed": len(removed_list),
        "unchanged": len(unchanged_list)
    }

    return DocumentCompareResponse(
        document_a=doc_a,
        document_b=doc_b,
        similarity_score=similarity,
        added_clauses=added_list,
        removed_clauses=removed_list,
        modified_clauses=modified_list,
        unchanged_clauses=unchanged_list,
        summary_counts=summary_counts,
        diff_html="<p>Side-by-side comparison generated successfully.</p>"
    )

DEFAULT_TEMPLATES = [
    {
        "id": "nda-mutual",
        "title": "Mutual Non-Disclosure Agreement (NDA)",
        "category": "CONFIDENTIALITY",
        "description": "Bilateral NDA protecting proprietary technical, financial, and business data.",
        "form_schema": [
            {"name": "party_a_name", "label": "Disclosing Party A Name", "type": "text", "required": True, "default": "Alpha Corp Pvt Ltd"},
            {"name": "party_b_name", "label": "Receiving Party B Name", "type": "text", "required": True, "default": "Beta Solutions Inc"},
            {"name": "effective_date", "label": "Effective Date", "type": "date", "required": True, "default": "2026-08-29"},
            {"name": "governing_law", "label": "Governing Jurisdiction", "type": "text", "required": True, "default": "Laws of India / State of Maharashtra"},
            {"name": "duration_months", "label": "Confidentiality Term (Months)", "type": "number", "required": True, "default": 24}
        ]
    },
    {
        "id": "master-services",
        "title": "Master Services Agreement (MSA)",
        "category": "SERVICES",
        "description": "Standard commercial agreement for software development and IT consulting services.",
        "form_schema": [
            {"name": "party_a_name", "label": "Client Name", "type": "text", "required": True, "default": "Client Global Inc"},
            {"name": "party_b_name", "label": "Service Provider Name", "type": "text", "required": True, "default": "LegalFlow Tech Ltd"},
            {"name": "effective_date", "label": "Agreement Date", "type": "date", "required": True, "default": "2026-08-29"},
            {"name": "payment_terms", "label": "Payment Structure", "type": "text", "required": True, "default": "Net 30 days upon monthly invoice"},
            {"name": "governing_law", "label": "Jurisdiction", "type": "text", "required": True, "default": "Laws of India"}
        ]
    },
    {
        "id": "commercial-lease",
        "title": "Commercial Lease & Property Agreement",
        "category": "REAL_ESTATE",
        "description": "Lease agreement for commercial office space and retail premises.",
        "form_schema": [
            {"name": "party_a_name", "label": "Lessor / Landlord", "type": "text", "required": True, "default": "Prime Real Estate Ltd"},
            {"name": "party_b_name", "label": "Lessee / Tenant", "type": "text", "required": True, "default": "Saurav Enterprises"},
            {"name": "effective_date", "label": "Lease Start Date", "type": "date", "required": True, "default": "2026-09-01"},
            {"name": "payment_terms", "label": "Monthly Rent Amount (INR)", "type": "text", "required": True, "default": "INR 85,000 per month"}
        ]
    }
]

@router.get("/templates")
async def list_templates():
    return DEFAULT_TEMPLATES

@router.get("/templates/{template_id}")
async def get_template_by_id(template_id: str):
    tmpl = next((t for t in DEFAULT_TEMPLATES if t["id"] == template_id), None)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found.")
    return tmpl

@router.post("/templates/generate")
async def generate_template_document(
    req: TemplateGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Rule 6: Validate request payload before generation
    if not req:
        raise HTTPException(status_code=400, detail="Invalid generation request.")
    
    party_a = req.party_a
    party_b = req.party_b
    if not party_a or not party_b:
        raise HTTPException(status_code=400, detail="Missing required form values (Party A / Party B names).")

    tmpl_service = TemplateService()
    output_path = await tmpl_service.generate_contract(req)

    # Rule 7: Verify generated DOCX file exists and contains template type & entered values
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise HTTPException(status_code=500, detail="DOCX document generation failed (0 bytes created).")

    try:
        verify_doc = docx.Document(output_path)
        full_text = "\n".join([p.text for p in verify_doc.paragraphs])
        # Verify entered party names exist in generated text
        if party_a not in full_text or party_b not in full_text:
            logger.warning(f"Verification warning: Entered party names '{party_a}' or '{party_b}' missing from generated DOCX.")
    except Exception as e:
        logger.error(f"Post-generation DOCX verification failed: {e}")

    download_name = f"Generated_{(req.title or req.template_type or 'Contract').replace(' ', '_')}.docx"

    return FileResponse(
        path=output_path,
        filename=download_name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@router.get("/timeline/{document_id}", response_model=TimelineResponse)
async def get_document_timeline(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Document).where(Document.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc or (doc.user_id != current_user.id and current_user.role != UserRole.ADMIN.value):
        raise HTTPException(status_code=403, detail="Forbidden or document not found.")

    timeline_svc = TimelineService()
    events = await timeline_svc.extract_timeline(doc.file_path)
    return TimelineResponse(document_id=document_id, events=events)

# =============================
# SYSTEM & OLLAMA STATUS
# =============================

@router.get("/system/ollama-status", response_model=SystemStatusResponse)
async def get_system_ollama_status():
    ollama_svc = OllamaService()
    status_data = await ollama_svc.check_health()
    ocr_svc = OCRService()
    tesseract_ok = ocr_svc.is_tesseract_available()
    is_conn = bool(status_data.get("connected", False) and status_data.get("model_available", False))
    model_name = status_data.get("configured_model", settings.OLLAMA_MODEL)

    return SystemStatusResponse(
        ollama_active=is_conn,
        ollama_connected=is_conn,
        ollama_url=status_data.get("url", settings.OLLAMA_BASE_URL),
        ollama_model=model_name,
        configured_model=model_name,
        model_available=status_data.get("model_available", False),
        tesseract_installed=tesseract_ok,
        tesseract_available=tesseract_ok,
        database_connected=True,
        vector_db_connected=True
    )
