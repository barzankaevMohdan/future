<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Menu as IconMenu,
  Location,
  Document,
  Setting,
  User,
  VideoCamera,
  View,
  TrendCharts,
  OfficeBuilding,
  Monitor,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeIndex = computed(() => route.path)

const menuItems = computed(() => {
  const items = [
    { index: '/dashboard', title: 'Дашборд', icon: TrendCharts },
    { index: '/employees', title: 'Сотрудники', icon: User },
    { index: '/cameras', title: 'Камеры', icon: VideoCamera },
    { index: '/presence', title: 'Присутствие', icon: Location },
    { index: '/events', title: 'События', icon: Document },
    { index: '/statistics', title: 'Статистика', icon: TrendCharts },
    { index: '/live', title: 'Прямые трансляции', icon: Monitor },
  ]
  
  if (authStore.isSuperAdmin) {
    items.push({ index: '/companies', title: 'Компании', icon: OfficeBuilding })
  }
  
  return items
})

function handleSelect(index: string) {
  router.push(index)
}

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <el-aside width="250px" class="sidebar">
      <div class="logo">
        <h2>Face Recognition</h2>
      </div>
      
      <el-menu
        :default-active="activeIndex"
        class="sidebar-menu"
        @select="handleSelect"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.index"
          :index="item.index"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
      
      <div class="user-section">
        <div class="user-info">
          <el-icon size="20"><User /></el-icon>
          <div class="user-details">
            <div class="user-email">{{ authStore.user?.email }}</div>
            <div class="user-role">{{ authStore.user?.role }}</div>
          </div>
        </div>
        <el-button type="danger" size="small" @click="logout" style="width: 100%">
          Выйти
        </el-button>
      </div>
    </el-aside>

    <el-container>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  min-height: 100vh;
}

.sidebar {
  background: #ffffff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 24px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.logo h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
}

.user-section {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  padding: 8px;
  background: #f5f7fa;
  border-radius: 8px;
}

.user-details {
  flex: 1;
  min-width: 0;
}

.user-email {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: 12px;
  color: #909399;
}

.main-content {
  background: #f0f2f5;
  padding: 0;
}

@media (max-width: 768px) {
  .sidebar {
    width: 200px !important;
  }
  
  .logo h2 {
    font-size: 16px;
  }
}
</style>


