<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import apiClient from '@/api/client'

const authStore = useAuthStore()

const stats = ref({
  totalEmployees: 0,
  presentEmployees: 0,
  eventsToday: 0,
})

const loading = ref(true)

onMounted(async () => {
  try {
    const [employees, presence] = await Promise.all([
      apiClient.get('/api/employees'),
      apiClient.get('/api/presence'),
    ])

    stats.value.totalEmployees = employees.data.length
    stats.value.presentEmployees = presence.data.filter((p: any) => p.present).length

    const today = new Date().toISOString().split('T')[0]
    const events = await apiClient.get('/api/events', {
      params: { dateFrom: today, dateTo: today, limit: 1 },
    })
    stats.value.eventsToday = events.data.pagination.total
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
})

function logout() {
  authStore.logout()
}
</script>

<template>
  <div class="dashboard">
    <header class="header">
      <h1>Dashboard</h1>
      <div class="user-info">
        <span>{{ authStore.user?.email }}</span>
        <button @click="logout" class="secondary">Logout</button>
      </div>
    </header>

    <nav class="nav">
      <router-link to="/dashboard">Dashboard</router-link>
      <router-link to="/presence">Presence</router-link>
      <router-link to="/events">Events</router-link>
      <router-link to="/statistics">Statistics</router-link>
      <router-link to="/live">Live</router-link>
    </nav>

    <main class="content">
      <div v-if="loading" class="loading">Loading...</div>
      
      <div v-else class="stats-grid">
        <div class="stat-card card">
          <div class="stat-label">Total Employees</div>
          <div class="stat-value">{{ stats.totalEmployees }}</div>
        </div>

        <div class="stat-card card">
          <div class="stat-label">Present Now</div>
          <div class="stat-value success">{{ stats.presentEmployees }}</div>
        </div>

        <div class="stat-card card">
          <div class="stat-label">Events Today</div>
          <div class="stat-value">{{ stats.eventsToday }}</div>
        </div>
      </div>

      <div class="card" style="margin-top: 2rem">
        <h2>Quick Access</h2>
        <div class="quick-links">
          <router-link to="/presence" class="quick-link">
            <span>✅</span>
            <span>View Presence</span>
          </router-link>
          <router-link to="/events" class="quick-link">
            <span>📊</span>
            <span>Event History</span>
          </router-link>
          <router-link to="/statistics" class="quick-link">
            <span>📈</span>
            <span>Statistics</span>
          </router-link>
          <router-link to="/live" class="quick-link">
            <span>📺</span>
            <span>Live Streams</span>
          </router-link>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f5f5f5;
}

.header {
  background: white;
  padding: 1rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav {
  background: white;
  padding: 0 2rem;
  display: flex;
  gap: 2rem;
  border-bottom: 1px solid var(--border-color);
}

.nav a {
  padding: 1rem 0;
  text-decoration: none;
  color: var(--text-secondary);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.nav a:hover {
  color: var(--primary-color);
}

.nav a.router-link-active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
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

.stat-value.success {
  color: var(--success-color);
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.quick-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s;
}

.quick-link:hover {
  background: var(--primary-color);
  color: white;
  transform: translateY(-2px);
}

.quick-link span:first-child {
  font-size: 2rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>





