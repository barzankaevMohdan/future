<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { User, VideoCamera, Calendar, TrendCharts } from '@element-plus/icons-vue'
import apiClient from '@/api/client'

const stats = ref({
  totalEmployees: 0,
  presentEmployees: 0,
  eventsToday: 0,
  activeCameras: 0,
})

const loading = ref(true)

onMounted(async () => {
  await loadStats()
})

async function loadStats() {
  loading.value = true
  try {
    const [employees, presence, cameras] = await Promise.all([
      apiClient.get('/api/employees'),
      apiClient.get('/api/presence'),
      apiClient.get('/api/cameras'),
    ])

    stats.value.totalEmployees = employees.data.length
    stats.value.presentEmployees = presence.data.filter((p: any) => p.present).length
    stats.value.activeCameras = cameras.data.filter((c: any) => c.isActive).length

    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const tomorrow = new Date(today)
    tomorrow.setDate(tomorrow.getDate() + 1)
    
    const events = await apiClient.get('/api/events', {
      params: {
        dateFrom: today.toISOString(),
        dateTo: tomorrow.toISOString(),
        limit: 1
      },
    })
    stats.value.eventsToday = events.data.pagination.total
  } catch (error) {
    console.error('Failed to load stats:', error)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <h1 class="page-title">Панель управления</h1>

    <div v-loading="loading" class="stats-grid">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon primary">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalEmployees }}</div>
            <div class="stat-label">Всего сотрудников</div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon success">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value success">{{ stats.presentEmployees }}</div>
            <div class="stat-label">Присутствуют сейчас</div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon warning">
            <el-icon :size="32"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.eventsToday }}</div>
            <div class="stat-label">События сегодня</div>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-icon info">
            <el-icon :size="32"><VideoCamera /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeCameras }}</div>
            <div class="stat-label">Активные камеры</div>
          </div>
        </div>
      </el-card>
    </div>

    <el-card shadow="never" style="margin-top: 24px">
      <template #header>
        <h2 style="margin: 0; font-size: 18px;">Быстрые действия</h2>
      </template>
      
      <div class="quick-links">
        <router-link to="/employees" class="quick-link">
          <el-icon :size="40"><User /></el-icon>
          <span>Управление сотрудниками</span>
        </router-link>
        <router-link to="/cameras" class="quick-link">
          <el-icon :size="40"><VideoCamera /></el-icon>
          <span>Управление камерами</span>
        </router-link>
        <router-link to="/presence" class="quick-link">
          <el-icon :size="40"><TrendCharts /></el-icon>
          <span>Посещаемость</span>
        </router-link>
        <router-link to="/events" class="quick-link">
          <el-icon :size="40"><Calendar /></el-icon>
          <span>История событий</span>
        </router-link>
        <router-link to="/live" class="quick-link">
          <el-icon :size="40"><VideoCamera /></el-icon>
          <span>Прямые трансляции</span>
        </router-link>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  margin: 0 0 24px 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  }
  
  .page-container {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}

.stat-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-4px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.primary {
  background: #ecf5ff;
  color: #409eff;
}

.stat-icon.success {
  background: #f0f9ff;
  color: #67c23a;
}

.stat-icon.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.stat-icon.info {
  background: #f4f4f5;
  color: #909399;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
  line-height: 1;
  margin-bottom: 8px;
}

.stat-value.success {
  color: #67c23a;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}

@media (max-width: 768px) {
  .quick-links {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
}

@media (max-width: 480px) {
  .quick-links {
    grid-template-columns: 1fr 1fr;
  }
}

.quick-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  text-decoration: none;
  color: #303133;
  transition: all 0.3s;
  min-height: 120px;
}

.quick-link:hover {
  background: #409eff;
  color: white;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.quick-link span {
  font-size: 14px;
  font-weight: 500;
  text-align: center;
}
</style>
