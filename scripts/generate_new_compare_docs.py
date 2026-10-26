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
    fontSize=13,
    leading=16,
    textColor=colors.HexColor('#102A43'),
    alignment=1,
    spaceAfter=3
)
subtitle_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontSize=8,
    leading=11,
    textColor=colors.HexColor('#64748B'),
    alignment=1,
    spaceAfter=6
)
version_badge_style = ParagraphStyle(
    'Badge',
    parent=styles['Normal'],
    fontSize=8.5,
    leading=11,
    fontName="Helvetica-Bold",
    alignment=1
)
section_heading = ParagraphStyle(
    'SecHead',
    parent=styles['Heading2'],
    fontSize=9,
    leading=12,
    textColor=colors.HexColor('#163A59'),
    spaceBefore=6,
    spaceAfter=2,
    fontName="Helvetica-Bold"
)
body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontSize=7.8,
    leading=10.5,
    textColor=colors.HexColor('#17202A'),
    alignment=4,
    spaceAfter=3
)
meta_style = ParagraphStyle(
    'Meta',
    parent=styles['Normal'],
    fontSize=7.2,
    leading=9.5,
    textColor=colors.HexColor('#475569')
)
sig_title = ParagraphStyle(
    'SigTitle',
    parent=styles['Normal'],
    fontSize=7.5,
    leading=10,
    fontName="Helvetica-Bold",
    textColor=colors.HexColor('#1E293B')
)

def create_compare_doc(filename, title, version_label, version_color, parties, date_str, clauses):
    filepath = os.path.join(OUT_DIR, filename)
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=36,
        bottomMargin=36
    )
    story = []

    # Title & Subtitle
    story.append(Paragraph(title.upper(), title_style))
    story.append(Paragraph(f"LEGALFLOW AI COMPARISON SUITE • REF: {filename[:12]}", subtitle_style))
    
    # Version Banner
    v_badge = Paragraph(f"<font color='{version_color}'><b>{version_label.upper()}</b></font>", version_badge_style)
    v_table = Table([[v_badge]], colWidths=[520])
    v_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor(version_color)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(v_table)
    story.append(Spacer(1, 6))

    # Metadata Table
    meta_data = [
        [Paragraph(f"<b>Effective Date:</b> {date_str}", meta_style),
         Paragraph(f"<b>Document Status:</b> {version_label}", meta_style)],
        [Paragraph(f"<b>Primary Party:</b> {parties[0]}", meta_style),
         Paragraph(f"<b>Counterparty:</b> {parties[1]}", meta_style)]
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=2, spaceAfter=5))

    # Preamble
    preamble = (
        f"This Agreement is entered into as of {date_str}, by and between {parties[0]} "
        f"and {parties[1]}. Both parties covenant and agree to the following legal terms:"
    )
    story.append(Paragraph(preamble, body_style))
    story.append(Spacer(1, 4))

    # Clauses
    for heading, text in clauses:
        story.append(Paragraph(heading, section_heading))
        story.append(Paragraph(text, body_style))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#CBD5E1'), spaceBefore=4, spaceAfter=8))

    # Signature Block
    sig_data = [
        [Paragraph("<b>AUTHORIZED SIGNATURE (PARTY 1)</b>", sig_title),
         Paragraph("<b>AUTHORIZED SIGNATURE (PARTY 2)</b>", sig_title)],
        [Paragraph(f"Signature: __________________________<br/>Name: Arthur Sterling<br/>Title: VP, Legal Counsel<br/>Date: {date_str}", meta_style),
         Paragraph(f"Signature: __________________________<br/>Name: Elena Vance<br/>Title: Chief Operating Officer<br/>Date: {date_str}", meta_style)]
    ]
    sig_table = Table(sig_data, colWidths=[260, 260])
    sig_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sig_table)

    doc.build(story)
    print(f"Generated: {filename} -> {os.path.getsize(filepath)} bytes")

# ==============================================================================
# PAIR 1: CLOUD DATA PROCESSING AGREEMENT (DPA)
# ==============================================================================
# vA: Provider Balanced Standard
# vB: Enterprise Customer Aggressive Redline
# ==============================================================================

pair1_title = "Data Processing Agreement & Information Security Addendum"
pair1_parties = ["StrataCloud Systems Inc. (Data Processor)", "Vanguard Health Technologies Corp. (Data Controller)"]
pair1_date = "November 14, 2026"

clauses_pair1_vA = [
    ("1. Scope and Nature of Processing",
     "Processor agrees to process Customer Personal Data exclusively on documented instructions from Controller, solely as necessary to provide Cloud Analytics Services under the Master Agreement."),
    ("2. Technical and Organizational Measures (TOMs)",
     "Processor shall maintain commercially reasonable administrative, physical, and technical safeguards, including AES-256 encryption at rest and TLS 1.3 in transit, designed to protect personal data against unauthorized disclosure."),
    ("3. Security Breach Notification Window",
     "In the event of a confirmed Personal Data Breach impacting Controller's records, Processor shall notify Controller without undue delay and, where feasible, within seventy-two (72) hours of becoming aware of the confirmed breach."),
    ("4. Sub-processors and Third Parties",
     "Controller grants general written authorization to Processor to engage infrastructure sub-processors. Processor shall provide thirty (30) days prior written notice of any intended changes or additions of sub-processors."),
    ("5. Limitation of Liability and Data Claims",
     "Each party's maximum aggregate cumulative liability arising out of or related to this Data Processing Agreement, including data protection fines and breaches, shall be strictly capped at the total fees paid by Customer during the prior twelve (12) months."),
    ("6. Audit Rights and Security Assessments",
     "Controller may conduct an audit of Processor's compliance no more than once per calendar year upon thirty (30) business days prior written notice. Audits must occur during normal business hours and shall not disrupt live infrastructure."),
    ("7. Indemnification and Defense",
     "Each party shall defend, indemnify, and hold harmless the other party against third-party claims arising from gross negligence or willful misconduct in the handling of Personal Data, subject to the liability limitations in Section 5.")
]

clauses_pair1_vB = [
    ("1. Scope and Nature of Processing",
     "Processor agrees to process Customer Personal Data strictly pursuant to Controller's sole discretion and unilateral written directives, reserving to Controller all ownership and exclusive control over all processing workflows."),
    ("2. Technical and Organizational Measures (TOMs)",
     "Processor shall implement strict SOC2 Type II, ISO 27001, and HIPAA-compliant safeguards, warranting zero unauthorized intrusions, continuous intrusion testing, and zero downtime failover guarantees."),
    ("3. Security Breach Notification Window [MODIFIED]",
     "In the event of any suspected, threatened, or confirmed Personal Data Breach, Processor shall notify Controller immediately in writing, and in no event later than twelve (12) hours after initial suspicion or system anomaly."),
    ("4. Sub-processors and Third Parties [MODIFIED]",
     "Processor is strictly prohibited from engaging or transferring data to any sub-processor without Controller's prior express affirmative written consent for each specific sub-processor."),
    ("5. Limitation of Liability and Data Claims [UNCAPPED REDLINE]",
     "Notwithstanding anything to the contrary in the Master Agreement, Processor's liability for any data breach, confidentiality breach, or privacy regulatory penalty shall be entirely UNCAPPED and exempt from all aggregate liability limitations."),
    ("6. Audit Rights and Security Assessments [EXPANDED REDLINE]",
     "Controller or its designated third-party forensic auditors may conduct unannounced on-site audits and physical data center inspections at any time without prior notice, at Processor's sole cost and expense."),
    ("7. Indemnification and Defense [UNILATERAL REDLINE]",
     "Processor shall unconditionally indemnify, defend, and hold Controller harmless against any and all claims, regulatory fines, customer churn damages, and attorney fees, plus pre-stipulated liquidated damages of $100,000 per breached individual record.")
]

# ==============================================================================
# PAIR 2: EXECUTIVE EMPLOYMENT & INTELLECTUAL PROPERTY AGREEMENT
# ==============================================================================
# vA: Balanced Executive Draft
# vB: Highly Restrictive Company Redline
# ==============================================================================

pair2_title = "Executive Employment & Proprietary Rights Agreement"
pair2_parties = ["Apex AI Robotics Corp. (Company)", "Marcus Sterling (Executive)"]
pair2_date = "December 1, 2026"

clauses_pair2_vA = [
    ("1. Position and Executive Duties",
     "Executive shall serve as Chief Technical Officer (CTO) and shall faithfully perform duties consistent with such senior executive office, subject to the strategic direction of the Board of Directors."),
    ("2. Compensation and Annual Incentive Bonus",
     "Company shall pay Executive an annual base salary of $320,000, payable semi-monthly, plus an annual performance bonus targeted at 35% of base salary based on mutually agreed milestone objectives."),
    ("3. Standard Confidentiality Covenants",
     "Executive agrees to hold all Company Proprietary Information in strict confidence during employment and for a period of two (2) years following separation. Information publicly available shall not constitute proprietary info."),
    ("4. Scope of Non-Competition and Non-Solicitation",
     "During employment and for six (6) months post-termination, Executive shall not directly operate or manage a direct competitor within the same metropolitan territory. Non-solicitation of key technical personnel shall extend for nine (9) months."),
    ("5. Intellectual Property and Inventions Assignment",
     "Executive assigns to Company all inventions, software, and discoveries created during company working hours or directly utilizing Company proprietary resources and directly related to Company's autonomous robotics line."),
    ("6. Termination Without Cause and Severance Package",
     "In the event of termination without Cause, Company shall pay Executive ninety (90) days of continuation base salary, accrued milestone bonus pro-rated, and three (3) months of continued health insurance coverage."),
    ("7. Governing Law and Mutual Dispute Resolution",
     "This Agreement shall be governed by Delaware law. Any unresolved dispute shall be submitted to confidential binding arbitration before a single JAMS arbitrator in Wilmington, Delaware.")
]

clauses_pair2_vB = [
    ("1. Position and Executive Duties",
     "Executive shall serve as CTO at the absolute pleasure of the Board, which reserves the right to demote, alter job titles, or assign arbitrary duties without Executive consent or constructive discharge claims."),
    ("2. Compensation and Annual Incentive Bonus",
     "Company shall pay Executive an annual base salary of $320,000. All bonus incentives, equity vests, and commission awards remain at the sole, unreviewable discretion of the Board and may be rescinded retroactively."),
    ("3. Standard Confidentiality Covenants",
     "Executive covenants to maintain perpetual confidentiality over all Company concepts, workflows, code, and customer records forever without expiration or temporal limitation."),
    ("4. Scope of Non-Competition and Non-Solicitation [AGGRESSIVE REDLINE]",
     "For twenty-four (24) months following termination for any reason, Executive is strictly barred worldwide from engaging in, advising, investing in, or consulting for any technology, software, or artificial intelligence business."),
    ("5. Intellectual Property and Inventions Assignment [EXPANDED REDLINE]",
     "Executive irrevocably assigns to Company all inventions, concepts, code, and patentable ideas conceived or developed by Executive at ANY time, including weekends, off-duty hours, and on personal devices, regardless of relatedness to Company business."),
    ("6. Termination Without Cause and Severance Package [ZERO SEVERANCE]",
     "Company may terminate Executive at any time without cause upon immediate written notice with ZERO (0) severance pay, immediate forfeiture of all unvested stock options, and no continuation benefits."),
    ("7. Governing Law and Mutual Dispute Resolution [ONE-WAY REDLINE]",
     "Delaware law governs. Company may seek immediate ex parte injunctive relief and $50,000 liquidated damages per covenant violation, whereas Executive waives all rights to jury trial, class action, and punitive damages.")
]

if __name__ == "__main__":
    create_compare_doc(
        filename="07_Pair1_Cloud_DPA_vA_Provider_Standard.pdf",
        title=pair1_title,
        version_label="Version A: Provider Standard Baseline",
        version_color="#1E3A8A",
        parties=pair1_parties,
        date_str=pair1_date,
        clauses=clauses_pair1_vA
    )

    create_compare_doc(
        filename="08_Pair1_Cloud_DPA_vB_Customer_Aggressive.pdf",
        title=pair1_title,
        version_label="Version B: Enterprise Customer Redline (Uncapped Liability)",
        version_color="#B91C1C",
        parties=pair1_parties,
        date_str=pair1_date,
        clauses=clauses_pair1_vB
    )

    create_compare_doc(
        filename="09_Pair2_Executive_Employment_vA_Balanced.pdf",
        title=pair2_title,
        version_label="Version A: Balanced Executive Baseline",
        version_color="#0D9488",
        parties=pair2_parties,
        date_str=pair2_date,
        clauses=clauses_pair2_vA
    )

    create_compare_doc(
        filename="10_Pair2_Executive_Employment_vB_Company_Restrictive.pdf",
        title=pair2_title,
        version_label="Version B: Company Restrictive Redline (Worldwide Non-Compete)",
        version_color="#DC2626",
        parties=pair2_parties,
        date_str=pair2_date,
        clauses=clauses_pair2_vB
    )

    print("\nAll 4 comparison documents successfully generated in:")
    print(OUT_DIR)
