<template>
  <div class="statistics">
    <!-- Фильтры -->
    <el-card shadow="never" class="filters-card">
      <el-row :gutter="16" align="middle">
        <el-col :xs="24" :sm="8">
          <el-date-picker
            v-model="dateFrom"
            type="date"
            placeholder="От"
            style="width: 100%"
            @change="fetchStatistics"
            format="DD.MM.YYYY"
            :prefix-icon="Calendar"
          />
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-date-picker
            v-model="dateTo"
            type="date"
            placeholder="До"
            style="width: 100%"
            @change="fetchStatistics"
            format="DD.MM.YYYY"
            :prefix-icon="Calendar"
          />
        </el-col>
        <el-col :xs="24" :sm="8">
          <el-button
            type="primary"
            :icon="Refresh"
            @click="fetchStatistics"
            :loading="loading"
            style="width: 100%"
          >
            Обновить
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <div v-loading="loading" element-loading-text="Загрузка статистики...">
      <div v-if="stats">
        <!-- Общая статистика -->
        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="Всего событий" :value="stats.summary.totalEvents">
                <template #prefix>
                  <el-icon color="#409eff" :size="24">
                    <DataLine />
                  </el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="Уникальных сотрудников" :value="stats.summary.uniqueEmployees">
                <template #prefix>
                  <el-icon color="#67c23a" :size="24">
                    <User />
                  </el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card shadow="hover" class="stat-card">
              <el-statistic title="Среднее событий/день" :value="stats.summary.avgEventsPerDay">
                <template #prefix>
                  <el-icon color="#e6a23c" :size="24">
                    <TrendCharts />
                  </el-icon>
                </template>
              </el-statistic>
            </el-card>
          </el-col>
        </el-row>

        <!-- График событий по дням -->
        <el-card shadow="hover" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Histogram /></el-icon>
                События по дням
              </span>
            </div>
          </template>
          
          <div class="chart-container">
            <div
              v-for="day in stats.eventsByDay.slice(0, 14)"
              :key="day.date"
              class="chart-bar"
            >
              <el-tooltip
                :content="`${formatDate(day.date)}: Приход ${day.ins}, Уход ${day.outs}`"
                placement="top"
              >
                <div class="bar-container">
                  <div
                    class="bar bar-in"
                    :style="{ height: (day.ins / maxEvents * 100) + '%' }"
                  ></div>
                  <div
                    class="bar bar-out"
                    :style="{ height: (day.outs / maxEvents * 100) + '%' }"
                  ></div>
                </div>
              </el-tooltip>
              <div class="bar-label">{{ formatDate(day.date) }}</div>
            </div>
          </div>
          
          <div class="legend">
            <el-tag type="success" effect="plain" size="small">
              <el-icon><Bottom /></el-icon>
              <span style="margin-left: 4px">Приход</span>
            </el-tag>
            <el-tag type="warning" effect="plain" size="small">
              <el-icon><Top /></el-icon>
              <span style="margin-left: 4px">Уход</span>
            </el-tag>
          </div>
        </el-card>

        <!-- Топ сотрудников -->
        <el-card shadow="hover" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Trophy /></el-icon>
                Топ 10 сотрудников по активности
              </span>
            </div>
          </template>
          
          <el-table
            :data="stats.topEmployees"
            stripe
            :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
          >
            <el-table-column label="Место" width="80" align="center">
              <template #default="{ $index }">
                <el-tag
                  v-if="$index === 0"
                  type="warning"
                  effect="dark"
                  size="large"
                >
                  🥇
                </el-tag>
                <el-tag
                  v-else-if="$index === 1"
                  type="info"
                  effect="dark"
                  size="large"
                >
                  🥈
                </el-tag>
                <el-tag
                  v-else-if="$index === 2"
                  type="danger"
                  effect="dark"
                  size="large"
                >
                  🥉
                </el-tag>
                <span v-else class="rank">{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            
            <el-table-column prop="name" label="Имя" min-width="150">
              <template #default="{ row }">
                <div class="employee-cell">
                  <el-icon><User /></el-icon>
                  <span class="employee-name">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="eventCount" label="Событий" width="120" align="center" sortable>
              <template #default="{ row }">
                <el-tag type="primary" effect="plain">
                  {{ row.eventCount }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <!-- Среднее время работы -->
        <el-card shadow="hover" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Clock /></el-icon>
                Среднее время на работе
              </span>
            </div>
          </template>
          
          <el-table
            :data="stats.workHours"
            stripe
            :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
          >
            <el-table-column prop="name" label="Имя" min-width="150">
              <template #default="{ row }">
                <div class="employee-cell">
                  <el-icon><User /></el-icon>
                  <span class="employee-name">{{ row.name }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column prop="totalDays" label="Дней на работе" width="150" align="center" sortable>
              <template #default="{ row }">
                <el-tag type="success" effect="plain">
                  {{ row.totalDays }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column prop="avgHoursPerDay" label="Средние часы/день" width="180" align="center" sortable>
              <template #default="{ row }">
                <el-tag type="warning" effect="plain">
                  {{ row.avgHoursPerDay }} ч
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Calendar,
  Refresh,
  DataLine,
  User,
  TrendCharts,
  Histogram,
  Trophy,
  Clock,
  Bottom,
  Top
} from '@element-plus/icons-vue';
import { config } from '../config.js';

const backendBase = config.backendUrl;

const stats = ref(null);
const loading = ref(false);
const dateFrom = ref(getDefaultDateFrom());
const dateTo = ref(getDefaultDateTo());

function getDefaultDateFrom() {
  const date = new Date();
  date.setDate(date.getDate() - 30);
  return date;
}

function getDefaultDateTo() {
  return new Date();
}

const maxEvents = computed(() => {
  if (!stats.value?.eventsByDay?.length) return 1;
  return Math.max(...stats.value.eventsByDay.map(d => Math.max(d.ins, d.outs)));
});

const fetchStatistics = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      dateFrom: dateFrom.value.toISOString().split('T')[0],
      dateTo: dateTo.value.toISOString().split('T')[0]
    });
    const res = await fetch(`${backendBase}/api/statistics?${params}`);
    stats.value = await res.json();
  } catch (e) {
    console.error(e);
    ElMessage.error('Не удалось загрузить статистику');
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
.statistics {
  width: 100%;
}

.filters-card {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  margin-bottom: 16px;
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%);
  border: none;
  border-radius: 12px;
}

:deep(.el-statistic__head) {
  font-size: 14px;
  color: #909399;
  font-weight: 500;
  margin-bottom: 12px;
}

:deep(.el-statistic__content) {
  display: flex;
  align-items: center;
  gap: 12px;
}

:deep(.el-statistic__number) {
  font-size: 32px;
  font-weight: 700;
  color: #303133;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.chart-container {
  display: flex;
  gap: 8px;
  height: 240px;
  align-items: flex-end;
  padding: 20px 0;
  border-bottom: 2px solid #303133;
  overflow-x: auto;
}

.chart-bar {
  flex: 1;
  min-width: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.bar-container {
  width: 100%;
  height: 200px;
  display: flex;
  gap: 3px;
  align-items: flex-end;
  justify-content: center;
}

.bar {
  width: 45%;
  min-height: 4px;
  border-radius: 6px 6px 0 0;
  transition: all 0.3s ease;
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
  transform: scaleY(1.05);
}

.bar-in {
  background: linear-gradient(180deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 -2px 8px rgba(103, 194, 58, 0.3);
}

.bar-out {
  background: linear-gradient(180deg, #e6a23c 0%, #ebb563 100%);
  box-shadow: 0 -2px 8px rgba(230, 162, 60, 0.3);
}

.bar-label {
  font-size: 11px;
  margin-top: 8px;
  text-align: center;
  color: #606266;
  font-weight: 500;
}

.legend {
  display: flex;
  gap: 16px;
  margin-top: 20px;
  justify-content: center;
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

.rank {
  font-size: 18px;
  font-weight: 600;
  color: #909399;
}

/* Адаптивность */
@media (max-width: 768px) {
  :deep(.el-col) {
    margin-bottom: 12px;
  }

  .chart-container {
    height: 200px;
    overflow-x: auto;
    padding: 10px 0;
  }

  .bar-container {
    height: 160px;
  }

  .bar-label {
    font-size: 10px;
  }

  :deep(.el-statistic__number) {
    font-size: 24px;
  }

  .card-title {
    font-size: 16px;
  }
  
  .employee-cell {
    font-size: 13px;
  }
}

/* Улучшение для средних экранов */
@media (min-width: 768px) and (max-width: 1023px) {
  .chart-container {
    height: 220px;
  }
  
  .bar-container {
    height: 180px;
  }
}
</style>
