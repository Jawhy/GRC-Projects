# Supplier Due Diligence Validator

🔗 **[Live Demo](#)** ← update after deployment

A financial-sector aligned supplier due diligence validation tool built in Python and Streamlit.

This project simulates the third-party onboarding workflow used in banking and regulated technology environments — validating mandatory control fields, flagging critical and conditional risks, and assigning assurance status aligned to FCA and ISO regulatory requirements.

---

## Overview

This tool validates supplier questionnaires against mandatory controls and produces:

- Mandatory field completeness check
- Red Risk identification (critical control failures → Reject)
- Amber Risk identification (remediation required → Conditional)
- Materiality-based escalation (amber risks escalate to Reject for material/critical suppliers)
- Assurance status assignment: Approved / Conditional / Reject
- Rationale generation per vendor
- Markdown validation report export
- CSV summary export
- Interactive Streamlit dashboard with filters and download buttons

---

## Regulatory & Framework Alignment

| Framework | Application Within Tool |
|-----------|-------------------------|
| ISO/IEC 27001:2022 | Control validation — encryption, MFA, access control, BCP/DR, vulnerability management |
| FCA SS2/21 | Outsourcing oversight and materiality-based escalation logic |
| EBA GL/2019/02 | ICT and security risk management in financial services |
| UK GDPR Art.28 | Processor due diligence and subprocessor disclosure requirements |

---

## Validation Methodology

### Mandatory Fields
Fifteen mandatory fields are checked for completeness. Missing fields trigger an automatic Reject status.

### Red Risks (→ Reject)
Critical control failures that trigger immediate rejection regardless of other factors:

| Control | Reference |
|---------|-----------|
| No encryption at rest | ISO 27001 A.8.24 |
| No encryption in transit | ISO 27001 A.8.24 |
| MFA not enforced | ISO 27001 A.5.17 |
| No incident response plan | ISO 27001 A.5.26 |
| BCP/DR not tested | ISO 27001 A.5.30 |
| Subprocessors not disclosed | ISO 27001 A.5.19 / UK GDPR Art.28 |
| No vulnerability management | ISO 27001 A.8.8 |
| No access control policy | ISO 27001 A.5.15 |

### Amber Risks (→ Conditional or Reject)
Conditional risks requiring remediation. For **material or critical suppliers**, amber risks escalate to Reject:

- Penetration test older than 12 months
- No certifications held
- Data residency in high-risk jurisdiction

### Status Logic
| Status | Condition |
|--------|-----------|
| Reject | Missing fields, red risks, or escalated amber risks |
| Conditional | Amber risks present (non-material suppliers) |
| Approved | All controls satisfied, no risks identified |

---

## Project Structure

```
06-due-diligence-validator/
├── main.py
├── app.py
├── README.md
├── requirements.txt
└── sample_data/
    └── questionnaires.json
```

---

## How to Run

1. Activate virtual environment:
```
source ~/GRC-Projects/venv/bin/activate
```

2. Navigate to project:
```
cd ~/GRC-Projects/06-due-diligence-validator
```

3. Run CLI tool:
```
python3 main.py
```

4. Run Streamlit app:
```
streamlit run app.py
```

---

## Sample Dataset

The included sample dataset (`sample_data/questionnaires.json`) contains 6 suppliers producing:

- 2 Approved — strong controls, UK-based, certified
- 2 Conditional — amber risks only, non-material suppliers
- 2 Reject — one with red control failures, one with amber escalated due to materiality and high-risk data residency

---

## Author

Ajibola Yusuff
Governance, Risk & Compliance | ISO 27001 | ISO 42001 | CompTIA Security+
Third-Party Risk Management | AI Vendor Risk | Identity Security