import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

OUT_DIR = r"C:\Users\shiva\.gemini\antigravity\scratch\saurav\legalguard-ai\comparison_documents"
os.makedirs(OUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=14,
    leading=17,
    textColor=colors.HexColor('#102A43'),
    alignment=1,
    spaceAfter=4
)
subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#64748B'),
    alignment=1,
    spaceAfter=8
)
version_badge_style = ParagraphStyle(
    'Badge',
    parent=styles['Normal'],
    fontSize=9,
    leading=12,
    fontName="Helvetica-Bold",
    alignment=1
)
section_heading = ParagraphStyle(
    'SecHead',
    parent=styles['Heading2'],
    fontSize=9.5,
    leading=12,
    textColor=colors.HexColor('#163A59'),
    spaceBefore=7,
    spaceAfter=3,
    fontName="Helvetica-Bold"
)
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#17202A'),
    alignment=4,
    spaceAfter=4
)
meta_style = ParagraphStyle(
    'Meta',
    parent=styles['Normal'],
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor('#475569')
)

def create_compare_doc(filename, title, version_label, version_color, parties, date_str, clauses):
    filepath = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=40,
        bottomMargin=40
    )
    story = []

    # Title & Version Banner
    story.append(Paragraph(title.upper(), title_style))
    story.append(Paragraph(f"CONTRACT COMPARISON BENCHMARK • LEGALFLOW AI VAULT • REF: {filename[:12]}", subtitle_style))
    
    # Version Banner Box
    v_badge = Paragraph(f"<font color='{version_color}'><b>{version_label.upper()}</b></font>", version_badge_style)
    v_table = Table([[v_badge]], colWidths=[520])
    v_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F1E8')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(version_color)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(v_table)
    story.append(Spacer(1, 8))

    # Parties Metadata Table
    meta_data = [
        [Paragraph(f"<b>Effective Date:</b> {date_str}", meta_style),
         Paragraph(f"<b>Version Status:</b> {version_label}", meta_style)],
        [Paragraph(f"<b>Disclosing / First Party:</b> {parties[0]}", meta_style),
         Paragraph(f"<b>Receiving / Second Party:</b> {parties[1]}", meta_style)]
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#FAFAF9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D6CC')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Preamble
    story.append(Paragraph(
        f"This Agreement is entered into by and between {parties[0]} and {parties[1]} under the mutual covenants and terms outlined in the following sections:",
        body_style
    ))

    # Numbered Clauses
    for num, heading, text in clauses:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"\n\n{num}. {heading}\n", section_heading))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 6))

    # Signatures
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D9D6CC'), spaceAfter=8))
    sig_data = [
        [Paragraph("<b>AUTHORIZED SIGNATORY (PARTY A):</b><br/><br/>_____________________________________<br/>Name: Corporate Counsel", meta_style),
         Paragraph("<b>AUTHORIZED SIGNATORY (PARTY B):</b><br/><br/>_____________________________________<br/>Name: Authorized Representative", meta_style)]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    story.append(sig_table)

    doc.build(story)
    print(f"Generated: {filepath}")

# ==============================================================================
# PAIR 1: SaaS Cloud Subscription Agreement (vA Vendor Baseline vs vB Enterprise Customer Redline)
# ==============================================================================

# 1A: Original Vendor Draft (Balanced / Moderate)
create_compare_doc(
    filename="01_Pair1_SaaS_Enterprise_Agreement_vA_Original.pdf",
    title="Cloud Software as a Service (SaaS) Agreement",
    version_label="Version A — Original Vendor Baseline",
    version_color="#0F766E", # Teal
    parties=["Apex Cloud Technologies Inc.", "Meridian Commercial Systems Ltd."],
    date_str="March 01, 2026",
    clauses=[
        ("1", "Scope of Services",
         "Provider grants Customer a non-exclusive license to access and use the hosted Cloud Analytics Platform during the Subscription Term in accordance with standard documentation."),
        ("2", "Fees and Payment",
         "Customer shall pay monthly subscription fees of $8,500. All invoices shall be paid within thirty (30) days from the invoice date via electronic wire transfer."),
        ("3", "Confidentiality",
         "Each party agrees to safeguard the other party's Confidential Information and not disclose it to third parties for a period of twenty-four (24) months following disclosure."),
        ("4", "Intellectual Property",
         "Provider retains all right, title, and interest in the Cloud Platform and underlying source code. Customer retains all rights to Customer Data submitted into the system."),
        ("5", "Liability & Indemnity",
         "Each party's maximum aggregate liability under this Agreement shall be limited to the total fees paid by Customer during the twelve (12) months preceding the claim."),
        ("6", "Termination",
         "Either party may terminate this Agreement without cause upon sixty (60) days prior written notice, or immediately for material breach uncured within thirty (30) days."),
        ("7", "Renewal",
         "This Agreement shall automatically renew for successive one-year terms unless either party gives written notice of non-renewal at least thirty (30) days prior to the expiration."),
        ("8", "Dispute Resolution",
         "Any dispute arising out of this Agreement shall be resolved through binding arbitration in New York City under the Commercial Arbitration Rules of the American Arbitration Association.")
    ]
)

# 1B: Customer Enterprise Redline (Heavy revisions to Fees, Liability, Data Security, Renewal)
create_compare_doc(
    filename="02_Pair1_SaaS_Enterprise_Agreement_vB_Customer_Redline.pdf",
    title="Cloud Software as a Service (SaaS) Agreement",
    version_label="Version B — Counterparty Customer Redline",
    version_color="#B58B45", # Gold
    parties=["Apex Cloud Technologies Inc.", "Meridian Commercial Systems Ltd."],
    date_str="March 08, 2026",
    clauses=[
        ("1", "Scope of Services",
         "Provider grants Customer an irrevocable, enterprise-wide license to access and use the hosted Cloud Analytics Platform with a guaranteed 99.99% monthly service uptime commitment."),
        ("2", "Fees and Payment",
         "Customer shall pay discounted monthly subscription fees of $6,800. All invoices shall be payable within sixty (60) days from receipt of a verified itemized invoice."),
        ("3", "Confidentiality",
         "Each party agrees to safeguard Confidential Information in strict confidence for a period of sixty (60) months, excluding public domain data and independently derived information."),
        ("4", "Intellectual Property",
         "Provider retains platform IP. Customer retains exclusive title to all Customer Data, generated analytical reports, custom dashboard exports, and derived business intelligence."),
        ("5", "Liability & Indemnity",
         "Provider agrees to defend, indemnify, and hold harmless Customer against all third-party IP infringement claims with uncapped liability, excluding consequential damages."),
        ("6", "Termination",
         "Customer may terminate this Agreement without cause upon thirty (30) days written notice. Provider may terminate only upon ninety (90) days advance notice with full pro-rata fee refunds."),
        ("7", "Renewal",
         "This Agreement shall not renew automatically. Any extension shall require an affirmative written amendment signed by both authorized representatives at least 30 days prior."),
        ("8", "Dispute Resolution",
         "Any dispute arising out of this Agreement shall be resolved through binding arbitration in New York City under the Commercial Arbitration Rules of the American Arbitration Association."),
        ("9", "Data Security",
         "Provider shall maintain annual SOC2 Type II compliance, continuous penetration testing, and 256-bit AES encryption at rest and in transit for all Customer data stored on platform servers.")
    ]
)

# ==============================================================================
# PAIR 2: Master Services Agreement (vA Contractor-Friendly vs vB Corporate Client Strict)
# ==============================================================================

# 2A: Original Contractor Draft
create_compare_doc(
    filename="03_Pair2_Consulting_Services_MSA_vA_Original.pdf",
    title="Master Professional Services Agreement (MSA)",
    version_label="Version A — Original Contractor Baseline",
    version_color="#0F766E",
    parties=["Quantum Digital Solutions LLC (Consultant)", "Vanguard Healthcare Corporation (Client)"],
    date_str="April 10, 2026",
    clauses=[
        ("1", "Scope of Services",
         "Consultant shall perform healthcare data integration, API workflow modernization, and EHR compliance consulting per mutually executed Statements of Work (SOW)."),
        ("2", "Fees and Payment",
         "Client shall pay Consultant a fixed retainer of $150 per hour. Payment is due strictly within fifteen (15) days of invoice date, subject to 1.5% monthly late interest."),
        ("3", "Confidentiality",
         "Both parties agree to treat business methodologies and project specifications as confidential for two (2) years following project completion."),
        ("4", "Intellectual Property",
         "Consultant grants Client a non-exclusive license to use custom project deliverables. Consultant retains full ownership of pre-existing software libraries, developer tools, and proprietary algorithms."),
        ("5", "Liability & Indemnity",
         "Consultant's total aggregate liability arising out of this MSA shall be capped at the total fees paid under the applicable SOW during the preceding three (3) months."),
        ("6", "Termination",
         "Either party may terminate this MSA for convenience upon thirty (30) days prior written notice, provided Client pays all accrued fees through the termination date."),
        ("7", "Dispute Resolution",
         "Disputes shall be settled through mutual executive negotiation, and if unresolved, through binding arbitration in Wilmington, Delaware.")
    ]
)

# 2B: Strict Corporate Client Revision
create_compare_doc(
    filename="04_Pair2_Consulting_Services_MSA_vB_Client_Revised.pdf",
    title="Master Professional Services Agreement (MSA)",
    version_label="Version B — Revised Corporate Client Version",
    version_color="#C62828", # Crimson Red
    parties=["Quantum Digital Solutions LLC (Consultant)", "Vanguard Healthcare Corporation (Client)"],
    date_str="April 18, 2026",
    clauses=[
        ("1", "Scope of Services",
         "Consultant shall perform healthcare data integration, API workflow modernization, and dedicated on-site engineering under strict supervision of Client's Chief Information Officer."),
        ("2", "Fees and Payment",
         "Client shall pay Consultant $125 per hour. Invoices shall be payable within seventy-five (75) days following Client's formal quality acceptance of all milestone deliverables."),
        ("3", "Confidentiality",
         "Consultant agrees to maintain confidentiality in perpetuity for all patient records, hospital data, clinical schemas, and corporate strategic financial plans."),
        ("4", "Intellectual Property",
         "All deliverables, source code, data pipelines, scripts, and documentation developed by Consultant shall be deemed work made for hire and belong exclusively to Client with full waiver of moral rights."),
        ("5", "Liability & Indemnity",
         "Consultant agrees to defend, indemnify, and hold harmless Client from any regulatory violation or security breach with uncapped liability, without any limitation of liability cap."),
        ("6", "Termination",
         "Client may terminate this MSA immediately without cause and without prior notice. Consultant must provide one hundred eighty (180) days written notice prior to termination."),
        ("7", "Dispute Resolution",
         "All disputes shall be litigated exclusively in the state or federal courts located in Chicago, Illinois, and Consultant waives any right to transfer venue."),
        ("8", "Insurance",
         "Consultant shall maintain a minimum of $5,000,000 in Commercial General Liability and $10,000,000 in Cyber Security and Professional Errors & Omissions insurance naming Client as additional insured.")
    ]
)

# ==============================================================================
# PAIR 3: Commercial Real Estate Lease (vA Standard Commercial vs vB Aggressive Landlord Strict)
# ==============================================================================

# 3A: Standard Commercial Lease
create_compare_doc(
    filename="05_Pair3_Commercial_Real_Estate_Lease_vA_Standard.pdf",
    title="Commercial Office Building Master Lease Agreement",
    version_label="Version A — Standard Commercial Baseline",
    version_color="#0F766E",
    parties=["Pacific Horizon Properties LLC (Landlord)", "Apex Global Logistics Inc. (Tenant)"],
    date_str="May 01, 2026",
    clauses=[
        ("1", "Scope of Services",
         "Landlord leases to Tenant Suites 400 and 410 comprising approximately 12,500 rentable square feet located at 500 Financial Plaza for general commercial business office use."),
        ("2", "Fees and Payment",
         "Tenant shall pay monthly Base Rent of $32,000 due on the first day of each calendar month, subject to a 5-day grace period before assessment of a 2% late charge."),
        ("3", "Confidentiality",
         "The financial terms and lease concession allowances of this Agreement shall remain confidential between Landlord, Tenant, and their designated financial advisors."),
        ("4", "Intellectual Property",
         "Tenant retains all ownership and trade secret rights to its proprietary business equipment, signs, trade fixtures, and communication systems installed on the Premises."),
        ("5", "Liability & Indemnity",
         "Each party shall indemnify and defend the other party against third-party bodily injury claims occurring on the Premises to the extent caused by the indemnifying party's negligence."),
        ("6", "Termination",
         "In the event of default, the non-defaulting party shall provide thirty (30) days written notice and opportunity to cure prior to exercising any lease termination remedies."),
        ("7", "Renewal",
         "Tenant shall have the option to renew this Lease for one additional 3-year term by providing written notice to Landlord at least sixty (60) days prior to lease expiration."),
        ("8", "Dispute Resolution",
         "Any controversy or claim arising under this Lease shall be settled by arbitration in accordance with the real estate arbitration rules of the local judicial district.")
    ]
)

# 3B: Landlord Aggressive Redline
create_compare_doc(
    filename="06_Pair3_Commercial_Real_Estate_Lease_vB_Landlord_Strict.pdf",
    title="Commercial Office Building Master Lease Agreement",
    version_label="Version B — Landlord Aggressive Revision",
    version_color="#C62828",
    parties=["Pacific Horizon Properties LLC (Landlord)", "Apex Global Logistics Inc. (Tenant)"],
    date_str="May 09, 2026",
    clauses=[
        ("1", "Scope of Services",
         "Landlord leases to Tenant Suites 400 and 410. Landlord reserves the unilateral right to relocate Tenant to comparable space within the building upon thirty (30) days notice."),
        ("2", "Fees and Payment",
         "Tenant shall pay monthly Base Rent of $36,500 due on the first day of each calendar month. Any payment received after the 2nd day shall incur an immediate 10% penalty fee."),
        ("3", "Confidentiality",
         "Tenant agrees that all lease terms and building operations policies shall remain strictly confidential in perpetuity."),
        ("4", "Intellectual Property",
         "All custom architectural improvements, partitioning, and electrical fixtures installed by Tenant shall immediately become the permanent exclusive property of Landlord."),
        ("5", "Liability & Indemnity",
         "Tenant agrees to defend, indemnify, and hold harmless Landlord against all claims, liabilities, and damages occurring on the property under all circumstances with uncapped liability."),
        ("6", "Termination",
         "Landlord may declare instant default without cure period upon any rent payment delay and accelerate all remaining lease payments for the unexpired term immediately."),
        ("7", "Renewal",
         "This Lease auto-renews annually for successive three-year periods unless Tenant delivers written non-renewal notice at least one hundred twenty (120) days prior notice."),
        ("8", "Dispute Resolution",
         "Disputes shall be litigated exclusively in the state or federal courts of Delaware, and Tenant waives all rights to trial by jury or procedural forum objections."),
        ("9", "Insurance",
         "Tenant shall carry minimum $10,000,000 comprehensive general liability and property damage insurance naming Landlord as primary and non-contributory beneficiary.")
    ]
)

print("All 6 comparison PDFs successfully created in comparison_documents folder!")
