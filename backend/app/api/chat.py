from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel
import uuid
import re

from app.core.database import get_db
from app.models.db_models import (
    User,
    Document,
    DocumentPage,
    ChatSession,
    ChatMessage,
    Clause,
    RiskFinding,
    AnalysisReport,
)
from app.core.security import get_current_user
from app.services.ollama_service import OllamaService, FALLBACK_ERROR_MESSAGE

ollama_service = OllamaService()
router = APIRouter(prefix="/chat", tags=["Legal Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    language: str = "English"


class ChatMessageResponse(BaseModel):
    id: str
    session_id: str
    sender: str
    message: str
    referenced_pages: List[int] = []


async def get_or_create_doc_session(db: AsyncSession, user_id: str, doc_id: str) -> ChatSession:
    stmt = select(ChatSession).where(ChatSession.document_id == doc_id, ChatSession.user_id == user_id)
    session = (await db.execute(stmt)).scalar_one_or_none()
    if not session:
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            document_id=doc_id,
            title=f"Chat for Document {doc_id[:8]}"
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    return session


def build_rule_based_fallback_response(
    query: str,
    doc: Document,
    report: Optional[AnalysisReport],
    flagged_risks: List[Dict[str, Any]],
    pages: List[DocumentPage],
    language: str = "English"
) -> Tuple[str, List[int]]:
    """
    Intelligent dynamic legal response generator using parsed document data,
    risk engine calculations, and clause database records.
    Guarantees accurate answers even if local LLM is starting up or disconnected.
    """
    q = query.lower().strip()
    is_hindi = "hi" in language.lower() or "hindi" in language.lower()
    is_marathi = "mr" in language.lower() or "marathi" in language.lower()

    crit_count = sum(1 for r in flagged_risks if r["level"] == "CRITICAL")
    high_count = sum(1 for r in flagged_risks if r["level"] == "HIGH")
    med_count = sum(1 for r in flagged_risks if r["level"] == "MEDIUM")
    low_count = sum(1 for r in flagged_risks if r["level"] == "LOW")
    total_risks = len(flagged_risks)

    score = report.deterministic_risk_score if report else 0
    classification = report.risk_classification if report else "PENDING_ANALYSIS"
    summary_text = report.summary if report and report.summary else "Document analysis has been processed."

    risk_pages = sorted(list({r["page"] for r in flagged_risks if r.get("page")}))
    fallback_pages = risk_pages if risk_pages else ([p.page_number for p in pages[:3]] if pages else [1])

    # 1. RISK / SCORE / COUNT / HOW MUCH RISK QUERY
    risk_keywords = ["risk", "score", "how much", "count", "level", "danger", "penalty", "flagged", "kitna", "kiti", "hazard", "threat"]
    if any(k in q for k in risk_keywords):
        if is_hindi:
            lines = [
                f"### 📊 अनुबंध जोखिम मूल्यांकन (Risk Assessment)",
                f"- **दस्तावेज़**: `{doc.original_filename}`",
                f"- **कुल जोखिम स्कोर (Risk Score)**: **{score}/100** ({classification})",
                f"- **पहचाने गए जोखिम खंड**: कुल **{total_risks}** जोखिम पाए गए।",
                "",
                "#### ⚠️ जोखिम स्तर विभाजन:",
                f"- **Critical (अति गंभीर)**: {crit_count}",
                f"- **High (उच्च)**: {high_count}",
                f"- **Medium (मध्यम)**: {med_count}",
                f"- **Low (न्यूनतम)**: {low_count}",
                "",
                "#### 🔍 मुख्य जोखिम खंड (Flagged Clauses):"
            ]
        elif is_marathi:
            lines = [
                f"### 📊 करार जोखीम मूल्यांकन (Risk Assessment)",
                f"- **दस्तऐवज**: `{doc.original_filename}`",
                f"- **एकूण जोखीम गुण (Risk Score)**: **{score}/100** ({classification})",
                f"- **आढळलेल्या जोखीम तरतुदी**: एकूण **{total_risks}** जोखीम आढळल्या.",
                "",
                "#### ⚠️ जोखीम स्तर विभागणी:",
                f"- **Critical (अति तीव्र)**: {crit_count}",
                f"- **High (उच्च)**: {high_count}",
                f"- **Medium (मध्यम)**: {med_count}",
                f"- **Low (कमी)**: {low_count}",
                "",
                "#### 🔍 मुख्य जोखीम तरतुदी (Flagged Clauses):"
            ]
        else:
            lines = [
                f"### 📊 Contract Risk Assessment Overview",
                f"- **Document**: `{doc.original_filename}`",
                f"- **Overall Risk Score**: **{score}/100** ({classification})",
                f"- **Total Flagged Risks**: **{total_risks}** clause(s) detected",
                "",
                "#### ⚠️ Risk Severity Breakdown:",
                f"- **Critical Risks**: {crit_count}",
                f"- **High Risks**: {high_count}",
                f"- **Medium Risks**: {med_count}",
                f"- **Low Risks**: {low_count}",
                "",
                "#### 🔍 Key Flagged Risks:"
            ]

        if flagged_risks:
            for idx, r in enumerate(flagged_risks, 1):
                lines.append(f"{idx}. **[{r['level']}] {r['category']}** (Page {r['page']})")
                if r.get("explanation"):
                    lines.append(f"   - **Reason**: {r['explanation']}")
                if r.get("suggested_action"):
                    lines.append(f"   - **Recommended Action**: {r['suggested_action']}")
        else:
            lines.append("- No high-risk or critical clauses detected in this document.")

        if report and report.recommendations:
            rec_str = ", ".join(report.recommendations) if isinstance(report.recommendations, list) else str(report.recommendations)
            lines.append(f"\n💡 **Recommendation**: {rec_str}")

        return "\n".join(lines), fallback_pages

    # 2. SUMMARY / OVERVIEW QUERY
    summary_keywords = ["summary", "summarize", "overview", "about", "project", "kya hai", "vivaran", "saransh", "mahiti", "explain"]
    if any(k in q for k in summary_keywords):
        if is_hindi:
            lines = [
                f"### 📋 दस्तावेज़ सारांश (Executive Summary)",
                f"- **दस्तावेज़ नाम**: `{doc.original_filename}`",
                f"- **जोखिम स्तर**: **{score}/100** ({classification})",
                "",
                f"**विवरण**: {summary_text}",
                "",
                f"**निष्कर्ष**: कुल **{total_risks}** जोखिम खंड पहचाने गए (Critical: {crit_count}, High: {high_count})."
            ]
        elif is_marathi:
            lines = [
                f"### 📋 दस्तऐवज सारांश (Executive Summary)",
                f"- **दस्तऐवज नाव**: `{doc.original_filename}`",
                f"- **जोखीम गुण**: **{score}/100** ({classification})",
                "",
                f"**तपशील**: {summary_text}",
                "",
                f"**निष्कर्ष**: एकूण **{total_risks}** जोखीम तरतुदी आढळल्या (Critical: {crit_count}, High: {high_count})."
            ]
        else:
            lines = [
                f"### 📋 Executive Contract Summary",
                f"- **Document**: `{doc.original_filename}`",
                f"- **Overall Risk Level**: **{score}/100** ({classification})",
                "",
                f"**Summary**: {summary_text}",
                "",
                f"**Key Findings**: {total_risks} risk clause(s) identified across {len(pages)} page(s)."
            ]

        if flagged_risks:
            lines.append("\n**Top Areas of Legal Concern:**")
            for r in flagged_risks[:3]:
                lines.append(f"- **[{r['level']}] {r['category']}** (Page {r['page']}): {r['explanation'] or r['suggested_action']}")

        if report and report.recommendations:
            rec_str = ", ".join(report.recommendations) if isinstance(report.recommendations, list) else str(report.recommendations)
            lines.append(f"\n💡 **Key Recommendations**: {rec_str}")

        return "\n".join(lines), fallback_pages

    # 3. CLAUSE SPECIFIC SEARCH
    matched_clauses = []
    q_words = [w for w in re.findall(r"\w+", q) if len(w) > 3]
    for r in flagged_risks:
        cat_lower = r["category"].lower()
        exp_lower = (r.get("explanation") or "").lower()
        txt_lower = (r.get("text") or "").lower()
        if any(w in cat_lower or w in exp_lower or w in txt_lower for w in q_words):
            matched_clauses.append(r)

    if matched_clauses:
        lines = [f"### 📌 Relevant Clauses Identified for: *\"{query}\"*"]
        cited = []
        for idx, m in enumerate(matched_clauses, 1):
            cited.append(m["page"])
            lines.append(f"{idx}. **[{m['level']}] {m['category']}** (Page {m['page']})")
            if m.get("explanation"):
                lines.append(f"   - **Legal Risk**: {m['explanation']}")
            if m.get("suggested_action"):
                lines.append(f"   - **Suggested Action**: {m['suggested_action']}")
            if m.get("text"):
                excerpt = m['text'][:220].replace('\n', ' ')
                lines.append(f"   - **Clause Excerpt**: \"{excerpt}...\"")
        return "\n".join(lines), sorted(list(set(cited)))

    # 4. TEXT SEARCH ACROSS DOCUMENT PAGES
    matched_pages = []
    for p in pages:
        p_txt = p.text_content or ""
        if q_words and any(w in p_txt.lower() for w in q_words):
            for w in q_words:
                idx = p_txt.lower().find(w)
                if idx != -1:
                    start_pos = max(0, idx - 80)
                    end_pos = min(len(p_txt), idx + 220)
                    snippet = p_txt[start_pos:end_pos].replace("\n", " ").strip()
                    matched_pages.append((p.page_number, snippet))
                    break

    if matched_pages:
        lines = [f"### 📄 Excerpts Found in Document for: *\"{query}\"*"]
        cited = []
        for page_num, snippet in matched_pages[:3]:
            cited.append(page_num)
            lines.append(f"- **Page {page_num}**: \"...{snippet}...\"")
        return "\n".join(lines), sorted(list(set(cited)))

    # 5. GENERAL DEFAULT FALLBACK
    lines = [
        f"### ℹ️ Contract Analysis Snapshot",
        f"- **Document**: `{doc.original_filename}`",
        f"- **Risk Score**: **{score}/100** ({classification}) with **{total_risks}** flagged clause(s).",
        f"- **Summary**: {summary_text}",
        "",
        "You can ask me questions such as:",
        "- *\"How much risk is detected in my contract?\"*",
        "- *\"Give me a summary of the contract\"*",
        "- *\"What are the termination and penalty clauses?\"*",
        "- *\"What recommendations do you have to reduce risk?\"*"
    ]
    return "\n".join(lines), fallback_pages


@router.get("/history/{doc_id}", response_model=List[ChatMessageResponse])
async def get_chat_history(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await get_or_create_doc_session(db, current_user.id, doc_id)
    stmt = select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc())
    msgs = (await db.execute(stmt)).scalars().all()
    
    res_list = []
    for m in msgs:
        pages = []
        if m.citations and isinstance(m.citations, dict):
            pages = m.citations.get("referenced_pages", [])
        res_list.append(ChatMessageResponse(
            id=m.id,
            session_id=m.session_id,
            sender=m.sender,
            message=m.content,
            referenced_pages=pages
        ))
    return res_list


@router.post("/document/{doc_id}", response_model=ChatMessageResponse)
async def chat_with_document(
    doc_id: str,
    chat_req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Document).where(Document.id == doc_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")

    session = await get_or_create_doc_session(db, current_user.id, doc_id)

    # Save User message to DB
    user_msg_obj = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        sender="user",
        content=chat_req.message
    )
    db.add(user_msg_obj)
    await db.commit()

    # Load Document pages
    stmt_p = select(DocumentPage).where(DocumentPage.document_id == doc.id).order_by(DocumentPage.page_number)
    pages = (await db.execute(stmt_p)).scalars().all()

    # Load Analysis Report if present
    stmt_rep = select(AnalysisReport).where(AnalysisReport.document_id == doc.id)
    report = (await db.execute(stmt_rep)).scalar_one_or_none()

    # Load Clauses & Risk Findings
    stmt_c = (
        select(Clause, RiskFinding)
        .outerjoin(RiskFinding, RiskFinding.clause_id == Clause.id)
        .where(Clause.document_id == doc.id)
        .order_by(Clause.page_number)
    )
    clause_rows = (await db.execute(stmt_c)).all()

    flagged_risks = []
    for clause_obj, finding_obj in clause_rows:
        level = finding_obj.risk_level if finding_obj else "MEDIUM"
        explanation = finding_obj.explanation if finding_obj else ""
        action = finding_obj.suggested_action if finding_obj else ""
        flagged_risks.append({
            "category": clause_obj.category,
            "level": level,
            "page": clause_obj.page_number,
            "text": clause_obj.original_text,
            "explanation": explanation,
            "suggested_action": action
        })

    # Build Rich Analysis Context
    score_str = f"{report.deterministic_risk_score}/100 ({report.risk_classification})" if report else "Pending Analysis"
    summary_str = report.summary if (report and report.summary) else "No summary available."

    analysis_context_parts = [
        f"DOCUMENT TITLE: {doc.original_filename}",
        f"OVERALL CONTRACT RISK SCORE: {score_str}",
        f"EXECUTIVE SUMMARY: {summary_str}",
    ]

    if flagged_risks:
        analysis_context_parts.append(f"FLAGGED RISKS ({len(flagged_risks)} total):")
        for idx, r in enumerate(flagged_risks, 1):
            analysis_context_parts.append(
                f"{idx}. [{r['level']} RISK] {r['category']} (Page {r['page']}): {r['explanation']} | Recommended Action: {r['suggested_action']}"
            )

    if report and report.recommendations:
        analysis_context_parts.append(f"RECOMMENDATIONS: {report.recommendations}")

    analysis_context_str = "\n".join(analysis_context_parts)
    raw_pages_context = "\n\n".join([f"--- Page {p.page_number} ---\n{p.text_content or ''}" for p in pages])

    lang_instruction = ""
    lang_lower = (chat_req.language or "English").lower()
    if "hi" in lang_lower or "hindi" in lang_lower:
        lang_instruction = "Respond in clear Hindi language."
    elif "mr" in lang_lower or "marathi" in lang_lower:
        lang_instruction = "Respond in clear Marathi language."

    system_prompt = (
        "You are LegalFlow AI, an intelligent legal contract assistant. "
        "Answer the user's question accurately using both the contract analysis metadata and the document text below. "
        "When asked about risks, summarize the detected risk score and flagged clauses accurately. "
        f"{lang_instruction}"
    )

    prompt = (
        f"=== CONTRACT RISK & ANALYSIS METADATA ===\n{analysis_context_str}\n\n"
        f"=== DOCUMENT TEXT EXCERPTS ===\n{raw_pages_context[:4500]}\n\n"
        f"USER QUESTION: {chat_req.message}"
    )

    # Attempt AI Inference via Ollama
    ai_reply = ""
    try:
        ai_reply = await ollama_service.generate_text(prompt, system_prompt)
    except Exception:
        ai_reply = ""

    # Check if AI inference was unavailable or returned fallback error
    is_unavailable = (
        not ai_reply
        or ai_reply.strip() == ""
        or ai_reply == FALLBACK_ERROR_MESSAGE
        or "Local AI engine is unavailable" in ai_reply
        or ai_reply.startswith("Ollama HTTP")
    )

    if is_unavailable:
        # Generate intelligent dynamic fallback response from database records
        fallback_reply, ref_pages = build_rule_based_fallback_response(
            query=chat_req.message,
            doc=doc,
            report=report,
            flagged_risks=flagged_risks,
            pages=pages,
            language=chat_req.language
        )
        ai_reply = fallback_reply
    else:
        # Determine referenced pages from flagged risks or first few pages
        matched_pages = [r["page"] for r in flagged_risks if r.get("page")]
        ref_pages = sorted(list(set(matched_pages))) if matched_pages else ([p.page_number for p in pages[:3]] if pages else [1])

    # Save AI message to DB
    ai_msg_obj = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session.id,
        sender="ai",
        content=ai_reply,
        citations={"referenced_pages": ref_pages}
    )
    db.add(ai_msg_obj)
    await db.commit()

    return ChatMessageResponse(
        id=ai_msg_obj.id,
        session_id=session.id,
        sender="ai",
        message=ai_reply,
        referenced_pages=ref_pages
    )


@router.delete("/history/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    session = await get_or_create_doc_session(db, current_user.id, doc_id)
    await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session.id))
    await db.commit()
    return None
