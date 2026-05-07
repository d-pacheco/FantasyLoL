import axios from 'axios'

export const api = axios.create({
  baseURL: '/api/v1',
})

function attachToken(config: import('axios').InternalAxiosRequestConfig) {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}

function handleUnauthorized(error: unknown) {
  if (axios.isAxiosError(error) && error.response?.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }
  return Promise.reject(error)
}

api.interceptors.request.use(attachToken)
api.interceptors.response.use((r) => r, handleUnauthorized)
