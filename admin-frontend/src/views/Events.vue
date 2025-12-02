<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Calendar } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/client'

interface Event {
  id: number
  employeeId: number
  type: string
  timestamp: string
  employee: {
    name: string
    role: string | null
  }
  camera?: {
    name: string
  }
}

const events = ref<Event[]>([])
const loading = ref(true)
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

const filters = ref({
  dateFrom: '',
  dateTo: '',
  type: '',
})

onMounted(async () => {
  await loadEvents()
})

async function loadEvents() {
  loading.value = true
  try {
    const params: any = {
      page: currentPage.value,
      limit: pageSize.value,
    }
    
    // Add filters with proper ISO format
    if (filters.value.dateFrom) {
      const fromDate = new Date(filters.value.dateFrom)
      fromDate.setHours(0, 0, 0, 0)
      params.dateFrom = fromDate.toISOString()
    }
    
    if (filters.value.dateTo) {
      const toDate = new Date(filters.value.dateTo)
      toDate.setHours(23, 59, 59, 999)
      params.dateTo = toDate.toISOString()
    }
    
    if (filters.value.type) {
      params.type = filters.value.type
    }
    
    const response = await apiClient.get('/api/events', { params })
    events.value = response.data.events
    total.value = response.data.pagination.total
  } catch (error) {
    ElMessage.error('Не удалось загрузить события')
  } finally {
    loading.value = false
  }
}

function formatTime(time: string): string {
  return new Date(time).toLocaleString('ru-RU')
}

function handlePageChange(page: number) {
  currentPage.value = page
  loadEvents()
}

function resetFilters() {
  filters.value = { dateFrom: '', dateTo: '', type: '' }
  currentPage.value = 1
  loadEvents()
}
</script>

<template>
  <div class="page-container">
    <el-page-header class="page-header">
      <template #content>
        <h1 class="page-title">События</h1>
      </template>
      <template #extra>
        <el-button :icon="Refresh" @click="loadEvents" :loading="loading">
          Обновить
        </el-button>
      </template>
    </el-page-header>

    <el-card shadow="never" style="margin-bottom: 16px">
      <template #header>
        <div style="display: flex; align-items: center; gap: 8px;">
          <el-icon><Calendar /></el-icon>
          <span>Фильтры</span>
        </div>
      </template>
      
      <el-form :model="filters" label-width="100px">
        <el-row :gutter="16">
          <el-col :xs="24" :sm="8">
            <el-form-item label="От даты">
              <el-date-picker
                v-model="filters.dateFrom"
                type="date"
                placeholder="Выберите дату"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="loadEvents"
              />
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="8">
            <el-form-item label="До даты">
              <el-date-picker
                v-model="filters.dateTo"
                type="date"
                placeholder="Выберите дату"
                style="width: 100%"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                @change="loadEvents"
              />
            </el-form-item>
          </el-col>
          
          <el-col :xs="24" :sm="8">
            <el-form-item label="Тип">
              <el-select v-model="filters.type" placeholder="Все" style="width: 100%" @change="loadEvents">
                <el-option label="Все" value="" />
                <el-option label="Вход (IN)" value="IN" />
                <el-option label="Выход (OUT)" value="OUT" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item>
          <el-button @click="resetFilters">Сбросить фильтры</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never">
      <el-table :data="events" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="Время" width="200">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="employee.name" label="Сотрудник" min-width="180" />
        
        <el-table-column label="Должность" min-width="150">
          <template #default="{ row }">
            {{ row.employee.role || '—' }}
          </template>
        </el-table-column>
        
        <el-table-column label="Тип" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'IN' ? 'success' : 'warning'">
              {{ row.type === 'IN' ? 'Вход' : 'Выход' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Камера" min-width="150">
          <template #default="{ row }">
            {{ row.camera?.name || '—' }}
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top: 16px; display: flex; justify-content: flex-end;">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="handlePageChange"
        />
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

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
}
</style>
