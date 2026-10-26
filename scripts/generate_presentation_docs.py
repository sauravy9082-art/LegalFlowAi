import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

OUT_DIR = r"C:\Users\shiva\.gemini\antigravity\scratch\saurav\legalguard-ai\presentation_documents"
os.makedirs(OUT_DIR, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=15,
    leading=18,
    textColor=colors.HexColor('#102A43'),
    alignment=1, # Center
    spaceAfter=6
)
subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#64748B'),
    alignment=1,
    spaceAfter=12
)
section_heading = ParagraphStyle(
    'SecHead',
    parent=styles['Heading2'],
    fontSize=10,
    leading=13,
    textColor=colors.HexColor('#163A59'),
    spaceBefore=8,
    spaceAfter=4,
    fontName="Helvetica-Bold"
)
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=8.5,
    leading=12,
    textColor=colors.HexColor('#17202A'),
    alignment=4, # Justified
    spaceAfter=5
)
meta_box_style = ParagraphStyle(
    'Meta',
    parent=styles['Normal'],
    fontSize=7.5,
    leading=10,
    textColor=colors.HexColor('#475569')
)

def create_pdf(filename, title, doc_type, effective_date, parties, sections):
    filepath = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    story = []

    # Title & Subtitle
    story.append(Paragraph(title.upper(), title_style))
    story.append(Paragraph(f"CONFIDENTIAL & PROPRIETARY • {doc_type.upper()} • GOVERNED BY COMMERCIAL CODE", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#B58B45'), spaceAfter=10))

    # Meta Table (Parties & Date)
    meta_data = [
        [Paragraph(f"<b>Effective Date:</b> {effective_date}", meta_box_style),
         Paragraph(f"<b>Document Ref:</b> LG-{filename[:6]}-2026", meta_box_style)],
        [Paragraph(f"<b>Party A (Disclosing / Provider):</b> {parties[0]}", meta_box_style),
         Paragraph(f"<b>Party B (Recipient / Customer):</b> {parties[1]}", meta_box_style)]
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F4F1E8')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#D9D6CC')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Preamble
    story.append(Paragraph(
        f"This Master Agreement (this <b>\"Agreement\"</b>) is entered into as of the Effective Date by and between {parties[0]} and {parties[1]}. "
        "The parties, in consideration of the mutual covenants contained herein and other good and valuable consideration, agree to the terms below:",
        body_style
    ))

    # Sections
    for num, heading, text in sections:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"\n\n{num}. {heading.upper()}\n", section_heading))
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 6))

    # Signature Block
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#D9D6CC'), spaceAfter=10))
    sig_data = [
        [Paragraph("<b>AUTHORIZED SIGNATURE (PARTY A):</b>", meta_box_style),
         Paragraph("<b>AUTHORIZED SIGNATURE (PARTY B):</b>", meta_box_style)],
        [Paragraph("<br/><br/>_____________________________________<br/>Name: Arthur Sterling, Esq.<br/>Title: Chief Legal Officer", meta_box_style),
         Paragraph("<br/><br/>_____________________________________<br/>Name: Saurav Verma<br/>Title: Authorized Signatory", meta_box_style)]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(sig_table)

    doc.build(story)
    print(f"Created: {filepath}")

# ==============================================================================
# DOC 1: GREEN (Target: 92/100) - Enterprise AI Platform Master License
# Risks: Dispute Resolution & Onerous Jurisdiction (-8 pts) -> Score: 92
# ==============================================================================
create_pdf(
    filename="01_GREEN_Enterprise_AI_Platform_Master_License.pdf",
    title="Enterprise AI Platform Master License Agreement",
    doc_type="Cloud Software Subscription",
    effective_date="January 15, 2026",
    parties=["Apex Neural Systems Corp. (Delaware)", "Global Enterprise Dynamics LLC"],
    sections=[
        ("1", "Grant of Commercial License",
         "Subject to timely payment of subscription fees, Provider grants Customer a non-exclusive, non-transferable, commercial license during the Term to access the AI API inference engine solely for Customer's internal operational requirements."),
        ("2", "Service Levels & Redundancy",
         "Provider shall use commercially reasonable efforts to maintain a 99.9% Monthly Uptime Percentage. In the event of confirmed service degradation, Customer shall receive proportional fee credits against subsequent renewal invoices as the sole and exclusive financial remedy."),
        ("3", "Mutual Data Protection & Privacy",
         "Customer retains sole ownership and title to all proprietary prompt inputs and query data. Provider shall not use Customer data to train public foundation models without prior written opt-in consent, conforming strictly to ISO 27001 data isolation benchmarks."),
        ("4", "Mutual Liability Cap",
         "Each party's total aggregate liability arising out of or related to this Agreement shall not exceed the total fees actually paid or payable by Customer in the twelve (12) months preceding the incident giving rise to liability."),
        ("5", "Dispute Resolution & Forum Selection",
         "Any controversy, dispute, or claim arising out of or relating to this Agreement shall be litigated exclusively in the state or federal courts of Delaware, and the parties hereby consent to the personal and exclusive jurisdiction of the courts of Delaware.")
    ]
)

# ==============================================================================
# DOC 2: YELLOW (Target: 77/100) - Fintech Payment Gateway Merchant Agreement
# Risks: Asymmetric Liability Limitation (-8 pts) + Immediate Termination (-15 pts) -> Score: 77
# ==============================================================================
create_pdf(
    filename="02_YELLOW_Fintech_Payment_Gateway_Merchant_Agreement.pdf",
    title="Fintech Payment Gateway & Processing Agreement",
    doc_type="Financial Merchant Services Contract",
    effective_date="February 01, 2026",
    parties=["NovaPay Financial Technologies Ltd.", "OmniRetail eCommerce Group Inc."],
    sections=[
        ("1", "Merchant Processing Services",
         "NovaPay agrees to route and settle credit card, debit card, and automated clearing house (ACH) electronic transactions initiated via Merchant's online point-of-sale checkout portals in compliance with PCI-DSS Tier 1 protocols."),
        ("2", "Settlement Reserves & Interchange Fees",
         "Merchant shall pay interchange fees and assessment surcharges per Schedule A. NovaPay shall deposit net settlement batches into Merchant's designated depository account on a rolling T+2 business day settlement schedule."),
        ("3", "Asymmetric Liability Limitation",
         "Merchant agrees that vendor's total aggregate liability under any theory of contract or tort shall be strictly capped at the total processing margins received by NovaPay in the preceding three months, whereas Merchant's liability for indemnified chargebacks and regulatory fines shall be unlimited."),
        ("4", "Immediate Termination Without Cause",
         "NovaPay reserves the right to terminate this agreement immediately without cause and immediately without prior notice upon written notification if Provider determines in its sole discretion that Merchant's processing category introduces reputational exposure."),
        ("5", "Governing Law & Neutral Venue",
         "This Agreement shall be construed in accordance with the laws of the State of New York, and disputes shall be resolved before a mutually agreed neutral arbitration panel in New York City.")
    ]
)

# ==============================================================================
# DOC 3: ORANGE (Target: 52/100) - Pharma Clinical Trial Manufacturing Agreement
# Risks: Unilateral Liability & Indemnity (-25) + Unilateral IP Assignment (-15) + Auto-Renewal Trap (-8) -> Score: 52
# ==============================================================================
create_pdf(
    filename="03_ORANGE_Pharma_Biotech_Clinical_Manufacturing_Agreement.pdf",
    title="Pharmaceutical Clinical Trial Batch Manufacturing Agreement",
    doc_type="Biotechnology Sourcing & CMO Contract",
    effective_date="March 10, 2026",
    parties=["BioVenture Therapeutics Inc.", "Precision Synthesis Contract Manufacturing AG"],
    sections=[
        ("1", "Scope of cGMP Batch Formulation",
         "Manufacturer shall formulate, encapsulate, and package specified investigational batches of therapeutic compound BV-409 in strict adherence to current Good Manufacturing Practice (cGMP) regulations and FDA guidelines."),
        ("2", "Unilateral IP Assignment Prior to Payment",
         "Contractor agrees that all patentable inventions, chemical formulations, analytical testing methods, and technical know-how developed under this engagement shall belong exclusively to Sponsor as work made for hire. Contractor hereby agrees to waive moral rights and execute irrevocable assignment of all IP unconditionally prior to payment of final manufacturing retainers."),
        ("3", "Unilateral Customer Indemnity & Uncapped Liability",
         "Contractor shall defend, indemnify, and hold harmless Sponsor from and against all claims, regulatory sanctions, product liabilities, and third-party damages under all circumstances with uncapped liability, without any monetary ceiling or reciprocal indemnity from Sponsor."),
        ("4", "Onerous Perpetual Auto-Renewal",
         "The initial term of this Agreement shall be twenty-four (24) months and auto-renews annually for successive one-year periods unless Sponsor delivers written non-renewal notice at least 120 days prior notice before the expiration of the current period."),
        ("5", "Audits & Quality Assurance",
         "Sponsor's authorized quality representatives may conduct standard semi-annual inspections of cleanroom manufacturing facilities during regular business hours upon ten (10) business days advance written notice.")
    ]
)

# ==============================================================================
# DOC 4: RED (Target: 27/100) - Aerospace Defense Engineering Subcontract
# Risks: Perpetual Confidentiality (-25) + Global 10-Yr Non-Compete (-25) + 5-Yr Non-Solicitation (-15) + Default Acceleration (-15) -> Score: 20
# ==============================================================================
create_pdf(
    filename="04_RED_Aerospace_Defense_Subcontractor_Agreement.pdf",
    title="Aerospace & Defense Subcontractor Engineering Master Agreement",
    doc_type="Defense Subcontract & Technical Services",
    effective_date="April 05, 2026",
    parties=["Stratosphere Defense Systems Corp.", "AeroVanguard Propulsion Dynamics LLC"],
    sections=[
        ("1", "Technical Defense Subcontracting Scope",
         "Subcontractor shall deliver high-temperature alloy turbine blade computational fluid dynamic (CFD) models and thermal barrier coating specifications per Prime Contract DOD-AF-98210."),
        ("2", "Perpetual Confidentiality Obligations",
         "Subcontractor agrees that all classified designs, telemetry data, and technical specifications disclosed under this Agreement shall remain protected under confidentiality in perpetuity. The obligation to protect proprietary information shall survive the expiration or termination of this Agreement forever."),
        ("3", "Overbroad 10-Year Global Non-Compete",
         "Subcontractor and its key personnel are strictly prohibited from accepting employment, consulting, or engaging with any competing business across the global aviation and aerospace technology sector for a period of 10 years following contract termination."),
        ("4", "Excessive Five-Year Non-Solicitation",
         "Subcontractor covenants that for a period of 5 years following termination, it shall not directly or indirectly solicit any employee, technical specialist, or solicit any customer of Prime Contractor to terminate or alter their commercial relationship."),
        ("5", "Instant Default & Acceleration Without Cure",
         "Prime Contractor reserves the unilateral right to declare instant default without cure period and re-enter premises upon the occurrence of any technical deviation or delivery schedule delay, accelerating all contractual milestone recoupments immediately.")
    ]
)

# ==============================================================================
# DOC 5: CRITICAL RED (Target: 0/100) - Venture-Backed Executive Employment & Severance
# Risks: Claim Waiver (-25) + Liquidated Damages (-25) + Device Surveillance (-25) + Personal Guarantee (-25) + Salary Deduction (-25) -> Score: 0
# ==============================================================================
create_pdf(
    filename="05_CRITICAL_RED_Executive_Employment_and_Severance_Contract.pdf",
    title="Executive Employment, Founder Severance & Restrictive Agreement",
    doc_type="Executive Severance & Restrictive Covenants",
    effective_date="May 01, 2026",
    parties=["HyperScale Ventures Holding Corp.", "Executive Officer (Johnathan Sterling)"],
    sections=[
        ("1", "Executive Appointment & Duties",
         "Executive is appointed to serve as Senior Vice President of Operations and agrees to devote 100% of professional working energies exclusively to the commercial success of the Company."),
        ("2", "Unilateral Release & Broad Claim Waiver",
         "Executive does hereby unconditionally forever release and waive any and all claims, statutory rights, wage demands, severance entitlements, or legal actions of every nature whatsoever, whether currently known or unknown, against the Company and its venture sponsors."),
        ("3", "Unilateral Device Inspection & Surveillance",
         "Company reserves the absolute right to conduct unannounced audit and inspection of Executive's personal phone, personal laptop, and private account at any time without advance notice, to ensure compliance with trade secret protocols."),
        ("4", "Excessive Liquidated Penalty Without Proof",
         "In the event of any alleged breach of intellectual property or non-disclosure provisions, Executive agrees to pay a fixed liquidated penalty of $2,000,000 without requiring proof of actual financial damage or direct economic loss incurred by Company."),
        ("5", "Arbitrary Salary & Compensation Deductions",
         "Company reserves the absolute unilateral right to deduct any amount from monthly compensation, earned bonuses, or final settlement without employee consent to offset perceived operational mistakes or project variances."),
        ("6", "Uncapped Personal Guarantee & Asset Liability",
         "Executive does hereby personally guarantee all commercial leases and banking credit lines of Company in a personal capacity, agreeing that Executive's personal asset portfolio and personal savings shall be personally liable for any corporate balance sheet shortfall.")
    ]
)
print("All 5 presentation PDFs generated successfully!")
