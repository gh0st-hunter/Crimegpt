# CrimeGPT — Complete System Workflow Flowcharts (Mermaid.js)

This document contains the complete set of workflow flowcharts for the **CrimeGPT** AI-Powered Crime Documentation & Legal Intelligence Platform, written in standard **Mermaid.js** syntax. 

You can render these diagrams in any Markdown viewer that supports Mermaid (like GitHub, VS Code Markdown Preview, Obsidian, etc.) or paste them directly into the [Mermaid Live Editor](https://mermaid.live).

---

## 📋 Table of Contents
1. [System Architecture](#1-system-architecture)
2. [Authentication & Authorization Flow](#2-authentication--authorization-flow)
3. [AI-Powered FIR Generation Workflow](#3-ai-powered-fir-generation-workflow)
4. [Case Lifecycle & Status Transitions](#4-case-lifecycle--status-transitions)
5. [Legal Document Generation (4-Step Wizard)](#5-legal-document-generation-4-step-wizard)
6. [AI Engine & Service Layer](#6-ai-engine--service-layer)
7. [Database Entity Relationship Diagram](#7-database-entity-relationship-diagram)
8. [Frontend Navigation & User Journey](#8-frontend-navigation--user-journey)

---

## 1. System Architecture
This diagram outlines the complete technology stack and data flow between the client application, API layer, services, databases, and external APIs.

```mermaid
graph LR
    subgraph CLIENT["🖥️ Frontend — React + Vite :5173"]
        A["Login / Register Page"]
        B["Dashboard Page"]
        C["Cases Page"]
        D["Case Detail Page<br/>(5 Tabs)"]
        E["New Case Page"]
        F["Documents Page"]
        G["Legal Sections Page"]
        H["Chat Page"]
        I["Analytics Page"]
        J["Notifications Page"]
    end

    subgraph API["⚙️ Backend — FastAPI :8000"]
        R1["auth.py<br/>JWT Auth"]
        R2["cases.py<br/>Case CRUD + AI"]
        R3["documents.py<br/>Legal Docs"]
        R4["evidence.py<br/>File Upload"]
        R5["chat.py<br/>AI Chatbot"]
        R6["dataset.py<br/>Legal Sections"]
        R7["kanoon.py<br/>Case Law"]
        R8["notifications.py<br/>Alerts"]
    end

    subgraph SERVICES["🧠 Services Layer"]
        S1["ai_service.py<br/>Core AI Engine"]
        S2["document_service.py<br/>HTML Templates"]
        S3["auth.py<br/>JWT + bcrypt"]
        S4["kanoon_service.py<br/>API Client"]
    end

    subgraph DB["🗄️ SQLite Database"]
        T1[("users<br/>cases<br/>evidence<br/>timeline_events<br/>notifications<br/>reminders<br/>chat_messages")]
    end

    subgraph EXT["☁️ External APIs"]
        X1["OpenAI GPT-4o"]
        X2["Indian Kanoon API"]
    end

    CLIENT -- "Axios HTTP + JWT" --> API
    R1 --> S3
    R2 --> S1
    R3 --> S2
    R4 --> S1
    R5 --> S1
    R7 --> S4
    API --> DB
    S1 -.-> X1
    S4 -.-> X2

    style CLIENT fill:#1a1f35,stroke:#4f6ef7,stroke-width:2px,color:#e8ecf4
    style API fill:#1a1f35,stroke:#8b5cf6,stroke-width:2px,color:#e8ecf4
    style SERVICES fill:#1a1f35,stroke:#06d6a0,stroke-width:2px,color:#e8ecf4
    style DB fill:#1a1f35,stroke:#f59e0b,stroke-width:2px,color:#e8ecf4
    style EXT fill:#1a1f35,stroke:#ef4444,stroke-width:2px,color:#e8ecf4
```

---

## 2. Authentication & Authorization Flow
Details the workflow of checking credentials/tokens, user registration and login, JWT validation, and the permissions granted to each Role-Based Access Control (RBAC) role.

```mermaid
flowchart TD
    START(["🌐 User Opens App"])
    START --> CHECK{"Token in<br/>localStorage?"}
    CHECK -- "Yes" --> VERIFY["GET /api/auth/me<br/>Verify token"]
    CHECK -- "No" --> LOGIN_PAGE["Show Login / Register Page"]

    VERIFY -- "Valid" --> DASHBOARD["✅ Load Dashboard"]
    VERIFY -- "Invalid / Expired" --> CLEAR["Clear localStorage"]
    CLEAR --> LOGIN_PAGE

    LOGIN_PAGE --> REG_OR_LOGIN{"Register or<br/>Login?"}
    REG_OR_LOGIN -- "Register" --> REGISTER["POST /api/auth/register<br/>email, password, role,<br/>full_name, badge, station"]
    REG_OR_LOGIN -- "Login" --> LOGIN["POST /api/auth/login<br/>email, password"]

    REGISTER --> HASH["Hash password (bcrypt)"]
    HASH --> CREATE_USER["Create User in DB"]
    CREATE_USER --> GEN_TOKEN["Generate JWT Token<br/>(sub: user.id, role)"]
    GEN_TOKEN --> STORE["Store token +<br/>user in localStorage"]

    LOGIN --> VALIDATE["Validate credentials"]
    VALIDATE -- "Invalid" --> ERROR["❌ 401 Error"]
    VALIDATE -- "Account Inactive" --> DEACTIVATED["❌ 403 Deactivated"]
    VALIDATE -- "Valid" --> GEN_TOKEN2["Generate JWT Token"]
    GEN_TOKEN2 --> STORE

    STORE --> DASHBOARD

    style START fill:#06d6a0,stroke:#059669,color:#000
    style DASHBOARD fill:#4f6ef7,stroke:#3b5ce4,color:#fff
    style ERROR fill:#ef4444,stroke:#dc2626,color:#fff
    style DEACTIVATED fill:#ef4444,stroke:#dc2626,color:#fff
```

### Route Guard Validation Flow
```mermaid
flowchart LR
    REQ["API Request"] --> MW{"JWT Middleware"}
    MW -- "No Token" --> R401["401 Unauthorized"]
    MW -- "Valid Token" --> DECODE["Decode JWT<br/>Extract user_id + role"]
    DECODE --> ROLE{"Check Role<br/>Permission"}
    ROLE -- "Allowed" --> HANDLER["✅ Route Handler"]
    ROLE -- "Denied" --> R403["403 Forbidden"]

    style R401 fill:#ef4444,stroke:#dc2626,color:#fff
    style R403 fill:#ef4444,stroke:#dc2626,color:#fff
    style HANDLER fill:#06d6a0,stroke:#059669,color:#000
```

---

## 3. AI-Powered FIR Generation Workflow
Visualizes the two entry points (Manual Case Registration and AI Direct Complaint Submission) and the processing pipeline that extracts sections, sets priority, generates formal FIR text, and writes to database tables.

```mermaid
flowchart TD
    subgraph INPUT["📝 User Input"]
        U1["Victim / Officer<br/>writes complaint in<br/>natural language"]
    end

    subgraph PATHS["Two Entry Paths"]
        P1["<b>Path A: Manual</b><br/>NewCasePage form<br/>POST /api/cases/"]
        P2["<b>Path B: AI Direct</b><br/>Complaint text input<br/>POST /api/cases/from-complaint"]
    end

    subgraph AI_PROCESSING["🧠 AI Processing — ai_service.py"]
        AI1["classify_priority()<br/>→ Critical / High / Medium / Low"]
        AI2["generate_fir()<br/>→ Formal FIR text"]
        AI3["get_legal_suggestions()<br/>→ BNS / BNSS / BSA / IT Act sections"]
        AI4["Investigation steps<br/>→ Required evidence list"]
    end

    subgraph STORAGE["💾 Database Storage"]
        DB1["Create Case record<br/>status: DRAFT or FILED"]
        DB2["Store AI outputs:<br/>ai_fir_text,<br/>ai_legal_sections,<br/>ai_investigation_steps,<br/>ai_required_evidence"]
        DB3["Generate FIR Number<br/>FIR/2026/XXXXXX"]
        DB4["Create Timeline Events<br/>Complaint Filed → FIR Generated → Legal Sections"]
        DB5["Send Notification<br/>to complainant"]
    end

    subgraph OUTPUT["📋 Result"]
        O1["CaseDetailPage<br/>Overview Tab"]
        O2["FIR text displayed"]
        O3["Legal sections listed"]
        O4["Investigation steps shown"]
        O5["Priority badge displayed"]
    end

    U1 --> P1
    U1 --> P2

    P1 --> AI1
    AI1 --> DB1
    DB1 --> LATER["Officer clicks<br/>'Generate FIR'"]
    LATER --> AI2

    P2 --> AI2
    AI2 --> AI3
    AI3 --> AI4
    AI4 --> DB2
    DB2 --> DB3
    DB3 --> DB4
    DB4 --> DB5
    DB5 --> O1

    O1 --> O2
    O1 --> O3
    O1 --> O4
    O1 --> O5

    style INPUT fill:#1a1f35,stroke:#f59e0b,stroke-width:2px,color:#e8ecf4
    style PATHS fill:#1a1f35,stroke:#4f6ef7,stroke-width:2px,color:#e8ecf4
    style AI_PROCESSING fill:#1a1f35,stroke:#8b5cf6,stroke-width:2px,color:#e8ecf4
    style STORAGE fill:#1a1f35,stroke:#06d6a0,stroke-width:2px,color:#e8ecf4
    style OUTPUT fill:#1a1f35,stroke:#14b8a6,stroke-width:2px,color:#e8ecf4
```

---

## 4. Case Lifecycle & Status Transitions
Shows the state machine for the 8 case statuses (`DRAFT`, `FILED`, `UNDER_INVESTIGATION`, `EVIDENCE_COLLECTION`, `CHARGESHEET_FILED`, `COURT_PROCEEDINGS`, `CLOSED`, `REOPENED`).

```mermaid
stateDiagram-v2
    [*] --> DRAFT : Complaint filed\n(manual form)

    DRAFT --> FILED : FIR generated\n(AI processing)

    [*] --> FILED : From complaint\n(auto-generated FIR)

    FILED --> UNDER_INVESTIGATION : Officer starts\ninvestigation
    FILED --> EVIDENCE_COLLECTION : Direct to\nevidence phase

    UNDER_INVESTIGATION --> EVIDENCE_COLLECTION : Collecting\nevidence
    EVIDENCE_COLLECTION --> UNDER_INVESTIGATION : More\ninvestigation needed

    UNDER_INVESTIGATION --> CHARGESHEET_FILED : Chargesheet\nsubmitted
    EVIDENCE_COLLECTION --> CHARGESHEET_FILED : Evidence\ncomplete

    CHARGESHEET_FILED --> COURT_PROCEEDINGS : Court\nhearings begin

    COURT_PROCEEDINGS --> CLOSED : Judgment\ndelivered

    FILED --> CLOSED : Case dismissed
    UNDER_INVESTIGATION --> CLOSED : Investigation\ncomplete
    
    CLOSED --> REOPENED : New evidence\nor appeal

    REOPENED --> UNDER_INVESTIGATION : Re-investigate

    note right of DRAFT : Initial state\nNo FIR number
    note right of FILED : FIR# assigned\nAI content generated
    note right of CLOSED : closed_at timestamp\nNotification sent
```

---

## 5. Legal Document Generation (4-Step Wizard)
Steps to select a legal document template (Remand Request, Seizure Panchnama, Medical Treatment Letter, or Court Custody Letter), merge case metadata, and export/preview the final document.

```mermaid
flowchart TD
    subgraph STEP1["Step 1: Select Document Type"]
        D1["⚖️ Remand Request Letter<br/>(Section 187 BNSS)"]
        D2["📋 Seizure Receipt / Panchnama<br/>(Section 105 BNSS)"]
        D3["🏥 Medical Treatment Letter<br/>(Section 51/184 BNSS)"]
        D4["🏛️ Court Custody Letter<br/>(Section 187 BNSS)"]
    end

    subgraph STEP2["Step 2: Select Case"]
        CASE["Choose from filed cases<br/>(fetched via GET /api/cases/)"]
    end

    subgraph STEP3["Step 3: Fill Details"]
        FORM["Officer name, rank, badge<br/>Police station, court name<br/>Magistrate name<br/>Accused details<br/>Arrest date, items seized<br/>Hospital name, doctor name"]
    end

    subgraph STEP4["Step 4: Generate & Preview"]
        GEN["POST /api/documents/{case_id}/generate"]
        SERVICE["document_service.py<br/>generate_legal_document()"]
        HTML["Official HTML document<br/>with case data merged"]
        PREVIEW["iframe preview<br/>in browser"]
        ACTIONS["📥 Download HTML<br/>🖨️ Print as PDF"]
    end

    D1 --> CASE
    D2 --> CASE
    D3 --> CASE
    D4 --> CASE
    CASE --> FORM
    FORM --> GEN
    GEN --> SERVICE
    SERVICE --> HTML
    HTML --> PREVIEW
    PREVIEW --> ACTIONS

    style STEP1 fill:#1a1f35,stroke:#8b5cf6,stroke-width:2px,color:#e8ecf4
    style STEP2 fill:#1a1f35,stroke:#4f6ef7,stroke-width:2px,color:#e8ecf4
    style STEP3 fill:#1a1f35,stroke:#f59e0b,stroke-width:2px,color:#e8ecf4
    style STEP4 fill:#1a1f35,stroke:#06d6a0,stroke-width:2px,color:#e8ecf4
```

---

## 6. AI Engine & Service Layer
Depicts the core functions implemented in `ai_service.py` and how the application switches between Live OpenAI Mode and Local Mock Mode based on API Key configuration.

```mermaid
flowchart TD
    subgraph TRIGGER["🔌 Trigger Points"]
        T1["Create Case"]
        T2["Generate FIR"]
        T3["Classify Crime (NLP)"]
        T4["Legal Suggestions"]
        T5["Landmark Judgments"]
        T6["Evidence Upload"]
        T7["Chat Message"]
        T8["Victim Guidance"]
    end

    subgraph ENGINE["🧠 ai_service.py — Core Engine"]
        F1["generate_fir()"]
        F2["classify_priority()"]
        F3["classify_crime_nlp()"]
        F4["get_legal_suggestions()"]
        F5["get_landmark_judgments()"]
        F6["analyze_evidence()"]
        F7["chat_response()"]
        F8["get_multilingual_guidance()"]
    end

    subgraph MODE{"🔀 Operating Mode"}
        M1["🟢 OpenAI Mode<br/>(OPENAI_API_KEY set)<br/>GPT-4o live processing"]
        M2["🟡 Mock Mode<br/>(No API key)<br/>Rule-based + templates"]
    end

    subgraph OUTPUT["📊 AI Outputs"]
        O1["FIR Text (formal format)"]
        O2["Legal Sections (BNS/BNSS/BSA/IT Act)"]
        O3["Priority Level + Reasoning"]
        O4["Investigation Steps"]
        O5["Required Evidence List"]
        O6["Crime Category Scores"]
        O7["Landmark Judgments (SC/HC)"]
        O8["Evidence Analysis Text"]
        O9["Chat Responses (multilingual)"]
    end

    T1 --> F2
    T2 --> F1
    T3 --> F3
    T4 --> F4
    T5 --> F5
    T6 --> F6
    T7 --> F7
    T8 --> F8

    F1 & F2 & F3 & F4 & F5 & F6 & F7 & F8 --> MODE
    M1 --> OUTPUT
    M2 --> OUTPUT

    style TRIGGER fill:#1a1f35,stroke:#f59e0b,stroke-width:2px,color:#e8ecf4
    style ENGINE fill:#1a1f35,stroke:#14b8a6,stroke-width:2px,color:#e8ecf4
    style OUTPUT fill:#1a1f35,stroke:#4f6ef7,stroke-width:2px,color:#e8ecf4
```

---

## 7. Database Entity Relationship Diagram
Diagram of the 7 relational tables in the SQLite database (`users`, `cases`, `evidence`, `timeline_events`, `notifications`, `reminders`, `chat_messages`) with columns, keys, and cardinality.

```mermaid
erDiagram
    USER ||--o{ CASE_COMPLAINT : "files"
    USER ||--o{ CASE_ASSIGNED : "investigates"
    USER ||--o{ NOTIFICATION : "receives"
    USER ||--o{ CHAT_MESSAGE : "sends"
    USER ||--o{ REMINDER : "has"

    CASE_COMPLAINT ||--o{ EVIDENCE : "contains"
    CASE_COMPLAINT ||--o{ TIMELINE_EVENT : "logs"
    CASE_COMPLAINT ||--o{ REMINDER : "tracks"
    CASE_COMPLAINT ||--o{ NOTIFICATION : "triggers"

    USER {
        UUID id PK
        string email UK
        string hashed_password
        string full_name
        enum role "victim|officer|admin"
        string badge_number
        string station
        string rank
        boolean is_active
        boolean is_verified
    }

    CASE_COMPLAINT {
        UUID id PK
        string fir_number UK
        string title
        text description
        enum category "12 crime types"
        enum status "8 states"
        enum priority "4 levels"
        text ai_fir_text
        json ai_legal_sections
        json ai_investigation_steps
        json ai_required_evidence
        UUID complainant_id FK
        UUID assigned_officer_id FK
    }

    EVIDENCE {
        UUID id PK
        UUID case_id FK
        string title
        enum evidence_type "8 types"
        string file_path
        text ai_analysis
        text extracted_text
        UUID uploaded_by FK
    }

    TIMELINE_EVENT {
        UUID id PK
        UUID case_id FK
        string title
        string event_type
        datetime event_date
        boolean is_ai_generated
        UUID created_by FK
    }

    NOTIFICATION {
        UUID id PK
        UUID user_id FK
        string title
        text message
        enum notification_type
        enum channel
        boolean is_read
        UUID case_id FK
    }

    REMINDER {
        UUID id PK
        UUID case_id FK
        UUID user_id FK
        string title
        datetime due_date
        boolean is_completed
        string reminder_type
    }

    CHAT_MESSAGE {
        UUID id PK
        UUID user_id FK
        text message
        text response
        string context
    }
```

---

## 8. Frontend Navigation & User Journey
Navigation tree showing public routes, authentication checks, sidebar-accessible pages, and the 5-tab breakdown of the Case Details dashboard.

```mermaid
flowchart TD
    ENTRY(["🌐 User visits app"])
    ENTRY --> AUTH{"Authenticated?"}

    AUTH -- "No" --> PUBLIC["Public Routes"]
    AUTH -- "Yes" --> PROTECTED["Protected Routes (Layout)"]

    subgraph PUBLIC_PAGES["🔓 Public"]
        LP["/login<br/>LoginPage"]
        RP["/register<br/>RegisterPage"]
    end
    PUBLIC --> LP
    PUBLIC --> RP
    LP -- "Success" --> PROTECTED
    RP -- "Success" --> PROTECTED

    subgraph PROTECTED_PAGES["🔒 Protected (Sidebar Navigation)"]
        DASH["/ Dashboard<br/>📊 Stats, quick actions,<br/>seed demo data"]
        CASES["/cases CasesPage<br/>📂 List with filters:<br/>status, priority, category"]
        NEWCASE["/cases/new NewCasePage<br/>📝 Complaint form +<br/>AI from-complaint"]
        DETAIL["/cases/:id CaseDetailPage<br/>🔍 5-tab interface"]
        DOCS["/documents DocumentsPage<br/>📄 4-step doc wizard"]
        LEGAL["/legal-sections<br/>⚖️ BNS/BNSS/BSA browser"]
        CHAT["/chat ChatPage<br/>🤖 AI assistant"]
        ANALYTICS["/analytics<br/>📈 Charts & metrics"]
        NOTIFS["/notifications<br/>🔔 Alert center"]
    end

    PROTECTED --> DASH
    DASH --> CASES
    DASH --> NEWCASE
    CASES --> DETAIL
    CASES --> NEWCASE
    NEWCASE --> DETAIL
    DETAIL --> DOCS
    DASH --> CHAT
    DASH --> ANALYTICS
    DASH --> NOTIFS
    DASH --> LEGAL

    subgraph TABS["📑 CaseDetailPage Tabs"]
        TAB1["Overview<br/>FIR text, sections,<br/>investigation steps"]
        TAB2["Case Diary<br/>Timeline events,<br/>add entries"]
        TAB3["Evidence<br/>Upload files,<br/>AI analysis"]
        TAB4["Legal Intel<br/>Sections, judgments,<br/>Kanoon search"]
        TAB5["Documents<br/>Quick generate<br/>from case context"]
    end

    DETAIL --> TAB1
    DETAIL --> TAB2
    DETAIL --> TAB3
    DETAIL --> TAB4
    DETAIL --> TAB5

    style ENTRY fill:#4f6ef7,stroke:#3b5ce4,color:#fff
    style PUBLIC_PAGES fill:#1a1f35,stroke:#ef4444,stroke-width:2px,color:#e8ecf4
    style PROTECTED_PAGES fill:#1a1f35,stroke:#06d6a0,stroke-width:2px,color:#e8ecf4
    style TABS fill:#1a1f35,stroke:#8b5cf6,stroke-width:2px,color:#e8ecf4
```
