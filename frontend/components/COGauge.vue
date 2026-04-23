<template>
  <div class="card">
    <h3>⚡ Gas / TVOC Level in the Room</h3>

    <div class="gauge-container">
      <canvas ref="gaugeCanvas"></canvas>
      <canvas ref="needleCanvas" class="needle-layer"></canvas>
    </div>

    <div class="value">{{ coLevel }}% <span class="ppm">({{ tvocPpb }} ppb)</span></div>
    <div class="status" :class="statusClass">{{ statusText }}</div>
  </div>
</template>

<script>
import { Chart, ArcElement, Tooltip } from "chart.js"
Chart.register(ArcElement, Tooltip)

const API_BASE = "http://localhost:8000"

export default {
  data() {
    return {
      coLevel:  50,
      tvocPpb:  300,
      chart:    null,
      cx:       0,
      cy:       0
    }
  },

  computed: {
    statusText() {
      if (this.coLevel < 35) return "Low"
      if (this.coLevel < 65) return "Medium"
      return "High"
    },
    statusClass() {
      if (this.coLevel < 35) return "low"
      if (this.coLevel < 65) return "medium"
      return "high"
    }
  },

  async mounted() {
    await this.$nextTick()
    this.createGauge()
    setTimeout(async () => {
      const arc = this.chart.getDatasetMeta(0).data[0]
      this.cx = arc.x
      this.cy = arc.y
      this.syncNeedleCanvas()
      this.drawNeedle()
      await this.fetchData()
      setInterval(() => this.fetchData(), 8000)
    }, 600)
  },

  beforeUnmount() {
    if (this.chart) { this.chart.destroy(); this.chart = null }
  },

  methods: {
    createGauge() {
      const ctx = this.$refs.gaugeCanvas.getContext("2d")
      this.chart = new Chart(ctx, {
        type: "doughnut",
        data: {
          datasets: [{
            data:            [35, 30, 35],
            backgroundColor: ["#22c55e", "#f59e0b", "#ef4444"],
            borderWidth:     0
          }]
        },
        options: {
          rotation:      -90,
          circumference: 180,
          cutout:        "70%",
          animation:     { duration: 600 },
          plugins:       { legend: { display: false }, tooltip: { enabled: false } },
          events:        []
        }
      })
    },

    syncNeedleCanvas() {
      const gc = this.$refs.gaugeCanvas
      const nc = this.$refs.needleCanvas
      nc.width  = gc.width
      nc.height = gc.height
    },

    drawNeedle() {
      const nc  = this.$refs.needleCanvas
      const ctx = nc.getContext("2d")
      ctx.clearRect(0, 0, nc.width, nc.height)

      const angle = Math.PI + (this.coLevel / 100) * Math.PI

      ctx.save()
      ctx.translate(this.cx, this.cy)
      ctx.rotate(angle)
      ctx.beginPath()
      ctx.moveTo(0, -2)
      ctx.lineTo(80, 0)
      ctx.lineTo(0,  2)
      ctx.fillStyle = "#7c3aed"
      ctx.fill()
      ctx.restore()

      ctx.beginPath()
      ctx.arc(this.cx, this.cy, 5, 0, 2 * Math.PI)
      ctx.fillStyle = "#7c3aed"
      ctx.fill()
    },

    async fetchData() {
      try {
        const res  = await fetch(`${API_BASE}/api/co-level`)
        const data = await res.json()
        this.coLevel = data.co_level
        this.tvocPpb = data.tvoc_ppb ?? data.eco2_ppm
        this.drawNeedle()
      } catch (e) {
        console.error("Gas fetch failed:", e)
      }
    }
  }
}
</script>

<style scoped>
.card {
  background: #f5f5f5;
  padding: 25px;
  border-radius: 15px;
  text-align: center;
}
.gauge-container {
  position: relative;
  width: 220px;
  margin: auto;
}
.needle-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
.value {
  font-size: 28px;
  margin-top: 10px;
}
.ppm { font-size: 14px; color: #888; }
.status {
  margin-top: 8px;
  padding: 5px 15px;
  border-radius: 20px;
  display: inline-block;
  color: white;
}
.low    { background: #22c55e; }
.medium { background: #f59e0b; }
.high   { background: #ef4444; }
</style>