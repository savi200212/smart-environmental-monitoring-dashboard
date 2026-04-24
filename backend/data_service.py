"""
data_service.py
───────────────
Dataset: Smoke Detection Dataset (Kaggle)
https://www.kaggle.com/datasets/deepcontractor/smoke-detection-dataset

14 Variables:
  UTC            — timestamp
  Temperature[C] — ambient temperature
  Humidity[%]    — relative humidity
  TVOC[ppb]      — Total Volatile Organic Compounds
  eCO2[ppm]      — estimated CO2
  Raw H2         — raw hydrogen sensor
  Raw Ethanol    — ethanol sensor
  Pressure[hPa]  — air pressure
  PM1.0          — fine particulate matter
  PM2.5          — coarser particulate matter
  NC0.5          — particle number concentration
  NC1.0          — particle number concentration
  NC2.5          — particle number concentration
  CNT            — sensor reading count
  Fire Alarm     — ground truth label (0/1)

SNAPSHOT ARCHITECTURE:
  All components read from a single shared snapshot row that advances
  every 8 seconds via advance_snapshot(). This ensures all dashboard
  components display temporally consistent data from the same dataset row.
"""

import os
import time
import pandas as pd

CSV_PATH = os.path.join(os.path.dirname(__file__), "smoke_detection_iot.csv")

# ── Calibrated Thresholds ─────────────────────────────────────────
TVOC_MODERATE  = 300
TVOC_HIGH      = 1000
TVOC_DANGER    = 2500

ECO2_MODERATE  = 800
ECO2_HIGH      = 1100
ECO2_DANGER    = 2000

PM25_MODERATE  = 12
PM25_HIGH      = 35
PM25_DANGER    = 75

PM10_MODERATE  = 20
PM10_HIGH      = 50

TEMP_COOL      = 18
TEMP_WARM      = 26
TEMP_HOT       = 32

# ── WHO 2021 Cost Model ───────────────────────────────────────────
WHO_PM25_LIMIT              = 5.0
WHO_PM10_LIMIT              = 15.0
ANNUAL_HEALTH_COST_RS       = 15000
HOURS_PER_YEAR              = 8760
COST_PER_RISK_UNIT_PER_HOUR = ANNUAL_HEALTH_COST_RS / HOURS_PER_YEAR / 10
COST_PER_PM                 = 0.05  # legacy alias


class DataService:

    def __init__(self):
        self._df            = None
        self._pointer       = 0          # current snapshot row index
        self._snapshot      = {}         # current shared row — all components read this
        self._history       = []         # last 120 rows for chart history
        self._last_advance  = 0.0        # timestamp of last pointer advance
        self._load_data()
        self._advance_snapshot()         # seed first snapshot on startup

    # ── Data Loading ──────────────────────────────────────────────

    def _load_data(self):
        if os.path.exists(CSV_PATH):
            try:
                self._df = pd.read_csv(CSV_PATH)
                self._df.columns = self._df.columns.str.strip()
                self._df.rename(columns={
                    "Temperature[C]": "Temperature",
                    "Humidity[%]":    "Humidity",
                    "TVOC[ppb]":      "TVOC",
                    "eCO2[ppm]":      "eCO2",
                    "Raw H2":         "RawH2",
                    "Raw Ethanol":    "RawEthanol",
                    "Pressure[hPa]":  "Pressure",
                    "Fire Alarm":     "FireAlarm"
                }, inplace=True)
                print(f"Dataset loaded: {len(self._df)} rows — smoke_detection_iot.csv")
                return
            except Exception as e:
                print(f"Could not read smoke_detection_iot.csv: {e}")
        raise FileNotFoundError(
            "smoke_detection_iot.csv not found. Place it in the backend/ folder."
        )

    # ── Snapshot Management ───────────────────────────────────────

    def _advance_snapshot(self):
        """Move pointer to next row and update shared snapshot + history."""
        self._pointer = (self._pointer + 1) % len(self._df)
        self._snapshot = self._df.iloc[self._pointer].to_dict()
        self._last_advance = time.time()

        # Keep rolling history of last 120 rows
        self._history.append(self._snapshot.copy())
        if len(self._history) > 120:
            self._history.pop(0)

    def maybe_advance(self, interval_seconds=3):
        """
        Advance the snapshot if enough time has passed.
        Called by every API endpoint — advances at most once per interval.
        This means all components see the SAME row regardless of
        which endpoint they call.
        """
        if time.time() - self._last_advance >= interval_seconds:
            self._advance_snapshot()

    def _get_snapshot(self):
        """Return current shared snapshot row."""
        return self._snapshot

    def _get_history(self, n=12):
        """Return last N rows from rolling history."""
        return self._history[-n:] if len(self._history) >= n else self._history

    # ── Derived Metrics ───────────────────────────────────────────

    @staticmethod
    def _tvoc_to_percent(tvoc):
        """
        Map TVOC to gauge percentage using dataset-relative scale.
        This dataset's TVOC range is 0-100 ppb in normal conditions,
        spiking to 2500+ during fire events.
        Scale: 0-100ppb = 0-40% (normal range visible on gauge)
               100-500ppb = 40-70% (elevated)
               500+ ppb   = 70-100% (dangerous)
        """
        t = float(tvoc)
        if t <= 100:
            pct = (t / 100) * 40
        elif t <= 500:
            pct = 40 + ((t - 100) / 400) * 30
        else:
            pct = 70 + ((t - 500) / 2000) * 30
        return min(100, max(0, int(pct)))

    @staticmethod
    def _eco2_to_aqi(eco2):
        return int(float(eco2))

    @staticmethod
    def _health_score(row):
        score = 100
        tvoc  = float(row.get("TVOC",     0))
        eco2  = float(row.get("eCO2",     400))
        pm25  = float(row.get("PM2.5",    0))
        fire  = int(row.get("FireAlarm",  0))

        if tvoc > TVOC_MODERATE:  score -= 15
        if tvoc > TVOC_HIGH:      score -= 20
        if tvoc > TVOC_DANGER:    score -= 20
        if eco2 > ECO2_MODERATE:  score -= 10
        if eco2 > ECO2_HIGH:      score -= 15
        if pm25 > PM25_MODERATE:  score -= 10
        if pm25 > PM25_HIGH:      score -= 15
        if fire == 1:             score -= 25
        return max(0, score)

    @staticmethod
    def _is_fire_alarm(row):
        return int(row.get("FireAlarm", 0)) == 1

    @staticmethod
    def _is_occupied(row):
        """
        ASHRAE 62.1: eCO2 > 600ppm above outdoor baseline (~400ppm)
        indicates human respiration. TVOC > 100ppb indicates metabolic activity.
        """
        eco2 = float(row.get("eCO2", 400))
        tvoc = float(row.get("TVOC", 0))
        return eco2 > 600 or tvoc > 100

    @staticmethod
    def _is_smoking(row):
        """
        Smoking detection using three signals calibrated to dataset ranges:
        1. TVOC > 300 ppb — elevated VOC from smoke
        2. PM2.5 > 12 µg/m³ — elevated particulates from smoke
        3. eCO2 > 1000 ppm AND TVOC > 50 ppb — combined elevated gases
           indicating combustion products (not just human respiration)
        Raw Ethanol excluded — its baseline in this dataset (~19000-20500)
        makes simple threshold detection unreliable.
        """
        tvoc = float(row.get("TVOC",  0))
        pm25 = float(row.get("PM2.5", 0))
        eco2 = float(row.get("eCO2",  400))
        # Direct high TVOC or PM2.5
        if tvoc > TVOC_MODERATE or pm25 > PM25_HIGH:
            return True
        # Combined signal: elevated CO2 + any TVOC above idle
        if eco2 > 1000 and tvoc > 50:
            return True
        return False

    # ── API Methods ───────────────────────────────────────────────
    # Every method calls maybe_advance() first — pointer advances at
    # most once per 8 seconds regardless of how many components call.

    def get_air_quality_chart(self):
        self.maybe_advance()
        history = self._get_history(12)

        labels = []
        for row in history:
            try:
                ts = pd.to_datetime(row.get("UTC"), unit="s")
                labels.append(ts.strftime("%H:%M:%S"))
            except Exception:
                labels.append("--:--")

        aqi_values = [self._eco2_to_aqi(r.get("eCO2", 400)) for r in history]
        current    = aqi_values[-1] if aqi_values else 400

        if current < 800:    status = "Good"
        elif current < 1100: status = "Moderate"
        elif current < 1500: status = "Unhealthy"
        else:                status = "Dangerous"

        return {
            "labels":      labels,
            "aqi_values":  aqi_values,
            "current_aqi": current,
            "status":      status
        }

    def get_co_level(self):
        self.maybe_advance()
        row     = self._get_snapshot()
        tvoc    = float(row.get("TVOC", 0))
        eco2    = float(row.get("eCO2", 400))
        percent = self._tvoc_to_percent(tvoc)

        if percent < 35:   level = "Low"
        elif percent < 65: level = "Medium"
        else:              level = "High"

        return {
            "eco2_ppm": round(eco2, 1),
            "co_level": percent,
            "tvoc_ppb": round(tvoc, 1),
            "status":   level
        }

    def get_temperature(self):
        self.maybe_advance()
        row  = self._get_snapshot()
        temp = round(float(row.get("Temperature", 22)), 1)
        hum  = round(float(row.get("Humidity",    50)), 1)

        if temp < TEMP_WARM:  status = "cool"
        elif temp < TEMP_HOT: status = "warm"
        else:                 status = "hot"

        return {"temperature": temp, "humidity": hum, "status": status}

    def get_smoke_alert(self):
        self.maybe_advance()
        row     = self._get_snapshot()
        fire    = self._is_fire_alarm(row)
        smoking = self._is_smoking(row)
        eco2    = float(row.get("eCO2",  400))
        tvoc    = float(row.get("TVOC",  0))
        pm25    = float(row.get("PM2.5", 0))

        if fire:
            rec = "FIRE ALARM! Dangerous conditions detected. Evacuate immediately!"
        elif smoking:
            rec = "Smoke indicators detected — ventilate the room immediately."
        elif tvoc > TVOC_HIGH or eco2 > ECO2_HIGH:
            rec = "High gas levels detected. Open windows and increase ventilation."
        elif pm25 > PM25_HIGH:
            rec = "High particulate matter. Use air purifier and limit exposure."
        else:
            rec = "All readings within safe limits. No action required."

        return {
            "active":         fire,
            "fire_alarm":     fire,
            "eco2_ppm":       round(eco2, 1),
            "tvoc_ppb":       round(tvoc, 1),
            "pm25":           round(pm25, 1),
            "smoke_detected": fire or smoking,
            "recommendation": rec
        }

    def get_smoking_status(self):
        self.maybe_advance()
        row     = self._get_snapshot()
        smoking = self._is_smoking(row)
        tvoc    = float(row.get("TVOC",        0))
        pm25    = float(row.get("PM2.5",       0))
        eth     = float(row.get("RawEthanol",  0))

        return {
            "smoking_detected": smoking,
            "tvoc_ppb":         round(tvoc, 1),
            "pm25":             round(pm25, 1),
            "ethanol_raw":      round(eth,  1)
        }

    def get_health_insights(self):
        self.maybe_advance()
        row      = self._get_snapshot()
        score    = self._health_score(row)
        eco2     = float(row.get("eCO2",     400))
        tvoc     = float(row.get("TVOC",     0))
        pm25     = float(row.get("PM2.5",    0))
        fire     = int(row.get("FireAlarm",  0))
        occupied = self._is_occupied(row)

        if eco2 > 600 and tvoc > 100:
            presence_reason = f"High CO2 ({round(eco2)}ppm) & TVOC ({round(tvoc)}ppb) indicate occupancy"
        elif eco2 > 600:
            presence_reason = f"Elevated CO2 ({round(eco2)}ppm) indicates human presence"
        elif tvoc > 100:
            presence_reason = f"Elevated TVOC ({round(tvoc)}ppb) indicates human activity"
        else:
            presence_reason = f"CO2 ({round(eco2)}ppm) & TVOC ({round(tvoc)}ppb) at baseline — room likely empty"

        suggestions = []
        if fire:                   suggestions.append("FIRE ALARM active! Evacuate immediately.")
        if tvoc  > TVOC_HIGH:      suggestions.append("TVOC dangerously high — ventilate immediately.")
        if eco2  > ECO2_MODERATE:  suggestions.append("CO2 elevated — open windows for fresh air.")
        if pm25  > PM25_MODERATE:  suggestions.append("Fine particles detected — use an air purifier.")
        if occupied and eco2 > ECO2_MODERATE:
            suggestions.append("People detected in poor air quality — take action immediately.")
        if not suggestions:
            suggestions = [
                "Air quality is good. Continue monitoring.",
                "Maintain regular ventilation schedules.",
                "Avoid smoking in enclosed spaces."
            ]

        return {
            "health_score":    score,
            "presence":        occupied,
            "presence_reason": presence_reason,
            "eco2_ppm":        round(eco2, 1),
            "tvoc_ppb":        round(tvoc, 1),
            "pm25":            round(pm25, 1),
            "suggestions":     suggestions
        }

    def get_cost_pollution(self):
        self.maybe_advance()
        row  = self._get_snapshot()
        pm25 = float(row.get("PM2.5", 0))
        pm10 = float(row.get("PM1.0", 0))

        # Two-part cost model:
        # Part 1 — Baseline exposure: Rs. 2.00/µg/m³ PM2.5, Rs. 0.80/µg/m³ PM1.0
        baseline_cost = (pm25 * 2.00 + pm10 * 0.80)

        # Part 2 — Excess above WHO safe limits
        excess_pm25 = max(0.0, pm25 - WHO_PM25_LIMIT)
        excess_pm10 = max(0.0, pm10 - WHO_PM10_LIMIT)
        risk_units  = (excess_pm25 + excess_pm10) / 10.0
        excess_cost = risk_units * COST_PER_RISK_UNIT_PER_HOUR * 24

        daily   = round(baseline_cost + excess_cost, 2)
        monthly = round(daily * 30, 2)

        if pm25 <= WHO_PM25_LIMIT: risk_level = "Safe"
        elif pm25 <= 15:           risk_level = "Moderate"
        elif pm25 <= 35:           risk_level = "Unhealthy"
        else:                      risk_level = "Hazardous"

        return {
            "pm25":            round(pm25, 3),
            "pm10":            round(pm10, 3),
            "excess_pm25":     round(excess_pm25, 3),
            "excess_pm10":     round(excess_pm10, 3),
            "risk_level":      risk_level,
            "daily_cost_rs":   daily,
            "monthly_cost_rs": monthly,
            "who_pm25_limit":  WHO_PM25_LIMIT,
            "who_pm10_limit":  WHO_PM10_LIMIT
        }

    def get_full_summary(self):
        self.maybe_advance()
        row  = self._get_snapshot()
        eco2 = float(row.get("eCO2",        400))
        tvoc = float(row.get("TVOC",        0))
        pm25 = float(row.get("PM2.5",       0))
        pm10 = float(row.get("PM1.0",       0))
        temp = float(row.get("Temperature", 22))
        hum  = float(row.get("Humidity",    50))
        pres = float(row.get("Pressure",    1013))
        h2   = float(row.get("RawH2",       0))
        eth  = float(row.get("RawEthanol",  0))
        fire = int(row.get("FireAlarm",     0))

        return {
            "temperature":     round(temp, 1),
            "humidity":        round(hum,  1),
            "pressure":        round(pres, 1),
            "eco2_ppm":        round(eco2, 1),
            "tvoc_ppb":        round(tvoc, 1),
            "pm25":            round(pm25, 1),
            "pm10":            round(pm10, 1),
            "raw_h2":          round(h2,   1),
            "raw_ethanol":     round(eth,  1),
            "mq7_raw":         round(tvoc, 1),
            "mq135_raw":       round(eco2, 1),
            "dust_density":    round(pm25, 1),
            "motion_detected": self._is_occupied(row),
            "aqi_score":       self._eco2_to_aqi(eco2),
            "fire_alarm":      bool(fire),
            "smoking_detected":self._is_smoking(row),
            "health_score":    self._health_score(row),
            "cost_rs":         round((pm25 * 2.00 + pm10 * 0.80), 2),
        }

    def get_report_data(self, n=24):
        """Return last N rows from rolling history for report charts."""
        self.maybe_advance()
        history = self._get_history(n)

        labels = []
        for row in history:
            try:
                ts = pd.to_datetime(row.get("UTC"), unit="s")
                labels.append(ts.strftime("%H:%M:%S"))
            except Exception:
                labels.append("--:--")

        return {
            "labels":        labels,
            "eco2":          [int(r.get("eCO2",        400)) for r in history],
            "temperature":   [round(float(r.get("Temperature", 22)), 1) for r in history],
            "tvoc":          [round(float(r.get("TVOC",         0)),  1) for r in history],
            "pm25":          [round(float(r.get("PM2.5",        0)),  3) for r in history],
            "health_scores": [self._health_score(r) for r in history]
        }