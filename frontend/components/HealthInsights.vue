<template>
<div class="health-card">
  <h2>Room Health & Insights</h2>

  <div class="health-grid">

    <!-- Left side -->
    <div class="people-card">
      <h4>Any people in the Room?</h4>

      <div class="people-status" :class="presence ? 'occupied' : 'empty'">
        <span class="presence-icon">{{ presence ? '✔' : '✕' }}</span>
        <p class="presence-label">{{ presence ? 'Human Presence Detected' : 'Room Appears Empty' }}</p>
      </div>

      <!-- Presence reason from TVOC + eCO2 logic -->
      <p class="presence-reason">{{ presenceReason }}</p>

      <div class="sensor-values">
        <p>PM2.5: <strong>{{ pm25 }} µg/m³</strong></p>
        <p>TVOC: <strong>{{ tvoc }} ppb</strong></p>
        <p>CO₂: <strong>{{ eco2 }} ppm</strong></p>
      </div>
    </div>

    <!-- Right side -->
    <div class="health-info">

      <p class="occupancy-note">
        {{ presence
          ? 'Occupancy detected via elevated CO₂ & TVOC levels (ASHRAE 62.1). Air quality monitoring adjusted.'
          : 'CO₂ and TVOC at baseline levels — room likely unoccupied.'
        }}
      </p>

      <div class="health-bar">
        <div class="health-fill" :style="{ width: healthScore + '%', background: healthGradient }"></div>
      </div>
      <p class="health-score">{{ healthScore }}% Healthy</p>

      <ul class="suggestions">
        <li v-for="(s, i) in suggestions" :key="i">{{ s }}</li>
      </ul>

    </div>

  </div>
</div>
</template>

<script>
const API_BASE = "http://localhost:8000"

export default {
  data() {
    return {
      healthScore:    65,
      presence:       false,
      presenceReason: "Analysing sensor data...",
      pm25:           0,
      tvoc:           0,
      eco2:           400,
      suggestions:    ["Loading health data..."]
    }
  },

  computed: {
    healthGradient() {
      if (this.healthScore >= 70) return "linear-gradient(to right, green, #a8d08d)"
      if (this.healthScore >= 40) return "linear-gradient(to right, orange, #ffd580)"
      return "linear-gradient(to right, red, orange)"
    }
  },

  async mounted() {
    await this.fetchData()
    setInterval(() => this.fetchData(), 10000)
  },

  methods: {
    async fetchData() {
      try {
        const res  = await fetch(`${API_BASE}/api/health-insights`)
        const data = await res.json()
        this.healthScore    = data.health_score
        this.presence       = data.presence
        this.presenceReason = data.presence_reason
        this.pm25           = data.pm25 ?? data.pm2_5 ?? 0
        this.tvoc           = data.tvoc_ppb
        this.eco2           = data.eco2_ppm
        this.suggestions    = data.suggestions
      } catch (e) {
        console.error("HealthInsights fetch failed:", e)
      }
    }
  }
}
</script>

<style scoped>
.health-card {
  background: #f5f5f5;
  padding: 25px;
  border-radius: 15px;
  margin-top: 30px;
}
.health-grid {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
}
.people-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}
.people-card h4 { margin-bottom: 12px; }

/* Presence status */
.people-status {
  padding: 10px;
  border-radius: 10px;
  margin-bottom: 8px;
}
.occupied { background: #f0fff4; }
.empty    { background: #fff5f5; }

.presence-icon {
  font-size: 36px;
  display: block;
}
.occupied .presence-icon { color: #22c55e; }
.empty    .presence-icon { color: #ef4444; }

.presence-label {
  font-size: 14px;
  font-weight: bold;
  margin: 4px 0 0;
}
.occupied .presence-label { color: #16a34a; }
.empty    .presence-label { color: #dc2626; }

/* Reason text from TVOC/CO2 */
.presence-reason {
  font-size: 11px;
  color: #777;
  font-style: italic;
  margin: 6px 0 10px;
  padding: 0 4px;
}

.sensor-values {
  margin-top: 12px;
  font-size: 13px;
  text-align: left;
}
.sensor-values p { margin: 4px 0; }

/* Right side */
.occupancy-note {
  font-size: 13px;
  color: #555;
  margin-bottom: 10px;
}
.health-bar {
  height: 15px;
  background: #ddd;
  border-radius: 10px;
  margin: 10px 0;
  overflow: hidden;
}
.health-fill {
  height: 15px;
  border-radius: 10px;
  transition: width 0.8s ease;
}
.health-score { font-weight: bold; }
.suggestions {
  margin-top: 10px;
  font-size: 14px;
}
</style>