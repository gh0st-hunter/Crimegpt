# CrimeGPT — System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CrimeGPT Platform                        │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Frontend   │      │   Backend    │      │  External    │  │
│  │  React/Vite  │◄────►│   FastAPI    │◄────►│  Services    │  │
│  │  Port: 5173  │      │  Port: 8000  │      │              │  │
│  └──────────────┘      └──────────────┘      │ • OpenAI API │  │
│                               │              │ • Indian     │  │
│                               ▼              │   Kanoon API │  │
│                        ┌──────────────┐      └──────────────┘  │
│                        │  SQLite DB   │                         │
│                        │ (Dev/Demo)   │                         │
│                        └──────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Backend (FastAPI)

```
backend/
├── main.py                          # FastAPI app entry point
│   └── CORS, routes, static files
│
├── app/
│   ├── config.py                    # Environment settings
│   ├── database.py                  # SQLAlchemy engine + session
│   │
│   ├── models/
│   │   └── models.py               # Database models
│   │       ├── User                 # Auth + role management
│   │       ├── Case                 # FIR + AI content
│   │       ├── Evidence             # Uploaded files
│   │       ├── TimelineEvent        # Case diary entries
│   │       ├── Notification         # Alerts
│   │       ├── Reminder             # Deadlines
│   │       └── ChatMessage          # AI chat history
│   │
│   ├── routes/
│   │   ├── auth.py                  # JWT auth endpoints
│   │   ├── cases.py                 # Case CRUD + AI + NLP
│   │   ├── documents.py             # Legal document generation
│   │   ├── dataset.py               # Sample data + legal sections
│   │   ├── evidence.py              # File upload + AI analysis
│   │   ├── chat.py                  # AI chatbot
│   │   ├── kanoon.py                # Indian Kanoon integration
│   │   └── notifications.py         # Alert management
│   │
│   ├── services/
│   │   ├── ai_service.py            # Core AI engine
│   │   │   ├── generate_fir()       # FIR generation
│   │   │   ├── get_legal_suggestions() # Section recommendations
│   │   │   ├── classify_priority()  # Priority classification
│   │   │   ├── classify_crime_nlp() # NLP classification
│   │   │   ├── get_landmark_judgments() # Case law
│   │   │   ├── get_multilingual_guidance() # Multi-language
│   │   │   ├── chat_response()      # Chatbot
│   │   │   └── analyze_evidence()   # Evidence AI
│   │   │
│   │   ├── document_service.py      # Legal document templates
│   │   │   ├── generate_remand_request()
│   │   │   ├── generate_seizure_receipt()
│   │   │   ├── generate_medical_letter()
│   │   │   └── generate_court_custody()
│   │   │
│   │   ├── auth.py                  # JWT + password hashing
│   │   └── kanoon_service.py        # Indian Kanoon API client
│   │
│   └── schemas/
│       └── schemas.py               # Pydantic models
```

### Frontend (React + Vite)

```
frontend/src/
├── App.jsx                          # Router setup
├── AuthContext.jsx                  # Auth state management
├── api.js                           # Axios API client
│
├── pages/
│   ├── LoginPage.jsx                # Authentication
│   ├── RegisterPage.jsx
│   ├── DashboardPage.jsx            # Stats + quick actions + seed
│   ├── CasesPage.jsx                # Case list with filters
│   ├── CaseDetailPage.jsx           # Case + tabs (5 tabs)
│   │   ├── Overview tab             # FIR, investigation steps
│   │   ├── Case Diary tab           # Timeline + add entry
│   │   ├── Evidence tab             # File upload + AI
│   │   ├── Legal Intel tab          # Sections + judgments + Kanoon
│   │   └── Documents tab            # Quick document generation
│   ├── NewCasePage.jsx              # Complaint intake form
│   ├── DocumentsPage.jsx            # Full document editor (4-step)
│   ├── LegalSectionsPage.jsx        # BNS/BNSS/BSA browser
│   ├── ChatPage.jsx                 # AI assistant
│   ├── AnalyticsPage.jsx            # Charts + metrics
│   └── NotificationsPage.jsx
│
└── components/
    └── Layout.jsx                   # Sidebar + header
```

## Data Flow

### FIR Generation Flow
```
User (Natural Language Complaint)
        │
        ▼
    CasesPage/NewCasePage
        │ POST /api/cases/from-complaint
        ▼
    cases.py route
        │ calls generate_fir()
        ▼
    ai_service.py
        │ → OpenAI GPT-4 (if configured)
        │ → Mock templates (fallback)
        ▼
    Database (Case model)
        │
        ▼
    CaseDetailPage (Overview tab)
```

### Document Generation Flow
```
Officer selects Case + Document Type
        │
        ▼
    DocumentsPage (Step 3: Fill Details)
        │ POST /api/documents/{case_id}/generate
        ▼
    documents.py route
        │ calls generate_legal_document()
        ▼
    document_service.py
        │ → HTML template with case data
        ▼
    Frontend (iframe preview)
        │
        ▼
    Download as HTML / Print as PDF
```

## Database Schema

```sql
-- Core tables
users (id, email, role, full_name, badge_number, station, rank)
cases (id, fir_number, title, description, category, status, priority,
       ai_fir_text, ai_legal_sections, ai_investigation_steps,
       complainant_id, assigned_officer_id, filed_at)
evidence (id, case_id, title, evidence_type, file_path, ai_analysis)
timeline_events (id, case_id, title, event_type, event_date, is_ai_generated)
notifications (id, user_id, title, message, notification_type, is_read)
reminders (id, case_id, user_id, title, due_date, is_completed)
chat_messages (id, user_id, message, response, context)
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│              Security Layers            │
│                                         │
│  1. JWT Authentication (HS256)          │
│     └── 30-day expiry, Bearer token     │
│                                         │
│  2. Role-Based Access Control           │
│     ├── VICTIM: own cases only          │
│     ├── OFFICER: assigned + unassigned  │
│     └── ADMIN: full access              │
│                                         │
│  3. Input Validation (Pydantic)         │
│     └── All request bodies validated    │
│                                         │
│  4. Password Hashing (bcrypt)           │
│     └── Never stored in plaintext       │
│                                         │
│  5. CORS Configuration                  │
│     └── Configurable origins list       │
└─────────────────────────────────────────┘
```

## AI Architecture

```
┌─────────────────────────────────────────────────────┐
│                   AI Service Layer                  │
│                                                     │
│  ┌─────────────────┐    ┌──────────────────────┐   │
│  │   OpenAI Mode   │    │      Mock Mode       │   │
│  │  (API key set)  │    │  (no API key = demo) │   │
│  │                 │    │                      │   │
│  │ • GPT-4o        │    │ • Rule-based NLP     │   │
│  │ • Real FIRs     │    │ • Template FIRs      │   │
│  │ • Live analysis │    │ • Keyword matching   │   │
│  └─────────────────┘    └──────────────────────┘   │
│                                                     │
│  Features (both modes):                             │
│  ✓ FIR Generation       ✓ Crime NLP Classification  │
│  ✓ Legal Sections       ✓ Landmark Judgments        │
│  ✓ Priority Scoring     ✓ Multilingual Guidance     │
│  ✓ Evidence Analysis    ✓ Chat Assistance           │
└─────────────────────────────────────────────────────┘
```

## Deployment Architecture (Docker)

```
docker-compose.yml
├── backend (Python/FastAPI)
│   └── Port: 8000
├── frontend (Nginx static)
│   └── Port: 80
└── Volumes
    ├── crimegpt_data (SQLite DB)
    └── crimegpt_uploads (Evidence files)
```
