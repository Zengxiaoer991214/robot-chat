/**
 * API service for backend communication
 */
import axios from 'axios'
import type { Agent, Room, Message, CreateAgentRequest, CreateRoomRequest } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Agent API
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

  join: async (roomId: number, agentId: number): Promise<Room> => {
    const response = await api.post<Room>(`/rooms/${roomId}/join`, { agent_id: agentId })
    return response.data
  },

  start: async (roomId: number): Promise<void> => {
    await api.post(`/rooms/${roomId}/start`)
  },

  stop: async (roomId: number): Promise<void> => {
    await api.post(`/rooms/${roomId}/stop`)
  },

  getMessages: async (roomId: number): Promise<Message[]> => {
    const response = await api.get<Message[]>(`/rooms/${roomId}/messages`)
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
