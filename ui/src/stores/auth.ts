import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin, signup as apiSignup } from '../api/authApi'

function parseJwtUsername(token: string | null): string | null {
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.username || null
  } catch {
    return null
  }
}

function isTokenExpired(token: string | null): boolean {
  if (!token) return true
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const username = computed(() => parseJwtUsername(token.value))
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !isTokenExpired(token.value))

  async function login(user: string, password: string) {
    error.value = null
    try {
      const accessToken = await apiLogin({ username: user, password })
      token.value = accessToken
      localStorage.setItem('token', accessToken)
    } catch (e: unknown) {
      error.value = 'Invalid username or password'
      throw e
    }
  }

  async function signup(user: string, email: string, password: string) {
    error.value = null
    try {
      await apiSignup({ username: user, email, password })
    } catch (e: unknown) {
      error.value = 'Signup failed. Please try again.'
      throw e
    }
  }

  function logout() {
    token.value = null
    localStorage.removeItem('token')
  }

  return { token, username, error, isAuthenticated, login, signup, logout }
})
