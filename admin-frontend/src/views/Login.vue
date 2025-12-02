<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = ref({
  email: '',
  password: '',
})

const loading = ref(false)

async function handleLogin() {
  loading.value = true

  try {
    await authStore.login(loginForm.value.email, loginForm.value.password)
    ElMessage.success('Вход выполнен успешно')
    router.push('/dashboard')
  } catch (err: any) {
    ElMessage.error(err.response?.data?.error || 'Ошибка входа')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <el-card class="login-card" shadow="always">
      <div class="login-header">
        <h1>Панель управления</h1>
        <p class="subtitle">Система учета посещаемости с распознаванием лиц</p>
      </div>

      <el-form
        :model="loginForm"
        @submit.prevent="handleLogin"
        label-position="top"
        size="large"
      >
        <el-form-item label="Email">
          <el-input
            v-model="loginForm.email"
            :prefix-icon="User"
            type="email"
            placeholder="admin@example.com"
            required
          />
        </el-form-item>

        <el-form-item label="Пароль">
          <el-input
            v-model="loginForm.password"
            :prefix-icon="Lock"
            type="password"
            placeholder="••••••••"
            show-password
            required
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            style="width: 100%"
            size="large"
          >
            {{ loading ? 'Вход...' : 'Войти' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-footer">
        <el-divider />
        <p class="demo-accounts">
          <strong>Тестовые аккаунты:</strong><br>
          SUPERADMIN: superadmin@system.com<br>
          ADMIN: admin@demo.com
        </p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 420px;
  border-radius: 12px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.login-footer {
  margin-top: 24px;
}

.demo-accounts {
  margin: 0;
  font-size: 12px;
  color: #909399;
  text-align: center;
  line-height: 1.6;
}

@media (max-width: 480px) {
  .login-page {
    padding: 16px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>
