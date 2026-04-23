# 🌬 Indoor Air Quality — Intelligent Visual Analytics System

> **SLIIT VAUED Assignment 02** | Visual Analytics & User Experience Design  
> A real-time indoor air quality monitoring dashboard with AI-powered conversational agent

![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883?style=flat-square&logo=vue.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square&logo=python)
![Groq](https://img.shields.io/badge/AI-Groq%20LLaMA%203.1-f55036?style=flat-square)
![Dataset](https://img.shields.io/badge/Dataset-Kaggle%2014%20Variables-20beff?style=flat-square)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Dataset](#dataset)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Dashboard Components](#dashboard-components)
- [AI Chatbot](#ai-chatbot)
- [Screenshots](#screenshots)

---

## Overview

This system is a full-stack intelligent visual analytics dashboard for indoor air quality monitoring. It integrates:

- **Real-time sensor data** from the Kaggle Smoke Detection Dataset (62,630 rows, 14 variables)
- **8 interactive Vue.js components** with live data refresh
- **AI-powered chatbot** (Groq LLaMA 3.1 8B) with live sensor context injection
- **Brushing & linking** between chart data points and multi-sensor snapshots
- **Sensor category filtering** for focused analysis
- **Historical report modal** with time-window drill-down and PDF export
- **WHO-based pollution cost model** for health impact quantification

---

## Features

| Feature | Description |
|---|---|
| 🚨 Smart Alerts | 3-state banner: Safe / Smoking Detected / Fire Alarm |
| 📈 Air Quality Chart | Live eCO2 trend with brushing & linking |
| 🌡 Temperature Card | Real-time temperature + humidity |
| ⚡ TVOC Gauge | Semicircular gauge with CSS needle |
| ❤ Health Insights | Composite health score + ASHRAE occupancy detection |
| 🚬 Smoking Status | Detection via TVOC + Raw Ethanol thresholds |
| 💰 Cost of Pollution | WHO 2021 PM-based health cost estimation |
| 📊 Report Modal | Historical charts with 6hr–1y time filters + PDF export |
| 🤖 AI Chatbot | Natural language queries with live sensor context |
| 🔍 Sensor Filter | Category filter bar for focused dashboard views |

---

## Dataset

**Smoke Detection Dataset** — Kaggle  
🔗 https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset

| Variable | Type | Description |
|---|---|---|
| UTC | Timestamp | Unix timestamp of reading |
| Temperature[C] | Float | Ambient room temperature |
| Humidity[%] | Float | Relative humidity |
| TVOC[ppb] | Float | Total Volatile Organic Compounds |
| eCO2[ppm] | Float | Estimated CO2 concentration |
| Raw H2 | Integer | Hydrogen sensor reading |
| Raw Ethanol | Integer | Ethanol sensor reading |
| Pressure[hPa] | Float | Atmospheric pressure |
| PM1.0 | Float | Fine particulate matter |
| PM2.5 | Float | Coarser particulate matter |
| NC0.5 / NC1.0 / NC2.5 | Float | Particle number concentrations |
| CNT | Integer | Sensor reading count |
| Fire Alarm | Binary | Ground truth fire label (0/1) |

**62,630 rows** — real IoT sensor readings

---

## Tech Stack

```
Frontend    →  Vue.js 3 + Chart.js + vue-chartjs
Backend     →  Python FastAPI + Pandas
AI Chatbot  →  Groq API (LLaMA 3.1 8B Instant)
PDF Export  →  jsPDF + html2canvas
Dataset     →  Kaggle CSV (62,630 rows)
```

---

## Project Structure

```
Web Based Dashboard/
│
├── backend/
│   ├── main.py                  # FastAPI server — 10 REST endpoints
│   ├── data_service.py          # Dataset loading, row cycling, metrics
│   ├── smoke_detection_iot.csv  # Kaggle dataset (download separately)
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # GROQ_API_KEY (create this)
│
└── src/
    ├── views/
    │   └── Dashboard.vue        # Main layout + sensor filter bar
    └── components/
        ├── SmokeAlert.vue       # 3-state alert banner
        ├── AirQualityChart.vue  # Line chart + brushing & linking
        ├── TemperatureCard.vue  # Temperature + humidity
        ├── COGauge.vue          # TVOC semicircular gauge
        ├── HealthInsights.vue   # Health score + occupancy
        ├── SmokingStatus.vue    # Smoking detection
        ├── CostPollution.vue    # WHO cost model
        ├── ReportModal.vue      # Historical charts + PDF export
        └── ChatBot.vue          # AI conversational agent
```

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- Node.js 18+
- Kaggle account (to download dataset)

### Step 1 — Download Dataset

1. Go to https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset
2. Download `smoke_detection_iot.csv`
3. Place it inside the `backend/` folder

### Step 2 — Get Free Groq API Key

1. Go to https://console.groq.com
2. Sign up → API Keys → Create Key
3. Create `backend/.env`:

```env
GROQ_API_KEY=gsk_your-key-here
```

### Step 3 — Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install fastapi uvicorn pandas httpx python-dotenv pydantic
```

### Step 4 — Frontend Setup

```bash
cd "Web Based Dashboard"
npm install
```

---

## Running the Application

### Terminal 1 — Start Backend

```bash
cd backend
venv\Scripts\activate        # Windows
uvicorn main:app --reload --port 8000
```

You should see:
```
Dataset loaded: 62630 rows — smoke_detection_iot.csv
INFO: Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 — Start Frontend

```bash
cd "Web Based Dashboard"
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/smoke-alert` | GET | Fire/smoke status + recommendation |
| `/api/air-quality` | GET | Last 12 eCO2 readings with timestamps |
| `/api/temperature` | GET | Temperature + humidity + status |
| `/api/co-level` | GET | TVOC as percentage + ppb |
| `/api/health-insights` | GET | Health score + occupancy + suggestions |
| `/api/smoking-status` | GET | Smoking detection from TVOC + ethanol |
| `/api/cost-pollution` | GET | WHO-based health cost estimate |
| `/api/report-data?n=24` | GET | N rows of all sensors for historical charts |
| `/api/summary` | GET | Full sensor summary (used for chatbot context) |
| `/api/chat` | POST | Send message + history, receive AI response |

Test backend: http://127.0.0.1:8000/api/summary

---

## Dashboard Components

### Sensor Filter Bar
Filter the dashboard by sensor category:
`All Sensors` | `Air Quality` | `Temperature` | `Gas / TVOC` | `Particulates` | `Health`

### Brushing & Linking
Click any data point on the Air Quality chart to reveal a linked snapshot showing all sensor values (eCO2, Temperature, TVOC, PM2.5, Health Score, Fire Alarm) at that exact timestamp — color-coded against safety thresholds.

### Report Modal
Click **Print Report** in the Cost of Pollution section to open the historical report modal with:
- Time filters: 6hr / 12hr / 1day / 1 week / 6 months / 1y
- 5 historical line charts: Air Quality, Temperature, TVOC, Health Score, PM2.5
- Print to PDF / Print to paper

---

## AI Chatbot

The chatbot uses **LLaMA 3.1 8B** via Groq API with **live context injection**:

1. Every message triggers a call to `/api/summary` to get current sensor readings
2. Sensor values are injected into the LLM system prompt
3. The LLM answers based on real data — not training data hallucinations
4. Conversation history (last 10 turns) maintained for multi-turn dialogue

### Example Queries

```
"Is the air quality safe right now?"
"What is the current CO2 level and is it dangerous?"
"Should I open windows?"
"Why is the smoking alert triggered?"
"What is the health cost of current pollution?"
```

---

## Key Design Decisions

### Occupancy Detection (ASHRAE 62.1)
Human presence is inferred from sensor data rather than a PIR sensor:
- `eCO2 > 600 ppm` → 200 ppm above outdoor baseline indicates human respiration
- `TVOC > 100 ppb` → lower bound of human metabolic VOC emission (German UBA guideline)

### WHO Cost Model
Pollution cost is calculated using WHO 2021 Air Quality Guidelines:
```
Excess PM2.5 = max(0, PM2.5 - 5 µg/m³)
Risk units   = Excess PM / 10
Daily cost   = Risk units × (Rs.15,000 / 8760) × 24
```

### Smoking Detection
Three independent signals trigger smoking detection:
- TVOC > 300 ppb (elevated VOC from smoke)
- PM2.5 > 35 µg/m³ (particulate matter from smoke)
- Raw Ethanol > 18,000 (ethanol signature in smoke)

---

## References

- WHO Global Air Quality Guidelines (2021)
- ASHRAE Standard 62.1-2022
- German Federal Environment Agency Guide Values for Indoor Air (2007)
- Smoke Detection Dataset — Kaggle (Deep Contractor, 2022)
- Tufte, E.R. — The Visual Display of Quantitative Information (2001)
