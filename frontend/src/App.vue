<template>
  <div class="app-wrapper">
    <div class="app-container">
      <el-container>
        <el-header class="app-header">
          <div class="header-content">
            <div class="logo-section">
              <el-icon :size="32" color="#409eff">
                <VideoCamera />
              </el-icon>
              <h1 class="app-title">Учёт присутствия сотрудников</h1>
            </div>
            <el-menu
              :default-active="currentTab"
              mode="horizontal"
              @select="handleTabChange"
              class="nav-menu"
            >
              <el-menu-item index="main">
                <el-icon><HomeFilled /></el-icon>
                <span>Главная</span>
              </el-menu-item>
              <el-menu-item index="stats">
                <el-icon><DataAnalysis /></el-icon>
                <span>Статистика</span>
              </el-menu-item>
            </el-menu>
          </div>
        </el-header>

        <el-main class="app-main">
        <!-- Главная страница -->
        <div v-if="currentTab === 'main'" class="main-layout">
          <!-- Камера - полная ширина сверху -->
          <el-card class="video-card full-width" shadow="hover">
            <VideoStream />
          </el-card>

          <!-- Сотрудники и Добавление сотрудника -->
          <div class="two-columns">
            <el-card class="employees-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">
                    <el-icon><User /></el-icon>
                    Сотрудники и присутствие
                  </span>
                </div>
              </template>
              <EmployeeList />
            </el-card>

            <el-card class="add-employee-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span class="card-title">
                    <el-icon><UserFilled /></el-icon>
                    Добавить сотрудника
                  </span>
                </div>
              </template>
              <AddEmployee @added="reloadEmployees" />
            </el-card>
          </div>

          <!-- События - полная ширина -->
          <el-card class="events-card full-width" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><List /></el-icon>
                  События
                </span>
              </div>
            </template>
            <EventsTable />
          </el-card>
        </div>

        <!-- Страница статистики -->
        <div v-if="currentTab === 'stats'" class="stats-layout">
          <el-card class="stats-card full-width" shadow="hover">
            <template #header>
              <div class="card-header">
                <span class="card-title">
                  <el-icon><DataAnalysis /></el-icon>
                  Статистика
                </span>
              </div>
            </template>
            <Statistics />
          </el-card>
        </div>
      </el-main>
    </el-container>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import {
  VideoCamera,
  HomeFilled,
  DataAnalysis,
  User,
  UserFilled,
  List
} from '@element-plus/icons-vue';
import VideoStream from './components/VideoStream.vue';
import EmployeeList from './components/EmployeeList.vue';
import AddEmployee from './components/AddEmployee.vue';
import EventsTable from './components/EventsTable.vue';
import Statistics from './components/Statistics.vue';

const currentTab = ref('main');

const handleTabChange = (key) => {
  currentTab.value = key;
};

const reloadEmployees = () => {
  // компонент EmployeeList сам обновляется через WebSocket
};
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app-wrapper {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  display: flex;
  justify-content: center;
}

.app-container {
  width: 100%;
  max-width: 1320px;
  margin: 0 auto;
}

.el-container {
  background: transparent;
  min-height: calc(100vh - 40px);
}

.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 0;
  height: auto;
  margin-bottom: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 16px;
}

.app-title {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  border: none;
  background: transparent;
}

.nav-menu .el-menu-item {
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
  margin: 0 4px;
}

.app-main {
  padding: 0;
}

.main-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.two-columns {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 1024px) {
  .two-columns {
    grid-template-columns: 1fr;
  }
}

.stats-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.full-width {
  grid-column: 1 / -1;
}

.video-card,
.employees-card,
.add-employee-card,
.events-card,
.stats-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  border: none;
}

:deep(.el-card__header) {
  background: transparent;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  padding: 20px;
}

:deep(.el-card__body) {
  padding: 20px;
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

/* Адаптивность для мобильных */
@media (max-width: 768px) {
  .app-wrapper {
    padding: 12px;
  }

  .header-content {
    padding: 16px;
  }

  .app-title {
    font-size: 20px;
  }

  .logo-section {
    gap: 12px;
  }

  .card-title {
    font-size: 16px;
  }
}

/* Адаптивность для планшетов */
@media (min-width: 768px) and (max-width: 1023px) {
  .two-columns {
    grid-template-columns: 1fr;
  }
}
</style>
