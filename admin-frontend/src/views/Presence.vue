<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Refresh, User } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { io, Socket } from 'socket.io-client'
import apiClient from '@/api/client'

interface PresenceStatus {
  id: number
  name: string
  role: string | null
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

onUnmounted(() => {
  if (socket) {
    socket.disconnect()
  }
})

async function loadPresence() {
  loading.value = true
  try {
    const response = await apiClient.get('/api/presence')
    presence.value = response.data
  } catch (error) {
    ElMessage.error('Не удалось загрузить данные о присутствии')
  } finally {
    loading.value = false
  }
}

function connectSocket() {
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000'
  
  socket = io(API_BASE_URL, {
    path: '/ws',
  })

  socket.on('connect', () => {
    console.log('Socket connected')
  })

  socket.on('event:created', (data: any) => {
    console.log('Event received:', data)
    loadPresence()
  })

  socket.on('disconnect', () => {
    console.log('Socket disconnected')
  })
}

function formatTime(time: string | null): string {
  if (!time) return '—'
  return new Date(time).toLocaleString('ru-RU')
}
</script>

<template>
  <div class="page-container">
    <el-page-header class="page-header">
      <template #content>
        <h1 class="page-title">Присутствие сотрудников</h1>
      </template>
      <template #extra>
        <el-button :icon="Refresh" @click="loadPresence" :loading="loading">
          Обновить
        </el-button>
      </template>
    </el-page-header>

    <div v-loading="loading" class="presence-grid">
      <el-card
        v-for="emp in presence"
        :key="emp.id"
        shadow="hover"
        :class="['presence-card', emp.present ? 'present' : 'absent']"
      >
        <div class="employee-content">
          <el-avatar :src="emp.photoUrl" :size="100">
            <el-icon :size="50"><User /></el-icon>
          </el-avatar>

          <div class="employee-info">
            <h3 class="employee-name">{{ emp.name }}</h3>
            <p class="employee-role">{{ emp.role || 'Сотрудник' }}</p>
            
            <el-tag :type="emp.present ? 'success' : 'info'" size="large" style="margin-top: 12px;">
              {{ emp.present ? '✅ Присутствует' : '⭕ Отсутствует' }}
            </el-tag>

            <div v-if="emp.lastEventTime" class="last-event">
              Последнее: {{ emp.lastEventType }} в {{ formatTime(emp.lastEventTime) }}
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && presence.length === 0" description="Нет сотрудников" />
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

.presence-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

@media (max-width: 768px) {
  .presence-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  
  .page-container {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .presence-grid {
    grid-template-columns: 1fr;
  }
}

.presence-card {
  transition: all 0.3s;
}

.presence-card.present {
  border-left: 4px solid #67c23a;
}

.presence-card.absent {
  border-left: 4px solid #909399;
}

.presence-card:hover {
  transform: translateY(-4px);
}

.employee-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.employee-info {
  width: 100%;
  margin-top: 16px;
}

.employee-name {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.employee-role {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.last-event {
  margin-top: 12px;
  font-size: 12px;
  color: #909399;
  line-height: 1.5;
}
</style>
