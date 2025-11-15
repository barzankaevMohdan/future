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
          </tr>
        </tbody>
      </table>
      <div v-if="!employees.length">Пока нет сотрудников</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const backendBase = 'http://localhost:3000';

const employees = ref([]);
const loading = ref(false);
let intervalId = null;

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

onMounted(() => {
  fetchPresence();
  intervalId = setInterval(fetchPresence, 5000);
});

onBeforeUnmount(() => {
  if (intervalId) clearInterval(intervalId);
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
</style>
