<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

const statistics = ref<any>(null)
const loading = ref(true)

const dateFrom = ref('')
const dateTo = ref('')

onMounted(async () => {
  // Default: last 30 days
  const today = new Date()
  const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
  
  dateFrom.value = thirtyDaysAgo.toISOString().split('T')[0]
  dateTo.value = today.toISOString().split('T')[0]

  await loadStatistics()
})

async function loadStatistics() {
  try {
    loading.value = true
    const response = await apiClient.get('/api/statistics', {
      params: {
        dateFrom: dateFrom.value,
        dateTo: dateTo.value,
      },
    })
    statistics.value = response.data
  } catch (error) {
    console.error('Failed to load statistics:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Statistics</h1>
    </header>

    <div class="card filters">
      <div class="filter-row">
        <div class="form-group">
          <label>From Date</label>
          <input v-model="dateFrom" type="date" />
        </div>

        <div class="form-group">
          <label>To Date</label>
          <input v-model="dateTo" type="date" />
        </div>

        <div class="form-group">
          <label>&nbsp;</label>
          <button @click="loadStatistics" class="primary">Apply</button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else-if="statistics">
      <div class="stats-grid">
        <div class="stat-card card">
          <div class="stat-label">Total Events</div>
          <div class="stat-value">{{ statistics.summary.totalEvents }}</div>
        </div>

        <div class="stat-card card">
          <div class="stat-label">Unique Employees</div>
          <div class="stat-value">{{ statistics.summary.uniqueEmployees }}</div>
        </div>

        <div class="stat-card card">
          <div class="stat-label">Avg Events/Day</div>
          <div class="stat-value">{{ statistics.summary.avgEventsPerDay }}</div>
        </div>
      </div>

      <div class="card" style="margin-top: 2rem">
        <h2>Top Employees</h2>
        <table class="table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Events</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in statistics.topEmployees" :key="emp.id">
              <td>{{ emp.name }}</td>
              <td>{{ emp.eventCount }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card" style="margin-top: 2rem">
        <h2>Events by Day</h2>
        <table class="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Total</th>
              <th>IN</th>
              <th>OUT</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="day in statistics.eventsByDay" :key="day.date">
              <td>{{ day.date }}</td>
              <td>{{ day.count }}</td>
              <td><span class="badge success">{{ day.ins }}</span></td>
              <td><span class="badge danger">{{ day.outs }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.filters {
  margin-bottom: 2rem;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.form-group {
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.875rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  text-align: center;
  padding: 2rem 1rem;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

h2 {
  margin-bottom: 1rem;
}
</style>







