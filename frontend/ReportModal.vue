<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box" ref="reportBox">

      <!-- Header -->
      <div class="modal-header">
        <h2 class="modal-title">Air Quality Reports</h2>
        <button class="close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- Time Filters -->
      <div class="time-filters">
        <button
          v-for="f in filters"
          :key="f.label"
          :class="['filter-btn', { active: activeFilter === f.label }]"
          @click="setFilter(f)"
        >{{ f.label }}</button>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid" v-if="loaded">
        <div class="chart-box">
          <h4>Air Quality (eCO2 ppm)</h4>
          <Line :data="airQualityData" :options="lineOpts('ppm')" />
        </div>
        <div class="chart-box">
          <h4>Room Temperature (°C)</h4>
          <Line :data="temperatureData" :options="lineOpts('°C')" />
        </div>
        <div class="chart-box">
          <h4>Gas / TVOC Level (ppb)</h4>
          <Line :data="tvocData" :options="lineOpts('ppb')" />
        </div>
        <div class="chart-box">
          <h4>Room Health Score</h4>
          <Line :data="healthData" :options="lineOpts('%')" />
        </div>
        <div class="chart-box wide">
          <h4>Cost of Pollution (PM2.5)</h4>
          <Line :data="costData" :options="lineOpts('µg/m³')" />
        </div>
      </div>

      <div v-else class="loading-charts">Loading report data...</div>

      <!-- Actions (hidden in print/PDF) -->
      <div class="modal-actions no-print">
        <button class="action-btn pdf-btn" @click="printPDF">
          🖨 Print to PDF
        </button>
        <button class="action-btn paper-btn" @click="printPaper">
          🖨 Print to paper
        </button>
        <button class="action-btn back-btn" @click="$emit('close')">
          ← Back
        </button>
      </div>

    </div>
  </div>
</template>

<script>
import { Line } from "vue-chartjs"
import {
  Chart as ChartJS, LineElement, CategoryScale,
  LinearScale, PointElement, Tooltip, Legend, Filler
} from "chart.js"
import jsPDF from "jspdf"
import html2canvas from "html2canvas"

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend, Filler)

const API_BASE = "http://localhost:8000"

const FILTERS = [
  { label: "6hr",      n: 6  },
  { label: "12hr",     n: 12 },
  { label: "1day",     n: 24 },
  { label: "1 month",  n: 48 },
  { label: "1 week",   n: 72 },
  { label: "6 months", n: 96 },
  { label: "1y",       n: 120 }
]

const makeDataset = (label, data, color) => ({
  label,
  data,
  borderColor:     color,
  backgroundColor: color + "33",
  borderWidth:     2,
  pointRadius:     3,
  tension:         0.4,
  fill:            true
})

export default {
  components: { Line },
  emits: ["close"],

  data() {
    return {
      loaded:        false,
      filters:       FILTERS,
      activeFilter:  "1day",
      labels:        [],
      airQualityData:  { labels: [], datasets: [] },
      temperatureData: { labels: [], datasets: [] },
      tvocData:        { labels: [], datasets: [] },
      healthData:      { labels: [], datasets: [] },
      costData:        { labels: [], datasets: [] }
    }
  },

  async mounted() {
    await this.fetchReport(24)
  },

  methods: {
    lineOpts(unit) {
      return {
        responsive:          true,
        maintainAspectRatio: false,  // allow explicit height control via CSS
        plugins: { legend: { display: false } },
        scales:  {
          x: { ticks: { maxTicksLimit: 6, font: { size: 10 } } },
          y: { ticks: { font: { size: 10 } }, title: { display: true, text: unit, font: { size: 10 } } }
        }
      }
    },

    setFilter(f) {
      this.activeFilter = f.label
      this.loaded = false
      this.fetchReport(f.n)
    },

    async fetchReport(n) {
      try {
        const res  = await fetch(`${API_BASE}/api/report-data?n=${n}`)
        const data = await res.json()
        const lbl  = data.labels

        this.airQualityData  = { labels: lbl, datasets: [makeDataset("eCO2",        data.eco2,          "#3b82f6")] }
        this.temperatureData = { labels: lbl, datasets: [makeDataset("Temperature", data.temperature,   "#ef4444")] }
        this.tvocData        = { labels: lbl, datasets: [makeDataset("TVOC",        data.tvoc,          "#f59e0b")] }
        this.healthData      = { labels: lbl, datasets: [makeDataset("Health",      data.health_scores, "#22c55e")] }
        this.costData        = { labels: lbl, datasets: [makeDataset("PM2.5",       data.pm25,          "#8b5cf6")] }

        this.loaded = true
      } catch (e) {
        console.error("Report fetch failed:", e)
      }
    },

    async printPDF() {
      const el      = this.$refs.reportBox
      const actions = el.querySelector(".no-print")

      // Hide buttons before capture
      if (actions) actions.style.display = "none"

      // Scroll to top before capture so nothing is cut off
      el.scrollTop = 0
      await new Promise(r => setTimeout(r, 300))

      const canvas = await html2canvas(el, {
        scale:       1.5,
        useCORS:     true,
        scrollY:     0,
        windowWidth: el.scrollWidth,
        width:       el.scrollWidth,
        height:      el.scrollHeight   // capture full height not just visible area
      })

      const img = canvas.toDataURL("image/png")
      const pdf = new jsPDF("p", "mm", "a4")
      const pageW = pdf.internal.pageSize.getWidth()
      const pageH = pdf.internal.pageSize.getHeight()
      const imgW  = pageW
      const imgH  = (canvas.height * pageW) / canvas.width

      // If content is taller than one page, add multiple pages
      let yPos = 0
      let remaining = imgH
      while (remaining > 0) {
        pdf.addImage(img, "PNG", 0, -yPos, imgW, imgH)
        remaining -= pageH
        yPos      += pageH
        if (remaining > 0) pdf.addPage()
      }

      pdf.save("AirQualityReport.pdf")

      // Restore buttons after capture
      if (actions) actions.style.display = ""
    },

    printPaper() {
      window.print()
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: #fffef5;
  border-radius: 16px;
  padding: 28px;
  width: 820px;
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.modal-title {
  color: #22c55e;
  font-size: 22px;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

/* Time filter pills */
.time-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 22px;
}

.filter-btn {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1.5px solid #ccc;
  background: white;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.filter-btn:hover:not(.active) {
  border-color: #3b82f6;
  color: #3b82f6;
}

/* Charts */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 22px;
}

.chart-box {
  border: 1.5px solid #ef4444;
  border-radius: 10px;
  padding: 14px;
  background: white;
}

.chart-box canvas {
  height: 160px !important;
}

.chart-box.wide {
  grid-column: 1 / -1;
}

.chart-box.wide canvas {
  height: 180px !important;
}

.chart-box h4 {
  color: #3b82f6;
  margin: 0 0 10px;
  font-size: 14px;
}

.loading-charts {
  text-align: center;
  padding: 40px;
  color: #888;
}

/* Action buttons */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid #eee;
  position: sticky;
  bottom: 0;
  background: #fffef5;
  z-index: 10;
}

.action-btn {
  padding: 10px 22px;
  border-radius: 8px;
  border: 1.5px solid #ccc;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.pdf-btn, .paper-btn {
  background: white;
  color: #333;
}

.pdf-btn:hover, .paper-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.back-btn {
  background: #22c55e;
  color: white;
  border-color: #22c55e;
}

.back-btn:hover { background: #16a34a; }

@media print {
  .no-print { display: none !important; }
}
</style>