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

export interface Role {
  id: number
  name: string
  gender?: string
  age?: string
  profession?: string
  personality?: string
  aggressiveness: number
  agent_id: number
  agent?: Agent
}

export interface Room {
  id: number
  name: string
  topic: string
  max_rounds: number
  current_rounds: number
  status: 'idle' | 'running' | 'finished'
  mode: 'debate' | 'group_chat'
  session_id: number
  creator_id?: number
  created_at: string
  roles: Role[]
}

export interface Message {
  id: number
  room_id: number
  role_id?: number
  agent_id?: number // Added for compatibility with backend message format
  content: string
  role: 'user' | 'assistant' | 'system'
  sender_name?: string
  created_at: string
  sender_role?: Role
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

export interface CreateRoleRequest {
  name: string
  gender?: string
  age?: string
  profession?: string
  personality?: string
  aggressiveness?: number
  agent_id: number
}

export interface CreateRoomRequest {
  name: string
  topic: string
  max_rounds?: number
  creator_id?: number
  agent_ids?: number[]
  role_ids?: number[]
  mode?: 'debate' | 'group_chat'
}

export interface WSMessageData {
  id?: number
  agent_id?: number | null
  role_id?: number | null
  agent_name?: string
  sender_name?: string
  content?: string
  created_at?: string
  [key: string]: unknown  // Allow additional properties with unknown type
}

export interface WSMessage {
  type: string  // message, status, error
  data: WSMessageData
}
