import os
import pytest
import zipfile
import xml.etree.ElementTree as ET
from app.services.docx_redliner import DocxRedliner

def test_openxml_native_track_changes_redlining(tmp_path):
    print("\n--- Running OpenXML Native Track Changes Redline Test ---")

    risk_findings = [
        {
            "page": 1,
            "category": "Security Deposit Forfeiture",
            "original_text": "Tenant shall forfeit the entire security deposit of $2,500 if lease terminates early.",
            "suggested_action": "Landlord shall return deposit less documented damages within 30 days.",
            "explanation": "Unilateral deposit forfeiture is illegal in many jurisdictions."
        },
        {
            "page": 1,
            "category": "Uncapped Liability",
            "original_text": "Tenant agrees to uncapped liability and indemnifies landlord against all damages.",
            "suggested_action": "Tenant liability shall be capped at $5,000 except for willful misconduct.",
            "explanation": "Exposes tenant to unlimited financial claims."
        }
    ]

    dummy_orig = str(tmp_path / "original_lease.docx")

    # Generate Native OpenXML Redlined DOCX
    out_path, summary = DocxRedliner.create_openxml_redline(dummy_orig, str(tmp_path), risk_findings)

    assert os.path.exists(out_path)
    assert out_path.endswith(".docx")
    print(f"[OK] Redlined DOCX generated at: {out_path}")

    # 1. Verify ZIP package structure
    assert zipfile.is_zipfile(out_path)
    with zipfile.ZipFile(out_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        assert 'word/document.xml' in file_list
        print("[OK] ZIP package structure contains word/document.xml")

        # 2. Parse word/document.xml
        xml_bytes = zip_ref.read('word/document.xml')
        root = ET.fromstring(xml_bytes)
        print("[OK] word/document.xml parsed as valid XML")

        # 3. Verify Native OpenXML <w:del> and <w:ins> elements exist
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        del_nodes = root.findall('.//w:del', ns)
        ins_nodes = root.findall('.//w:ins', ns)

        assert len(del_nodes) >= 2
        assert len(ins_nodes) >= 2
        print(f"[OK] Found {len(del_nodes)} <w:del> and {len(ins_nodes)} <w:ins> WordprocessingML revision elements")

        # 4. Verify text inside revision nodes
        del_texts = "".join(["".join(n.itertext()) for n in del_nodes])
        ins_texts = "".join(["".join(n.itertext()) for n in ins_nodes])

        assert "DELETED" in del_texts or "forfeit" in del_texts
        assert "INSERTED" in ins_texts or "Landlord" in ins_texts
        print("[OK] Verified inserted and deleted text contents inside WordprocessingML revision tags")

    # 5. Verify helper verification method
    assert DocxRedliner.verify_docx_openxml_structure(out_path) is True
    print("[OK] Automated OpenXML structural verification passed successfully!")
