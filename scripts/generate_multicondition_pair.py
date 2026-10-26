import asyncio
import sys
import os
import shutil

sys.path.append(r"C:\Users\shiva\.gemini\antigravity\scratch\saurav\legalguard-ai\backend")
from app.services.comparison_service import ComparisonService
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

out_dir = r"C:\Users\shiva\.gemini\antigravity\scratch\saurav\legalguard-ai\comparison_documents"
artifact_dir = r"C:\Users\shiva\.gemini\antigravity\brain\be12513c-2f03-4589-a9ca-dbdd6b773f8f"

# -------------------------------------------------------------
# CLAUSES DEFINITION
# -------------------------------------------------------------
# Version A (Baseline): 9 clauses
# 1. Scope (Unchanged in B)
# 2. Fees (Modified in B)
# 3. Confidentiality (Unchanged in B)
# 4. Insurance (Removed in B)
# 5. Limitation of Liability (Modified in B)
# 6. Data Security (Removed in B)
# 7. Termination (Modified in B)
# 8. Intellectual Property (Unchanged in B)
# 9. Governing Law (Unchanged in B)

clauses_A = [
    ("1. Scope of Services",
     "Vendor shall provide enterprise cloud architecture consulting and technical implementation services as detailed in each Statement of Work executed by the parties."),
    
    ("2. Fees and Payment Terms",
     "Client shall pay all undisputed invoice amounts within thirty (30) days of receipt of invoice. Late payments shall accrue interest at 1.0 percent per month."),
    
    ("3. Confidentiality and Trade Secrets",
     "Each party shall maintain the confidentiality of the other party proprietary information for a period of three (3) years from the date of disclosure."),
    
    ("4. Insurance Obligations",
     "Vendor shall maintain comprehensive commercial general liability insurance with policy limits of not less than $2,000,000 per occurrence during the entire term."),
    
    ("5. Limitation of Liability",
     "Each party total aggregate liability arising out of or related to this Agreement shall be strictly capped at the total fees paid by Client during the preceding twelve (12) months."),
    
    ("6. Data Security Safeguards",
     "Vendor shall implement SOC2 Type II administrative, physical, and technical safeguards to protect all Client data stored or processed within Vendor systems."),
    
    ("7. Termination for Convenience",
     "Either party may terminate this Agreement without cause by providing at least sixty (60) days prior written notice to the other party."),
    
    ("8. Intellectual Property Ownership",
     "Each party retains sole ownership of its background intellectual property. Client shall own all custom deliverables created specifically under an executed Statement of Work."),
    
    ("9. Governing Law and Dispute Resolution",
     "This Agreement shall be governed by and construed in accordance with the substantive laws of the State of Delaware, without regard to conflict of law principles.")
]

# Version B (Revised):
# Has:
# - UNCHANGED: Scope (1), Confidentiality (3), Intellectual Property (8), Governing Law (9)
# - MODIFIED: Fees (2), Liability (5), Termination (7)
# - REMOVED: Insurance (4), Data Security (6)
# - ADDED: SLA Liquidated Damages (New), Unannounced Facility Audits (New)

clauses_B = [
    ("1. Scope of Services",
     "Vendor shall provide enterprise cloud architecture consulting and technical implementation services as detailed in each Statement of Work executed by the parties."),
    
    ("2. Fees and Payment Terms",
     "Client shall pay all invoice amounts within fifteen (15) days of receipt of invoice. Late payments shall accrue interest at 2.0 percent per month."),
    
    ("3. Confidentiality and Trade Secrets",
     "Each party shall maintain the confidentiality of the other party proprietary information for a period of three (3) years from the date of disclosure."),
    
    ("4. Limitation of Liability",
     "Notwithstanding anything to the contrary, Vendor total aggregate liability for any breach, damages, or claims shall be entirely uncapped and unlimited."),
    
    ("5. Termination for Convenience",
     "Client may terminate this Agreement without cause by providing at least fifteen (15) days prior written notice. Vendor shall have no right to terminate for convenience."),
    
    ("6. Intellectual Property Ownership",
     "Each party retains sole ownership of its background intellectual property. Client shall own all custom deliverables created specifically under an executed Statement of Work."),
    
    ("7. Governing Law and Dispute Resolution",
     "This Agreement shall be governed by and construed in accordance with the substantive laws of the State of Delaware, without regard to conflict of law principles."),
    
    ("8. Service Level Agreement and Liquidated Damages",
     "Vendor guarantees 99.95 percent platform uptime. Vendor shall pay liquidated damages of $25,000 for each failure to meet monthly availability thresholds."),
    
    ("9. Unannounced On-Site Facility Audits",
     "Client and its authorized agents shall have the right to conduct unannounced on-site physical audits of Vendor facilities and inspect records at any time without advance notice.")
]

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'Title',
    parent=styles['Heading1'],
    fontSize=13,
    leading=16,
    textColor=colors.HexColor('#102A43'),
    alignment=1,
    spaceAfter=4
)
subtitle_style = ParagraphStyle(
    'Subtitle',
    parent=styles['Normal'],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#64748B'),
    alignment=1,
    spaceAfter=6
)
badge_style = ParagraphStyle(
    'Badge',
    parent=styles['Normal'],
    fontSize=8.5,
    fontName='Helvetica-Bold',
    alignment=1
)
meta_style = ParagraphStyle(
    'Meta',
    parent=styles['Normal'],
    fontSize=7.2,
    leading=9.5,
    textColor=colors.HexColor('#475569')
)
sec_style = ParagraphStyle(
    'Sec',
    parent=styles['Heading2'],
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor('#163A59'),
    fontName='Helvetica-Bold',
    spaceBefore=5,
    spaceAfter=2
)
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=7.6,
    leading=10.2,
    textColor=colors.HexColor('#17202A'),
    spaceAfter=2
)
sig_title = ParagraphStyle(
    'SigTitle',
    parent=styles['Normal'],
    fontSize=7.5,
    fontName='Helvetica-Bold',
    textColor=colors.HexColor('#1E293B')
)

def make_pdf(filename, title, badge_text, badge_col, doc_status, clauses):
    filepath = os.path.join(out_dir, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=36,
        bottomMargin=36
    )
    story = [
        Paragraph(title.upper(), title_style),
        Paragraph(f"LEGALFLOW AI BENCHMARK • CONTRACT COMPARISON TEST • {filename[:16]}", subtitle_style),
        Spacer(1, 2),
        Table([[Paragraph(f'<font color="{badge_col}"><b>{badge_text.upper()}</b></font>', badge_style)]],
              colWidths=[520],
              style=[
                  ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                  ('BOX', (0,0), (-1,-1), 1, colors.HexColor(badge_col)),
                  ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                  ('TOPPADDING', (0,0), (-1,-1), 3),
                  ('BOTTOMPADDING', (0,0), (-1,-1), 3)
              ]),
        Spacer(1, 6)
    ]

    # Meta Table
    meta_data = [
        [Paragraph("<b>Effective Date:</b> November 15, 2026", meta_style),
         Paragraph(f"<b>Document Status:</b> {doc_status}", meta_style)],
        [Paragraph("<b>Service Provider:</b> Nexus Cloud Solutions LLC", meta_style),
         Paragraph("<b>Enterprise Client:</b> Global Logistics Network Inc.", meta_style)]
    ]
    t_meta = Table(meta_data, colWidths=[260, 260],
                   style=[
                       ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
                       ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                       ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                       ('TOPPADDING', (0,0), (-1,-1), 3),
                       ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                       ('LEFTPADDING', (0,0), (-1,-1), 6),
                       ('RIGHTPADDING', (0,0), (-1,-1), 6)
                   ])
    story.append(t_meta)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=4))

    for h, b in clauses:
        story.append(Paragraph(h, sec_style))
        story.append(Paragraph(b, body_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceBefore=4, spaceAfter=6))

    sig_data = [
        [Paragraph("<b>AUTHORIZED SIGNATURE (PROVIDER)</b>", sig_title),
         Paragraph("<b>AUTHORIZED SIGNATURE (CLIENT)</b>", sig_title)],
        [Paragraph("Signature: __________________________<br/>Name: Jason Reed<br/>Title: Chief Legal Officer", meta_style),
         Paragraph("Signature: __________________________<br/>Name: Catherine Vance<br/>Title: VP, Procurement Operations", meta_style)]
    ]
    t_sig = Table(sig_data, colWidths=[260, 260],
                  style=[
                      ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                      ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
                      ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                      ('TOPPADDING', (0,0), (-1,-1), 4),
                      ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                      ('LEFTPADDING', (0,0), (-1,-1), 6),
                      ('RIGHTPADDING', (0,0), (-1,-1), 6)
                  ])
    story.append(t_sig)

    doc.build(story)
    print(f"Generated: {filename} ({os.path.getsize(filepath)} bytes)")
    shutil.copy2(filepath, os.path.join(artifact_dir, filename))

file_a = "11_MultiCondition_MSA_vA_Original.pdf"
file_b = "12_MultiCondition_MSA_vB_MixedRedline.pdf"

make_pdf(
    file_a,
    "Master Professional Services Agreement",
    "Version A: Baseline Original Draft (9 Clauses)",
    "#1E40AF",
    "Baseline Approved Standard",
    clauses_A
)

make_pdf(
    file_b,
    "Master Professional Services Agreement",
    "Version B: Redline with Added, Removed & Modified Clauses",
    "#DC2626",
    "Client Revised Draft (Mixed Conditions)",
    clauses_B
)

async def run_verification():
    comp = ComparisonService()
    diffs = await comp.compare_two_documents(
        os.path.join(out_dir, file_a),
        os.path.join(out_dir, file_b)
    )
    counts = {"UNCHANGED": 0, "MODIFIED": 0, "ADDED": 0, "REMOVED": 0}
    print("\n--- DETAILED CLAUSE COMPARISON BREAKDOWN ---")
    for d in diffs:
        c_type = d.status or d.change_type
        counts[c_type] = counts.get(c_type, 0) + 1
        print(f"[{c_type:9}] {d.category[:32]:32} | A: {'YES' if d.text_a else '---'} | B: {'YES' if d.text_b else '---'}")

    print("\n==========================================")
    print(f"MODIFIED:  {counts.get('MODIFIED', 0)}")
    print(f"ADDED:     {counts.get('ADDED', 0)}")
    print(f"REMOVED:   {counts.get('REMOVED', 0)}")
    print(f"UNCHANGED: {counts.get('UNCHANGED', 0)}")
    print("==========================================")

asyncio.run(run_verification())
