import axios from 'axios'

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

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
