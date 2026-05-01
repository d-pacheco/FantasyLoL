import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, signup as apiSignup } from '../api/authApi'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    error.value = null
    try {
      const accessToken = await apiLogin({ username, password })
      token.value = accessToken
      localStorage.setItem('token', accessToken)
    } catch (e: unknown) {
      error.value = 'Invalid username or password'
      throw e
    }
  }

  async function signup(username: string, email: string, password: string) {
    error.value = null
    try {
      await apiSignup({ username, email, password })
    } catch (e: unknown) {
      error.value = 'Signup failed. Please try again.'
      throw e
    }
  }

  function logout() {
    token.value = null
    localStorage.removeItem('token')
  }

  return { token, error, isAuthenticated, login, signup, logout }
})
