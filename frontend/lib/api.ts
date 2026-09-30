const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
}

interface ApiError {
  detail: string
}

export class ApiClientError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiClientError'
    this.status = status
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let errorMessage = 'An error occurred'
    try {
      const error: ApiError = await response.json()
      errorMessage = error.detail || errorMessage
    } catch {
      // Use default error message
    }
    throw new ApiClientError(errorMessage, response.status)
  }
  return response.json()
}

export async function apiClient<T>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options

  const config: RequestInit = {
    method,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  }

  if (body) {
    config.body = JSON.stringify(body)
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config)
  return handleResponse<T>(response)
}

// Auth API
export interface LoginRequest {
  organization: string
  email: string
  password: string
}

export interface UserResponse {
  id: string
  full_name: string
  email: string
  role: 'admin' | 'manager' | 'sales'
  is_active: boolean
  organization_id: string
  created_at: string
  updated_at: string
}

export interface OrganizationResponse {
  id: string
  name: string
  slug: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface UserWithOrganizationResponse extends UserResponse {
  organization: OrganizationResponse
}

export interface LoginResponse {
  message: string
  user: UserWithOrganizationResponse
}

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient<LoginResponse>('/api/v1/auth/login', { method: 'POST', body: data }),

  logout: () => apiClient<{ message: string }>('/api/v1/auth/logout', { method: 'POST' }),

  me: () => apiClient<UserWithOrganizationResponse>('/api/v1/auth/me'),
}

// Users API
export interface UserListResponse {
  items: UserResponse[]
  total: number
  limit: number
  offset: number
}

export interface UserCreateRequest {
  full_name: string
  email: string
  password: string
  role: 'admin' | 'manager' | 'sales'
}

export interface UserUpdateRequest {
  full_name?: string
  email?: string
  role?: 'admin' | 'manager' | 'sales'
  is_active?: boolean
}

export const usersApi = {
  list: (limit = 20, offset = 0) =>
    apiClient<UserListResponse>(`/api/v1/users?limit=${limit}&offset=${offset}`),

  create: (data: UserCreateRequest) =>
    apiClient<UserResponse>('/api/v1/users', { method: 'POST', body: data }),

  get: (id: string) => apiClient<UserResponse>(`/api/v1/users/${id}`),

  update: (id: string, data: UserUpdateRequest) =>
    apiClient<UserResponse>(`/api/v1/users/${id}`, { method: 'PATCH', body: data }),
}

// Organization API
export const organizationApi = {
  get: () => apiClient<OrganizationResponse>('/api/v1/organization'),
}
