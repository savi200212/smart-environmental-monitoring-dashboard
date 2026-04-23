<template>
<div class="alert-box" :class="alertClass">

  <h2>{{ alertTitle }}</h2>

  <p v-if="alertActive">
    Elevated CO₂ ({{ eco2Ppm }} ppm) and VOC levels detected!
  </p>
  <p v-else-if="smokeDetected">
    Smoke indicators detected — TVOC: {{ tvocPpb }} ppb
  </p>
  <p v-else>
    All sensor readings are within safe limits.
  </p>

  <div class="recommend">
    {{ recommendation }}
  </div>

</div>
</template>

<script>
const API_BASE = "http://localhost:8000"

export default {
  data() {
    return {
      alertActive:    false,
      smokeDetected:  false,
      eco2Ppm:        400,
      tvocPpb:        0,
      recommendation: "Monitoring environment..."
    }
  },

  computed: {
    alertClass() {
      if (this.alertActive)   return "fire"
      if (this.smokeDetected) return "smoke"
      return "safe"
    },
    alertTitle() {
      if (this.alertActive)   return "🚨 Fire / Smoke Alert"
      if (this.smokeDetected) return "🚬 Smoking Detected"
      return "✅ Air Quality Normal"
    }
  },

  async mounted() {
    await this.fetchData()
    setInterval(() => this.fetchData(), 6000)
  },

  methods: {
    async fetchData() {
      try {
        const res  = await fetch(`${API_BASE}/api/smoke-alert`)
        const data = await res.json()
        this.alertActive    = data.active
        this.smokeDetected  = data.smoke_detected
        this.eco2Ppm        = data.eco2_ppm
        this.tvocPpb        = data.tvoc_ppb ?? 0
        this.recommendation = data.recommendation
      } catch (e) {
        console.error("SmokeAlert fetch failed:", e)
      }
    }
  }
}
</script>

<style scoped>
.alert-box {
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 30px;
  transition: all 0.5s;
}

/* Fire alarm — red */
.fire {
  background: #f8e7e7;
  border: 2px solid red;
}

/* Smoking detected — orange */
.smoke {
  background: #fff3e0;
  border: 2px solid #f59e0b;
}

/* All safe — green */
.safe {
  background: #e8f5e9;
  border: 2px solid #22c55e;
}

.recommend {
  background: white;
  padding: 10px;
  border-radius: 8px;
  margin-top: 10px;
  font-size: 14px;
}
</style>