<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

interface Camera {
  id: number
  name: string
  location: string | null
  ip: string
  rtspPort: number
  username: string
  rtspPath: string
  isActive: boolean
  recognitionEnabled: boolean
}

const cameras = ref<Camera[]>([])
const loading = ref(true)
const showForm = ref(false)

const form = ref({
  name: '',
  location: '',
  ip: '',
  rtspPort: 554,
  username: '',
  password: '',
  rtspPath: '/ISAPI/Streaming/Channels/101',
  recognitionEnabled: true,
})

onMounted(async () => {
  await loadCameras()
})

async function loadCameras() {
  try {
    const response = await apiClient.get('/api/cameras')
    cameras.value = response.data
  } catch (error) {
    console.error('Failed to load cameras:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  try {
    await apiClient.post('/api/cameras', form.value)
    showForm.value = false
    form.value = {
      name: '',
      location: '',
      ip: '',
      rtspPort: 554,
      username: '',
      password: '',
      rtspPath: '/ISAPI/Streaming/Channels/101',
      recognitionEnabled: true,
    }
    await loadCameras()
  } catch (error: any) {
    alert(error.response?.data?.error || 'Failed to create camera')
  }
}

async function toggleCamera(id: number, isActive: boolean) {
  try {
    await apiClient.put(`/api/cameras/${id}`, { isActive: !isActive })
    await loadCameras()
  } catch (error) {
    alert('Failed to update camera')
  }
}

async function deleteCamera(id: number) {
  if (!confirm('Delete this camera?')) return

  try {
    await apiClient.delete(`/api/cameras/${id}`)
    await loadCameras()
  } catch (error) {
    alert('Failed to delete camera')
  }
}

const selectedCamera = ref<number | null>(null)
const streamUrl = ref<string>('')
const streamKey = ref(0)
const testingCamera = ref<number | null>(null)

async function viewStream(id: number) {
  try {
    const response = await apiClient.get(`/api/cameras/${id}/stream-url`)
    streamUrl.value = response.data.mjpegUrl
    selectedCamera.value = id
    streamKey.value++
  } catch (error) {
    alert('Failed to get stream URL')
  }
}

function closeStream() {
  selectedCamera.value = null
  streamUrl.value = ''
  streamKey.value++
}

function handleStreamError() {
  console.error('Failed to load stream:', streamUrl.value)
}

function handleStreamLoad() {
  console.log('Stream loaded successfully')
}

async function testConnection(id: number) {
  try {
    testingCamera.value = id
    const response = await apiClient.get(`/api/cameras/${id}/rtsp-preview`)
    alert(`RTSP OK (latency ${response.data.latencyMs ?? 'n/a'} ms)`)
  } catch (error: any) {
    alert(
      error.response?.data?.error?.error ||
        error.response?.data?.error ||
        'Не удалось проверить поток'
    )
  } finally {
    testingCamera.value = null
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Cameras</h1>
      <button @click="showForm = !showForm" class="primary">
        {{ showForm ? 'Cancel' : '+ Add Camera' }}
      </button>
    </header>

    <div v-if="selectedCamera" class="modal" @click="closeStream">
      <div class="modal-content" @click.stop>
        <button @click="closeStream" class="close-btn">✕</button>
        <h2>Camera {{ selectedCamera }} Stream</h2>
        <div class="stream-container">
          <img
            :src="streamUrl"
            :key="streamKey"
            crossorigin="anonymous"
            alt="Camera stream"
            class="stream-view"
            @error="handleStreamError"
            @load="handleStreamLoad"
          />
        </div>
      </div>
    </div>

    <div v-if="showForm" class="card form-card">
      <h2>Add Camera</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-row">
          <div class="form-group">
            <label>Name *</label>
            <input v-model="form.name" required />
          </div>

          <div class="form-group">
            <label>Location</label>
            <input v-model="form.location" placeholder="Front Door, Office, etc." />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>IP Address *</label>
            <input v-model="form.ip" required placeholder="192.168.1.11" />
          </div>

          <div class="form-group">
            <label>RTSP Port</label>
            <input v-model.number="form.rtspPort" type="number" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Username *</label>
            <input v-model="form.username" required />
          </div>

          <div class="form-group">
            <label>Password *</label>
            <input v-model="form.password" type="password" required />
          </div>
        </div>

        <div class="form-group">
          <label>RTSP Path</label>
          <input v-model="form.rtspPath" placeholder="/ISAPI/Streaming/Channels/101" />
        </div>

        <div class="form-group">
          <label>
            <input v-model="form.recognitionEnabled" type="checkbox" />
            Enable Recognition
          </label>
        </div>

        <button type="submit" class="primary">Create Camera</button>
      </form>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="card">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Location</th>
            <th>IP</th>
            <th>Status</th>
            <th>Recognition</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="camera in cameras" :key="camera.id">
            <td>{{ camera.id }}</td>
            <td>{{ camera.name }}</td>
            <td>{{ camera.location || '-' }}</td>
            <td>{{ camera.ip }}:{{ camera.rtspPort }}</td>
            <td>
              <span :class="['badge', camera.isActive ? 'success' : 'danger']">
                {{ camera.isActive ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <span :class="['badge', camera.recognitionEnabled ? 'success' : 'warning']">
                {{ camera.recognitionEnabled ? 'Enabled' : 'Disabled' }}
              </span>
            </td>
            <td>
              <button @click="viewStream(camera.id)" class="secondary small">
                View
              </button>
              <button
                @click="testConnection(camera.id)"
                class="secondary small"
                :disabled="testingCamera === camera.id"
              >
                {{ testingCamera === camera.id ? 'Testing...' : 'Test RTSP' }}
              </button>
              <button @click="toggleCamera(camera.id, camera.isActive)" class="secondary small">
                {{ camera.isActive ? 'Disable' : 'Enable' }}
              </button>
              <button @click="deleteCamera(camera.id)" class="danger small">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
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

.form-card {
  margin-bottom: 2rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

button.small {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  margin-right: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 0.5rem;
  max-width: 90vw;
  max-height: 90vh;
  position: relative;
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: var(--danger-color);
  color: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
}

.stream-container {
  text-align: center;
}

.stream-view {
  max-width: 100%;
  max-height: 70vh;
  display: block;
  margin: 1rem auto;
  border: 2px solid var(--border-color);
  border-radius: 0.5rem;
}

.stream-info {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--bg-secondary);
  border-radius: 0.375rem;
  text-align: left;
}

.stream-info p {
  margin: 0.5rem 0;
  font-size: 0.875rem;
}

.stream-info small {
  color: var(--text-secondary);
}
</style>




