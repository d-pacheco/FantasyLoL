import { api } from './client'

interface LoginRequest {
  username: string
  password: string
}

interface SignupRequest {
  username: string
  email: string
  password: string
}

interface LoginResponse {
  access_token: string
}

export async function login(data: LoginRequest): Promise<string> {
  const res = await api.post<LoginResponse>('/user/login', data)
  return res.data.access_token
}

export async function signup(data: SignupRequest): Promise<void> {
  await api.post('/user/signup', data)
}
