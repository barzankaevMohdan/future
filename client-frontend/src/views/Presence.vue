<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
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

const presentEmployees = computed(() => presence.value.filter(p => p.present))
const absentEmployees = computed(() => presence.value.filter(p => !p.present))

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

  socket.on('event:created', () => {
    loadPresence()
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

    <div v-loading="loading">
      <el-card shadow="never" style="margin-bottom: 24px">
        <template #header>
          <h2 style="margin: 0; font-size: 18px; color: #67c23a;">
            ✅ Присутствуют ({{ presentEmployees.length }})
          </h2>
        </template>
        
        <div class="presence-grid">
          <el-card
            v-for="emp in presentEmployees"
            :key="emp.id"
            shadow="hover"
            class="presence-card present"
          >
            <div class="employee-content">
              <el-avatar :src="emp.photoUrl" :size="100">
                <el-icon :size="50"><User /></el-icon>
              </el-avatar>

              <div class="employee-info">
                <h3 class="employee-name">{{ emp.name }}</h3>
                <p class="employee-role">{{ emp.role || 'Сотрудник' }}</p>
                
                <el-tag type="success" size="large" style="margin-top: 12px;">
                  ✅ Присутствует
                </el-tag>

                <div v-if="emp.lastEventTime" class="last-event">
                  С {{ formatTime(emp.lastEventTime) }}
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <el-empty v-if="presentEmployees.length === 0" description="Нет присутствующих" />
      </el-card>

      <el-card shadow="never">
        <template #header>
          <h2 style="margin: 0; font-size: 18px; color: #909399;">
            ⭕ Отсутствуют ({{ absentEmployees.length }})
          </h2>
        </template>
        
        <div class="presence-grid">
          <el-card
            v-for="emp in absentEmployees"
            :key="emp.id"
            shadow="hover"
            class="presence-card absent"
          >
            <div class="employee-content">
              <el-avatar :src="emp.photoUrl" :size="100">
                <el-icon :size="50"><User /></el-icon>
              </el-avatar>

              <div class="employee-info">
                <h3 class="employee-name">{{ emp.name }}</h3>
                <p class="employee-role">{{ emp.role || 'Сотрудник' }}</p>
                
                <el-tag type="info" size="large" style="margin-top: 12px;">
                  ⭕ Отсутствует
                </el-tag>

                <div v-if="emp.lastEventTime" class="last-event">
                  Последний раз: {{ formatTime(emp.lastEventTime) }}
                </div>
              </div>
            </div>
          </el-card>
        </div>
        
        <el-empty v-if="absentEmployees.length === 0" description="Все присутствуют" />
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
  opacity: 0.85;
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
