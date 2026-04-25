<template>
  <div class="cost-section">

    <div class="cost-card">
      <h3>Cost of Pollution</h3>

      <div class="cost-grid">
        <div class="cost-item">
          <span class="cost-label">Daily Estimate</span>
          <div class="cost-value">Rs. {{ dailyCost }}</div>
        </div>
        <div class="cost-item">
          <span class="cost-label">Monthly Estimate</span>
          <div class="cost-value">Rs. {{ monthlyCost }}</div>
        </div>
      </div>

      <!-- WHO info row -->
      <div class="who-row">
        <div class="who-item">
          <span class="who-label">PM2.5</span>
          <span class="who-val">{{ pm25 }} µg/m³</span>
          <span class="who-limit">(WHO limit: 5 µg/m³)</span>
        </div>
        <div class="who-item">
          <span class="who-label">PM1.0</span>
          <span class="who-val">{{ pm10 }} µg/m³</span>
          <span class="who-limit">(WHO limit: 15 µg/m³)</span>
        </div>
        <div class="who-item">
          <span class="who-label">Risk Level</span>
          <span class="risk-badge" :class="riskClass">{{ riskLevel }}</span>
        </div>
      </div>

      <p class="formula-note">
        Based on WHO 2021 Air Quality Guidelines — cost estimated from
        excess PM exposure × Sri Lanka avg. health cost (Rs. 15,000/year)
      </p>
    </div>

    <div class="report-card">
      <button @click="showReport = true" class="print-btn">
        🖨 Print Report
      </button>
    </div>

    <!-- Report Modal -->
    <ReportModal v-if="showReport" @close="showReport = false" />

  </div>
</template>

<script>
import ReportModal from "./ReportModal.vue"

const API_BASE = "http://localhost:8000"

export default {
  components: { ReportModal },

  data() {
    return {
      dailyCost:   "0.00",
      monthlyCost: "0.00",
      pm25:        "0.000",
      pm10:        "0.000",
      riskLevel:   "Safe",
      showReport:  false
    }
  },

  computed: {
    riskClass() {
      if (this.riskLevel === "Safe")      return "safe"
      if (this.riskLevel === "Moderate")  return "moderate"
      if (this.riskLevel === "Unhealthy") return "unhealthy"
      return "hazardous"
    }
  },

  async mounted() {
    await this.fetchData()
    setInterval(() => this.fetchData(), 15000)
  },

  methods: {
    async fetchData() {
      try {
        const res  = await fetch(`${API_BASE}/api/cost-pollution`)
        const data = await res.json()
        this.dailyCost   = data.daily_cost_rs.toFixed(2)
        this.monthlyCost = data.monthly_cost_rs.toFixed(2)
        this.pm25        = data.pm25
        this.pm10        = data.pm10
        this.riskLevel   = data.risk_level
      } catch (e) {
        console.error("Cost fetch failed:", e)
      }
    }
  }
}
</script>

<style scoped>
.cost-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-top: 30px;
}
.cost-card {
  background: #f5f5f5;
  padding: 25px;
  border-radius: 15px;
  text-align: center;
}
.cost-grid {
  display: flex;
  justify-content: space-around;
  margin: 15px 0;
}
.cost-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.cost-label { font-size: 12px; color: #888; }
.cost-value {
  font-size: 24px;
  color: #2b7cff;
  font-weight: bold;
}

/* WHO row */
.who-row {
  display: flex;
  justify-content: space-around;
  margin: 12px 0;
  padding: 12px;
  background: white;
  border-radius: 10px;
  gap: 10px;
}
.who-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
}
.who-label {
  font-size: 11px;
  color: #888;
  font-weight: bold;
}
.who-val {
  font-size: 15px;
  font-weight: bold;
  color: #333;
}
.who-limit {
  font-size: 10px;
  color: #aaa;
}

/* Risk badge */
.risk-badge {
  padding: 3px 12px;
  border-radius: 12px;
  color: white;
  font-size: 13px;
  font-weight: bold;
}
.safe      { background: #22c55e; }
.moderate  { background: #f59e0b; }
.unhealthy { background: #ef4444; }
.hazardous { background: #7c3aed; }

.formula-note {
  font-size: 11px;
  color: #999;
  margin-top: 10px;
  font-style: italic;
}

.report-card {
  display: flex;
  align-items: center;
  justify-content: center;
}
.print-btn {
  background: #2b7cff;
  color: white;
  border: none;
  padding: 12px 25px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 15px;
  transition: background 0.2s;
}
.print-btn:hover { background: #1a6aee; }
</style>