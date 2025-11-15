<template>
  <div>
    <div class="controls">
      <button @click="fetchEvents" :disabled="loading">
        {{ loading ? 'Обновляю...' : 'Обновить' }}
      </button>
    </div>
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
          <td>{{ ev.type }}</td>
          <td>{{ formatTime(ev.timestamp) }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else>Событий пока нет</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const backendBase = 'http://localhost:3000';

const events = ref([]);
const loading = ref(false);

const fetchEvents = async () => {
  loading.value = true;
  try {
    const res = await fetch(backendBase + '/api/events?limit=200');
    events.value = await res.json();
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
  fetchEvents();
});
</script>

<style scoped>
.controls {
  margin-bottom: 8px;
}

button {
  padding: 4px 8px;
  font-size: 14px;
  cursor: pointer;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th, td {
  padding: 4px 8px;
  border-bottom: 1px solid #eee;
}
</style>
