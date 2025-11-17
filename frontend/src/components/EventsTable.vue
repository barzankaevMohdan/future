<template>
  <div>
    <!-- Фильтры -->
    <div class="filters">
      <input 
        type="text" 
        v-model="filters.search" 
        placeholder="Поиск по имени..."
        @input="debouncedFetch"
      />
      <select v-model="filters.type" @change="fetchEvents">
        <option value="">Все типы</option>
        <option value="IN">Приход</option>
        <option value="OUT">Уход</option>
      </select>
      <input 
        type="date" 
        v-model="filters.dateFrom" 
        @change="fetchEvents"
        placeholder="От"
      />
      <input 
        type="date" 
        v-model="filters.dateTo" 
        @change="fetchEvents"
        placeholder="До"
      />
      <button @click="resetFilters">Сбросить</button>
    </div>

    <!-- Кнопки действий -->
    <div class="controls">
      <button @click="fetchEvents" :disabled="loading">
        {{ loading ? 'Обновляю...' : 'Обновить' }}
      </button>
      <button @click="exportData('csv')" :disabled="loading">
        Экспорт CSV
      </button>
      <button @click="exportData('json')" :disabled="loading">
        Экспорт JSON
      </button>
    </div>

    <!-- Таблица -->
    <table class="table" v-if="events.length">
      <thead>
        <tr>
          <th>ID</th>
          <th>Сотрудник</th>
          <th>Роль</th>
          <th>Тип</th>
          <th>Время</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="ev in events" :key="ev.id">
          <td>{{ ev.id }}</td>
          <td>{{ ev.name }}</td>
          <td>{{ ev.role || '—' }}</td>
          <td>
            <span :class="['badge', ev.type === 'IN' ? 'badge-in' : 'badge-out']">
              {{ ev.type }}
            </span>
          </td>
          <td>{{ formatTime(ev.timestamp) }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else class="no-data">
      {{ loading ? 'Загрузка...' : 'Событий не найдено' }}
    </div>

    <!-- Пагинация -->
    <div class="pagination" v-if="pagination && pagination.totalPages > 1">
      <button 
        @click="changePage(1)" 
        :disabled="pagination.page === 1"
      >
        ««
      </button>
      <button 
        @click="changePage(pagination.page - 1)" 
        :disabled="!pagination.hasPrev"
      >
        «
      </button>
      <span class="page-info">
        Страница {{ pagination.page }} из {{ pagination.totalPages }}
        ({{ pagination.total }} событий)
      </span>
      <button 
        @click="changePage(pagination.page + 1)" 
        :disabled="!pagination.hasNext"
      >
        »
      </button>
      <button 
        @click="changePage(pagination.totalPages)" 
        :disabled="pagination.page === pagination.totalPages"
      >
        »»
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
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
    if (filters.value.dateFrom) params.append('dateFrom', filters.value.dateFrom);
    if (filters.value.dateTo) params.append('dateTo', filters.value.dateTo);
    
    const res = await fetch(`${backendBase}/api/events?${params}`);
    const data = await res.json();
    
    events.value = data.events || data; // Поддержка старого формата
    pagination.value = data.pagination;
  } catch (e) {
    console.error(e);
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

const changePage = (page) => {
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
    
    if (filters.value.dateFrom) params.append('dateFrom', filters.value.dateFrom);
    if (filters.value.dateTo) params.append('dateTo', filters.value.dateTo);
    
    const url = `${backendBase}/api/export/events?${params}`;
    window.open(url, '_blank');
  } catch (e) {
    console.error(e);
    alert('Ошибка экспорта');
  }
};

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString();
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
.filters {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.filters input,
.filters select {
  padding: 6px 8px;
  font-size: 14px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.filters input[type="text"] {
  flex: 1;
  min-width: 200px;
}

.filters button {
  padding: 6px 12px;
  background: #666;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.filters button:hover {
  background: #555;
}

.controls {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

button {
  padding: 6px 12px;
  font-size: 14px;
  cursor: pointer;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
}

button:hover:not(:disabled) {
  background: #f5f5f5;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th, td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f5f5f5;
  font-weight: 600;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.badge-in {
  background: #e0f7e9;
  color: #136b2b;
}

.badge-out {
  background: #ffe6e6;
  color: #a11616;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #666;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
}

.pagination button {
  padding: 6px 12px;
  min-width: 40px;
}

.page-info {
  margin: 0 8px;
  font-size: 14px;
  color: #666;
}
</style>
