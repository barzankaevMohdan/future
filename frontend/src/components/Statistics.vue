<template>
  <div>
    <div class="filters">
      <label>
        От:
        <input type="date" v-model="dateFrom" @change="fetchStatistics" />
      </label>
      <label>
        До:
        <input type="date" v-model="dateTo" @change="fetchStatistics" />
      </label>
      <button @click="fetchStatistics" :disabled="loading">
        {{ loading ? 'Загрузка...' : 'Обновить' }}
      </button>
    </div>

    <div v-if="loading" class="loading">Загрузка статистики...</div>

    <div v-else-if="stats">
      <!-- Общая статистика -->
      <div class="summary-cards">
        <div class="card">
          <div class="card-title">Всего событий</div>
          <div class="card-value">{{ stats.summary.totalEvents }}</div>
        </div>
        <div class="card">
          <div class="card-title">Уникальных сотрудников</div>
          <div class="card-value">{{ stats.summary.uniqueEmployees }}</div>
        </div>
        <div class="card">
          <div class="card-title">Среднее событий/день</div>
          <div class="card-value">{{ stats.summary.avgEventsPerDay }}</div>
        </div>
      </div>

      <!-- График событий по дням -->
      <div class="section">
        <h3>События по дням</h3>
        <div class="chart-container">
          <div v-for="day in stats.eventsByDay.slice(0, 14)" :key="day.date" class="chart-bar">
            <div class="bar-container">
              <div 
                class="bar bar-in" 
                :style="{ height: (day.ins / maxEvents * 100) + '%' }"
                :title="`IN: ${day.ins}`"
              ></div>
              <div 
                class="bar bar-out" 
                :style="{ height: (day.outs / maxEvents * 100) + '%' }"
                :title="`OUT: ${day.outs}`"
              ></div>
            </div>
            <div class="bar-label">{{ formatDate(day.date) }}</div>
          </div>
        </div>
        <div class="legend">
          <span class="legend-item"><span class="legend-color legend-in"></span> Приход</span>
          <span class="legend-item"><span class="legend-color legend-out"></span> Уход</span>
        </div>
      </div>

      <!-- Топ сотрудников -->
      <div class="section">
        <h3>Топ 10 сотрудников по активности</h3>
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Имя</th>
              <th>Событий</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(emp, idx) in stats.topEmployees" :key="emp.id">
              <td>{{ idx + 1 }}</td>
              <td>{{ emp.name }}</td>
              <td>{{ emp.eventCount }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Среднее время работы -->
      <div class="section">
        <h3>Среднее время на работе</h3>
        <table class="table">
          <thead>
            <tr>
              <th>Имя</th>
              <th>Дней на работе</th>
              <th>Средние часы/день</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="emp in stats.workHours" :key="emp.id">
              <td>{{ emp.name }}</td>
              <td>{{ emp.totalDays }}</td>
              <td>{{ emp.avgHoursPerDay }} ч</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { config } from '../config.js';

const backendBase = config.backendUrl;

const stats = ref(null);
const loading = ref(false);
const dateFrom = ref(getDefaultDateFrom());
const dateTo = ref(getDefaultDateTo());

function getDefaultDateFrom() {
  const date = new Date();
  date.setDate(date.getDate() - 30);
  return date.toISOString().split('T')[0];
}

function getDefaultDateTo() {
  return new Date().toISOString().split('T')[0];
}

const maxEvents = computed(() => {
  if (!stats.value?.eventsByDay?.length) return 1;
  return Math.max(...stats.value.eventsByDay.map(d => Math.max(d.ins, d.outs)));
});

const fetchStatistics = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      dateFrom: dateFrom.value,
      dateTo: dateTo.value
    });
    const res = await fetch(`${backendBase}/api/statistics?${params}`);
    stats.value = await res.json();
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', { month: 'short', day: 'numeric' });
};

onMounted(() => {
  fetchStatistics();
});
</script>

<style scoped>
.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.filters label {
  display: flex;
  flex-direction: column;
  font-size: 14px;
}

.filters input {
  margin-top: 4px;
  padding: 4px 6px;
}

.filters button {
  padding: 6px 12px;
  cursor: pointer;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.card {
  background: #f5f5f5;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #ddd;
}

.card-title {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.card-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.section {
  margin-bottom: 32px;
}

.section h3 {
  margin-bottom: 12px;
  font-size: 16px;
}

.chart-container {
  display: flex;
  gap: 8px;
  height: 200px;
  align-items: flex-end;
  padding: 10px 0;
  border-bottom: 2px solid #333;
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.bar-container {
  width: 100%;
  height: 180px;
  display: flex;
  gap: 2px;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 40%;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s;
}

.bar:hover {
  opacity: 0.8;
}

.bar-in {
  background: #4caf50;
}

.bar-out {
  background: #f44336;
}

.bar-label {
  font-size: 11px;
  margin-top: 4px;
  text-align: center;
  color: #666;
}

.legend {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-in {
  background: #4caf50;
}

.legend-out {
  background: #f44336;
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
</style>


