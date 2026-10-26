import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.db_models import Document, AnalysisReport, Clause, RiskFinding, DocumentPage
from app.services.ollama_service import OllamaService, FALLBACK_ERROR_MESSAGE
from app.services.vector_store import VectorStoreService
from app.api.chat import build_rule_based_fallback_response

logger = logging.getLogger(__name__)
router = APIRouter()

LEGAL_DISCLAIMER_CHAT = "LegalFlow AI provides informational document analysis and does not constitute legal advice."


@router.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    ollama_svc = OllamaService()
    vector_svc = VectorStoreService()

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg_payload = json.loads(raw_data)
                user_query = msg_payload.get("message", "")
                document_id = msg_payload.get("document_id")
                language = msg_payload.get("language", "English")
            except json.JSONDecodeError:
                user_query = raw_data
                document_id = None
                language = "English"

            if not user_query.strip():
                await websocket.send_json({"error": "Empty message."})
                continue

            doc_obj = None
            report_obj = None
            flagged_risks = []
            doc_pages = []
            context_str = ""
            citations = []

            # Retrieve Document & Analysis context if document_id provided
            if document_id:
                async with AsyncSessionLocal() as db:
                    doc_obj = (await db.execute(select(Document).where(Document.id == document_id))).scalar_one_or_none()
                    if doc_obj:
                        report_obj = (await db.execute(select(AnalysisReport).where(AnalysisReport.document_id == document_id))).scalar_one_or_none()
                        stmt_c = (
                            select(Clause, RiskFinding)
                            .outerjoin(RiskFinding, RiskFinding.clause_id == Clause.id)
                            .where(Clause.document_id == document_id)
                            .order_by(Clause.page_number)
                        )
                        c_rows = (await db.execute(stmt_c)).all()
                        for c_clause, c_finding in c_rows:
                            flagged_risks.append({
                                "category": c_clause.category,
                                "level": c_finding.risk_level if c_finding else "MEDIUM",
                                "page": c_clause.page_number,
                                "text": c_clause.original_text,
                                "explanation": c_finding.explanation if c_finding else "",
                                "suggested_action": c_finding.suggested_action if c_finding else ""
                            })

                        stmt_p = select(DocumentPage).where(DocumentPage.document_id == document_id).order_by(DocumentPage.page_number)
                        doc_pages = list((await db.execute(stmt_p)).scalars().all())

                # Search vector store for relevant excerpts
                retrieved_chunks = await vector_svc.search_relevant_context(user_query, document_id=document_id)
                if retrieved_chunks:
                    context_str = "\n".join([f"Excerpt: {c['text']}" for c in retrieved_chunks])
                    citations = [c["metadata"] for c in retrieved_chunks]
                elif doc_pages:
                    context_str = "\n\n".join([f"Page {p.page_number}: {p.text_content[:600]}" for p in doc_pages[:3]])

            # Build enriched system prompt
            score_text = f"{report_obj.deterministic_risk_score}/100 ({report_obj.risk_classification})" if report_obj else "Not yet scored"
            system_prompt = (
                "You are LegalFlow AI, an intelligent legal contract assistant.\n"
                f"Disclaimer: {LEGAL_DISCLAIMER_CHAT}\n"
                "The user may refer to their contract or document as 'my project' or 'this document'.\n"
                f"Overall Contract Risk Score: {score_text}\n"
                "Answer questions strictly based on the provided contract context and analysis findings."
            )

            prompt = (
                f"User Question: {user_query}\n\n"
                f"Contract Context:\n{context_str[:4000]}\n\n"
                f"Language: {language}"
            )

            ai_response = ""
            try:
                ai_response = await ollama_svc.generate_text(prompt, system_prompt=system_prompt)
            except Exception:
                ai_response = ""

            # Check if AI inference failed or returned unavailable message
            is_unavailable = (
                not ai_response
                or ai_response.strip() == ""
                or ai_response == FALLBACK_ERROR_MESSAGE
                or "Local AI engine is unavailable" in ai_response
                or ai_response.startswith("Ollama HTTP")
            )

            if is_unavailable and doc_obj:
                fallback_text, ref_pages = build_rule_based_fallback_response(
                    query=user_query,
                    doc=doc_obj,
                    report=report_obj,
                    flagged_risks=flagged_risks,
                    pages=doc_pages,
                    language=language
                )
                ai_response = fallback_text
                citations = [{"page": p} for p in ref_pages]

            await websocket.send_json({
                "sender": "ASSISTANT",
                "content": ai_response,
                "citations": citations,
                "disclaimer": LEGAL_DISCLAIMER_CHAT
            })

    except WebSocketDisconnect:
        logger.info("WebSocket chat client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except RuntimeError:
            pass
