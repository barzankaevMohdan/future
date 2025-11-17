<template>
  <div class="employee-list">
    <el-skeleton :loading="loading" :rows="5" animated>
      <div v-if="employees.length > 0">
        <el-table
          :data="employees"
          style="width: 100%"
          :default-sort="{ prop: 'present', order: 'descending' }"
          stripe
          :header-cell-style="{ background: '#f5f7fa', fontWeight: '600' }"
        >
          <el-table-column label="Фото" width="80" align="center">
            <template #default="{ row }">
              <el-avatar
                v-if="row.photoUrl"
                :src="backendBase + row.photoUrl"
                :size="56"
                shape="circle"
                fit="cover"
              />
              <el-avatar v-else :size="56" :icon="UserFilled" />
            </template>
          </el-table-column>

          <el-table-column prop="name" label="Имя" min-width="120" sortable>
            <template #default="{ row }">
              <div class="name-cell">
                <span class="employee-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>

          <el-table-column prop="role" label="Роль" min-width="100">
            <template #default="{ row }">
              <el-tag v-if="row.role" type="info" size="small" effect="plain">
                {{ row.role }}
              </el-tag>
              <span v-else class="no-role">—</span>
            </template>
          </el-table-column>

          <el-table-column prop="present" label="Статус" width="130" sortable>
            <template #default="{ row }">
              <el-tag
                :type="row.present ? 'success' : 'info'"
                effect="dark"
                size="default"
              >
                <el-icon><CircleCheck v-if="row.present" /><CircleClose v-else /></el-icon>
                <span style="margin-left: 4px">
                  {{ row.present ? 'На месте' : 'Отсутствует' }}
                </span>
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="Последнее событие" min-width="160">
            <template #default="{ row }">
              <div v-if="row.lastEventType" class="event-info">
                <el-tag
                  :type="row.lastEventType === 'IN' ? 'success' : 'warning'"
                  size="small"
                  effect="plain"
                >
                  {{ row.lastEventType === 'IN' ? 'Приход' : 'Уход' }}
                </el-tag>
                <div class="event-time">{{ formatTime(row.lastEventTime) }}</div>
              </div>
              <span v-else class="no-event">—</span>
            </template>
          </el-table-column>

          <el-table-column label="Действия" width="120" align="center" fixed="right">
            <template #default="{ row }">
              <el-popconfirm
                :title="`Удалить сотрудника ${row.name}?`"
                confirm-button-text="Удалить"
                cancel-button-text="Отмена"
                confirm-button-type="danger"
                width="250"
                @confirm="deleteEmployee(row.id)"
              >
                <template #reference>
                  <el-button
                    type="danger"
                    size="small"
                    :icon="Delete"
                    :loading="deleting === row.id"
                    circle
                  />
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <el-empty v-else description="Пока нет сотрудников" :image-size="120">
        <template #image>
          <el-icon :size="80" color="#909399">
            <User />
          </el-icon>
        </template>
      </el-empty>
    </el-skeleton>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { ElMessage } from 'element-plus';
import {
  UserFilled,
  Delete,
  CircleCheck,
  CircleClose,
  User
} from '@element-plus/icons-vue';
import { config } from '../config.js';
import { getSocket } from '../socket.js';

const backendBase = config.backendUrl;

const employees = ref([]);
const loading = ref(false);
const deleting = ref(null);
let socket = null;

const fetchPresence = async () => {
  loading.value = true;
  try {
    const res = await fetch(backendBase + '/api/presence');
    employees.value = await res.json();
  } catch (e) {
    console.error(e);
    ElMessage.error('Не удалось загрузить список сотрудников');
  } finally {
    loading.value = false;
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
    minute: '2-digit'
  });
};

const deleteEmployee = async (id) => {
  deleting.value = id;
  try {
    const res = await fetch(`${backendBase}/api/employees/${id}`, {
      method: 'DELETE'
    });

    if (res.ok) {
      await fetchPresence();
      ElMessage.success('Сотрудник удалён');
    } else {
      const error = await res.json().catch(() => ({ error: 'Unknown error' }));
      ElMessage.error(`Ошибка: ${error.error}`);
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('Ошибка при удалении сотрудника');
  } finally {
    deleting.value = null;
  }
};

onMounted(() => {
  fetchPresence();

  // WebSocket для реал-тайм обновлений
  socket = getSocket();

  socket.on('event:created', () => {
    console.log('[EmployeeList] Event created, refreshing...');
    fetchPresence();
  });

  socket.on('employee:added', () => {
    console.log('[EmployeeList] Employee added, refreshing...');
    fetchPresence();
  });

  socket.on('employee:deleted', () => {
    console.log('[EmployeeList] Employee deleted, refreshing...');
    fetchPresence();
  });
});

onBeforeUnmount(() => {
  if (socket) {
    socket.off('event:created');
    socket.off('employee:added');
    socket.off('employee:deleted');
  }
});
</script>

<style scoped>
.employee-list {
  width: 100%;
}

.name-cell {
  display: flex;
  flex-direction: column;
}

.employee-name {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
}

.no-role,
.no-event {
  color: #909399;
  font-size: 14px;
}

.event-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.event-time {
  font-size: 12px;
  color: #909399;
}

:deep(.el-table) {
  font-size: 14px;
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__row) {
  transition: all 0.3s;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-button.is-circle) {
  padding: 8px;
}

/* Адаптивность таблицы */
@media (max-width: 768px) {
  :deep(.el-table) {
    font-size: 12px;
  }
  
  .employee-name {
    font-size: 13px;
  }
}
</style>
