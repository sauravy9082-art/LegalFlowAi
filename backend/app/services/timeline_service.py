import re
import os
from typing import List
from app.models.schemas import TimelineEvent
from app.services.pdf_parser import PDFParserService

DATE_PATTERNS = [
    (r"\b(?:\d{1,2}[-/th|st|nd|rd]*\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b", "Specific Milestone Date"),
    (r"\b\d{4}-\d{2}-\d{2}\b", "ISO Date Format"),
    (r"\b(?:within\s+\d+\s+days|30\s+days|60\s+days|90\s+days)\b", "Notice / Deadline Period")
]

class TimelineService:
    """
    Timeline Extractor Engine (Rule 28).
    Extracts actual contract dates and milestones with source evidence.
    Never invents fictitious dates.
    """

    async def extract_timeline(self, file_path: str) -> List[TimelineEvent]:
        pdf_parser = PDFParserService()
        pages = await pdf_parser.extract_text_and_coords(file_path, os.path.basename(file_path))

        events: List[TimelineEvent] = []

        for p in pages:
            page_num = p["page_number"]
            text = p["text"]

            for pat, event_type in DATE_PATTERNS:
                matches = re.finditer(pat, text, re.IGNORECASE)
                for m in matches:
                    date_str = m.group(0)
                    start_idx = max(0, m.start() - 50)
                    end_idx = min(len(text), m.end() + 50)
                    snippet = text[start_idx:end_idx].replace("\n", " ").strip()

                    events.append(TimelineEvent(
                        date_str=date_str,
                        event_type=event_type,
                        description=f"Contract milestone event referenced on Page {page_num}.",
                        source_evidence=snippet,
                        page_number=page_num
                    ))

        return events[:15]
