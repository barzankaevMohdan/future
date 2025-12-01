<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { VideoCamera, Monitor } from '@element-plus/icons-vue'
import apiClient from '@/api/client'

interface Camera {
  id: number
  name: string
  location: string | null
  isActive: boolean
}

const cameras = ref<Camera[]>([])
const streams = ref<Record<number, string>>({})
const recognitionStreams = ref<Record<number, string>>({})
const loading = ref(true)
const showRecognition = ref<Record<number, boolean>>({})

onMounted(async () => {
  await loadCameras()
})

async function loadCameras() {
  loading.value = true
  try {
    const response = await apiClient.get('/api/cameras')
    cameras.value = response.data

    for (const camera of response.data) {
      if (camera.isActive) {
        const stream = await apiClient.get(`/api/cameras/${camera.id}/stream-url`)
        streams.value[camera.id] = `${stream.data.mjpegUrl}?ts=${Date.now()}`
        recognitionStreams.value[camera.id] = `http://localhost:${5000 + camera.id}/video_feed?ts=${Date.now()}`
        showRecognition.value[camera.id] = false
      }
    }
  } catch (error) {
    console.error('Failed to load cameras', error)
  } finally {
    loading.value = false
  }
}

function toggleRecognition(cameraId: number) {
  showRecognition.value[cameraId] = !showRecognition.value[cameraId]
}
</script>

<template>
  <div class="page-container">
    <el-page-header class="page-header">
      <template #content>
        <h1 class="page-title">Прямые трансляции</h1>
      </template>
      <template #extra>
        <el-button @click="loadCameras" :loading="loading">
          Обновить
        </el-button>
      </template>
    </el-page-header>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else class="cameras-grid">
      <el-card
        v-for="camera in cameras"
        :key="camera.id"
        class="camera-card"
        shadow="hover"
      >
        <template #header>
          <div class="card-header">
            <div class="camera-info">
              <h3 class="camera-name">{{ camera.name }}</h3>
              <p class="camera-location">{{ camera.location || '—' }}</p>
            </div>
            <el-tag :type="camera.isActive ? 'success' : 'danger'" size="small">
              {{ camera.isActive ? 'Активна' : 'Неактивна' }}
            </el-tag>
          </div>
        </template>

        <div v-if="camera.isActive && streams[camera.id]" class="stream-wrapper">
          <img
            :src="showRecognition[camera.id] ? recognitionStreams[camera.id] : streams[camera.id]"
            class="stream-image"
            :alt="camera.name"
          />
          
          <el-button
            :type="showRecognition[camera.id] ? 'success' : 'primary'"
            :icon="showRecognition[camera.id] ? Monitor : VideoCamera"
            @click="toggleRecognition(camera.id)"
            class="toggle-button"
          >
            {{ showRecognition[camera.id] ? 'AI Распознавание' : 'Обычный поток' }}
          </el-button>
        </div>
        
        <el-empty v-else description="Нет активного потока" :image-size="100" />
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.loading-container {
  padding: 24px;
}

.cameras-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

@media (max-width: 768px) {
  .cameras-grid {
    grid-template-columns: 1fr;
  }
  
  .page-container {
    padding: 16px;
  }
}

.camera-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.camera-info {
  flex: 1;
  min-width: 0;
}

.camera-name {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.camera-location {
  margin: 0;
  font-size: 14px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.stream-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stream-image {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  background: #f5f7fa;
}

.toggle-button {
  width: 100%;
}
</style>
