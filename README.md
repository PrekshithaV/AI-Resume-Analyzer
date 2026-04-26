# 📄 AI Resume Analyzer

An end-to-end intelligent resume analysis platform powered by **OpenAI GPT-4o**, **FastAPI**, **Streamlit**, and **Microsoft Azure**.

---

## 🗂 Project Structure

```
resume_analyzer/
├── backend/
│   ├── main.py                  ← FastAPI app entry point
│   ├── config.py                ← Settings (pydantic-settings)
│   ├── schemas.py               ← Request/Response models
│   ├── routers/
│   │   ├── upload.py            ← POST /upload/
│   │   └── analyze.py           ← POST /analyze/
│   ├── services/
│   │   ├── analyzer.py          ← OpenAI GPT integration
│   │   └── storage.py           ← Azure Blob Storage
│   └── utils/
│       └── extractor.py         ← PDF / DOCX text extraction
├── frontend/
│   └── app.py                   ← Streamlit UI
├── tests/
│   └── test_analyzer.py         ← Unit tests (pytest)
├── requirements.txt
├── .env.example
├── azure.config.ini             ← Azure deployment notes
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone and create virtual environment

```bash
git clone https://github.com/your-username/resume-analyzer.git
cd resume_analyzer

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your real keys:
#   OPENAI_API_KEY
#   AZURE_STORAGE_CONNECTION_STRING
#   AZURE_CONTAINER_NAME
```

### 3. Run the FastAPI backend

```bash
uvicorn backend.main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 4. Run the Streamlit frontend (new terminal)

```bash
streamlit run frontend/app.py
```

Frontend available at: http://localhost:8501

### 5. Run tests

```bash
pytest tests/ -v
```

---

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Status + env |
| POST | `/upload/` | Upload resume to Azure Blob |
| POST | `/analyze/` | Upload + analyze resume (main endpoint) |

### Example: Analyze via curl

```bash
curl -X POST http://localhost:8000/analyze/ \
  -F "file=@/path/to/your/resume.pdf" \
  -F "job_role=Senior Python Developer"
```

---

## 🧠 How the AI Analysis Works

1. Resume file (PDF/DOCX) is uploaded
2. Text is extracted using `pdfplumber` / `python-docx`
3. Text + job role are sent to OpenAI GPT-4o with a structured prompt
4. GPT returns a JSON object with:
   - **ATS Score** (0–100)
   - **Job Match %**
   - **Matched Skills**
   - **Missing Skills** with importance levels
   - **Section-level Improvements**
   - **Strengths**
   - **Executive Summary**
5. Results are validated with Pydantic and returned to the UI

---

## ☁️ Azure Deployment

### Azure Blob Storage
1. Create a Storage Account in Azure Portal
2. Create a container named `resumes` (or your preferred name)
3. Copy the connection string → set as `AZURE_STORAGE_CONNECTION_STRING` in App Settings

### Azure App Service (FastAPI)
```bash
# Install Azure CLI
az login
az webapp up \
  --name resume-analyzer-api \
  --resource-group my-rg \
  --runtime PYTHON:3.11 \
  --sku B1

# Set environment variables
az webapp config appsettings set \
  --name resume-analyzer-api \
  --resource-group my-rg \
  --settings \
    OPENAI_API_KEY="sk-..." \
    AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=..." \
    AZURE_CONTAINER_NAME="resumes" \
    APP_ENV="production"
```

### Azure App Service (Streamlit)
```bash
az webapp up \
  --name resume-analyzer-ui \
  --resource-group my-rg \
  --runtime PYTHON:3.11 \
  --sku B1
```

Update `BACKEND_URL` in `frontend/app.py` to point to your deployed API URL.

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| AI | OpenAI GPT-4o |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| PDF Parsing | pdfplumber |
| DOCX Parsing | python-docx |
| File Storage | Azure Blob Storage |
| Hosting | Azure App Service |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio |

---

## 📋 Future Enhancements

- [ ] LinkedIn profile URL analysis
- [ ] Resume builder / export to PDF
- [ ] Multi-language resume support
- [ ] User authentication (Azure AD B2C)
- [ ] Analytics dashboard (Azure Monitor)
- [ ] Batch resume screening for HR teams
