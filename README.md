# CrimeGPT — AI-Powered Crime Documentation & Legal Intelligence Platform

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-green" alt="FastAPI" />
  <img src="https://img.shields.io/badge/React-18+-blue" alt="React" />
  <img src="https://img.shields.io/badge/AI-OpenAI%20GPT-orange" alt="AI" />
  <img src="https://img.shields.io/badge/Law-BNS%202023-red" alt="BNS" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License" />
</div>

---

## 🌟 Overview

**CrimeGPT** is a comprehensive AI-powered platform for Indian law enforcement agencies and legal professionals. It automates FIR generation, recommends applicable BNS/BNSS/BSA sections, generates official legal documents, and provides multilingual victim guidance.

### Key Capabilities
- 🤖 **AI FIR Generation** — Convert natural language complaints into formal FIRs
- ⚖️ **Legal Intelligence** — BNS, BNSS, BSA, IT Act section recommendations
- 📄 **Document Automation** — 4 official legal documents auto-generated
- 🔍 **NLP Crime Classification** — AI-powered crime category detection
- 🏛️ **Landmark Judgments** — Supreme Court & High Court case references
- 📚 **Digital Case Diary** — Timeline-based investigation logging
- 🌐 **Multilingual** — Hindi, Tamil, Telugu, Bengali, Marathi support
- 📊 **Analytics Dashboard** — Case statistics and trends

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture](#architecture)
3. [Features](#features)
4. [API Documentation](#api-documentation)
5. [Dataset](#dataset)
6. [Deployment](#deployment)
7. [Contributing](#contributing)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) OpenAI API Key for live AI features

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd crimegpt

# Backend setup
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env
# Edit .env with your settings (OpenAI API key optional)
uvicorn main:app --reload --port 8000

# Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### Demo Data
1. Register as an Officer account
2. Go to Dashboard
3. Click **"Load Demo Data"** to seed 5 sample FIRs
4. Explore the full workflow

---

## 🏗️ Architecture

```
crimegpt/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── models/             # SQLAlchemy database models
│   │   ├── routes/             # API route handlers
│   │   │   ├── auth.py         # Authentication
│   │   │   ├── cases.py        # Case management + AI
│   │   │   ├── documents.py    # Document generation
│   │   │   ├── dataset.py      # Sample data + legal sections
│   │   │   ├── evidence.py     # Evidence management
│   │   │   ├── chat.py         # AI chatbot
│   │   │   └── kanoon.py       # Indian Kanoon integration
│   │   ├── services/
│   │   │   ├── ai_service.py   # AI/ML features
│   │   │   └── document_service.py  # Document templates
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   └── database.py         # SQLite/PostgreSQL connection
│   └── main.py                 # FastAPI entry point
│
├── frontend/                   # React + Vite frontend
│   └── src/
│       ├── pages/              # Page components
│       │   ├── DashboardPage.jsx
│       │   ├── CasesPage.jsx
│       │   ├── CaseDetailPage.jsx
│       │   ├── DocumentsPage.jsx       # NEW
│       │   ├── LegalSectionsPage.jsx   # NEW
│       │   ├── ChatPage.jsx
│       │   └── AnalyticsPage.jsx
│       └── components/
│           └── Layout.jsx
│
└── docs/                       # Documentation
```

---

## ✨ Features

### 1. AI-Powered FIR Generation
- Natural language complaint → formal FIR
- Automatic legal section recommendations
- Priority classification (Critical/High/Medium/Low)
- Investigation step generation

### 2. Legal Document Generator
Four official legal documents:
| Document | Legal Basis | Purpose |
|----------|-------------|---------|
| Remand Request Letter | Section 187 BNSS | Police custody extension |
| Seizure Receipt (Panchnama) | Section 105 BNSS | Evidence seizure record |
| Medical Treatment Letter | Section 51/184 BNSS | Medical examination request |
| Court Custody Letter | Section 187 BNSS | Judicial custody transfer |

### 3. Legal Sections Browser
- Complete BNS 2023 (replaces IPC)
- BNSS 2023 (replaces CrPC)  
- BSA 2023 (replaces Indian Evidence Act)
- IT Act 2000 sections
- Cross-references to old IPC/CrPC sections
- Landmark Supreme Court cases

### 4. Digital Case Diary
- Timeline-based investigation logging
- AI-tagged events
- Export to PDF/HTML

### 5. Multilingual Support
- English (default)
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)
- Marathi (मराठी)

### 6. NLP Crime Classification
- Automatic crime category detection from complaint text
- Confidence scoring
- Multi-category scoring

---

## 📡 API Documentation

Full API documentation available at `/api/docs` (Swagger UI) and `/api/redoc`.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login |
| POST | `/api/cases/` | Create case |
| POST | `/api/cases/from-complaint` | Create from natural language |
| POST | `/api/cases/generate-fir/{id}` | Generate AI FIR |
| GET | `/api/cases/{id}/landmark-judgments` | Get landmark judgments |
| POST | `/api/cases/classify-nlp` | NLP crime classification |
| POST | `/api/documents/{id}/generate` | Generate legal document |
| GET | `/api/dataset/legal-sections` | Browse BNS/BNSS/BSA sections |
| POST | `/api/dataset/seed` | Seed sample data |
| POST | `/api/chat/` | AI chatbot |

---

## 📊 Dataset

### Sample FIRs
5 pre-loaded sample FIRs covering:
- Online Banking Fraud (Cybercrime)
- Residential Burglary (Theft)
- Domestic Violence (BNSS § 85)
- Investment Fraud / Ponzi Scheme
- Cyberstalking / Online Harassment

### Legal Sections Database
30+ sections from:
- BNS 2023 (Bharatiya Nyaya Sanhita)
- BNSS 2023 (Bharatiya Nagarik Suraksha Sanhita)
- BSA 2023 (Bharatiya Sakshya Adhiniyam)
- Information Technology Act 2000

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

Access the app at http://localhost

---

## 🔑 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (optional) | None (mock mode) |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `DATABASE_URL` | Database URL | SQLite |
| `KANOON_API_TOKEN` | Indian Kanoon token | None (mock) |

---

## 📜 Legal Framework

CrimeGPT is designed for India's new criminal laws effective 1 July 2024:
- **Bharatiya Nyaya Sanhita (BNS) 2023** — Replaces IPC 1860
- **Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023** — Replaces CrPC 1973
- **Bharatiya Sakshya Adhiniyam (BSA) 2023** — Replaces Indian Evidence Act 1872

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

---

## ⚠️ Disclaimer

CrimeGPT is an educational and demonstration tool. AI-generated content should be reviewed by qualified legal professionals before use in actual proceedings.

---

*Built with ❤️ for Indian Law Enforcement · CrimeGPT v2.0*
