<template>

<div class="card">

  <h3>🌡 Room Temperature</h3>

  <div class="temp-icon" :class="thermoClass">🌡</div>

  <div class="temp-value" :class="thermoClass">
    {{ temperature }}°C
  </div>

  <p>Humidity: <strong>{{ humidity }}%</strong></p>

</div>

</template>

<script>
const API_BASE = "http://localhost:8000"

export default {

data() {
  return {
    temperature: 27,
    humidity:    50,
    thermoClass: "warm"
  }
},

async mounted() {
  await this.fetchData()
  setInterval(() => this.fetchData(), 8000)
},

methods: {
  async fetchData() {
    try {
      const res  = await fetch(`${API_BASE}/api/temperature`)
      const data = await res.json()
      this.temperature = data.temperature
      this.humidity    = data.humidity
      this.thermoClass = data.status
    } catch (e) {
      console.error("Temperature fetch failed:", e)
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

.temp-icon {
  font-size: 60px;
  margin: 10px 0;
  transition: 0.3s;
}

.temp-value {
  font-size: 40px;
  margin: 10px 0;
  transition: 0.3s;
}

.cool { color: green; }
.warm { color: #f4b400; }
.hot  { color: red; }

</style>
