from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
    <html>
    <head>
        <title>Shield Cyber Forensic Investigation</title>
    </head>
    <body style="background:#0f172a;color:white;font-family:Arial;text-align:center;padding:50px;">
        <h1>🛡 Shield Cyber Forensic Investigation</h1>
        <h3>AI Investigation Dashboard</h3>

        <textarea id="case" placeholder="Enter cyber complaint details"
        style="width:80%;height:120px;padding:10px;"></textarea>

        <br><br>

        <button onclick="analyze()" 
        style="padding:10px 20px;background:#2563eb;color:white;border:none;">
        Analyze Case
        </button>

        <div id="result" style="margin-top:30px;font-size:18px;"></div>

        <script>
        async function analyze(){
            const text = document.getElementById("case").value;

            let res = await fetch("/analyze",{
                method:"POST",
                headers:{"Content-Type":"application/json"},
                body:JSON.stringify({query:text})
            });

            let data = await res.json();

            document.getElementById("result").innerHTML =
            "<b>Risk Level:</b> "+data.risk_level+"<br>"+data.summary;
        }
        </script>
    </body>
    </html>
    """

from pydantic import BaseModel

class InputData(BaseModel):
    query:str


@app.post("/analyze")
def analyze(data:InputData):

    text = data.query.lower()

    risk="LOW"

    if "fraud" in text or "scam" in text:
        risk="HIGH"

    elif "suspicious" in text:
        risk="MEDIUM"

    summary = "Preliminary cyber forensic analysis suggests potential digital risk. Further investigation recommended."

    return {
        "risk_level":risk,
        "summary":summary
    }
