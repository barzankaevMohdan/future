import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'

interface User {
  id: number
  email: string
  role: string
  companyId: number | null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)

  const isAuthenticated = computed(() => !!accessToken.value)
  const isSuperAdmin = computed(() => user.value?.role === 'SUPERADMIN')
  const isCompanyAdmin = computed(() => user.value?.role === 'COMPANY_ADMIN')

  // Load from localStorage on init
  const storedAccessToken = localStorage.getItem('accessToken')
  const storedRefreshToken = localStorage.getItem('refreshToken')
  const storedUser = localStorage.getItem('user')

  if (storedAccessToken && storedRefreshToken && storedUser) {
    accessToken.value = storedAccessToken
    refreshToken.value = storedRefreshToken
    user.value = JSON.parse(storedUser)
  }

  async function login(email: string, password: string) {
    const response = await apiClient.post('/api/auth/login', { email, password })
    
    accessToken.value = response.data.accessToken
    refreshToken.value = response.data.refreshToken
    user.value = response.data.user

    localStorage.setItem('accessToken', accessToken.value)
    localStorage.setItem('refreshToken', refreshToken.value)
    localStorage.setItem('user', JSON.stringify(user.value))
  }

  async function refreshTokenFn() {
    if (!refreshToken.value) {
      throw new Error('No refresh token')
    }

    const response = await apiClient.post('/api/auth/refresh', {
      refreshToken: refreshToken.value,
    })

    accessToken.value = response.data.accessToken
    localStorage.setItem('accessToken', accessToken.value)
  }

  function logout() {
    accessToken.value = null
    refreshToken.value = null
    user.value = null

    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('user')
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isSuperAdmin,
    isCompanyAdmin,
    login,
    refreshTokenFn,
    logout,
  }
})



