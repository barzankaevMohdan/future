<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Plus, OfficeBuilding } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import apiClient from '@/api/client'

interface Company {
  id: number
  name: string
  slug: string
  isActive: boolean
  createdAt: string
}

const companies = ref<Company[]>([])
const loading = ref(true)
const dialogVisible = ref(false)

const form = ref({
  name: '',
  slug: '',
})

onMounted(async () => {
  await loadCompanies()
})

async function loadCompanies() {
  loading.value = true
  try {
    const response = await apiClient.get('/api/companies')
    companies.value = response.data
  } catch (error) {
    ElMessage.error('Не удалось загрузить компании')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  try {
    await apiClient.post('/api/companies', form.value)
    ElMessage.success('Компания успешно создана')
    dialogVisible.value = false
    form.value = { name: '', slug: '' }
    await loadCompanies()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || 'Не удалось создать компанию')
  }
}

async function toggleCompany(id: number, isActive: boolean) {
  try {
    await apiClient.put(`/api/companies/${id}`, { isActive: !isActive })
    ElMessage.success(isActive ? 'Компания деактивирована' : 'Компания активирована')
    await loadCompanies()
  } catch (error) {
    ElMessage.error('Не удалось обновить компанию')
  }
}

function generateSlug() {
  form.value.slug = form.value.name
    .toLowerCase()
    .replace(/[^a-z0-9а-я]+/g, '-')
    .replace(/^-|-$/g, '')
}
</script>

<template>
  <div class="page-container">
    <el-page-header class="page-header">
      <template #content>
        <h1 class="page-title">Компании</h1>
      </template>
      <template #extra>
        <el-button type="primary" :icon="Plus" @click="dialogVisible = true">
          Добавить компанию
        </el-button>
      </template>
    </el-page-header>

    <el-card shadow="never">
      <el-table :data="companies" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column prop="name" label="Название" min-width="200" />
        
        <el-table-column label="Slug" min-width="180">
          <template #default="{ row }">
            <el-tag type="info">{{ row.slug }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Статус" width="120">
          <template #default="{ row }">
            <el-tag :type="row.isActive ? 'success' : 'danger'">
              {{ row.isActive ? 'Активна' : 'Неактивна' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="Создана" width="150">
          <template #default="{ row }">
            {{ new Date(row.createdAt).toLocaleDateString('ru-RU') }}
          </template>
        </el-table-column>
        
        <el-table-column label="Действия" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              size="small"
              :type="row.isActive ? 'warning' : 'success'"
              @click="toggleCompany(row.id, row.isActive)"
            >
              {{ row.isActive ? 'Деактивировать' : 'Активировать' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      title="Добавить компанию"
      width="500px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="Название" required>
          <el-input
            v-model="form.name"
            placeholder="Название компании"
            @input="generateSlug"
          />
        </el-form-item>

        <el-form-item label="Slug" required>
          <el-input
            v-model="form.slug"
            placeholder="company-slug"
          >
            <template #prepend>/</template>
          </el-input>
          <template #extra>
            <span style="font-size: 12px; color: #909399;">
              Только строчные буквы, цифры и дефисы
            </span>
          </template>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">Отмена</el-button>
        <el-button type="primary" @click="handleSubmit">Создать</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.page-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }
}
</style>
