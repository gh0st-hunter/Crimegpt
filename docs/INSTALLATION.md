# CrimeGPT — Installation Guide

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 10 / Ubuntu 20.04 | Windows 11 / Ubuntu 22.04 |
| Python | 3.10 | 3.11+ |
| Node.js | 18.0 | 20+ |
| RAM | 4 GB | 8 GB |
| Storage | 2 GB | 5 GB |

---

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd crimegpt
```

---

## Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your preferred editor:

```env
# Required
SECRET_KEY=your-secret-key-here-change-this

# Optional: OpenAI API key for live AI features
# Without this, CrimeGPT runs in "Mock Mode" with demo data
OPENAI_API_KEY=sk-...your-key...

# Optional: Indian Kanoon API token for live case law search
KANOON_API_TOKEN=your-token-here

# Database (defaults to SQLite for local dev)
DATABASE_URL=sqlite:///./crimegpt.db
```

---

## Step 3: Backend Setup

### Option A: Manual Setup (Development)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
uvicorn main:app --reload --port 8000
```

The backend API will be available at:
- **API Base**: http://localhost:8000/api
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Option B: Docker

```bash
docker build -t crimegpt-backend .
docker run -p 8000:8000 -e SECRET_KEY=your-key crimegpt-backend
```

---

## Step 4: Frontend Setup

### Option A: Manual Setup (Development)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### Option B: Production Build

```bash
npm run build
# Serve the dist/ folder with any static server
```

---

## Step 5: Docker Compose (Full Stack)

For the complete stack including both backend and frontend:

```bash
# From project root
docker-compose up --build

# Access at http://localhost
```

---

## Step 6: First Time Setup

1. Open http://localhost:5173
2. Click **"Register"** and create an Officer account
3. Log in with your credentials
4. Go to **Dashboard** → Click **"Load Demo Data"**
5. Explore the 5 sample FIRs that are created

---

## Troubleshooting

### Backend Issues

**Error: `ModuleNotFoundError`**
```bash
pip install -r requirements.txt
```

**Error: `Port 8000 already in use`**
```bash
uvicorn main:app --reload --port 8001
# Update frontend VITE_API_URL in .env accordingly
```

**Database corruption (SQLite)**
```bash
rm backend/crimegpt.db
uvicorn main:app --reload  # Tables auto-recreated
```

### Frontend Issues

**Error: `npm: command not found`**
Install Node.js from https://nodejs.org

**Error: `ECONNREFUSED` (API unreachable)**
Ensure the backend is running at http://localhost:8000

---

## Dependencies

### Backend
```
fastapi >= 0.100
uvicorn >= 0.20
sqlalchemy >= 2.0
pydantic >= 2.0
python-jose >= 3.3  # JWT
passlib >= 1.7      # Password hashing
python-multipart    # File uploads
openai >= 1.0       # Optional: AI features
httpx               # HTTP client
```

### Frontend
```
react >= 18
react-router-dom >= 6
axios               # HTTP client
lucide-react        # Icons
```
