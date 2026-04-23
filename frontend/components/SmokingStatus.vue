<template>

<div class="smoke-section">

  <div class="smoke-card" :class="smokingDetected ? 'smoking' : 'safe-inactive'">
    <h3>🚨 Someone Smoking</h3>
    <p>{{ smokingDetected ? "Alert Triggered" : "Not Detected" }}</p>
    <small v-if="smokingDetected">TVOC: {{ tvocPpb }} ppb</small>
  </div>

  <div class="smoke-card" :class="!smokingDetected ? 'safe' : 'safe-inactive'">
    <h3>🙂 Not Smoking</h3>
    <p>{{ !smokingDetected ? "All Clear" : "Monitoring..." }}</p>
  </div>

</div>

</template>

<script>
const API_BASE = "http://localhost:8000"

export default {

data() {
  return {
    smokingDetected: false,
    tvocPpb:         0
  }
},

async mounted() {
  await this.fetchData()
  setInterval(() => this.fetchData(), 8000)
},

methods: {
  async fetchData() {
    try {
      const res  = await fetch(`${API_BASE}/api/smoking-status`)
      const data = await res.json()
      this.smokingDetected = data.smoking_detected
      this.tvocPpb         = data.tvoc_ppb
    } catch (e) {
      console.error("SmokingStatus fetch failed:", e)
    }
  }
}

}
</script>

<style scoped>

.smoke-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 30px;
}

.smoke-card {
  padding: 25px;
  border-radius: 15px;
  text-align: center;
  font-size: 18px;
  transition: all 0.4s;
}

.smoking {
  background: #ffe6ea;
  border: 2px solid #ff4b6e;
  color: #ff4b6e;
}

.safe {
  background: #e8f5e9;
  border: 2px solid #22c55e;
  color: #22c55e;
}

.safe-inactive {
  background: #f5f5f5;
  color: #888;
}

</style>
