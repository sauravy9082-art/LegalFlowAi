# LegalFlow AI — Utility & Generator Scripts

This folder contains Python scripts used to synthesize realistic legal contracts, presentation benchmarks, and test pairs for LegalFlow AI.

---

## 📜 Script Manifest

### 1. `generate_multicondition_pair.py`
- **Purpose**: Generates the exact calibrated contract pair (`13_TargetConditions_MSA_vA_Original.pdf` and `14_TargetConditions_MSA_vB_Redline.pdf`).
- **Output Target**: Produces **4 Modified**, **2 Added**, **1 Removed**, and **3 Unchanged** clauses when evaluated in the Compare tool.
- **Run**: `python scripts/generate_multicondition_pair.py`

### 2. `generate_presentation_docs.py`
- **Purpose**: Synthesizes the 5 realistic industrial presentation contracts with diverse Safety Scores (from 94% down to 28%) in `presentation_documents/`.
- **Run**: `python scripts/generate_presentation_docs.py`

### 3. `generate_comparison_docs.py` & `generate_new_compare_docs.py`
- **Purpose**: Generates multi-pair comparison test suites (SaaS agreements, MSAs, Executive Employment agreements) in `comparison_documents/`.
- **Run**: `python scripts/generate_new_compare_docs.py`
