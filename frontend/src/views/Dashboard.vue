<template>
<div class="dashboard">

  <!-- Filter Bar -->
  <div class="filter-bar">
    <span class="filter-label">🔍 Filter by Sensor:</span>
    <button
      v-for="f in filters"
      :key="f.key"
      :class="['filter-btn', { active: activeFilter === f.key }]"
      @click="activeFilter = f.key"
    >
      {{ f.icon }} {{ f.label }}
    </button>
  </div>

  <!-- Alert — always visible -->
  <SmokeAlert/>

  <!-- Air Quality — visible for: all, airquality -->
  <AirQualityChart v-if="show('airquality')"/>

  <!-- Sensors row — visible for: all, temperature, gas -->
  <div class="grid-two" v-if="show('temperature') || show('gas')">
    <TemperatureCard v-if="show('temperature')"/>
    <COGauge         v-if="show('gas')"/>
  </div>

  <!-- Health Insights — visible for: all, health -->
  <HealthInsights v-if="show('health')"/>

  <!-- Smoking Status — visible for: all, gas -->
  <SmokingStatus v-if="show('gas')"/>

  <!-- Cost — visible for: all, particulates -->
  <CostPollution v-if="show('particulates')"/>

  <!-- Chatbot — always visible -->
  <ChatBot/>

</div>
</template>

<script>
import SmokeAlert      from "../components/SmokeAlert.vue"
import AirQualityChart from "../components/AirQualityChart.vue"
import TemperatureCard from "../components/TemperatureCard.vue"
import COGauge         from "../components/COGauge.vue"
import HealthInsights  from "../components/HealthInsights.vue"
import SmokingStatus   from "../components/SmokingStatus.vue"
import CostPollution   from "../components/CostPollution.vue"
import ChatBot         from "../components/ChatBot.vue"

export default {
  name: "Dashboard",
  components: {
    SmokeAlert, AirQualityChart, TemperatureCard,
    COGauge, HealthInsights, SmokingStatus, CostPollution, ChatBot
  },

  data() {
    return {
      activeFilter: "all",
      filters: [
        { key: "all",          icon: "📊", label: "All Sensors"   },
        { key: "airquality",   icon: "🌬", label: "Air Quality"   },
        { key: "temperature",  icon: "🌡", label: "Temperature"   },
        { key: "gas",          icon: "⚡", label: "Gas / TVOC"    },
        { key: "particulates", icon: "🌫", label: "Particulates"  },
        { key: "health",       icon: "❤", label: "Health"        }
      ]
    }
  },

  methods: {
    show(category) {
      if (this.activeFilter === "all") return true
      // Temperature filter also shows gas gauge for context
      if (this.activeFilter === "temperature" && category === "gas") return true
      return this.activeFilter === category
    }
  }
}
</script>

<style>
.dashboard {
  background: #dbe7f3;
  min-height: 100vh;
  max-width: 1200px;
  margin: auto;
  padding: 40px;
  font-family: Arial;
}

/* ── Filter Bar ───────────────────────────────── */
.filter-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  background: white;
  padding: 14px 20px;
  border-radius: 14px;
  margin-bottom: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

.filter-label {
  font-size: 14px;
  font-weight: bold;
  color: #555;
  margin-right: 6px;
}

.filter-btn {
  padding: 7px 16px;
  border-radius: 20px;
  border: 1.5px solid #ddd;
  background: white;
  cursor: pointer;
  font-size: 13px;
  color: #555;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  font-weight: bold;
}

/* ── Layout ───────────────────────────────────── */
.grid-two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 25px;
  margin-top: 25px;
}

@media (max-width: 900px) {
  .grid-two {
    grid-template-columns: 1fr;
  }
  .filter-bar {
    gap: 8px;
  }
}
</style>