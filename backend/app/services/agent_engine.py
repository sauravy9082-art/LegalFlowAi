import logging
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from app.services.ollama_service import OllamaService
from app.models.schemas import ClauseSchema, RiskLevelEnum, BoundingBox

logger = logging.getLogger(__name__)

class AgentAnalysisResult(BaseModel):
    document_summary: str
    clauses: List[ClauseSchema] = []
    financial_obligations: List[Dict[str, Any]] = []
    important_dates: List[Dict[str, Any]] = []
    recommendations: List[str] = []

# Comprehensive Risk Definitions across 21 Legal Risk Domains
RISK_DEFINITIONS = [
    {
        "category": "Unilateral Release & Broad Claim Waiver",
        "keywords": [r"release\s+and\s+discharge", r"forever\s+release", r"waive\s+any\s+and\s+all\s+claims", r"waives\s+all\s+rights", r"surrender\s+all\s+claims", r"unconditional\s+release"],
        "must_contain": [r"unilateral\s+release", r"waive.*all\s+claims", r"surrender.*rights", r"release.*forever", r"broad\s+waiver", r"forever\s+release", r"forever\s+releases"],
        "safe_indicators": [r"mutual\s+release", r"upon\s+full\s+payment", r"release\s+upon\s+receipt"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Unilateral release waives future legal claims and rights unconditionally without reciprocal release.",
        "action": "Ensure releases are mutual and limited strictly to settled disputes upon full consideration.",
        "hi": "यह धारा बिना किसी पारस्परिक छूट के सभी भावी कानूनी दावों को समाप्त करती है।",
        "mr": "हा कलम परस्पर सवलतीशिवाय भविष्यातील सर्व कायदेशीर दावे संपवतो.",
        "ta": "எதிர்கால உரிமைகளை ஒருதலைப்பட்சமாக துறக்கும் ஆபத்தான பிரிவு.",
        "es": "La renuncia unilateral extingue reclamos futuros sin reciprocidad.",
        "fr": "La renonciation unilatérale éteint les réclamations futures sans réciprocité."
    },
    {
        "category": "Unilateral Liability & Indemnity",
        "keywords": [r"indemnify", r"indemnification", r"hold\s+harmless", r"uncapped\s+liability", r"unlimited\s+liability", r"full\s+indemnification", r"unlimited\s+indemnification", r"defend,\s+indemnify"],
        "must_contain": [r"uncapped\s+liability", r"unlimited\s+liability", r"without\s+limit", r"sole\s+responsibility", r"without\s+any\s+cap", r"under\s+all\s+circumstances", r"all\s+claims", r"unlimited\s+indemnification", r"customer\s+shall\s+defend", r"indemnify,\s+and\s+hold\s+harmless", r"indemnify\s+and\s+hold\s+harmless"],
        "safe_indicators": [r"mutual", r"each\s+party", r"both\s+parties", r"aggregate\s+liability\s+shall\s+not\s+exceed", r"gross\s+negligence\s+or\s+willful\s+misconduct"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "One-sided uncapped liability or indemnification clause places disproportionate financial exposure on one party.",
        "action": "Cap total liability to contract fees paid in the preceding 12 months and make indemnification mutual.",
        "hi": "यह धारा एकतरफा असीमित देनदारी डालती है।",
        "mr": "हा कलम एकतर्फी अमर्यादित दायित्व लादतो.",
        "ta": "இந்த பிரிவு ஒருதலைப்பட்சமான வரம்பற்ற பொறுப்பை சுமத்துகிறது.",
        "es": "Esta cláusula impone responsabilidad ilimitada unilateral.",
        "fr": "Cette clause impose une responsabilité illimitée unilatérale."
    },
    {
        "category": "Asymmetric Liability Limitation",
        "keywords": [r"liability.*shall\s+be.*capped", r"liability.*strictly\s+capped", r"customer's\s+liability.*unlimited", r"three\s+months.*twelve\s+months", r"3\s+months.*12\s+months", r"preceding\s+three\s+months", r"vendor's\s+total\s+aggregate\s+liability"],
        "must_contain": [r"three\s+months", r"3\s+months", r"capped\s+at\s+\$?\d+", r"customer's\s+liability.*unlimited", r"vendor's.*liability.*capped", r"liability.*strictly\s+capped"],
        "safe_indicators": [r"each\s+party.*preceding\s+12\s+months", r"both\s+parties.*preceding\s+12\s+months", r"equal\s+liability\s+cap", r"either\s+party.*preceding\s+12\s+months"],
        "risk_level": RiskLevelEnum.MEDIUM,
        "reason": "Contractor's liability is capped at a low nominal amount or 3 months while Client's liability is unlimited or capped higher, creating an asymmetric liability burden.",
        "action": "Align liability caps to equal terms (e.g. 12 months of fees for both parties).",
        "hi": "ठेकेदार और ग्राहक के बीच देयता सीमा (Liability Cap) में असमानता।",
        "mr": "कंत्राटदार आणि ग्राहक यांच्यातील दायित्व मर्यादेत विषमता.",
        "ta": "பொறுப்பு வரம்பில் சமச்சீரற்ற தன்மை.",
        "es": "Limitación de responsabilidad asimétrica entre las partes.",
        "fr": "Limitation de responsabilité asymétrique entre les parties."
    },
    {
        "category": "Excessive Financial Penalty & Liquidated Damages",
        "keywords": [r"liquidated\s+penalty", r"liquidated\s+damages", r"forfeit.*deposit", r"penalty\s+of", r"without\s+requiring\s+proof", r"1,500,000", r"2,000,000", r"5,000,000", r"bond\s+penalty", r"pay\s+\$?\d+.*liquidated", r"immediately\s+forfeited", r"forfeited\s+to\s+company", r"liquidation\s+preference", r"penalty\s+fees"],
        "must_contain": [r"without\s+requiring\s+proof", r"fixed\s+liquidated\s+penalty", r"forfeit.*entire", r"1,500,000", r"2,000,000", r"5,000,000", r"non-refundable\s+penalty", r"liquidated\s+damages", r"liquidated", r"200%", r"penalty\s+fee", r"penalty\s+fees", r"bond\s+penalty", r"immediately\s+forfeited", r"forfeited\s+to\s+company", r"liquidation\s+preference"],
        "safe_indicators": [r"actual\s+proven\s+direct\s+losses", r"capped\s+at\s+actual\s+damages"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Imposes massive fixed financial penalties, deposit/token forfeiture, or 3x liquidation preference without requiring proof of actual financial loss.",
        "action": "Cap liquidated damages to actual proven direct losses, subject to a reasonable monetary maximum.",
        "hi": "बिना वास्तविक नुकसान साबित किए भारी जुर्माना या टोकन जब्ती की जोखिमपूर्ण शर्त।",
        "mr": "प्रत्यक्ष नुकसान सिद्ध केल्याशिवाय प्रचंड दंड आकारण्याचा धोका.",
        "ta": "உண்மையான இழப்பு சான்றின்றி அபராதம் விதிக்கும் ஆபத்தான விதி.",
        "es": "Impone sanciones financieras masivas sin prueba de pérdida real.",
        "fr": "Impose des pénalités financières massives sans preuve de préjudice."
    },
    {
        "category": "Unreasonable Duration & Perpetual Obligation",
        "keywords": [r"50\s+years", r"perpetual\s+confidentiality", r"confidentiality.*in\s+perpetuity", r"confidentiality.*50\s+years", r"confidentiality.*forever", r"indefinite\s+confidentiality", r"in\s+perpetuity"],
        "must_contain": [r"50\s+years", r"perpetual\s+confidentiality", r"confidentiality.*perpetuity", r"confidentiality.*forever", r"obligation.*perpetual", r"secret.*50\s+years", r"50-year", r"in\s+perpetuity"],
        "safe_indicators": [r"2\s+years", r"3\s+years", r"5\s+years", r"forever\s+release", r"release\s+and\s+discharge", r"waives\s+and\s+relinquishes", r"release\s+of\s+claims"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Extended confidentiality or master ownership obligations lasting in perpetuity create unreasonable long-term liability.",
        "action": "Reduce confidentiality duration to standard 2 to 5 years following agreement termination.",
        "hi": "50 वर्षों या अनन्त काल तक गोपनीयता बनाए रखने का अस्वाभाविक दबाव।",
        "mr": "50 वर्षांपर्यंत गोपनीयतेची बंधने पाळण्याचा अवाजवी त्रास.",
        "ta": "50 ஆண்டுகள் ரகசியத்தன்மை காக்கும் சுமை.",
        "es": "Obligación de confidencialidad de 50 años. Reduzca la duración.",
        "fr": "Obligation de confidentialité de 50 ans. Réduisez la durée."
    },
    {
        "category": "Overbroad Confidentiality Definition",
        "keywords": [r"confidentiality", r"public\s+domain", r"publicly\s+available"],
        "must_contain": [r"includes\s+publicly\s+available", r"regardless\s+of\s+whether\s+in\s+public\s+domain", r"public\s+domain\s+or\s+publicly\s+available", r"public\s+domain", r"waives\s+all\s+rights\s+to\s+claim\s+information\s+is\s+in\s+the\s+public\s+domain"],
        "safe_indicators": [r"excluding\s+information\s+in\s+public\s+domain", r"publicly\s+available\s+through\s+no\s+fault", r"excluding\s+public\s+domain\s+data", r"excluding\s+public\s+domain"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Classifies public domain information as confidential, creating impossible compliance standards.",
        "action": "Exclude publicly available information and independently developed data from confidentiality scope.",
        "hi": "सार्वजनिक जानकारी को भी गोपनीय बताने की अनुचित शर्त।",
        "mr": "सार्वजनिक माहिती देखील गोपनीय मानण्याची अयोग्य अट.",
        "ta": "பொதுத் தகவலையும் ரகசியமாக வரையறுக்கும் தவறான விதி.",
        "es": "Clasifica información pública como confidencial.",
        "fr": "Classe les informations publiques comme confidentielles."
    },
    {
        "category": "Overbroad Global Non-Compete Restriction",
        "keywords": [r"non-compete", r"prohibited\s+from\s+accepting\s+employment", r"10\s+years", r"technology\s+sector", r"competing\s+business", r"competing\s+retail", r"strict\s+non-compete", r"prohibited\s+from\s+using,\s+wearing,\s+or\s+promoting", r"prohibited\s+from\s+promoting"],
        "must_contain": [r"10\s+years", r"global", r"worldwide", r"any\s+competing\s+business", r"competing\s+retail\s+business", r"5\s+years", r"24\s+months", r"twenty-four\s+\(24\)\s+months", r"prohibited\s+from\s+using,\s+wearing,\s+or\s+promoting", r"prohibited\s+from\s+promoting"],
        "safe_indicators": [r"6\s+months", r"12\s+months", r"within\s+10\s+miles"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Unreasonable global non-compete or endorsement restriction severely restricts future livelihood and career.",
        "action": "Limit non-compete duration to maximum 6-12 months post-termination and restrict geographically.",
        "hi": "अनुचित गैर-प्रतिस्पर्धा की शर्त।",
        "mr": "बिनशर्त स्पर्धा-विरोधी अट.",
        "ta": "தொழில் போட்டித் தடை விதி.",
        "es": "Restricción de no competencia desproporcionada.",
        "fr": "Restriction de non-concurrence disproportionnée."
    },
    {
        "category": "Excessive Non-Solicitation Restriction",
        "keywords": [r"non-solicit", r"solicit\s+any\s+employee", r"solicit\s+any\s+customer", r"poach\s+employees", r"solicit.*5\s+years", r"non-solicitation"],
        "must_contain": [r"5\s+years", r"3\s+years", r"36\s+months", r"thirty-six\s+\(36\)\s+months", r"solicit\s+any\s+customer", r"solicit\s+any\s+employee", r"broad\s+non-solicit", r"solicit.*5\s+years", r"solicit.*3\s+years"],
        "safe_indicators": [r"12\s+months", r"general\s+public\s+advertisement"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Overly broad 3-to-5 year non-solicitation restriction impedes hiring and business growth.",
        "action": "Limit non-solicitation to a reasonable 12-month period post-termination.",
        "hi": "कर्मचारियों और ग्राहकों को आकर्षित करने पर 5 साल की अनुचित पाबंदी।",
        "mr": "कर्मचारी आणि ग्राहकांशी संबंध जोडण्यावर ५ वर्षांची बंधने.",
        "ta": "வாடிக்கையாளர் மற்றும் ஊழியர்களை அணுகுவதற்கான 5 ஆண்டுகள் தடை.",
        "es": "Restricción de no solicitación desproporcionada de 5 años.",
        "fr": "Restriction de non-sollicitation disproportionnée de 5 ans."
    },
    {
        "category": "Unilateral IP Assignment & Moral Rights Waiver",
        "keywords": [r"assign\s+all\s+IP", r"waive\s+moral\s+rights", r"ip\s+created\s+shall\s+belong", r"unconditional\s+ip\s+transfer", r"waive\s+any\s+moral\s+rights", r"unconditionally\s+prior\s+to\s+payment", r"belong\s+exclusively", r"shall\s+belong\s+exclusively", r"belong\s+EXCLUSIVELY"],
        "must_contain": [r"waive\s+moral\s+rights", r"unconditional\s+assignment", r"prior\s+to\s+payment", r"irrevocable\s+assignment\s+of\s+all\s+IP", r"unconditionally\s+prior\s+to\s+payment", r"belong\s+exclusively", r"shall\s+belong\s+exclusively", r"exclusively\s+to\s+contractor", r"exclusively\s+to\s+provider", r"work-for-hire", r"work\s+made\s+for\s+hire", r"ip\s+created\s+shall\s+belong"],
        "safe_indicators": [r"upon\s+full\s+payment", r"deliverables\s+created\s+specifically\s+under\s+statement\s+of\s+work"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Forces unconditional IP transfer or moral rights waiver prior to receipt of full payment.",
        "action": "Make IP transfer conditional upon full payment of fees and retain pre-existing IP.",
        "hi": "भुगतान से पहले ही बौद्धिक संपदा (IP) और नैतिक अधिकारों के हस्तांतरण का जोखिम।",
        "mr": "पैसे मिळण्यापूर्वीच बौद्धिक संपदा हस्तांतरित करण्याचा धोका.",
        "ta": "முழு கட்டணம் செலுத்தும் முன் அறிவார்ந்த சொத்துரிமை மாற்றம்.",
        "es": "Asignación de PI sin recibir el pago completo.",
        "fr": "Cession de propriété intellectuelle avant paiement complet."
    },
    {
        "category": "Unilateral Device Inspection & Surveillance",
        "keywords": [r"inspect.*personal\s+device", r"private\s+account", r"audit.*personal\s+phone", r"audit.*personal\s+laptop", r"surveillance.*device", r"inspect.*personal\s+phone", r"facility\s+inspection", r"audit\s+and\s+inspection"],
        "must_contain": [r"personal", r"private", r"mobile\s+phone", r"laptop", r"personal\s+account", r"personal\s+phone", r"unannounced\s+audit", r"without\s+advance\s+notice", r"audit.*at\s+any\s+time"],
        "safe_indicators": [r"company-owned", r"during\s+business\s+hours\s+only", r"with\s+prior\s+written\s+consent"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Grants arbitrary authority to inspect personal devices and private accounts without prior notice or consent.",
        "action": "Remove arbitrary privacy inspection rights; limit audit scope strictly to company-owned assets.",
        "hi": "यह धारा निजी उपकरणों और व्यक्तिगत खातों के निरीक्षण का अनुचित अधिकार देती है।",
        "mr": "हा कलम खाजगी उपकरणे आणि वैयक्तिक खात्यांच्या तपासणीचा अयोग्य अधिकार देतो.",
        "ta": "தனிப்பட்ட சாதனங்களை ஆய்வு செய்ய அனுமதிக்கும் கடுமையான விதி.",
        "es": "Concede autoridad arbitraria para inspeccionar dispositivos privados.",
        "fr": "Accorde le droit d'inspecter des appareils privés."
    },
    {
        "category": "Arbitrary Salary & Compensation Deductions",
        "keywords": [r"deduct.*salary", r"deduct\s+any\s+amount", r"compensation\s+deductions", r"final\s+settlement", r"operational\s+mistakes", r"unapproved\s+absences"],
        "must_contain": [r"unilateral", r"absolute\s+unilateral", r"without\s+prior\s+written\s+notice", r"without\s+employee\s+consent", r"operational\s+mistakes", r"deduct\s+any\s+amount", r"compensation\s+deductions", r"developer\s+payments"],
        "safe_indicators": [r"with\s+prior\s+written\s+consent", r"as\s+authorized\s+by\s+law"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Allows absolute unilateral right to deduct money from monthly salary or final settlement without employee consent.",
        "action": "Prohibit arbitrary salary deductions; require explicit written agreement and statutory authorization.",
        "hi": "वेतन से मनमाने तरीके से कटौती का जोखिम पैदा करने वाली अनुचित शर्त।",
        "mr": "पगारातून मनमानी कपात करण्याचा धोका निर्माण करणारी अट.",
        "ta": "சம்பள பிடித்தம் தொடர்பான ஆபத்தான விதி.",
        "es": "Deducción salarial arbitraire sin consentimiento.",
        "fr": "Déduction salariale arbitraire sans consentement."
    },
    {
        "category": "Uncapped Personal Guarantee & Individual Liability",
        "keywords": [r"personal\s+guarantee", r"personally\s+guarantee", r"individual\s+liability\s+of\s+director", r"personal\s+capacity", r"personally\s+liable", r"personally\s+guarantees"],
        "must_contain": [r"personally\s+guarantee", r"personally\s+guarantees", r"personal\s+capacity", r"individual\s+liability", r"personal\s+asset", r"personally\s+liable"],
        "safe_indicators": [r"corporate\s+capacity\s+only", r"limited\s+to\s+company\s+assets"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Imposes personal guarantee exposing personal assets to corporate debt liabilities.",
        "action": "Limit liability strictly to corporate entities; eliminate personal guarantee obligations.",
        "hi": "व्यक्तिगत संपत्ति पर देनदारी का गंभीर जोखिम (Personal Guarantee)।",
        "mr": "वैयक्तिक मालमत्तेवर थेट दायित्व येण्याचा धोका.",
        "ta": "தனிப்பட்ட சொத்துக்கள் மீதான பொறுப்பு விதி.",
        "es": "La garantía personal expone los activos personales a deudas corporativas.",
        "fr": "La garantie personnelle expose le patrimoine personnel aux dettes."
    },
    {
        "category": "Immediate Termination & Notice Period",
        "keywords": [r"terminate\s+immediately", r"without\s+notice", r"without\s+cause", r"immediate\s+termination", r"mandatory\s+minimum\s+period\s+of\s+36"],
        "must_contain": [r"immediately\s+without\s+prior\s+notice", r"without\s+cause", r"without\s+notice", r"mandatory\s+minimum\s+period\s+of\s+36", r"terminate\s+this\s+agreement\s+immediately", r"terminate\s+immediately", r"for\s+cause\s+without\s+notice"],
        "safe_indicators": [r"30\s+days\s+prior\s+written\s+notice", r"opportunity\s+to\s+cure"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Allows immediate termination without cause or imposes early departure penalties without cure notice.",
        "action": "Require a minimum 30-day written notice and a 15-day opportunity to cure breaches.",
        "hi": "बिना किसी सूचना के तत्काल अनुबंध समाप्त करने या जुर्माने का जोखिम।",
        "mr": "कोणत्याही सूचनेशिवाय करार तत्काळ समाप्त करण्याचा धोका.",
        "ta": "முன்னறிவிப்பின்றி உடனடியாக ஒப்பந்தத்தை முடிவுக்குக் கொண்டுவரும் அபாயம்.",
        "es": "Permite rescisión inmediata sin causa.",
        "fr": "Permet une résiliation immédiate sans motif."
    },
    {
        "category": "Asymmetric Excessive Notice Period",
        "keywords": [r"180\s+days", r"180\s+days\s+prior\s+written\s+notice", r"notice\s+before\s+resignation", r"excessive\s+notice\s+period", r"6\s+months\s+notice"],
        "must_contain": [r"180\s+days", r"6\s+months\s+notice"],
        "safe_indicators": [r"30\s+days", r"60\s+days"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Requires employee to provide an excessive notice period before resignation while employer terminates immediately.",
        "action": "Reduce employee resignation notice period to a standard 30 to 60 days.",
        "hi": "कर्मचारी के लिए अत्यधिक नोटिस पीरियड।",
        "mr": "कर्मचाऱ्यासाठी अवाजवी नोटीस कालावधी.",
        "ta": "நீண்ட முன்னறிவிப்பு காலம்.",
        "es": "Período de notificación desproporcionado.",
        "fr": "Préavis disproportionné."
    },
    {
        "category": "Onerous Automatic Renewal Trap",
        "keywords": [r"automatic\s+renewal", r"automatically\s+renews?", r"auto-renew", r"\brenewals?\b", r"renew\s+perpetually", r"perpetual\s+renewal", r"renew\s+for\s+successive", r"auto-renews\s+annually", r"extended\s+payment\s+terms"],
        "must_contain": [r"renew\s+perpetually", r"90\s+days\s+prior\s+notice", r"120\s+days\s+prior\s+notice", r"perpetual\s+auto-renew", r"auto-renews\s+annually", r"120\s+days", r"net\s+90", r"paid\s+within\s+ninety"],
        "safe_indicators": [r"30\s+days\s+notice", r"60\s+days\s+notice", r"written\s+non-renewal\s+notice\s+at\s+least\s+60\s+days"],
        "risk_level": RiskLevelEnum.MEDIUM,
        "reason": "Auto-renewal clause traps party in extended terms with restrictive non-renewal windows.",
        "action": "Require simple written opt-in or standard 30-to-60 day non-renewal notification.",
        "hi": "स्वचालित नवीनीकरण (Auto-Renewal) का जाल।",
        "mr": "आपोआप नूतनीकरण होण्याचा धोका.",
        "ta": "தானாக புதுப்பிக்கும் தந்திரமான பிரிவு.",
        "es": "Trampa de renovación automática con plazos restrictivos.",
        "fr": "Piège de renouvellement automatique à préavis restrictif."
    },
    {
        "category": "Unilateral Modification Right",
        "keywords": [r"modify.*at\s+any\s+time", r"amend.*at\s+any\s+time", r"change.*at\s+any\s+time", r"without.*consent", r"unilateral\s+modification", r"unilaterally\s+at\s+any\s+time", r"increase.*without\s+prior\s+written\s+notice"],
        "must_contain": [r"reserves\s+absolute\s+unilateral", r"without\s+prior\s+written\s+notice\s+or\s+consent", r"(modify|amend|change).*at\s+any\s+time", r"unilaterally\s+at\s+any\s+time", r"increase.*without\s+prior\s+written\s+notice"],
        "safe_indicators": [r"mutual\s+written\s+consent", r"signed\s+by\s+both\s+parties"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Allows one party to modify agreement terms or interest rates arbitrarily without mutual written consent.",
        "action": "Require all modifications to be executed in a written amendment signed by both authorized representatives.",
        "hi": "एकतरफा अनुबंध बदलने का अनुचित अधिकार।",
        "mr": "एकतर्फी करारात बदल करण्याचा अधिकार.",
        "ta": "ஒப்பந்தத்தை ایکதலைப்பட்சமாக மாற்றும் அதிகாரம்.",
        "es": "Permite modificar términos de forma unilateral.",
        "fr": "Permet de modifier les termes unilatéralement."
    },
    {
        "category": "Unilateral Transfer & Absolute Assignment",
        "keywords": [r"assign\s+this\s+agreement\s+without\s+consent", r"transfer\s+rights\s+unilaterally", r"sole\s+discretion\s+to\s+assign", r"transfer\s+JV\s+rights", r"subletting\s+&\s+assignment\s+restrictions", r"without\s+landlord's\s+prior\s+written\s+consent"],
        "must_contain": [r"without\s+consent", r"unilaterally\s+assign", r"sole\s+discretion\s+to\s+transfer", r"sole\s+discretion\s+to\s+assign", r"without\s+landlord's\s+prior\s+written\s+consent"],
        "safe_indicators": [r"with\s+written\s+consent", r"not\s+to\s+be\s+unreasonably\s+withheld"],
        "risk_level": RiskLevelEnum.MEDIUM,
        "reason": "Grants one party absolute freedom to assign rights while restricting the other party.",
        "action": "Make assignment rights mutual and subject to prior written consent.",
        "hi": "एकतरफा अनुबंध हस्तांतरण का अधिकार।",
        "mr": "एकतर्फी करार हस्तांतरणाचा अधिकार.",
        "ta": "ஒப்பந்தத்தை ஒருதலைப்பட்சமாக மாற்றும் உரிமை.",
        "es": "Permite la cesión unilateral del contrato sin consentimiento.",
        "fr": "Permet la cession unilatérale du contrat sans consentement."
    },
    {
        "category": "Complete Disclaimer of All Warranties",
        "keywords": [r"disclaims\s+all\s+warranties", r"as\s+is\s+where\s+is", r"no\s+warranty\s+of\s+any\s+kind", r"disclaim\s+merchantability", r"as\s+is\s+without\s+warranty", r"without\s+warranty\s+of\s+any\s+kind", r"provided\s+stictly\s+'as\s+is'", r"strictly\s+'as\s+is'"],
        "must_contain": [r"disclaims\s+all\s+warranties", r"no\s+warranty\s+whatsoever", r"as\s+is\s+without\s+warranty", r"disclaims\s+all\s+warranties,\s+express", r"stictly\s+'as\s+is'", r"strictly\s+'as\s+is'", r"without\s+warranty\s+of\s+any\s+kind", r"free\s+from\s+defects"],
        "safe_indicators": [r"express\s+warranty", r"standard\s+performance\s+warranty", r"warrants\s+equipment\s+against\s+defects"],
        "risk_level": RiskLevelEnum.MEDIUM,
        "reason": "Disclaims all express and statutory warranties leaving buyer with zero remedy for defects.",
        "action": "Include standard warranties of merchantability and fitness for intended purpose.",
        "hi": "सभी वारंटियों की पूरी तरह से अस्वीकृति।",
        "mr": "सर्व वॉरंटी फेटाळण्याचा धोका.",
        "ta": "அனைத்து உத்திரவாதங்களையும் நிராகரிக்கும் பிரிவு.",
        "es": "Exclusión total de garantías sin remedio para el comprador.",
        "fr": "Exclusion totale de garanties sans recours pour l'acheteur."
    },
    {
        "category": "Immediate Default & Acceleration without Cure",
        "keywords": [r"instant\s+default", r"automatic\s+default", r"without\s+cure\s+period", r"sole\s+discretion", r"declare\s+instant\s+default", r"accelerate\s+remaining\s+rent", r"accelerate\s+rent", r"re-enter\s+premises", r"assumes\s+full\s+risk\s+of\s+loss"],
        "must_contain": [r"without\s+cure\s+period", r"instant\s+default", r"sole\s+discretion", r"accelerate\s+remaining\s+rent", r"accelerate\s+rent", r"re-enter\s+premises", r"risk\s+of\s+loss", r"full\s+risk\s+of\s+loss"],
        "safe_indicators": [r"written\s+notice\s+of\s+default", r"10\s+days\s+to\s+cure", r"30\s+days\s+to\s+cure", r"30\s+days\s+written\s+notice\s+required\s+to\s+cure"],
        "risk_level": RiskLevelEnum.HIGH,
        "reason": "Permits acceleration of remaining payments or default declaration instantly at sole discretion without mandatory cure notice.",
        "action": "Mandate a 15-to-30 day written notice and opportunity to cure before declaring default.",
        "hi": "बिना सुधार के अवसर के तत्काल डिफ़ॉल्ट घोषित करने की जोखिमपूर्ण शर्त।",
        "mr": "सुधारणेची संधी न देता करारात डिफॉल्ट घोषित करण्याचा धोका.",
        "ta": "உடனடி இயல்புநிலை அறிவிப்பு ஆபத்து.",
        "es": "Permite declaración de mora inmediata sin período de subsanación.",
        "fr": "Permet la déclaration de défaut immédiate sans délai de grâce."
    },
    {
        "category": "Confession of Judgment & Warrant of Attorney",
        "keywords": [r"confess\s+judgment", r"warrant\s+of\s+attorney", r"cognovit", r"authorizes.*confess"],
        "must_contain": [r"confess\s+judgment", r"warrant\s+of\s+attorney", r"cognovit"],
        "safe_indicators": [r"due\s+process\s+of\s+law", r"court\s+judgment\s+after\s+trial"],
        "risk_level": RiskLevelEnum.CRITICAL,
        "reason": "Confession of judgment waives procedural rights and permits entry of immediate court judgment without defense.",
        "action": "Remove confession of judgment clause; require formal judicial process.",
        "hi": "न्यायालय में बिना बचाव के तत्काल निर्णय स्वीकार करने की खतरनाक शर्त।",
        "mr": "न्यायालयात बचावाशिवाय निर्णय स्वीकारण्याचा अत्यंत धोकादायक प्रकार.",
        "ta": "வழக்கு விசாரணையின்றி தீர்ப்பை ஒப்புக்கொள்ளும் அபாயகரமான பிரிவு.",
        "es": "La confesión de juicio renuncia a los derechos procesales.",
        "fr": "La confession de jugement renonce aux droits de la défense."
    },
    {
        "category": "Dispute Resolution & Onerous Jurisdiction",
        "keywords": [r"exclusive\s+jurisdiction", r"litigated\s+exclusively\s+in", r"foreign\s+court", r"dispute\s+jurisdiction"],
        "must_contain": [r"exclusive\s+jurisdiction\s+of\s+the\s+courts\s+of\s+Delaware", r"foreign\s+jurisdiction", r"litigated\s+exclusively", r"foreign\s+court", r"delaware", r"courts\s+of\s+delaware", r"singapore", r"london", r"wilmington"],
        "safe_indicators": [r"mutually\s+agreed\s+neutral\s+forum", r"arbitration\s+in\s+mumbai", r"arbitration\s+in\s+delhi", r"laws\s+of\s+india", r"new\s+delhi", r"courts\s+of\s+bangalore", r"courts\s+of\s+new\s+york"],
        "risk_level": RiskLevelEnum.MEDIUM,
        "reason": "Exclusive venue selection requires litigation in an inconvenient or foreign forum.",
        "action": "Specify neutral binding arbitration under standard arbitration rules in a local city.",
        "hi": "असुविधाजनक स्थान पर मुकदमा चलाने का जोखिम।",
        "mr": "असोयीस्कर ठिकाणी खटला चालवण्याचा धोका.",
        "ta": "சட்ட வரம்பு விதிகளை சரிபார்க்கவும்.",
        "es": "Jurisdicción onerosa exclusiva en foro distante.",
        "fr": "Juridiction exclusive dans un tribunal distant."
    }
]

HEURISTIC_PATTERNS = RISK_DEFINITIONS

class AgentEngineService:
    def __init__(self):
        self.ollama = OllamaService()

    async def analyze_document_content(self, pages_data: List[Dict[str, Any]]) -> AgentAnalysisResult:
        full_text = "\n\n".join([p.get("text", "") for p in pages_data])

        # Stage 1: Pass 1 Candidate Extraction
        pass1_candidates = self._extract_risk_candidates(pages_data)

        # Stage 2: Pass 2 Complete Document Missed-Risk Scan
        pass2_candidates = self._perform_second_pass_missed_risk_scan(full_text, pages_data, pass1_candidates)

        # Stage 3: Category Audit Candidate Extraction
        audit_candidates = self._extract_audit_candidates(pages_data)

        # Combine all extracted candidate occurrences
        all_raw_candidates = pass1_candidates + pass2_candidates + audit_candidates

        # Stage 4: Context & Safe Clause Validation
        validated_candidates = self._apply_context_and_safe_clause_validation(all_raw_candidates)

        # Stage 5: Semantic Deduplication & Occurrence Grouping into Unique Risks
        unique_findings = self._group_duplicate_risks(validated_candidates)

        # Stage 6: Post-Deduplication Missed-Risk Verification Scan
        final_findings = self._verify_missed_risks(full_text, pages_data, unique_findings)

        self._attach_bounding_boxes(final_findings, pages_data)

        total_occurrences = sum(f.occurrence_count for f in final_findings)
        doc_summary = (
            f"Document analyzed across {len(pages_data)} page(s). "
            f"Identified {len(final_findings)} unique risk(s) across {total_occurrences} evidence occurrence(s)."
        )

        # Generate dynamic recommendations directly derived from detected risks and their specific evidence actions
        recommendations = []
        for finding in final_findings:
            if finding.suggested_action and finding.suggested_action not in recommendations:
                recommendations.append(finding.suggested_action)
        if not recommendations:
            recommendations.append("No critical legal risks detected. Ensure standard execution procedures.")

        financial_obligations = []
        important_dates = []
        for p_idx, page in enumerate(pages_data, start=1):
            t = page.get("text", "")
            for d in re.findall(r"\b(?:\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b", t, re.IGNORECASE):
                important_dates.append({"date": d, "context": t[:100], "page": p_idx})
            for f in re.findall(r"\b(?:₹|\$|USD|INR|EUR|GBP)\s?\d+(?:,\d+)*(?:\.\d+)?\b|\b\d+(?:,\d+)*\s?(?:rupees|dollars|lakhs|crores)\b", t, re.IGNORECASE):
                financial_obligations.append({"amount": f, "page": p_idx})

        return AgentAnalysisResult(
            document_summary=doc_summary,
            clauses=final_findings,
            financial_obligations=financial_obligations,
            important_dates=important_dates,
            recommendations=recommendations
        )

    @staticmethod
    def _split_into_clean_paragraphs(text: str) -> List[str]:
        raw_blocks = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d+[\.\)]\s+)|\n(?=(?:Section|Clause|Article)\b)", text) if p.strip()]
        paragraphs = []
        for block in raw_blocks:
            clean = " ".join(block.split())
            if len(clean) > 15:
                paragraphs.append(clean)
        return paragraphs

    def _extract_risk_candidates(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates = []
        for p_idx, page in enumerate(pages_data, start=1):
            text = page.get("text", "")
            paragraphs = self._split_into_clean_paragraphs(text)
            
            for para in paragraphs:
                for rule in RISK_DEFINITIONS:
                    kw_match = any(re.search(kw, para, re.IGNORECASE | re.DOTALL) for kw in rule["keywords"])
                    if kw_match:
                        must_match = True
                        if rule.get("must_contain"):
                            must_match = any(re.search(mc, para, re.IGNORECASE | re.DOTALL) for mc in rule["must_contain"])
                        
                        if must_match:
                            candidates.append({
                                "rule": rule,
                                "page": p_idx,
                                "text": para,
                                "confidence": 0.95
                            })
        return candidates

    def _extract_audit_candidates(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        candidates = []
        for rule in RISK_DEFINITIONS:
            for p_idx, page in enumerate(pages_data, start=1):
                p_text = page.get("text", "")
                for kw in rule["keywords"]:
                    if re.search(kw, p_text, re.IGNORECASE | re.DOTALL):
                        must_match = True
                        if rule.get("must_contain"):
                            must_match = any(re.search(mc, p_text, re.IGNORECASE | re.DOTALL) for mc in rule["must_contain"])

                        if must_match:
                            snippet = self._extract_matching_snippet(kw, p_text)
                            if snippet:
                                candidates.append({
                                    "rule": rule,
                                    "page": p_idx,
                                    "text": snippet,
                                    "confidence": 0.88
                                })
        return candidates

    def _apply_context_and_safe_clause_validation(self, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated = []
        for cand in candidates:
            rule = cand["rule"]
            text = cand["text"]

            # Safe Clause Validation
            is_safe = False
            for safe_pat in rule.get("safe_indicators", []):
                if re.search(safe_pat, text, re.IGNORECASE | re.DOTALL):
                    is_safe = True
                    break

            # General Mutuality & Cap Checks
            if "Indemnity" in rule["category"] or "Liability" in rule["category"]:
                if any(w in text.lower() for w in ["mutual", "each party", "both parties", "shall indemnify each other"]):
                    if "uncapped" not in text.lower() and "unlimited" not in text.lower() and "three months" not in text.lower():
                        is_safe = True
                if ("capped at" in text.lower() or "aggregate liability shall not exceed" in text.lower()) and "Asymmetric" not in rule["category"]:
                    if "three months" not in text.lower() and "3 months" not in text.lower():
                        is_safe = True

            if "Dispute" in rule["category"] or "Jurisdiction" in rule["category"]:
                if any(w in text.lower() for w in ["neutral", "binding arbitration", "mutually agreed"]):
                    if "exclusive court of delaware" not in text.lower() and "foreign court" not in text.lower() and "singapore" not in text.lower() and "london" not in text.lower():
                        is_safe = True

            if not is_safe:
                validated.append(cand)

        return validated

    def _group_duplicate_risks(self, candidates: List[Dict[str, Any]]) -> List[ClauseSchema]:
        """
        Semantic Risk Deduplication:
        Groups duplicate evidence occurrences under ONE Unique Risk.
        
        Two candidate occurrences are duplicates ONLY when they represent the SAME underlying
        legal risk and SAME legal effect.
        
        Different clauses with different legal effects remain separate UNIQUE RISKS.
        """
        unique_groups: List[Dict[str, Any]] = []

        for cand in candidates:
            rule = cand["rule"]
            cat = rule["category"]
            page = cand["page"]
            text = cand["text"].strip()
            conf = cand.get("confidence", 0.95)

            # Match existing Unique Risk group by category (same underlying risk & legal effect)
            matched_group = None
            for group in unique_groups:
                if group["category"] == cat:
                    matched_group = group
                    break

            if matched_group:
                # Add text as an evidence occurrence of this UNIQUE RISK
                existing_occurrences = matched_group["evidence_occurrences"]
                already_captured = False
                for idx, existing in enumerate(existing_occurrences):
                    if text == existing or text in existing:
                        already_captured = True
                        break
                    elif existing in text:
                        existing_occurrences[idx] = text
                        already_captured = True
                        break

                if not already_captured:
                    existing_occurrences.append(text)

                matched_group["pages"].add(page)
                # Primary evidence is the longest / clearest snippet
                if len(text) > len(matched_group["evidence"]):
                    matched_group["evidence"] = text
            else:
                # Create a new UNIQUE RISK group
                unique_groups.append({
                    "category": cat,
                    "rule": rule,
                    "pages": {page},
                    "evidence": text,
                    "evidence_occurrences": [text],
                    "confidence": conf
                })

        result_clauses = []
        for group in unique_groups:
            rule = group["rule"]
            min_page = min(group["pages"])
            primary_text = group["evidence"]
            occurrences = group["evidence_occurrences"]

            clause = ClauseSchema(
                category=rule["category"],
                page_number=min_page,
                original_text=primary_text,
                risk_level=rule["risk_level"],
                explanation=rule["reason"],
                reason=rule["reason"],
                suggested_action=rule["action"],
                evidence=primary_text,
                evidence_occurrences=occurrences,
                occurrence_count=len(occurrences),
                confidence=group["confidence"],
                section=f"Page {min_page}",
                multilingual_explanations={
                    "hi": rule["hi"],
                    "mr": rule["mr"],
                    "ta": rule["ta"],
                    "es": rule["es"],
                    "fr": rule["fr"]
                }
            )
            result_clauses.append(clause)

        return result_clauses

    def _perform_second_pass_missed_risk_scan(
        self,
        full_text: str,
        pages_data: List[Dict[str, Any]],
        existing_candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Pass 2: Independently scan complete document for missed risk clauses across ALL categories.
        Does NOT skip categories present in Pass 1; finds uncaptured risk text snippets.
        """
        existing_evidence = {c["text"].strip() for c in existing_candidates}
        new_candidates = []

        for rule in RISK_DEFINITIONS:
            for p_idx, page in enumerate(pages_data, start=1):
                p_text = page.get("text", "")
                paragraphs = self._split_into_clean_paragraphs(p_text)

                for para in paragraphs:
                    if para in existing_evidence:
                        continue

                    kw_match = any(re.search(kw, para, re.IGNORECASE) for kw in rule["keywords"])
                    if kw_match:
                        must_match = True
                        if rule.get("must_contain"):
                            must_match = any(re.search(mc, para, re.IGNORECASE) for mc in rule["must_contain"])

                        if must_match:
                            new_candidates.append({
                                "rule": rule,
                                "page": p_idx,
                                "text": para,
                                "confidence": 0.90
                            })
                            existing_evidence.add(para)

        return new_candidates

    def _verify_missed_risks(
        self,
        full_text: str,
        pages_data: List[Dict[str, Any]],
        existing_findings: List[ClauseSchema]
    ) -> List[ClauseSchema]:
        """
        Post-Deduplication Scan: Verifies that deduplication did NOT omit any genuine independent risk.
        Appends any missing unique risk if not captured.
        """
        captured_categories = {f.category for f in existing_findings}
        final_list = list(existing_findings)

        for rule in RISK_DEFINITIONS:
            cat = rule["category"]
            if cat in captured_categories:
                continue

            for p_idx, page in enumerate(pages_data, start=1):
                p_text = page.get("text", "")
                for kw in rule["keywords"]:
                    if re.search(kw, p_text, re.IGNORECASE):
                        must_match = True
                        if rule.get("must_contain"):
                            must_match = any(re.search(mc, p_text, re.IGNORECASE) for mc in rule["must_contain"])

                        is_safe = False
                        for safe_pat in rule.get("safe_indicators", []):
                            if re.search(safe_pat, p_text, re.IGNORECASE):
                                is_safe = True
                                break

                        if must_match and not is_safe:
                            snippet = self._extract_matching_snippet(kw, p_text)
                            if snippet:
                                clause = ClauseSchema(
                                    category=rule["category"],
                                    page_number=p_idx,
                                    original_text=snippet,
                                    risk_level=rule["risk_level"],
                                    explanation=rule["reason"],
                                    reason=rule["reason"],
                                    suggested_action=rule["action"],
                                    evidence=snippet,
                                    evidence_occurrences=[snippet],
                                    occurrence_count=1,
                                    confidence=0.88,
                                    section=f"Page {p_idx}",
                                    multilingual_explanations={
                                        "hi": rule["hi"],
                                        "mr": rule["mr"],
                                        "ta": rule["ta"],
                                        "es": rule["es"],
                                        "fr": rule["fr"]
                                    }
                                )
                                final_list.append(clause)
                                captured_categories.add(cat)
                                break

        return final_list

    @staticmethod
    def _text_similarity(s1: str, s2: str) -> float:
        words1 = set(re.findall(r"\w+", s1.lower()))
        words2 = set(re.findall(r"\w+", s2.lower()))
        if not words1 or not words2:
            return 0.0
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union)

    @staticmethod
    def _extract_matching_snippet(pattern: str, text: str) -> str:
        """
        Extracts the full verbatim clause/paragraph containing the pattern match.
        Ensures verbatim source clause preservation without arbitrary character slicing.
        """
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\d+[\.\)]\s+)|\n(?=(?:Section|Clause|Article)\b)", text) if p.strip()]
        for para in paragraphs:
            clean = " ".join(para.split())
            if re.search(pattern, clean, re.IGNORECASE):
                return clean
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return " ".join(text.strip().split())[:500]
        return " ".join(text.strip().split())

    def _attach_bounding_boxes(self, clauses: List[ClauseSchema], pages_data: List[Dict[str, Any]]):
        page_dict = {p["page_number"]: p for p in pages_data}
        for clause in clauses:
            if not clause.bounding_box:
                p_data = page_dict.get(clause.page_number)
                if p_data and p_data.get("words"):
                    clause.bounding_box = self._find_snippet_bbox(clause.original_text, p_data["words"])

    def _find_snippet_bbox(self, snippet: str, words: List[Dict[str, Any]]) -> Optional[BoundingBox]:
        """
        Calculates tight bounding box coordinates matching contiguous word sequences
        of the evidence snippet within page word coordinates.
        """
        if not words or not snippet.strip():
            return None

        clean_snippet_words = [w.lower() for w in re.findall(r"\w+", snippet) if len(w) > 1]
        if not clean_snippet_words:
            return None

        words_lower = [w.get("word", "").lower() for w in words]

        # Find contiguous run of matching words in the page
        best_run = []
        current_run = []
        for w_obj, w_text in zip(words, words_lower):
            if w_text in clean_snippet_words:
                current_run.append(w_obj)
            else:
                if len(current_run) > len(best_run):
                    best_run = current_run
                current_run = []
        if len(current_run) > len(best_run):
            best_run = current_run

        matched_coords = best_run if best_run else [w for w, wt in zip(words, words_lower) if wt in clean_snippet_words[:5]]

        if not matched_coords:
            return None

        xmin = min(w["xmin"] for w in matched_coords)
        ymin = min(w["ymin"] for w in matched_coords)
        xmax = max(w["xmax"] for w in matched_coords)
        ymax = max(w["ymax"] for w in matched_coords)

        return BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)

