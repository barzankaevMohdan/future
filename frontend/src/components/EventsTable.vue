<template>
  <div class="events-table">
    <!-- Фильтры -->
    <el-card shadow="never" class="filters-card">
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-input
            v-model="filters.search"
            placeholder="Поиск по имени..."
            :prefix-icon="Search"
            clearable
            @input="debouncedFetch"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-select
            v-model="filters.type"
            placeholder="Тип события"
            clearable
            style="width: 100%"
            @change="fetchEvents"
          >
            <el-option label="Все типы" value="" />
            <el-option label="Приход" value="IN">
              <el-icon color="#67c23a"><Bottom /></el-icon>
              <span style="margin-left: 8px">Приход</span>
            </el-option>
            <el-option label="Уход" value="OUT">
              <el-icon color="#f56c6c"><Top /></el-icon>
              <span style="margin-left: 8px">Уход</span>
            </el-option>
          </el-select>
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-date-picker
            v-model="filters.dateFrom"
            type="date"
            placeholder="От"
            style="width: 100%"
            @change="fetchEvents"
            format="DD.MM.YYYY"
          />
        </el-col>
        <el-col :xs="24" :sm="12" :md="8" :lg="6">
          <el-date-picker
            v-model="filters.dateTo"
            type="date"
            placeholder="До"
            style="width: 100%"
            @change="fetchEvents"
            format="DD.MM.YYYY"
          />
        </el-col>
      </el-row>

      <el-row :gutter="16" style="margin-top: 16px">
        <el-col :span="24">
          <el-space wrap>
            <el-button
              :icon="Refresh"
              @click="fetchEvents"
              :loading="loading"
            >
              Обновить
            </el-button>
            <el-button
              :icon="RefreshLeft"
              @click="resetFilters"
            >
              Сбросить фильтры
            </el-button>
            <el-divider direction="vertical" />
            <el-button
              type="success"
              :icon="Download"
              @click="exportData('csv')"
              :loading="loading"
            >
              Экспорт CSV
            </el-button>
            <el-button
              type="warning"
              :icon="Download"
              @click="exportData('json')"
              :loading="loading"
            >
              Экспорт JSON
            </el-button>
          </el-space>
        </el-col>
      </el-row>
    </el-card>

    <!-- Таблица -->
    <el-table
      v-loading="loading"
      :data="events"
      style="width: 100%; margin-top: 20px"
      stripe
      :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
    >
      <el-table-column prop="id" label="ID" width="80" align="center" />
      
      <el-table-column prop="name" label="Сотрудник" min-width="150">
        <template #default="{ row }">
          <div class="employee-cell">
            <el-icon><User /></el-icon>
            <span class="employee-name">{{ row.name }}</span>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="role" label="Роль" min-width="120">
        <template #default="{ row }">
          <el-tag v-if="row.role" type="info" size="small" effect="plain">
            {{ row.role }}
          </el-tag>
          <span v-else class="no-data">—</span>
        </template>
      </el-table-column>

      <el-table-column prop="type" label="Тип" width="120" align="center">
        <template #default="{ row }">
          <el-tag
            :type="row.type === 'IN' ? 'success' : 'warning'"
            effect="dark"
            size="default"
          >
            <el-icon>
              <Bottom v-if="row.type === 'IN'" />
              <Top v-else />
            </el-icon>
            <span style="margin-left: 4px">{{ row.type }}</span>
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="timestamp" label="Время" min-width="180" sortable>
        <template #default="{ row }">
          <div class="time-cell">
            <el-icon><Clock /></el-icon>
            <span>{{ formatTime(row.timestamp) }}</span>
          </div>
        </template>
      </el-table-column>

      <template #empty>
        <el-empty description="Событий не найдено" :image-size="100">
          <template #image>
            <el-icon :size="60" color="#909399">
              <Document />
            </el-icon>
          </template>
        </el-empty>
      </template>
    </el-table>

    <!-- Пагинация -->
    <div v-if="pagination && pagination.totalPages > 1" class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="50"
        :total="pagination.total"
        layout="total, prev, pager, next, jumper"
        background
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Search,
  Refresh,
  RefreshLeft,
  Download,
  User,
  Clock,
  Bottom,
  Top,
  Document
} from '@element-plus/icons-vue';
import { config } from '../config.js';
import { getSocket } from '../socket.js';

const backendBase = config.backendUrl;

const events = ref([]);
const pagination = ref(null);
const loading = ref(false);
const filters = ref({
  search: '',
  type: '',
  dateFrom: '',
  dateTo: ''
});
const currentPage = ref(1);
let socket = null;
let debounceTimer = null;

const fetchEvents = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      limit: 50
    });

    if (filters.value.search) params.append('search', filters.value.search);
    if (filters.value.type) params.append('type', filters.value.type);
    if (filters.value.dateFrom) {
      const date = new Date(filters.value.dateFrom);
      params.append('dateFrom', date.toISOString().split('T')[0]);
    }
    if (filters.value.dateTo) {
      const date = new Date(filters.value.dateTo);
      params.append('dateTo', date.toISOString().split('T')[0]);
    }

    const res = await fetch(`${backendBase}/api/events?${params}`);
    const data = await res.json();

    events.value = data.events || data;
    pagination.value = data.pagination;
  } catch (e) {
    console.error(e);
    ElMessage.error('Не удалось загрузить события');
  } finally {
    loading.value = false;
  }
};

const debouncedFetch = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    currentPage.value = 1;
    fetchEvents();
  }, 500);
};

const handlePageChange = (page) => {
  currentPage.value = page;
  fetchEvents();
};

const resetFilters = () => {
  filters.value = {
    search: '',
    type: '',
    dateFrom: '',
    dateTo: ''
  };
  currentPage.value = 1;
  fetchEvents();
};

const exportData = async (format) => {
  try {
    const params = new URLSearchParams({ format });

    if (filters.value.dateFrom) {
      const date = new Date(filters.value.dateFrom);
      params.append('dateFrom', date.toISOString().split('T')[0]);
    }
    if (filters.value.dateTo) {
      const date = new Date(filters.value.dateTo);
      params.append('dateTo', date.toISOString().split('T')[0]);
    }

    const url = `${backendBase}/api/export/events?${params}`;
    window.open(url, '_blank');
    ElMessage.success(`Экспорт ${format.toUpperCase()} начался`);
  } catch (e) {
    console.error(e);
    ElMessage.error('Ошибка экспорта');
  }
};

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

onMounted(() => {
  fetchEvents();

  // WebSocket для реал-тайм обновлений
  socket = getSocket();

  socket.on('event:created', (data) => {
    console.log('[EventsTable] New event received:', data);
    if (currentPage.value === 1 && !filters.value.search) {
      fetchEvents();
    }
  });
});

onBeforeUnmount(() => {
  if (socket) {
    socket.off('event:created');
  }
  clearTimeout(debounceTimer);
});
</script>

<style scoped>
.events-table {
  width: 100%;
}

.filters-card {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  margin-bottom: 16px;
}

:deep(.filters-card .el-card__body) {
  padding: 20px;
}

.employee-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.employee-name {
  font-weight: 600;
  color: #303133;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.no-data {
  color: #909399;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

:deep(.el-pagination) {
  font-weight: 500;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

/* Адаптивность */
@media (max-width: 768px) {
  :deep(.el-col) {
    margin-bottom: 12px;
  }

  :deep(.el-space) {
    width: 100%;
  }

  :deep(.el-space .el-button) {
    flex: 1;
    min-width: auto;
  }
  
  .employee-cell {
    font-size: 13px;
  }
  
  .time-cell {
    font-size: 12px;
  }
}
</style>
