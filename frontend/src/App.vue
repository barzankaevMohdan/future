<template>
  <div class="app">
    <header class="header">
      <h1>Учёт присутствия сотрудников кафе</h1>
      <nav class="tabs">
        <button 
          @click="currentTab = 'main'" 
          :class="{ active: currentTab === 'main' }"
        >
          Главная
        </button>
        <button 
          @click="currentTab = 'stats'" 
          :class="{ active: currentTab === 'stats' }"
        >
          Статистика
        </button>
      </nav>
    </header>

    <main class="content" v-if="currentTab === 'main'">
      <section class="panel">
        <h2>Камера</h2>
        <VideoStream />
      </section>

      <section class="panel">
        <h2>Сотрудники и присутствие</h2>
        <EmployeeList />
      </section>

      <section class="panel">
        <h2>Добавить сотрудника</h2>
        <AddEmployee @added="reloadEmployees" />
      </section>

      <section class="panel full-width">
        <h2>События</h2>
        <EventsTable />
      </section>
    </main>

    <main class="content-stats" v-if="currentTab === 'stats'">
      <section class="panel full-width">
        <h2>Статистика</h2>
        <Statistics />
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import VideoStream from './components/VideoStream.vue';
import EmployeeList from './components/EmployeeList.vue';
import AddEmployee from './components/AddEmployee.vue';
import EventsTable from './components/EventsTable.vue';
import Statistics from './components/Statistics.vue';

const currentTab = ref('main');

const reloadEmployees = () => {
  // компонент EmployeeList сам обновляется через WebSocket
};
</script>

<style scoped>
.app {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  margin-bottom: 12px;
}

.tabs {
  display: flex;
  gap: 4px;
  border-bottom: 2px solid #ddd;
}

.tabs button {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 15px;
  color: #666;
  transition: all 0.2s;
}

.tabs button:hover {
  color: #333;
  background: #f5f5f5;
}

.tabs button.active {
  color: #2196f3;
  border-bottom-color: #2196f3;
  font-weight: 600;
}

.content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.content-stats {
  display: block;
}

.panel {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  background: #fafafa;
}

.full-width {
  grid-column: 1 / -1;
}

@media (min-width: 900px) {
  .content {
    grid-template-columns: 1fr 1fr;
  }
  
  .content > :first-child {
    grid-column: 1 / -1;
  }
}
</style>
