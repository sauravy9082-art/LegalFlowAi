import pytest
import os
import zipfile
from xml.etree import ElementTree as ET
from app.services.docx_redliner import DocxRedlinerService, W_NS
from app.models.schemas import ClauseSchema, RiskLevelEnum

@pytest.mark.asyncio
async def test_docx_openxml_redline_generation(tmp_path):
    redliner = DocxRedlinerService()
    
    # Create sample clauses
    clauses = [
        ClauseSchema(
            category="Indemnification & Liability",
            page=1,
            original_text="Party B shall indemnify Party A against unlimited damages.",
            risk_level=RiskLevelEnum.CRITICAL,
            explanation="Unlimited indemnification",
            reason="One-sided exposure",
            suggested_action="Cap indemnification to $50,000 max.",
            evidence="Unlimited damages"
        )
    ]

    source_docx = os.path.join(tmp_path, "sample_contract.docx")
    
    # Generate Redline
    output_path = await redliner.generate_openxml_redline(source_docx, clauses)
    assert os.path.exists(output_path)

    # 1. Validate ZIP format
    assert zipfile.is_zipfile(output_path) is True

    # 2. Extract document.xml
    with zipfile.ZipFile(output_path, 'r') as zip_ref:
        zip_ref.extract("word/document.xml", tmp_path)

    xml_file = os.path.join(tmp_path, "word", "document.xml")
    assert os.path.exists(xml_file)

    # 3. Validate XML tree and search for <w:del> and <w:ins>
    tree = ET.parse(xml_file)
    root = tree.getroot()

    dels = root.findall(f".//{{{W_NS}}}del")
    inss = root.findall(f".//{{{W_NS}}}ins")

    # 4. Verify expected XML elements exist
    assert len(dels) > 0, "No <w:del> nodes found in OpenXML document!"
    assert len(inss) > 0, "No <w:ins> nodes found in OpenXML document!"

    # 5. Verify deleted and inserted text content inside XML
    del_text = dels[0].find(f".//{{{W_NS}}}delText").text
    ins_text = inss[0].find(f".//{{{W_NS}}}t").text

    assert "indemnify Party A" in del_text
    assert "Cap indemnification" in ins_text
