<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import apiClient from '@/api/client'

interface Event {
  id: number
  employeeId: number
  type: string
  timestamp: string
  employee: {
    name: string
    roleTitle: string | null
  }
}

const events = ref<Event[]>([])
const loading = ref(true)
const page = ref(1)
const limit = ref(50)
const total = ref(0)

const filters = ref({
  dateFrom: '',
  dateTo: '',
  type: '',
})

onMounted(async () => {
  await loadEvents()
})

watch([page, filters], async () => {
  await loadEvents()
}, { deep: true })

async function loadEvents() {
  try {
    loading.value = true
    const response = await apiClient.get('/api/events', {
      params: {
        page: page.value,
        limit: limit.value,
        ...filters.value,
      },
    })
    events.value = response.data.events
    total.value = response.data.pagination.total
  } catch (error) {
    console.error('Failed to load events:', error)
  } finally {
    loading.value = false
  }
}

function formatTime(time: string): string {
  return new Date(time).toLocaleString()
}

function nextPage() {
  page.value++
}

function prevPage() {
  if (page.value > 1) {
    page.value--
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Events</h1>
    </header>

    <div class="card filters">
      <h3>Filters</h3>
      <div class="filter-row">
        <div class="form-group">
          <label>From Date</label>
          <input v-model="filters.dateFrom" type="date" />
        </div>

        <div class="form-group">
          <label>To Date</label>
          <input v-model="filters.dateTo" type="date" />
        </div>

        <div class="form-group">
          <label>Type</label>
          <select v-model="filters.type">
            <option value="">All</option>
            <option value="IN">IN</option>
            <option value="OUT">OUT</option>
          </select>
        </div>

        <div class="form-group">
          <label>&nbsp;</label>
          <button @click="filters = { dateFrom: '', dateTo: '', type: '' }" class="secondary">
            Clear
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="card">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Employee</th>
            <th>Role</th>
            <th>Type</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="event in events" :key="event.id">
            <td>{{ event.id }}</td>
            <td>{{ event.employee.name }}</td>
            <td>{{ event.employee.roleTitle || '-' }}</td>
            <td>
              <span :class="['badge', event.type === 'IN' ? 'success' : 'danger']">
                {{ event.type }}
              </span>
            </td>
            <td>{{ formatTime(event.timestamp) }}</td>
          </tr>
        </tbody>
      </table>

      <div class="pagination">
        <button @click="prevPage" :disabled="page === 1" class="secondary">
          Previous
        </button>
        <span>Page {{ page }} (Total: {{ total }} events)</span>
        <button @click="nextPage" :disabled="events.length < limit" class="secondary">
          Next
        </button>
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
  margin-top: 1rem;
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

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>







