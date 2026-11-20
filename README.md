# HireNova ⚡

**AI Resume Tailor & ATS Optimizer**

HireNova analyzes resumes against job descriptions, calculates ATS match scores, highlights matching and missing skills, and leverages Google Gemini AI to generate tailored, STAR-formatted resumes with professional PDF export.

---

## 🚀 Quick Start

### 1. Requirements & Setup
- **Python**: 3.11+ (Managed via the configured virtual environment `.venv/`)
- **Google Gemini API Key**: Required for AI resume rewriting (get one free at [Google AI Studio](https://aistudio.google.com/app/apikey))

### 2. Run the App

#### Option A: Double-Click
Double-click `run.bat` (or right-click `run.ps1` -> Run with PowerShell).

#### Option B: Terminal Command
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Then open your browser at **http://localhost:8501**.

---

## 🔑 Permissions & Configuration

1. **Google Gemini API Key**:
   - Set in `.env`:
     ```env
     GEMINI_API_KEY=your_gemini_api_key_here
     ```
   - **Or** paste your key directly into the **left sidebar** in the web UI.
2. **Network Access**:
   - Outbound HTTPS to `generativelanguage.googleapis.com` to communicate with the Gemini API.
3. **Local Storage**:
   - Write permissions for `uploads/`, `generated/`, and `history.db` (created automatically in the project folder).

---

## 📁 Project Structure

```
HireNova/
├── app.py                  # Main Streamlit web application
├── run.bat                 # One-click Windows launcher
├── run.ps1                 # PowerShell launcher
├── requirements.txt        # Python dependency manifest
├── .env.example            # Environment variables template
├── .env                    # Local environment config (API keys)
├── services/
│   ├── ai_service.py       # Google Gemini 2.5 Flash resume tailoring
│   ├── ats_score.py        # Keyword extraction & ATS percentage scoring
│   ├── parser.py           # PDF (pdfplumber) & DOCX (python-docx) text extraction
│   ├── pdf_generator.py    # ReportLab ATS-compliant PDF resume builder
│   └── db.py               # SQLite history database utilities
├── uploads/                # Directory for uploaded resumes
└── generated/              # Output directory for generated PDF resumes
```

---

## ✨ Key Features
- **Smart Parsing**: Extracts text and hyperlinks from both PDF and DOCX files.
- **ATS Match Score**: Computes compatibility percentage against job requirements.
- **Skill Gap Analysis**: Identifies matched and missing industry skills in color-coded badges.
- **AI Tailoring**: Uses Gemini to rewrite experience bullet points in STAR format.
- **ATS-Ready PDF Export**: Generates clean, 0.5-inch margin, ATS-friendly PDFs with clickable hyperlinks.
