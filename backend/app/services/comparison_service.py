import os
import re
import difflib
from typing import List, Dict
from app.models.schemas import ClauseDiff
from app.services.pdf_parser import PDFParserService

METADATA_PATTERNS = [
    r"^version\s+[ab][\s—–-].*",
    r"^contract\s+agreement\s+\(version\s+[ab]\)$",
    r"^original\s+baseline.*",
    r"^revised\s+counterparty.*",
    r"^page\s+\d+(\s+of\s+\d+)?$",
    r"^document\s+[ab]$",
    r"^fictional\s+test\s+document.*",
    r"^created\s+only\s+for\s+legalflow.*",
    r"^[a-z\s]+agreement(\s+version\s+[ab])?(\s+[—–-]\s+revised)?$",
    r"^[a-z\s]+contract(\s+version\s+[ab])?(\s+[—–-]\s+revised)?$"
]

COMMON_HEADINGS_MAP = [
    ("Scope of Services", [r"\bscope\b", r"\bservices\b", r"\bdeliverables\b", r"\bduties\b"]),
    ("Fees and Payment", [r"\bfee", r"\bpayment", r"\bcompensation\b", r"\brent\b", r"\binvoice"]),
    ("Confidentiality", [r"\bconfidential", r"\bnon-disclosure\b", r"\bnda\b", r"\bsecret"]),
    ("Intellectual Property", [r"\bintellectual\b", r"\bip\b", r"\bpatent\b", r"\bcopyright\b", r"\btrademark\b", r"\bwork product\b"]),
    ("Liability & Indemnity", [r"\bliabilit", r"\bindemn", r"\bdamage\b", r"\bcap\b", r"\bhold harmless\b"]),
    ("Termination", [r"\bterminat", r"\bcancel", r"\bremoval\b"]),
    ("Renewal", [r"\brenew", r"\bauto-renew", r"\bextension\b"]),
    ("Data Security", [r"\bdata security\b", r"\bcyber\b", r"\bsoc2\b", r"\bsecurity\b"]),
    ("Insurance", [r"\binsurance\b", r"\bcoverage\b", r"\bpolicy\b"]),
    ("Dispute Resolution", [r"\bdispute\b", r"\barbitrat\b", r"\bjurisdict\b", r"\bgoverning law\b", r"\bcourt\b", r"\bvenue\b"])
]

def is_metadata_line(line: str) -> bool:
    clean = line.strip()
    if not clean:
        return True
    for pat in METADATA_PATTERNS:
        if re.match(pat, clean, re.IGNORECASE):
            return True
    return False

def normalize_text(text: str) -> str:
    """Normalize text by lowering, removing punctuation and collapsing whitespace."""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", clean).strip()

def normalize_heading(title: str) -> str:
    """Map clause title to standard legal subject category if possible."""
    clean = title.lower()
    for std_name, patterns in COMMON_HEADINGS_MAP:
        for pat in patterns:
            if re.search(pat, clean):
                return std_name
    
    clean_title = re.sub(r"^[\d\.\s]+", "", title).strip()
    clean_title = re.sub(r"[:\-–—].*", "", clean_title).strip()
    if clean_title and len(clean_title) < 50:
        return clean_title.title()
    return "General Clause"

class ParsedClause:
    def __init__(self, raw_text: str, number: str = "", title: str = ""):
        self.raw_text = raw_text.strip()
        self.number = number.strip()
        self.title = title.strip() if title.strip() else "General Clause"
        self.normalized_subject = normalize_heading(self.title)
        
        # Extract body text excluding heading prefix
        body = self.raw_text
        if self.title and self.title.lower() != "general clause":
            body = re.sub(re.escape(self.title), "", body, flags=re.IGNORECASE).strip()
        self.normalized_body = normalize_text(body if len(body) > 10 else self.raw_text)

class ComparisonService:
    """
    Clause-Aligned Semantic Contract Comparison Engine.
    Accurately identifies MODIFIED, ADDED, REMOVED, and UNCHANGED clauses.
    """

    async def compare_two_documents(self, file_path_a: str, file_path_b: str) -> List[ClauseDiff]:
        raw_a = await self._read_document_text(file_path_a)
        raw_b = await self._read_document_text(file_path_b)

        clauses_a = self._parse_into_clauses(raw_a)
        clauses_b = self._parse_into_clauses(raw_b)

        clause_diffs: List[ClauseDiff] = []
        matched_b_indices = set()

        for a_idx, cl_a in enumerate(clauses_a):
            best_b_idx = None
            best_score = 0.0

            for b_idx, cl_b in enumerate(clauses_b):
                if b_idx in matched_b_indices:
                    continue

                score = self._calculate_clause_alignment_score(cl_a, cl_b)
                if score > best_score:
                    best_score = score
                    best_b_idx = b_idx

            # Alignment Threshold
            if best_b_idx is not None and best_score >= 0.55:
                matched_b_indices.add(best_b_idx)
                cl_b = clauses_b[best_b_idx]
                category = cl_a.normalized_subject if cl_a.normalized_subject != "General Clause" else cl_b.normalized_subject

                norm_body_a = cl_a.normalized_body
                norm_body_b = cl_b.normalized_body

                if norm_body_a == norm_body_b:
                    diff = ClauseDiff(
                        change_type="UNCHANGED",
                        category=category,
                        text_a=cl_a.raw_text,
                        text_b=cl_b.raw_text,
                        semantic_impact="Clause wording and terms remain identical.",
                        reason="Unchanged: Legal obligations and values are identical between versions.",
                        confidence=round(best_score, 2),
                        status="UNCHANGED",
                        version_a=cl_a.raw_text,
                        version_b=cl_b.raw_text
                    )
                    clause_diffs.append(diff)
                else:
                    reason = self._generate_change_reason(cl_a.raw_text, cl_b.raw_text)
                    diff = ClauseDiff(
                        change_type="MODIFIED",
                        category=category,
                        text_a=cl_a.raw_text,
                        text_b=cl_b.raw_text,
                        semantic_impact=reason,
                        reason=reason,
                        confidence=round(best_score, 2),
                        status="MODIFIED",
                        version_a=cl_a.raw_text,
                        version_b=cl_b.raw_text
                    )
                    clause_diffs.append(diff)
            else:
                # Unmatched clause in A is REMOVED
                reason = f"Clause '{cl_a.normalized_subject}' was removed in Version B."
                diff = ClauseDiff(
                    change_type="REMOVED",
                    category=cl_a.normalized_subject,
                    text_a=cl_a.raw_text,
                    text_b=None,
                    semantic_impact=reason,
                    reason=reason,
                    confidence=1.0,
                    status="REMOVED",
                    version_a=cl_a.raw_text,
                    version_b=None
                )
                clause_diffs.append(diff)

        # Any unmatched clause in B is ADDED
        for b_idx, cl_b in enumerate(clauses_b):
            if b_idx not in matched_b_indices:
                reason = f"New clause '{cl_b.normalized_subject}' was inserted into Version B."
                diff = ClauseDiff(
                    change_type="ADDED",
                    category=cl_b.normalized_subject,
                    text_a=None,
                    text_b=cl_b.raw_text,
                    semantic_impact=reason,
                    reason=reason,
                    confidence=1.0,
                    status="ADDED",
                    version_a=None,
                    version_b=cl_b.raw_text
                )
                clause_diffs.append(diff)

        return clause_diffs

    def _calculate_clause_alignment_score(self, cl_a: ParsedClause, cl_b: ParsedClause) -> float:
        """
        Calculates alignment score between two clauses.
        Prevents false matches between different legal subjects.
        """
        # Subject Match
        subj_match = (cl_a.normalized_subject == cl_b.normalized_subject and cl_a.normalized_subject != "General Clause")
        
        # Number Match
        num_match = (cl_a.number and cl_b.number and cl_a.number == cl_b.number)

        # Body Text Similarity
        body_sim = difflib.SequenceMatcher(None, cl_a.normalized_body, cl_b.normalized_body).ratio()

        if subj_match:
            return 0.60 + 0.40 * body_sim
        elif num_match and body_sim > 0.40:
            return 0.50 + 0.50 * body_sim
        else:
            # Different subjects / headings require high body similarity (> 0.60) to match
            return body_sim if body_sim >= 0.60 else 0.0

    def _parse_into_clauses(self, full_text: str) -> List[ParsedClause]:
        """Split document text into clean clauses, stripping metadata noise."""
        lines = [line.strip() for line in full_text.splitlines() if line.strip() and not is_metadata_line(line)]
        cleaned_text = "\n".join(lines)

        # Regex split by numbered clauses or explicit headers
        raw_blocks = re.split(r"\n\s*(?=\d+\.|\bSection\s+\d+|\bClause\s+\d+|[A-Z\s]{3,}:)", cleaned_text)
        if len(raw_blocks) <= 1:
            raw_blocks = re.split(r"\n\s*\n", cleaned_text)

        parsed: List[ParsedClause] = []
        for block in raw_blocks:
            clean_b = block.strip()
            if len(clean_b) < 10 or is_metadata_line(clean_b):
                continue

            num_match = re.match(r"^(\d+(\.\d+)?|\bSection\s+\d+|\bClause\s+\d+)", clean_b, re.IGNORECASE)
            number = num_match.group(0) if num_match else ""

            first_line = clean_b.split("\n")[0].strip()
            heading = re.sub(r"^[\d\.\s]+", "", first_line)
            heading = re.sub(r"[:\-–—].*", "", heading).strip()

            parsed.append(ParsedClause(clean_b, number=number, title=heading))

        return parsed

    def _generate_change_reason(self, text_a: str, text_b: str) -> str:
        """Detect specific monetary, time, notice period, or obligation changes."""
        changes = []

        # Strip clause numbers prefix (e.g. "1. ", "2. ")
        clean_a = re.sub(r"^\s*(\d+(\.\d+)?|\bSection\s+\d+|\bClause\s+\d+)[\.\s:]*", "", text_a, flags=re.IGNORECASE)
        clean_b = re.sub(r"^\s*(\d+(\.\d+)?|\bSection\s+\d+|\bClause\s+\d+)[\.\s:]*", "", text_b, flags=re.IGNORECASE)

        # Check numeric / currency changes
        nums_a = set(re.findall(r"\b(?:₹|\$|USD|INR|EUR|GBP)\s?\d+(?:,\d+)*(?:\.\d+)?\b|\b\d+(?:,\d+)*\s?(?:dollars|rupees|percent|%|lakhs|crores)\b", clean_a, re.IGNORECASE))
        nums_b = set(re.findall(r"\b(?:₹|\$|USD|INR|EUR|GBP)\s?\d+(?:,\d+)*(?:\.\d+)?\b|\b\d+(?:,\d+)*\s?(?:dollars|rupees|percent|%|lakhs|crores)\b", clean_b, re.IGNORECASE))

        diff_a = nums_a - nums_b
        diff_b = nums_b - nums_a

        if diff_a and diff_b:
            changes.append(f"financial/monetary terms changed from '{', '.join(sorted(diff_a))}' to '{', '.join(sorted(diff_b))}'")

        # Check notice period / day changes
        days_a = set(re.findall(r"\b\d+\s+(?:days?|months?|years?)\b", clean_a, re.IGNORECASE))
        days_b = set(re.findall(r"\b\d+\s+(?:days?|months?|years?)\b", clean_b, re.IGNORECASE))

        diff_days_a = days_a - days_b
        diff_days_b = days_b - days_a
        if diff_days_a and diff_days_b:
            changes.append(f"duration/notice terms changed from '{', '.join(sorted(diff_days_a))}' to '{', '.join(sorted(diff_days_b))}'")

        if changes:
            return "Modified: " + "; ".join(changes) + "."
        return "Modified: Legal wording or obligations updated between versions."

    async def _read_document_text(self, input_source: str) -> str:
        """Reads document text from PDF/TXT/DOCX file path or raw string."""
        if not input_source or not isinstance(input_source, str):
            return ""

        if os.path.exists(input_source) and os.path.isfile(input_source):
            ext = os.path.splitext(input_source)[1].lower()
            if ext == ".pdf":
                pdf_parser = PDFParserService()
                pages = await pdf_parser.extract_text_and_coords(input_source, os.path.basename(input_source))
                return "\n".join([p["text"] for p in pages])
            elif ext == ".docx":
                import docx
                doc = docx.Document(input_source)
                return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            else:
                with open(input_source, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()

        return input_source
