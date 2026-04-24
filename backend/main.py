from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import httpx
import os
from data_service import DataService

load_dotenv()

app = FastAPI(title="Air Quality Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ds = DataService()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

# ── Data endpoints — all read from same snapshot ──────────────────
@app.get("/api/summary")
def get_summary():
    return ds.get_full_summary()

@app.get("/api/temperature")
def get_temperature():
    return ds.get_temperature()

@app.get("/api/co-level")
def get_co_level():
    return ds.get_co_level()

@app.get("/api/smoke-alert")
def get_smoke_alert():
    return ds.get_smoke_alert()

@app.get("/api/aqi-history")
def get_aqi_history():
    return ds.get_air_quality_chart()

@app.get("/api/air-quality")
def get_air_quality():
    return ds.get_air_quality_chart()

@app.get("/api/smoking-status")
def get_smoking_status():
    return ds.get_smoking_status()

@app.get("/api/health-insights")
def get_health_insights():
    return ds.get_health_insights()

@app.get("/api/cost-pollution")
def get_cost_pollution():
    return ds.get_cost_pollution()

@app.get("/api/report-data")
def get_report_data(n: int = 24):
    return ds.get_report_data(n)

# ── Groq Chat endpoint ────────────────────────────────────────────
@app.post("/api/chat")
async def chat(req: ChatRequest):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not set in .env")

    try:
        summary = ds.get_full_summary()
        smoke   = ds.get_smoke_alert()
        co      = ds.get_co_level()
        temp    = ds.get_temperature()
    except Exception:
        summary = smoke = co = temp = {}

    system_context = f"""You are an AI assistant for an Indoor Air Quality Monitoring Dashboard.
Current live sensor readings (all from the same dataset timestamp):
- Temperature   : {temp.get('temperature', 'N/A')} C
- Humidity      : {temp.get('humidity', 'N/A')} %
- CO2 (eCO2)    : {co.get('eco2_ppm', 'N/A')} ppm ({co.get('co_level', 'N/A')}% of danger threshold)
- TVOC Gas Level: {summary.get('tvoc_ppb', 'N/A')} ppb
- PM2.5         : {summary.get('pm25', 'N/A')} ug/m3
- PM1.0         : {summary.get('pm10', 'N/A')} ug/m3
- Fire Alarm    : {'YES DANGER' if smoke.get('active') else 'No'}
- Smoking       : {'YES' if summary.get('smoking_detected') else 'No'}
- Occupancy     : {'People present' if summary.get('motion_detected') else 'Room likely empty'}
- Health Score  : {summary.get('health_score', 'N/A')}%
Answer questions about air quality and health based on these readings. Be concise and helpful."""

    messages = [{"role": "system", "content": system_context}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model":    "llama-3.1-8b-instant",
        "messages": messages,
        "temperature":  0.7,
        "max_tokens":   512
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Groq API error: {resp.text}")

    data = resp.json()
    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        reply = "Sorry, I could not generate a response."

    return {"reply": reply}

@app.get("/api/chat/test")
def test_key():
    key = os.getenv("GROQ_API_KEY", "").strip()
    if not key:
        return {"status": "ERROR", "detail": "GROQ_API_KEY is empty"}
    return {"status": "OK", "detail": f"Groq key loaded — {key[:8]}..."}