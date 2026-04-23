<template>
<div class="air-card">

  <div class="chart-section">
    <h2>🌬 Air Quality</h2>
    <Line :data="chartData" :options="chartOptions" v-if="loaded" ref="lineChart"/>
    <div v-else class="loading">Loading chart...</div>
  </div>

  <div class="score-section">
    <h1>{{ currentAqi }}</h1>
    <p>AQI Score</p>

    <div class="bar">
      <div class="bad"></div>
      <div class="good"></div>
    </div>

    <button class="status" :style="{ background: statusColor }">
      {{ status }}
    </button>
  </div>

</div>

<!-- ── Brushing & Linking Panel ── -->
<transition name="fade">
<div class="linked-panel" v-if="selectedPoint">
  <div class="linked-header">
    <span>📍 Sensor Snapshot — <strong>{{ selectedPoint.label }}</strong></span>
    <button class="close-link" @click="selectedPoint = null">✕</button>
  </div>
  <div class="linked-grid">
    <div class="linked-item" :class="eco2Class">
      <span class="linked-icon">🌬</span>
      <span class="linked-val">{{ selectedPoint.eco2 }} ppm</span>
      <span class="linked-lbl">eCO2</span>
    </div>
    <div class="linked-item" :class="tempClass">
      <span class="linked-icon">🌡</span>
      <span class="linked-val">{{ selectedPoint.temperature }}°C</span>
      <span class="linked-lbl">Temperature</span>
    </div>
    <div class="linked-item" :class="tvocClass">
      <span class="linked-icon">⚡</span>
      <span class="linked-val">{{ selectedPoint.tvoc }} ppb</span>
      <span class="linked-lbl">TVOC</span>
    </div>
    <div class="linked-item" :class="pm25Class">
      <span class="linked-icon">🌫</span>
      <span class="linked-val">{{ selectedPoint.pm25 }} µg/m³</span>
      <span class="linked-lbl">PM2.5</span>
    </div>
    <div class="linked-item" :class="healthClass">
      <span class="linked-icon">❤</span>
      <span class="linked-val">{{ selectedPoint.health }}%</span>
      <span class="linked-lbl">Health Score</span>
    </div>
    <div class="linked-item" :class="selectedPoint.fire ? 'danger' : 'safe-item'">
      <span class="linked-icon">🚨</span>
      <span class="linked-val">{{ selectedPoint.fire ? 'ALARM' : 'Clear' }}</span>
      <span class="linked-lbl">Fire Alarm</span>
    </div>
  </div>
</div>
</transition>
</template>

<script>
import { Line } from "vue-chartjs"
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
  Filler
} from "chart.js"

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, Filler)

const API_BASE = "http://localhost:8000"

export default {
  components: { Line },

  data() {
    return {
      loaded:        false,
      currentAqi:    0,
      status:        "Loading",
      selectedPoint: null,   // holds brushed data point
      reportRows:    [],     // full multi-sensor rows for linking
      chartData: {
        labels:   [],
        datasets: [{
          label:           "AQI",
          data:            [],
          borderColor:     "#3b82f6",
          pointRadius:     5,
          pointHoverRadius: 9,
          pointBackgroundColor: "#3b82f6",
          tension:         0.4,
          fill:            true,
          backgroundColor: (context) => {
            const chart = context.chart
            const { ctx, chartArea } = chart
            if (!chartArea) return null
            const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
            gradient.addColorStop(0,   "rgba(255,0,0,0.5)")
            gradient.addColorStop(0.4, "rgba(255,165,0,0.5)")
            gradient.addColorStop(0.7, "rgba(255,255,0,0.5)")
            gradient.addColorStop(1,   "rgba(0,200,0,0.5)")
            return gradient
          }
        }]
      },
      chartOptions: {
        responsive: true,
        plugins:    { legend: { display: false } },
        scales:     {
          y: {
            min: 0,
            ticks: { stepSize: 100 },
            grace: "10%"
          }
        }
      }
    }
  },

  computed: {
    statusColor() {
      if (this.status === "Good")      return "#22c55e"
      if (this.status === "Moderate")  return "#f59e0b"
      if (this.status === "Unhealthy") return "#ef4444"
      return "#7c3aed"
    },
    eco2Class()   { return this.selectedPoint?.eco2 > 800  ? "warn" : "safe-item" },
    tempClass()   { return this.selectedPoint?.temperature > 30 ? "warn" : "safe-item" },
    tvocClass()   { return this.selectedPoint?.tvoc > 300  ? "warn" : "safe-item" },
    pm25Class()   { return this.selectedPoint?.pm25 > 5    ? "warn" : "safe-item" },
    healthClass() { return this.selectedPoint?.health < 70 ? "warn" : "safe-item" }
  },

  async mounted() {
    await this.fetchData()
    setInterval(() => this.fetchData(), 10000)
  },

  methods: {
    async fetchData() {
      try {
        // Fetch AQI chart data
        const res  = await fetch(`${API_BASE}/api/air-quality`)
        const data = await res.json()

        // Also fetch full report rows for linking
        const repRes  = await fetch(`${API_BASE}/api/report-data?n=12`)
        const repData = await repRes.json()
        this.reportRows = repData

        const maxVal = Math.max(...data.aqi_values, 10)

        // Build chart options with onClick for brushing
        this.chartOptions = {
          responsive: true,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => `eCO2: ${ctx.raw} ppm — click to link all sensors`
              }
            }
          },
          scales: {
            y: {
              min: 0,
              max: Math.ceil(maxVal * 1.2),
              ticks: { stepSize: Math.ceil(maxVal / 5) }
            }
          },
          onClick: (event, elements) => {
            if (elements.length > 0) {
              const idx = elements[0].index
              this.brushPoint(idx, data.labels)
            }
          },
          onHover: (event, elements) => {
            event.native.target.style.cursor = elements.length ? "pointer" : "default"
          }
        }

        this.chartData = {
          ...this.chartData,
          labels:   data.labels,
          datasets: [{
            ...this.chartData.datasets[0],
            data: data.aqi_values
          }]
        }

        this.currentAqi = data.current_aqi
        this.status     = data.status
        this.loaded     = true
      } catch (e) {
        console.error("AirQuality fetch failed:", e)
      }
    },

    // ── Brushing: select a point and link all sensor values ──
    brushPoint(idx, labels) {
      const rows = this.reportRows
      if (!rows || !rows.eco2 || idx >= rows.eco2.length) return

      this.selectedPoint = {
        label:       labels[idx]         ?? "--:--",
        eco2:        rows.eco2[idx]      ?? 0,
        temperature: rows.temperature[idx] ?? 0,
        tvoc:        rows.tvoc[idx]      ?? 0,
        pm25:        rows.pm25[idx]      ?? 0,
        health:      rows.health_scores[idx] ?? 100,
        fire:        rows.eco2[idx] > 1100
      }
    }
  }
}
</script>

<style scoped>
.air-card {
  display: flex;
  gap: 40px;
  background: #f3f3f3;
  padding: 30px;
  border-radius: 15px;
  margin-top: 30px;
}
.chart-section { flex: 2; }
.score-section { flex: 1; text-align: center; }
.score-section h1 { font-size: 60px; margin: 0; }
.bar {
  display: flex;
  height: 20px;
  border-radius: 20px;
  overflow: hidden;
  margin-top: 20px;
}
.bad  { flex: 1; background: linear-gradient(to right, red, orange); }
.good { flex: 1; background: linear-gradient(to right, yellow, green); }
.status {
  margin-top: 15px;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 20px;
  cursor: default;
}
.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 150px;
  color: #888;
  font-size: 14px;
}

/* ── Linked Panel ── */
.linked-panel {
  background: white;
  border: 2px solid #3b82f6;
  border-radius: 14px;
  padding: 16px 20px;
  margin-top: 16px;
}
.linked-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  font-size: 14px;
  color: #333;
}
.close-link {
  background: none;
  border: none;
  font-size: 16px;
  cursor: pointer;
  color: #888;
}
.close-link:hover { color: #ef4444; }

.linked-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}
.linked-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 6px;
  border-radius: 10px;
  gap: 4px;
}
.linked-icon { font-size: 20px; }
.linked-val  { font-size: 15px; font-weight: bold; color: #333; }
.linked-lbl  { font-size: 11px; color: #888; }

.safe-item { background: #f0fff4; border: 1px solid #bbf7d0; }
.warn      { background: #fff7ed; border: 1px solid #fed7aa; }
.danger    { background: #fef2f2; border: 1px solid #fecaca; }

/* Transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s, transform 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>