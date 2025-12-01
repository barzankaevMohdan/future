<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

interface Camera {
  id: number
  name: string
  location: string | null
  isActive: boolean
}

const cameras = ref<Camera[]>([])
const streams = ref<Record<number, string>>({})
const loading = ref(true)

onMounted(async () => {
  await loadCameras()
})

async function loadCameras() {
  try {
    const response = await apiClient.get('/api/cameras')
    cameras.value = response.data

    for (const camera of response.data) {
      if (camera.isActive) {
        const stream = await apiClient.get(`/api/cameras/${camera.id}/stream-url`)
        streams.value[camera.id] = `${stream.data.mjpegUrl}?ts=${Date.now()}`
      }
    }
  } catch (error) {
    console.error('Failed to load cameras', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Live Streams</h1>
      <button @click="loadCameras" class="secondary">Refresh</button>
    </header>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="grid">
      <article
        v-for="camera in cameras"
        :key="camera.id"
        class="card"
      >
        <div class="card-header">
          <div>
            <h3>{{ camera.name }}</h3>
            <p class="muted">{{ camera.location || '—' }}</p>
          </div>
          <span :class="['badge', camera.isActive ? 'success' : 'danger']">
            {{ camera.isActive ? 'Active' : 'Inactive' }}
          </span>
        </div>
        <img
          v-if="camera.isActive && streams[camera.id]"
          :src="streams[camera.id]"
          class="stream"
          :alt="camera.name"
        />
        <p v-else class="muted small">Нет активного потока</p>
      </article>
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.muted {
  color: var(--text-secondary);
}

.muted.small {
  font-size: 0.875rem;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
}

.badge.success {
  background: #d1fae5;
  color: #065f46;
}

.badge.danger {
  background: #fee2e2;
  color: #991b1b;
}

.stream {
  width: 100%;
  border-radius: 0.5rem;
  border: 1px solid var(--border-color);
}

.loading {
  text-align: center;
  color: var(--text-secondary);
}
</style>



