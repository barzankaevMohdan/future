<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
const showForm = ref(false)

const form = ref({
  name: '',
  slug: '',
})

onMounted(async () => {
  await loadCompanies()
})

async function loadCompanies() {
  try {
    const response = await apiClient.get('/api/companies')
    companies.value = response.data
  } catch (error) {
    console.error('Failed to load companies:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  try {
    await apiClient.post('/api/companies', form.value)
    showForm.value = false
    form.value = { name: '', slug: '' }
    await loadCompanies()
  } catch (error: any) {
    alert(error.response?.data?.error || 'Failed to create company')
  }
}

async function toggleCompany(id: number, isActive: boolean) {
  try {
    await apiClient.put(`/api/companies/${id}`, { isActive: !isActive })
    await loadCompanies()
  } catch (error) {
    alert('Failed to update company')
  }
}

function generateSlug() {
  form.value.slug = form.value.name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Companies</h1>
      <button @click="showForm = !showForm" class="primary">
        {{ showForm ? 'Cancel' : '+ Add Company' }}
      </button>
    </header>

    <div v-if="showForm" class="card form-card">
      <h2>Add Company</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="form.name" @input="generateSlug" required />
        </div>

        <div class="form-group">
          <label>Slug *</label>
          <input v-model="form.slug" required pattern="[a-z0-9-]+" />
          <small>Lowercase letters, numbers and hyphens only</small>
        </div>

        <button type="submit" class="primary">Create Company</button>
      </form>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="card">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Slug</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="company in companies" :key="company.id">
            <td>{{ company.id }}</td>
            <td>{{ company.name }}</td>
            <td><code>{{ company.slug }}</code></td>
            <td>
              <span :class="['badge', company.isActive ? 'success' : 'danger']">
                {{ company.isActive ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ new Date(company.createdAt).toLocaleDateString() }}</td>
            <td>
              <button @click="toggleCompany(company.id, company.isActive)" class="secondary small">
                {{ company.isActive ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.form-card {
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

small {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-secondary);
  font-size: 0.75rem;
}

code {
  background: var(--bg-secondary);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.875rem;
}

button.small {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  margin-right: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>







