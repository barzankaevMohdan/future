<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { io, Socket } from 'socket.io-client'
import apiClient from '@/api/client'

interface PresenceStatus {
  id: number
  name: string
  roleTitle: string | null
  photoUrl: string | null
  present: boolean
  lastEventType: string | null
  lastEventTime: string | null
}

const presence = ref<PresenceStatus[]>([])
const loading = ref(true)
let socket: Socket | null = null

onMounted(async () => {
  await loadPresence()
  connectSocket()
})

async function loadPresence() {
  try {
    const response = await apiClient.get('/api/presence')
    presence.value = response.data
  } catch (error) {
    console.error('Failed to load presence:', error)
  } finally {
    loading.value = false
  }
}

function connectSocket() {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'
  
  socket = io(API_BASE_URL, {
    path: '/ws',
  })

  socket.on('event:created', () => {
    loadPresence()
  })
}

function formatTime(time: string | null): string {
  if (!time) return '-'
  return new Date(time).toLocaleString()
}

const presentEmployees = ref<PresenceStatus[]>([])
const absentEmployees = ref<PresenceStatus[]>([])

function updateLists() {
  presentEmployees.value = presence.value.filter(p => p.present)
  absentEmployees.value = presence.value.filter(p => !p.present)
}

onMounted(() => {
  updateLists()
})
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Employee Presence</h1>
      <button @click="loadPresence" class="secondary">Refresh</button>
    </header>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else>
      <div class="section">
        <h2>Present ({{ presentEmployees.length }})</h2>
        <div class="presence-grid">
          <div
            v-for="emp in presence.filter(p => p.present)"
            :key="emp.id"
            class="presence-card card present"
          >
            <img
              v-if="emp.photoUrl"
              :src="emp.photoUrl"
              class="employee-photo"
              alt="Photo"
            />
            <div v-else class="no-photo">No Photo</div>

            <div class="employee-info">
              <h3>{{ emp.name }}</h3>
              <p class="role">{{ emp.roleTitle || 'Employee' }}</p>
              <div class="status-badge present">✅ Present</div>
              <div v-if="emp.lastEventTime" class="last-event">
                Since {{ formatTime(emp.lastEventTime) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>Absent ({{ presence.filter(p => !p.present).length }})</h2>
        <div class="presence-grid">
          <div
            v-for="emp in presence.filter(p => !p.present)"
            :key="emp.id"
            class="presence-card card absent"
          >
            <img
              v-if="emp.photoUrl"
              :src="emp.photoUrl"
              class="employee-photo"
              alt="Photo"
            />
            <div v-else class="no-photo">No Photo</div>

            <div class="employee-info">
              <h3>{{ emp.name }}</h3>
              <p class="role">{{ emp.roleTitle || 'Employee' }}</p>
              <div class="status-badge absent">⭕ Absent</div>
              <div v-if="emp.lastEventTime" class="last-event">
                Last seen {{ formatTime(emp.lastEventTime) }}
              </div>
            </div>
          </div>
        </div>
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

.section {
  margin-bottom: 3rem;
}

.section h2 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.presence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1.5rem;
}

.presence-card {
  padding: 1.5rem;
  text-align: center;
  transition: all 0.2s;
}

.presence-card.present {
  border-left: 4px solid var(--success-color);
}

.presence-card.absent {
  border-left: 4px solid var(--text-secondary);
  opacity: 0.7;
}

.employee-photo {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 1rem;
}

.no-photo {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.employee-info h3 {
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
}

.role {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.status-badge {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.status-badge.present {
  background: #d1fae5;
  color: #065f46;
}

.status-badge.absent {
  background: #f3f4f6;
  color: #6b7280;
}

.last-event {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>







