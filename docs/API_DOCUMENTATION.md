# CrimeGPT — API Documentation

**Base URL**: `http://localhost:8000/api`  
**Interactive Docs**: http://localhost:8000/api/docs  
**Authentication**: Bearer JWT token in `Authorization` header

---

## Authentication

### POST /auth/register
Register a new user.

**Request Body**:
```json
{
  "email": "officer@police.gov.in",
  "password": "secure123",
  "full_name": "Rajesh Kumar",
  "phone": "9876543210",
  "role": "officer",          // victim | officer | admin
  "badge_number": "DL/2024/001",
  "station": "Cyber Crime PS, Delhi",
  "rank": "Sub-Inspector"
}
```

**Response**: `200 OK`
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": { "id": "uuid", "email": "...", "role": "officer", ... }
}
```

---

### POST /auth/login
Login and get JWT token.

**Request Body**:
```json
{ "email": "officer@police.gov.in", "password": "secure123" }
```

**Response**: Same as register.

---

### GET /auth/me
Get current user profile. Requires authentication.

---

## Cases

### POST /cases/
Create a new case.

**Request Body**:
```json
{
  "title": "Online Banking Fraud",
  "description": "Victim received call from person claiming to be bank official...",
  "category": "cybercrime",
  "incident_location": "New Delhi",
  "incident_date": "2026-05-15T14:30:00",
  "police_station": "Cybercrime PS, Delhi"
}
```

**Categories**: `cybercrime | theft | fraud | assault | domestic_violence | sexual_harassment | murder | kidnapping | drug_offense | property_crime | white_collar | other`

---

### POST /cases/from-complaint
Create case from natural language complaint with auto FIR generation.

**Request Body**:
```json
{
  "complaint_text": "I received a phone call from someone claiming to be from my bank...",
  "category": "cybercrime"  // optional, AI auto-classifies
}
```

---

### GET /cases/
List cases with filtering.

**Query Parameters**:
- `status`: `draft | filed | under_investigation | evidence_collection | chargesheet_filed | court_proceedings | closed | reopened`
- `priority`: `critical | high | medium | low`
- `category`: (any crime category)
- `search`: text search in title/FIR number
- `skip`: pagination offset (default: 0)
- `limit`: max results (default: 20, max: 100)

---

### GET /cases/{case_id}
Get case details including AI content.

---

### PUT /cases/{case_id}
Update case (Officers/Admins only).

```json
{
  "status": "under_investigation",
  "assigned_officer_id": "uuid"
}
```

---

### POST /cases/generate-fir/{case_id}
Generate AI-powered FIR for a case.

**Response**: Updated case with `ai_fir_text`, `ai_legal_sections`, `ai_investigation_steps`, `ai_required_evidence`.

---

### GET /cases/{case_id}/timeline
Get case diary / investigation timeline.

---

### POST /cases/{case_id}/timeline
Add a case diary entry.

```json
{
  "title": "Suspect traced via CDR",
  "description": "CDR obtained from Airtel showed calls from UP",
  "event_date": "2026-05-18T10:00:00",
  "event_type": "investigation"
}
```

**Event types**: `complaint | fir | investigation | evidence | legal | court | status_change`

---

### POST /cases/{case_id}/legal-suggestions
Get AI legal section suggestions for a case.

---

### GET /cases/{case_id}/landmark-judgments
Get landmark Supreme Court / High Court judgments relevant to the case.

**Response**:
```json
{
  "judgments": [
    {
      "case": "Shreya Singhal v. Union of India (2015)",
      "court": "Supreme Court of India",
      "citation": "AIR 2015 SC 1523",
      "significance": "Struck down Section 66A IT Act...",
      "url": "https://indiankanoon.org/doc/..."
    }
  ],
  "category": "cybercrime"
}
```

---

### POST /cases/classify-nlp
NLP-based crime classification from free text.

**Request Body**: `{ "text": "Someone hacked my bank account and transferred money via UPI" }`

**Response**:
```json
{
  "category": "cybercrime",
  "confidence": 0.78,
  "top_matches": [["cybercrime", 0.78], ["fraud", 0.15]],
  "all_scores": { "cybercrime": 0.78, "fraud": 0.15, ... }
}
```

---

### GET /cases/stats
Dashboard statistics.

---

## Documents

### GET /documents/types
List all available document types.

**Response**:
```json
{
  "types": [
    { "id": "remand_request", "name": "Remand Request Letter", ... },
    { "id": "seizure_receipt", "name": "Seizure Receipt (Panchnama)", ... },
    { "id": "medical_letter", "name": "Medical Treatment Letter", ... },
    { "id": "court_custody", "name": "Court Custody Letter", ... }
  ]
}
```

---

### POST /documents/{case_id}/generate
Generate a legal document for a case.

**Request Body**:
```json
{
  "doc_type": "remand_request",    // required
  "officer_name": "Rajesh Kumar",
  "officer_rank": "Inspector",
  "officer_badge": "DL/2024/001",
  "police_station": "Cybercrime PS, Delhi",
  "magistrate_name": "The Ld. CJM",
  "court_name": "Chief Judicial Magistrate Court",
  "accused_name": "John Doe",
  "accused_age": "35",
  "accused_address": "123 Main St, Delhi",
  "arrest_date": "20/05/2026",
  "items_seized": "Mobile Phone, Laptop",   // for seizure receipt
  "hospital_name": "AIIMS Delhi",           // for medical letter
  "additional_notes": "Recovery of funds pending"
}
```

**Response**:
```json
{
  "html": "<!DOCTYPE html><html>...",    // Full HTML document
  "doc_type": "remand_request",
  "case_id": "uuid"
}
```

---

### GET /documents/{case_id}/preview/{doc_type}
Returns the document as rendered HTML (browser viewable).

**Response**: `text/html` content

---

## Dataset

### POST /dataset/seed
Seed database with 5 sample FIRs (Officers/Admins only).

**Response**:
```json
{
  "message": "Successfully seeded 5 sample FIRs",
  "cases": [{ "id": "...", "title": "...", "fir_number": "..." }]
}
```

---

### GET /dataset/legal-sections
Browse BNS/BNSS/BSA/IT Act legal sections.

**Query Parameters**:
- `act`: `BNS | BNSS | BSA | IT_ACT`
- `category`: crime category filter
- `search`: text search

**Response**:
```json
{
  "sections": [
    {
      "act": "BNS",
      "section": "Section 318(4)",
      "offence": "Cheating",
      "description": "Cheating involving delivery of property...",
      "penalty": "Up to 7 years + fine",
      "old_section": "Section 420 IPC",
      "crime_category": "fraud",
      "landmark_cases": ["Dr. S. Dutt v. State of U.P. (1966)"]
    }
  ],
  "total": 30
}
```

---

### GET /dataset/sample-firs
Get anonymized sample FIR descriptions (for research/demo).

---

## Evidence

### POST /evidence/{case_id}
Upload evidence file. Multipart form data.

**Form fields**:
- `file`: the file
- `title`: display name
- `evidence_type`: `document | image | video | audio | chat_log | email | screenshot | other`

---

### GET /evidence/{case_id}
List all evidence for a case.

---

## Chat

### POST /chat/
Send message to AI assistant.

```json
{
  "message": "How do I file an FIR?",
  "context": "victim_guidance"   // victim_guidance | investigation | cybercrime | general
}
```

---

## Notifications

### GET /notifications
Get user notifications.

### PUT /notifications/{id}/read
Mark notification as read.

### PUT /notifications/read-all
Mark all notifications as read.

---

## Error Responses

| Code | Meaning |
|------|---------|
| 400 | Bad Request — Invalid input |
| 401 | Unauthorized — Invalid/missing token |
| 403 | Forbidden — Insufficient permissions |
| 404 | Not Found — Resource doesn't exist |
| 422 | Validation Error — Pydantic validation failed |
| 500 | Internal Server Error |

**Error format**:
```json
{ "detail": "Error message here" }
```
