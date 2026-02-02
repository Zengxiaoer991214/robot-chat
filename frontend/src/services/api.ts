/**
 * API service for backend communication
 */
import axios from 'axios'
import type { Agent, Room, Message, CreateAgentRequest, CreateRoomRequest, Role, CreateRoleRequest } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear auth state
      localStorage.removeItem('token')
      localStorage.removeItem('isAuthenticated')
      // Redirect to login if not already there
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (credentials: any): Promise<any> => {
    // credentials: { username, password }
    const params = new URLSearchParams()
    params.append('username', credentials.username)
    params.append('password', credentials.password)
    
    const response = await api.post<any>('/auth/token', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },
  
  register: async (data: any): Promise<any> => {
    // data: { username, password, email }
    const response = await api.post<any>('/auth/register', data)
    return response.data
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('isAuthenticated')
    window.location.href = '/login'
  }
}

export const agentApi = {
  getAll: async (): Promise<Agent[]> => {
    const response = await api.get<Agent[]>('/agents')
    return response.data
  },

  getById: async (id: number): Promise<Agent> => {
    const response = await api.get<Agent>(`/agents/${id}`)
    return response.data
  },

  create: async (data: CreateAgentRequest): Promise<Agent> => {
    const response = await api.post<Agent>('/agents', data)
    return response.data
  },

  update: async (id: number, data: Partial<CreateAgentRequest>): Promise<Agent> => {
    const response = await api.patch<Agent>(`/agents/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/agents/${id}`)
  },
}

// Role API
export const roleApi = {
  getAll: async (): Promise<Role[]> => {
    const response = await api.get<Role[]>('/roles')
    return response.data
  },

  getById: async (id: number): Promise<Role> => {
    const response = await api.get<Role>(`/roles/${id}`)
    return response.data
  },

  create: async (data: CreateRoleRequest): Promise<Role> => {
    const response = await api.post<Role>('/roles', data)
    return response.data
  },

  update: async (id: number, data: Partial<CreateRoleRequest>): Promise<Role> => {
    const response = await api.patch<Role>(`/roles/${id}`, data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/roles/${id}`)
  },
}

// Room API
export const roomApi = {
  getAll: async (): Promise<Room[]> => {
    const response = await api.get<Room[]>('/rooms')
    return response.data
  },

  getById: async (id: number): Promise<Room> => {
    const response = await api.get<Room>(`/rooms/${id}`)
    return response.data
  },

  create: async (data: CreateRoomRequest): Promise<Room> => {
    const response = await api.post<Room>('/rooms', data)
    return response.data
  },

  join: async (roomId: number, roleId: number): Promise<Room> => {
    const response = await api.post<Room>(`/rooms/${roomId}/join`, { role_id: roleId })
    return response.data
  },

  start: async (roomId: number): Promise<void> => {
    await api.post(`/rooms/${roomId}/start`)
  },

  stop: async (roomId: number): Promise<void> => {
    await api.post(`/rooms/${roomId}/stop`)
  },

  finish: async (roomId: number): Promise<void> => {
    await api.post(`/rooms/${roomId}/finish`)
  },

  restart: async (roomId: number): Promise<void> => {
    await api.post(`/rooms/${roomId}/restart`)
  },

  delete: async (roomId: number): Promise<void> => {
    await api.delete(`/rooms/${roomId}`)
  },

  getMessages: async (roomId: number, sessionId?: number): Promise<Message[]> => {
    const params: any = {}
    if (sessionId !== undefined) {
      params.session_id = sessionId
    }
    const response = await api.get<Message[]>(`/rooms/${roomId}/messages`, { params })
    return response.data
  },

  sendMessage: async (roomId: number, content: string): Promise<Message> => {
    const response = await api.post<Message>(`/rooms/${roomId}/messages`, { content })
    return response.data
  },
}

// Chat Session API
export const chatSessionApi = {
  getAll: async (skip = 0, limit = 50): Promise<any[]> => {
    const response = await api.get<any[]>('/chat/sessions', { params: { skip, limit } })
    return response.data
  },

  create: async (data: { agent_id: number; role_id?: number | null; title?: string }): Promise<any> => {
    const response = await api.post<any>('/chat/sessions', data)
    return response.data
  },

  delete: async (id: number): Promise<void> => {
    await api.delete(`/chat/sessions/${id}`)
  },

  getMessages: async (sessionId: number): Promise<any[]> => {
    const response = await api.get<any[]>(`/chat/sessions/${sessionId}/messages`)
    return response.data
  },
}

// WebSocket helper
export const createWebSocket = (roomId: number): WebSocket => {
  // Use environment variable or construct URL based on current location
  const baseUrl = import.meta.env.VITE_WS_BASE_URL
  const wsUrl = baseUrl 
    ? `${baseUrl}/ws/rooms/${roomId}`
    : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/rooms/${roomId}`
  return new WebSocket(wsUrl)
}
