<template>
  <div>
    <div v-if="loading">Загрузка...</div>
    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>Фото</th>
            <th>Имя</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Последнее событие</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="emp in employees" :key="emp.id">
            <td>
              <img
                v-if="emp.photoUrl"
                :src="backendBase + emp.photoUrl"
                alt="photo"
                class="avatar"
              />
            </td>
            <td>{{ emp.name }}</td>
            <td>{{ emp.role || '—' }}</td>
            <td>
              <span :class="['status', emp.present ? 'status--present' : 'status--absent']">
                {{ emp.present ? 'На месте' : 'Отсутствует' }}
              </span>
            </td>
            <td>
              <span v-if="emp.lastEventType">
                {{ emp.lastEventType }}<br />
                <small>{{ formatTime(emp.lastEventTime) }}</small>
              </span>
              <span v-else>—</span>
            </td>
            <td>
              <button 
                @click="deleteEmployee(emp.id, emp.name)" 
                class="btn-delete"
                :disabled="deleting === emp.id"
              >
                {{ deleting === emp.id ? 'Удаление...' : 'Удалить' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!employees.length">Пока нет сотрудников</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
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
  } finally {
    loading.value = false;
  }
};

const formatTime = (iso) => {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleString();
};

const deleteEmployee = async (id, name) => {
  if (!confirm(`Точно удалить сотрудника "${name}"? Это также удалит все события этого сотрудника.`)) {
    return;
  }
  
  deleting.value = id;
  try {
    const res = await fetch(`${backendBase}/api/employees/${id}`, {
      method: 'DELETE'
    });
    
    if (res.ok) {
      await fetchPresence();
    } else {
      const error = await res.json().catch(() => ({ error: 'Unknown error' }));
      alert(`Ошибка: ${error.error}`);
    }
  } catch (e) {
    console.error(e);
    alert('Ошибка при удалении сотрудника');
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
.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th, td {
  padding: 4px 8px;
  border-bottom: 1px solid #eee;
}

.avatar {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 50%;
}

.status {
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.status--present {
  background: #e0f7e9;
  color: #136b2b;
}

.status--absent {
  background: #ffe6e6;
  color: #a11616;
}

.btn-delete {
  background: #f44336;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.btn-delete:hover:not(:disabled) {
  background: #d32f2f;
}

.btn-delete:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>
