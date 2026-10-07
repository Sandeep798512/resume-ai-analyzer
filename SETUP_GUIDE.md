# 📖 ResumeAI V2 — Step-by-Step Installation & Setup Guide

Welcome to **ResumeAI V2**! Follow this step-by-step guide to run, test, and deploy the application locally or in the cloud.

---

## 🛠️ 1. System Requirements

Before starting, ensure you have the following installed on your machine:

- **Python**: Version `3.10`, `3.11`, `3.12`, or `3.13` (Recommended)
- **Git**: Latest version
- **Code Editor**: VS Code (Recommended), PyCharm, or any text editor
- **Operating System**: Windows 10/11, macOS, or Linux

---

## 🚀 2. Local Setup Instructions (VS Code & Windows / Mac)

### Step 1: Open Terminal & Navigate to Project Directory
Open **VS Code Terminal** (`Ctrl + ~`) or standard Command Prompt / Terminal:

```bash
cd "C:\Users\Er. SANDEEP GAUD\Desktop\ai resume analyzer"
```

---

### Step 2: Create & Activate Virtual Environment

Creating an isolated Python virtual environment prevents library conflicts:

#### On Windows (PowerShell / Command Prompt):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

#### On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

*(When active, you will see `(venv)` prefix at the start of your command prompt).*

---

### Step 3: Install Required Python Packages

Install all core dependencies specified in `requirements.txt`:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Environment Variables Configuration (`.env`)

1. Copy the template file `.env.example` to `.env`:

#### On Windows:
```cmd
copy .env.example .env
```

#### On macOS / Linux:
```bash
cp .env.example .env
```

2. Open `.env` in VS Code and add your keys (Optional for Live Gemini LLM):

```env
SECRET_KEY=resumeai-v2-super-secret-key-2026
DATABASE_URL=sqlite:///database/resumeai.db
GEMINI_API_KEY=AIzaSy...  # Paste your free Google AI Studio Key here
```

> 💡 **Note**: If `GEMINI_API_KEY` is not provided, the platform automatically falls back to the local rule-based NLP engine without crashing!

---

### Step 5: Initialize Database & Seed Demo Data

Run the database schema setup and seed script to populate sample resumes, profiles, and job analyses:

```bash
python seed_demo.py
```

Output:
```text
Database schema initialized and migrated successfully.
Demo user & sample resume versions seeded successfully!
```

---

### Step 6: Run Automated Unit Tests

Verify that all system components, security rules, and TF-IDF matchers are 100% healthy:

```bash
python -m unittest discover -s tests
```

Expected Result:
```text
Ran 11 tests in 0.126s
OK
```

---

### Step 7: Launch Application Server

Start the local Flask development web server:

```bash
python app.py
```

Terminal Output:
```text
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 🐳 3. Running with Docker & Docker Compose (Optional)

If you prefer containerized deployment:

```bash
# Build and run containers
docker-compose up --build -d

# Check running status
docker-compose ps
```

Application will be accessible at `http://localhost:5000`.

---

## 🌐 4. Cloud Deployment on Render.com

1. Sign up on **[Render.com](https://render.com)** using GitHub.
2. Click **New +** $\rightarrow$ Select **Web Service**.
3. Connect your repository: `Sandeep798512/resume-ai-analyzer`.
4. Configure these fields:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variable:
   - `GEMINI_API_KEY` = *your_key*
6. Click **Create Web Service**.

Your live URL will be ready in ~30 seconds: `https://resume-ai-analyzer-egj8.onrender.com`.

---

## ❓ 5. Troubleshooting & FAQs

- **Q: `python` command is not recognized?**  
  *Fix*: Ensure Python is added to PATH during installation or use `py app.py`.

- **Q: `pip install` fails on psycopg2?**  
  *Fix*: We use `psycopg2-binary` in `requirements.txt` which compiles pre-built binaries automatically.

- **Q: Gemini Chatbot shows fallback response?**  
  *Fix*: Check your internet connection or verify your key at [Google AI Studio](https://aistudio.google.com/).

---

*Enjoy building, analyzing, and optimizing your resumes with ResumeAI V2!*
