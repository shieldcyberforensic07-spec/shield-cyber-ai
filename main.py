from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware
import requests
import sqlite3
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import datetime
import os

app = FastAPI(title="Shield Cyber Forensic Investigation")
from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <body style="background:#0f172a;color:white;font-family:Arial;text-align:center;padding:50px;">
    <h1>🛡 Shield Cyber Forensic Investigation</h1>
    <h3>AI System Running</h3>
    <p>Your Cyber Investigation AI server is live.</p>
    </body>
    </html>
    """

# ================= SECURITY =================
app.add_middleware(SessionMiddleware, secret_key="shield_super_secure_key_2026")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "shield123"

# ================= STATIC =================
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================= INPUT MODEL =================
class InputData(BaseModel):
    query: str

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("shield_cases.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        query TEXT,
        risk_score INTEGER,
        risk_level TEXT,
        report_file TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

def save_case(case_id, query, risk_score, risk_level, report_file):
    conn = sqlite3.connect("shield_cases.db")
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO cases (case_id, query, risk_score, risk_level, report_file, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        query,
        risk_score,
        risk_level,
        report_file,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# ================= RISK ENGINE =================
def calculate_risk(text):
    score = 0
    keywords = {
        "fraud": 25,
        "scam": 25,
        "phishing": 20,
        "malware": 20,
        "identity theft": 30,
        "ransomware": 30
    }
    for word, value in keywords.items():
        if word in text.lower():
            score += value
    return min(score, 100)

# ================= CASE ID =================
def generate_case_id():
    return f"SCFI-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

# ================= PDF REPORT =================
def generate_pdf(case_id, query, summary, risk_score, risk_level):
    filename = f"{case_id}.pdf"
    filepath = os.path.join(os.getcwd(), filename)
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4

    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(logo, 50, height - 120, width=100, height=100, mask='auto')

    c.setFont("Helvetica-Bold", 16)
    c.drawString(170, height - 60, "Shield Cyber Forensic Investigation")
    c.setFont("Helvetica", 11)
    c.drawString(170, height - 80, "Official AI Investigation Report")

    c.drawString(50, height - 150, f"Case ID: {case_id}")
    c.drawString(50, height - 170, f"Date: {datetime.datetime.now()}")
    c.drawString(50, height - 190, f"Risk Score: {risk_score}/100")
    c.drawString(50, height - 210, f"Risk Level: {risk_level}")

    text = c.beginText(50, height - 250)
    text.setFont("Helvetica", 11)
    text.textLines(f"""
Input Case:
{query}

AI Investigation Summary:
{summary}
""")
    c.drawText(text)
    c.save()
    return filename

# ================= LOGIN =================
@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <html><body style='background:#0f172a;color:white;text-align:center;padding:100px;font-family:Arial;'>
    <h2>Admin Login</h2>
    <form method="post">
        <input name="username" placeholder="Username" style="padding:10px;"><br><br>
        <input name="password" type="password" placeholder="Password" style="padding:10px;"><br><br>
        <button type="submit" style="padding:10px 20px;">Login</button>
    </form>
    </body></html>
    """

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["user"] = username
        return RedirectResponse("/dashboard", status_code=302)
    return HTMLResponse("<h3 style='color:red;'>Invalid Credentials</h3>")

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

# ================= ANALYZE =================
@app.post("/analyze")
def analyze(data: InputData, request: Request):
    if "user" not in request.session:
        return {"error": "Unauthorized"}

    # 🔹 Temporary AI Demo Response (Internet Deploy Friendly)
    ai_text = f"""
Preliminary AI Investigation Report

Case Overview:
The submitted case indicates potential cyber-related activity based on the provided information.

Risk Indicators:
Keywords detected may suggest fraud, phishing, or suspicious digital behavior.

Recommended Actions:
• Preserve all digital evidence
• Conduct detailed forensic imaging
• Perform IP & device trace analysis
• Consult legal cyber expert if required

Submitted Details:
{data.query}
"""

    risk_score = calculate_risk(data.query)

    if risk_score >= 70:
        level = "HIGH"
    elif risk_score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    case_id = generate_case_id()
    pdf_file = generate_pdf(case_id, data.query, ai_text, risk_score, level)

    save_case(case_id, data.query, risk_score, level, pdf_file)

    return {
        "case_id": case_id,
        "summary": ai_text,
        "risk_score": risk_score,
        "risk_level": level,
        "report_file": pdf_file
    }

    return {
        "case_id": case_id,
        "summary": ai_text,
        "risk_score": risk_score,
        "risk_level": level,
        "report_file": pdf_file
    }

# ================= DASHBOARD =================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=302)

    return """
    <html>
    <body style="background:#0f172a;color:white;font-family:Arial;">
    <div style="text-align:center;padding:20px;background:#111827;">
        <img src="/static/logo.png" width="120"><br>
        <h1>Shield Cyber Forensic Investigation</h1>
        <a href="/cases" style="color:#facc15;">Case History</a> |
        <a href="/logout" style="color:#ef4444;">Logout</a>
    </div>
    <div style="padding:30px;">
        <textarea id="query" rows="5" style="width:100%;padding:10px;"></textarea>
        <button onclick="analyze()" style="padding:10px;width:100%;margin-top:10px;background:#2563eb;color:white;border:none;">Analyze</button>
        <div id="result" style="margin-top:20px;background:#1e293b;padding:20px;border-radius:10px;"></div>
    </div>
    <script>
    async function analyze() {
        const query = document.getElementById("query").value;
        const response = await fetch("/analyze", {
            method:"POST",
            headers:{ "Content-Type":"application/json" },
            body:JSON.stringify({query:query})
        });
        const data = await response.json();
        document.getElementById("result").innerHTML =
        `<h3>Case ID: ${data.case_id}</h3>
         <p><b>Risk:</b> ${data.risk_level}</p>
         <p>${data.summary}</p>`;
    }
    </script>
    </body>
    </html>
    """

# ================= CASE HISTORY =================
@app.get("/cases", response_class=HTMLResponse)
def cases(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login", status_code=302)

    conn = sqlite3.connect("shield_cases.db")
    cursor = conn.cursor()
    cursor.execute("SELECT case_id, risk_level, created_at FROM cases ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    table = ""
    for r in rows:
        table += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

    return f"""
    <html><body style='background:#0f172a;color:white;padding:30px;font-family:Arial;'>
    <h1>Case History</h1>
    <table border='1' cellpadding='10'>
    <tr><th>Case ID</th><th>Risk</th><th>Date</th></tr>
    {table}
    </table>
    <br><a href="/dashboard" style="color:#facc15;">Back</a>
    </body></html>

    """
