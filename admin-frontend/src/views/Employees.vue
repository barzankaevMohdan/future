<script setup lang="ts">
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'

interface Employee {
  id: number
  name: string
  role: string | null
  photoUrl: string | null
}

const employees = ref<Employee[]>([])
const loading = ref(true)
const showForm = ref(false)

const form = ref({
  name: '',
  roleTitle: '',
  photo: null as File | null,
})

onMounted(async () => {
  await loadEmployees()
})

async function loadEmployees() {
  try {
    const response = await apiClient.get('/api/employees')
    employees.value = response.data
  } catch (error) {
    console.error('Failed to load employees:', error)
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  try {
    const formData = new FormData()
    formData.append('name', form.value.name)
    if (form.value.roleTitle) {
      formData.append('roleTitle', form.value.roleTitle)
    }
    if (form.value.photo) {
      formData.append('photo', form.value.photo)
    }

    await apiClient.post('/api/employees', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    showForm.value = false
    form.value = { name: '', roleTitle: '', photo: null }
    await loadEmployees()
  } catch (error: any) {
    alert(error.response?.data?.error || 'Failed to create employee')
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    form.value.photo = target.files[0]
  }
}

async function deleteEmployee(id: number) {
  if (!confirm('Delete this employee?')) return

  try {
    await apiClient.delete(`/api/employees/${id}`)
    await loadEmployees()
  } catch (error) {
    alert('Failed to delete employee')
  }
}
</script>

<template>
  <div class="page">
    <header class="page-header">
      <h1>Employees</h1>
      <button @click="showForm = !showForm" class="primary">
        {{ showForm ? 'Cancel' : '+ Add Employee' }}
      </button>
    </header>

    <div v-if="showForm" class="card form-card">
      <h2>Add Employee</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="form.name" required />
        </div>

        <div class="form-group">
          <label>Role</label>
          <input v-model="form.roleTitle" placeholder="Manager, Staff, etc." />
        </div>

        <div class="form-group">
          <label>Photo</label>
          <input type="file" accept="image/*" @change="handleFileChange" />
        </div>

        <button type="submit" class="primary">Create Employee</button>
      </form>
    </div>

    <div v-if="loading" class="loading">Loading...</div>

    <div v-else class="card">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Photo</th>
            <th>Name</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="emp in employees" :key="emp.id">
            <td>{{ emp.id }}</td>
            <td>
              <img
                v-if="emp.photoUrl"
                :src="emp.photoUrl"
                class="employee-photo"
                alt="Photo"
              />
              <span v-else class="no-photo">No photo</span>
            </td>
            <td>{{ emp.name }}</td>
            <td>{{ emp.role || '-' }}</td>
            <td>
              <button @click="deleteEmployee(emp.id)" class="danger small">
                Delete
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
  max-width: 1200px;
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

input {
  width: 100%;
}

.employee-photo {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  object-fit: cover;
}

.no-photo {
  color: var(--text-secondary);
  font-size: 0.875rem;
}

button.small {
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}
</style>







