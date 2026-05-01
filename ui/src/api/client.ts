import axios from 'axios'

export const fantasyApi = axios.create({
  baseURL: import.meta.env.VITE_FANTASY_API_URL,
})

export const riotApi = axios.create({
  baseURL: import.meta.env.VITE_RIOT_API_URL,
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

fantasyApi.interceptors.request.use(attachToken)
fantasyApi.interceptors.response.use((r) => r, handleUnauthorized)

riotApi.interceptors.request.use(attachToken)
riotApi.interceptors.response.use((r) => r, handleUnauthorized)
