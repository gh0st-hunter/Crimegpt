# CrimeGPT — User Manual

## Getting Started

### Who is CrimeGPT for?

| Role | Use Cases |
|------|-----------|
| **Police Officer / IO** | Register FIRs, investigate cases, generate documents, track timeline |
| **Victim / Complainant** | File complaints, track case status, get legal guidance |
| **Admin** | Manage users, view all cases, analytics |

---

## Navigation Guide

### Sidebar Navigation
- **Dashboard** — Overview statistics and quick actions
- **Cases** — Browse and manage all FIRs
- **New Case** — File a new complaint
- **Documents** — Generate official legal documents
- **Legal Sections** — Browse BNS/BNSS/BSA sections
- **Analytics** — Charts and metrics
- **Notifications** — Alerts and updates
- **AI Assistant** — Chat with CrimeGPT AI

---

## Core Workflows

### 1. Filing an FIR

**Method A: Detailed Form**
1. Click **New Case** in sidebar
2. Fill in the complaint form (title, description, category, location, date)
3. Click **Create Case** → Case is created in DRAFT status
4. Go to the case → Click **Generate FIR** button
5. AI generates formal FIR text with applicable sections

**Method B: Natural Language (Quick)**
1. Click **New Case**
2. Select **"From Natural Language Complaint"** tab
3. Type your complaint in plain English
4. AI automatically creates the FIR with legal sections

---

### 2. Generating Legal Documents

1. Go to **Documents** page (sidebar)
2. **Step 1**: Select the case you want to generate documents for
3. **Step 2**: Choose document type:
   - ⚖️ **Remand Request Letter** — For police custody extension
   - 📋 **Seizure Receipt (Panchnama)** — For seized items
   - 🏥 **Medical Treatment Letter** — For medical examination
   - 🏛️ **Court Custody Letter** — For judicial custody
4. **Step 3**: Fill in document details (auto-populated from case)
5. **Step 4**: Preview the document in official letterhead format
6. Click **Download** (HTML) or **Print** (PDF via browser print)

**Quick Generation from Case Detail:**
1. Open any case → Go to **Documents** tab
2. Click **Generate** next to any document type
3. Download when ready

---

### 3. Case Diary (Digital)

1. Open any case → Click **Case Diary** tab
2. View all investigation timeline events
3. Click **+ Add Entry** to log new investigation steps:
   - Enter title, description, date/time
   - Select event type (Investigation/Evidence/Court/Legal)
4. AI-generated events are marked with **AI** badge

---

### 4. Legal Intelligence

In any case detail page → **Legal Intel** tab:

**Landmark Judgments**
- Auto-loaded based on crime category
- Links to Indian Kanoon for full text
- Shows Supreme Court & High Court decisions

**Case Law Search (Indian Kanoon)**
- Search for related cases and precedents
- Auto-searches based on crime category

**Applicable Sections**
- BNS/BNSS/BSA sections identified by AI
- Shows penalties and descriptions

---

### 5. Legal Sections Browser

1. Click **Legal Sections** in sidebar
2. Browse by act: BNS / BNSS / BSA / IT Act
3. Search by section number or offence name
4. Filter by crime category
5. Expand any section to see:
   - Full description and penalty
   - Cross-reference to old IPC/CrPC section
   - Landmark cases

---

### 6. AI Chat Assistant

1. Click **AI Assistant** in sidebar
2. Select context: Victim Guidance / Investigation / Cybercrime / General
3. Ask questions in plain English:
   - "How do I file an FIR?"
   - "What sections apply to cybercrime?"
   - "What are my rights as a victim?"
   - "How to preserve digital evidence?"
4. Get detailed responses with legal citations

---

### 7. Demo Data (Officers/Admins Only)

1. Go to **Dashboard**
2. Click **"Load Demo Data"** button
3. 5 sample FIRs are created covering:
   - Online Banking Fraud
   - House Burglary
   - Domestic Violence
   - Ponzi Scheme Fraud
   - Cyberstalking
4. Explore the full workflow with pre-loaded data

---

## Document Reference

### Remand Request Letter
- **Purpose**: Formal application to Magistrate for police custody extension
- **Legal basis**: Section 187 BNSS (formerly Section 167 CrPC)
- **Required fields**: Officer details, magistrate name, accused details, grounds for remand

### Seizure Receipt (Panchnama)
- **Purpose**: Official receipt for items seized during investigation
- **Legal basis**: Section 105 BNSS (formerly Section 100 CrPC)
- **Required fields**: Officer details, accused details, list of seized items, panch witnesses

### Medical Treatment Letter
- **Purpose**: Requisition for medical examination of accused or victim
- **Legal basis**: Section 51/184 BNSS (formerly Section 53/54 CrPC)
- **Required fields**: Officer details, hospital name, doctor name, purpose of examination

### Court Custody Letter
- **Purpose**: Production of accused before Magistrate and prayer for judicial custody
- **Legal basis**: Section 187 BNSS (formerly Section 167 CrPC)
- **Required fields**: Officer details, court/magistrate details, accused details, grounds for custody

---

## Tips & Best Practices

1. **Generate FIR first** before generating documents — AI populates legal sections automatically
2. **Load Demo Data** to explore the full workflow before entering real cases
3. **Case Diary** entries are timestamp-locked — add entries promptly
4. **Evidence upload** supports PDF, images, and documents
5. AI works in **Mock Mode** without an OpenAI key — configure for production use

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New Case | N (from Cases page) |
| Search Cases | Ctrl+F |
| Print Document | Ctrl+P (in document preview) |

---

## Multilingual Support

CrimeGPT AI Assistant supports guidance in:
- 🇮🇳 Hindi (हिंदी)
- 🇮🇳 Tamil (தமிழ்)
- 🇮🇳 Telugu (తెలుగు)
- 🇮🇳 Bengali (বাংলা)
- 🇮🇳 Marathi (मराठी)

Ask questions in your language in the AI Assistant.

---

## Helplines Reference

| Service | Number |
|---------|--------|
| Emergency | 112 |
| Women Helpline | 181 |
| Cybercrime | 1930 |
| Child Helpline | 1098 |
| Legal Aid (NALSA) | 15100 |
| Anti-Corruption | 1064 |
