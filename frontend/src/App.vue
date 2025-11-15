<template>
  <div class="app">
    <header class="header">
      <h1>Учёт присутствия сотрудников кафе</h1>
    </header>

    <main class="content">
      <section class="panel">
        <h2>Сотрудники и присутствие</h2>
        <EmployeeList />
      </section>

      <section class="panel">
        <h2>Добавить сотрудника</h2>
        <AddEmployee @added="reloadEmployees" />
      </section>

      <section class="panel">
        <h2>Последние события</h2>
        <EventsTable />
      </section>
    </main>
  </div>
</template>

<script setup>
import EmployeeList from './components/EmployeeList.vue';
import AddEmployee from './components/AddEmployee.vue';
import EventsTable from './components/EventsTable.vue';

const reloadEmployees = () => {
  // компонент EmployeeList сам с интервалом обновляется, так что пока ничего
};
</script>

<style scoped>
.app {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: 16px;
  max-width: 1100px;
  margin: 0 auto;
}

.header h1 {
  margin-bottom: 16px;
}

.content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.panel {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px 16px;
  background: #fafafa;
}

@media (min-width: 900px) {
  .content {
    grid-template-columns: 2fr 1fr;
  }

  .content > :nth-child(3) {
    grid-column: 1 / -1;
  }
}
</style>
