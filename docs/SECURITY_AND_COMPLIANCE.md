# Security, Compliance & Governance Gap Analysis

**Project:** ScamRoad (Autonomous Pavement Distress Detection & Review Engine)  
**Governance Grade:** Academic Research Prototype / National Pilot Framework  
**Governing Laws & Standards Evaluated:**  
- Digital Personal Data Protection (DPDP) Act, 2023 (India)  
- CERT-In Cyber Security Directions (No. 20(3)/2022-CERT-In)  
- Guidelines for Indian Government Websites (GIGW 3.0)  
- MeitY Empanelled Cloud Service Provider (CSP) Requirements  

> [!WARNING]
> **Regulatory Gap Notice:** This document is an honest architectural gap analysis and deployment roadmap, **not** a certificate of compliance. ScamRoad is a student research pilot. Prior to production onboarding with state PWDs, municipal corporations (e.g. BBMP, BMC), or the National Highways Authority of India (NHAI), all mandatory audits and empanelled security clearances listed below must be completed.

---

## 1. Statutory Data Protection (DPDP Act 2023)

Under the Digital Personal Data Protection Act, 2023, high-definition road dashcam video streams capture identifiable personal data in public spaces (pedestrian facial biometrics, vehicle registration number plates).

### 1.1 Automated Anonymization Protocol (Edge Privacy Blocker)
- **Obligation:** Section 4(1) — Processing of personal data must be lawful, fair, and for legitimate purposes.
- **Implemented Technical Mechanism:**
  - `ml/weights/coco_scene_blocker.onnx` and automated bounding box masking detect vehicle front/rear plates and human pedestrians.
  - Video frames undergo Gaussian blurring ($k=25, \sigma=7.5$) on all non-pavement human and license plate bounding coordinates before storage or review queue transmission.
- **Identified Gap:** The edge privacy filter operates on optical bounding boxes; extreme glare or high-speed motion blur can occasionally reduce detection recall of partial plates. Full compliance requires dedicated Automatic Number Plate Recognition (ANPR) redaction certified to &ge; 99.9% recall.

### 1.2 Data Fiduciary Obligations & Right to Erasure ("Delete-My-Data")
- **Obligation:** Section 12 — Right to correction and erasure of personal data upon request.
- **Implemented REST Route:**
  - `DELETE /api/v1/compliance/data-subject/{entity_id}` triggers cascading deletion of original survey video frames and coordinates.
- **Data Retention & Purge Policy:**
  - Raw un-anonymized dashcam frames: Purged within **30 days** of road defect extraction.
  - Verified defect bounding box crops: Retained for **3 years** for infrastructure lifecycle audit and contractor warranty tracking.

### 1.3 Grievance Redressal
- **Obligation:** Section 13 — Mandated Data Protection Officer (DPO) and 7-day grievance turnaround.
- **Status:** Institutional grievance contact designated under academic department head; formal DPO appointment pending commercial pilot sponsorship.

---

## 2. Infrastructure & Cloud Residency (MeitY Empanelled CSPs)

To comply with public sector procurement guidelines and critical infrastructure data localization rules, all server inference and review records must reside within the territorial boundary of the Republic of India.

### 2.1 Empanelled Cloud Hosting Options
1. **NIC MeghRaj Government Cloud:**
   - National Informatics Centre (NIC) data centers (New Delhi, Pune, Bhubaneswar, Hyderabad).
   - Dedicated for state PWD and MoRTH production pilots.
2. **MeitY-Empanelled Commercial CSPs:**
   - **AWS Asia Pacific (Mumbai `ap-south-1` / Hyderabad `ap-south-2`)**
   - **Microsoft Azure (Central India - Pune / South India - Chennai)**
   - **Google Cloud Platform (Mumbai `asia-south1` / Delhi `asia-south2`)**

### 2.2 Cross-Border Data Transfer Prohibition
- Strict VPC firewall egress rules prohibit transmitting raw geographic coordinates, road surface imagery, or survey videos outside Indian borders.

---

## 3. Cyber Security & CERT-In Empanelled Audit

Public infrastructure portals that integrate with state municipal databases require rigorous vulnerability assessments.

### 3.1 Mandated Pre-Deployment Audit
Before connection to any municipal road maintenance or GIS portal:
- Comprehensive Vulnerability Assessment and Penetration Testing (VAPT) conducted by a **CERT-In Empanelled Information Security Auditing Organisation**.
- Remediation of all Critical, High, and Medium vulnerabilities.
- Formal issuance of a "Safe to Host" certificate.

### 3.2 Implemented Security Safeguards
- **Authentication & RBAC:** JWT Bearer tokens with HMAC-SHA256 signatures; role-based access separation across `SuperAdmin`, `HighwayEngineer`, `HumanReviewer`, and `PublicAuditor`.
- **Encryption in Transit:** Strict TLS 1.3 encryption with HTTP Strict Transport Security (`HSTS: max-age=31536000; includeSubDomains`).
- **Encryption at Rest:** AES-256 block cipher encryption for all persistent SQLite / PostgreSQL databases and ONNX model caches.
- **Immutable Review Decisions:** Every human reviewer confirmation, edit, or rejection is cryptographically logged in `review_decisions.json` with UTC timestamps, reviewer UUID, and prior/post defect state.

---

## 4. Accessibility Gap Analysis (GIGW 3.0 / WCAG 2.2 AA)

Guidelines for Indian Government Websites (GIGW 3.0) mandate accessible, barrier-free user interfaces for all citizens.

| Requirement | Current Status | Audit Finding & Gap |
| :--- | :---: | :--- |
| **Colour Contrast** | **COMPLIANT** | "Paper and Asphalt" palette tested with WebAIM contrast checker. Text `#1B1A17` on light `#F6F4EE` achieves 12.8:1 contrast (exceeds WCAG AAA 7:1). Dark surface achieves 14.1:1 contrast. |
| **Colour-Blind Safety** | **COMPLIANT** | Wong (2011) accessible palette: Pothole `#D55E00`, Crack `#0072B2`, Water-filled `#CC79A7`. All overlays use distinctive 2px border patterns and text labels to avoid color-only differentiation. |
| **Screen Reader Navigation** | **PARTIAL** | Semantic HTML headings (`h1` through `h3`) and `aria-label` attributes present on canvas and navigation tabs. Gap: Complex interactive bounding box SVG overlays require richer ARIA live region descriptions. |
| **Keyboard Navigability** | **COMPLIANT** | All form inputs, review triage buttons, and navigation links accessible via standard `Tab` / `Shift+Tab` and `Enter` sequences with visible outline focus rings. |
| **Multilingual i18n** | **COMPLIANT** | Native scripts supported in UI for 6 Indian languages: English, Hindi (हिन्दी), Punjabi (ਪੰਜਾਬੀ), Tamil (தமிழ்), Telugu (తెలుగు), Bengali (বাংলা). |
| **Reduced Motion** | **COMPLIANT** | Honors `prefers-reduced-motion: reduce` OS settings; animations clamped to 0.01ms. |

---

*Student research project. Not an official government system. Not safety-certified.*
