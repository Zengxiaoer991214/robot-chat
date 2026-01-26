/**
 * Type definitions for the AI Group Chat application
 */

export interface Agent {
  id: number
  name: string
  avatar_url?: string
  provider: string
  model_name: string
  system_prompt: string
  api_key_config?: string
  temperature: number
}

export interface Room {
  id: number
  name: string
  topic: string
  max_rounds: number
  current_rounds: number
  status: 'idle' | 'running' | 'finished'
  creator_id?: number
  created_at: string
  agents: Agent[]
}

export interface Message {
  id: number
  room_id: number
  agent_id?: number
  content: string
  role: 'user' | 'assistant' | 'system'
  created_at: string
  agent?: Agent
}

export interface CreateAgentRequest {
  name: string
  avatar_url?: string
  provider: string
  model_name: string
  system_prompt: string
  api_key_config?: string
  temperature?: number
}

export interface CreateRoomRequest {
  name: string
  topic: string
  max_rounds?: number
  creator_id?: number
  agent_ids?: number[]
}

export interface WSMessage {
  type: string
  data: any
}
