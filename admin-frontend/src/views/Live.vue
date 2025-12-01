<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

interface Camera {
  id: number
  name: string
  location: string | null
  isActive: boolean
  recognitionEnabled: boolean
  streamUrl?: string
}

const cameras = ref<Camera[]>([])
const loading = ref(true)
const selectedCamera = ref<number | null>(null)
const streamUrls = ref<Record<number, string>>({})

onMounted(async () => {
  await loadCameras()
})

async function loadCameras() {
  try {
    const response = await apiClient.get('/api/cameras')
    cameras.value = response.data
  } catch (error) {
    console.error('Failed to load cameras', error)
  } finally {
    loading.value = false
  }
}

async function openStream(cameraId: number) {
  try {
    const response = await apiClient.get(`/api/cameras/${cameraId}/stream-url`)
    streamUrls.value[cameraId] = `${response.data.mjpegUrl}?ts=${Date.now()}`
    selectedCamera.value = cameraId
  } catch (error) {
    alert('Не удалось получить stream URL')
  }
}

function closeModal() {
  selectedCamera.value = null
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Live Streams</h1>
      <button @click="loadCameras" class="secondary">Refresh</button>
    </header>

    <div v-if="loading" class="loading">Loading...</div>

    <section v-else class="grid">
      <article
        v-for="camera in cameras"
        :key="camera.id"
        class="card camera-card"
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
        <button
          class="primary full-width"
          :disabled="!camera.isActive"
          @click="openStream(camera.id)"
        >
          View Stream
        </button>
      </article>
    </section>

    <div v-if="selectedCamera" class="modal" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="close-btn" @click="closeModal">✕</button>
        <img
          v-if="streamUrls[selectedCamera]"
          :src="streamUrls[selectedCamera]"
          alt="Live stream"
        />
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.5rem;
}

.camera-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.muted {
  color: var(--text-secondary);
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

.full-width {
  width: 100%;
}

.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 1rem;
  border-radius: 0.5rem;
  max-width: 90vw;
  max-height: 90vh;
  position: relative;
}

.modal img {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 0.5rem;
}

.close-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.loading {
  text-align: center;
  color: var(--text-secondary);
}
</style>



