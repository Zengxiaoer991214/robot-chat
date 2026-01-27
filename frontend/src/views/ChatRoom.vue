<template>
  <div class="h-[calc(100vh-4rem)] flex flex-col md:flex-row gap-4">
    <!-- Sidebar (Agents & Info) -->
    <div class="w-full md:w-1/4 bg-white shadow rounded-lg p-4 flex flex-col h-auto md:h-full overflow-hidden">
      <div v-if="loadingRoom" class="text-center py-4">Loading room...</div>
      <template v-else-if="room">
        <div class="mb-4">
          <h2 class="text-xl font-bold text-gray-900">{{ room.name }}</h2>
          <p class="text-sm text-gray-500 mt-1">{{ room.topic }}</p>
        </div>

        <div class="flex items-center justify-between mb-4 bg-gray-50 p-2 rounded">
          <span :class="statusClass(room.status)" class="px-2 py-1 text-xs rounded-full uppercase font-bold">
            {{ room.status }}
          </span>
          <span class="text-sm text-gray-500">
            {{ room.current_rounds }} / {{ room.max_rounds }} rounds
          </span>
        </div>

        <div class="flex-1 overflow-y-auto mb-4">
          <h3 class="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Roles</h3>
          <ul class="space-y-3">
            <li v-for="role in room.roles" :key="role.id" class="flex items-center">
              <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold mr-2 text-xs">
                {{ role.name.charAt(0) }}
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">{{ role.name }}</p>
                <p class="text-xs text-gray-500">{{ role.profession || 'Participant' }}</p>
              </div>
            </li>
          </ul>
        </div>

        <div class="mt-auto space-y-2">
          <button
            v-if="room.status !== 'running'"
            @click="startChat"
            :disabled="starting || room.current_rounds >= room.max_rounds"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none disabled:opacity-50"
          >
            {{ room.status === 'finished' ? 'Finished' : (starting ? 'Starting...' : 'Start Chat') }}
          </button>
          
          <button
            v-if="room.status === 'running'"
            @click="stopChat"
            :disabled="stopping"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none disabled:opacity-50"
          >
            {{ stopping ? 'Pausing...' : 'Pause Chat' }}
          </button>

          <button
            @click="restartChat"
            :disabled="restarting || starting || stopping"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-yellow-600 hover:bg-yellow-700 focus:outline-none disabled:opacity-50"
          >
            {{ restarting ? 'Restarting...' : 'Restart Session' }}
          </button>

          <button
            @click="deleteRoom"
            :disabled="deleting"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-gray-600 hover:bg-gray-700 focus:outline-none disabled:opacity-50"
          >
            {{ deleting ? 'Deleting...' : 'Delete Room' }}
          </button>
          
          <button
            @click="router.push('/')"
            class="w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
          >
            Back to Dashboard
          </button>
        </div>
      </template>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 bg-white shadow rounded-lg flex flex-col h-full overflow-hidden">
      <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="chatContainer">
        <div v-if="loadingMessages" class="text-center py-4 text-gray-500">Loading messages...</div>
        <div v-else-if="messages.length === 0" class="text-center py-12 text-gray-500">
          <p>No messages yet. Start the chat to begin!</p>
        </div>
        
        <div v-for="msg in messages" :key="msg.id" class="flex flex-col">
          <!-- System Message -->
          <div v-if="!msg.role_id" class="flex justify-center my-2">
            <span class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">
              {{ msg.content }}
            </span>
          </div>
          
          <!-- Role Message -->
          <div v-else class="flex space-x-3" :class="msg.role === 'user' ? 'justify-end' : ''">
            <div class="flex-shrink-0" v-if="msg.role !== 'user'">
              <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-lg">
                {{ getRoleName(msg.role_id).charAt(0) }}
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-2" :class="msg.role === 'user' ? 'justify-end' : ''">
                <p class="text-sm font-medium text-gray-900">{{ getRoleName(msg.role_id) }}</p>
                <span class="text-xs text-gray-500">{{ formatDate(msg.created_at) }}</span>
              </div>
              <div class="mt-1 bg-gray-50 p-3 rounded-lg text-sm text-gray-900 markdown-body" v-html="renderMarkdown(msg.content)"></div>
            </div>
            <div class="flex-shrink-0" v-if="msg.role === 'user'">
              <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center text-gray-600 font-bold text-lg">
                U
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Connection Status -->
      <div class="bg-gray-50 px-4 py-2 text-xs text-right border-t border-gray-200">
        <span :class="connected ? 'text-green-600' : 'text-red-600'">
          ● {{ connected ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { roomApi, createWebSocket } from '@/services/api'
import type { Room, Message, WSMessage, Role } from '@/types'
import { marked } from 'marked'

const route = useRoute()
const router = useRouter()
const roomId = parseInt(route.params.id as string)

const room = ref<Room | null>(null)
const messages = ref<Message[]>([])
const loadingRoom = ref(true)
const loadingMessages = ref(true)
const starting = ref(false)
const stopping = ref(false)
const restarting = ref(false)
const deleting = ref(false)
const connected = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
let socket: WebSocket | null = null

// Helper to get role name
const getRoleName = (roleId?: number | null) => {
  if (!roleId) return 'System'
  const role = room.value?.roles.find((r: Role) => r.id === roleId)
  return role ? role.name : 'Unknown Role'
}

// Format date
const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString()
}

// Render markdown
const renderMarkdown = (content: string) => {
  return marked(content)
}

// Status class
const statusClass = (status: string) => {
  switch (status) {
    case 'running': return 'bg-green-100 text-green-800'
    case 'finished': return 'bg-gray-100 text-gray-800'
    default: return 'bg-yellow-100 text-yellow-800'
  }
}

// Scroll to bottom
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// Load initial data
const loadData = async () => {
  try {
    // Load room first to get session_id
    const roomData = await roomApi.getById(roomId)
    room.value = roomData
    loadingRoom.value = false
    
    // Then load messages for current session
    const msgsData = await roomApi.getMessages(roomId, roomData.session_id)
    messages.value = msgsData
    loadingMessages.value = false
    scrollToBottom()
  } catch (error) {
    console.error('Failed to load room data:', error)
    alert('Failed to load room')
    router.push('/')
  }
}

// WebSocket connection
const connectWebSocket = () => {
  socket = createWebSocket(roomId)
  
  socket.onopen = () => {
    connected.value = true
    console.log('WebSocket connected')
  }
  
  socket.onmessage = (event) => {
    try {
      const data: WSMessage = JSON.parse(event.data)
      
      if (data.type === 'message') {
        const msgData = data.data
        // Add to messages if not already there
        
        // Construct a valid Message object with required fields
        const msg: Message = {
          id: msgData.id || Date.now(),
          room_id: roomId,
          role_id: msgData.role_id || undefined,
          content: msgData.content || '',
          role: (msgData.role as 'user' | 'assistant' | 'system') || (msgData.role_id ? 'assistant' : 'system'),
          sender_name: msgData.sender_name || msgData.agent_name,
          created_at: msgData.created_at || new Date().toISOString()
        }

        // Check if message ID exists to prevent dupes if we reload
        if (!messages.value.find((m: Message) => m.id === msg.id)) {
          messages.value.push(msg)
          scrollToBottom()
          
          // If system message and it's round increment related, update rounds?
          // Actually better to just refresh room status occasionally or infer from messages?
          // For now, let's just increment local round counter if a role spoke
          if (msg.role_id && room.value) {
            room.value.current_rounds++
          }
        }
      }
    } catch (e) {
      console.error('Error parsing WS message:', e)
    }
  }
  
  socket.onclose = () => {
    connected.value = false
    console.log('WebSocket disconnected')
    // Reconnect logic could go here
  }
  
  socket.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}

// Actions
const startChat = async () => {
  if (!room.value) return
  try {
    starting.value = true
    await roomApi.start(roomId)
    room.value.status = 'running'
  } catch (error) {
    console.error('Failed to start chat:', error)
    alert('Failed to start chat')
  } finally {
    starting.value = false
  }
}

const stopChat = async () => {
  if (!room.value) return
  try {
    stopping.value = true
    await roomApi.stop(roomId)
    room.value.status = 'idle' // or whatever backend sets
  } catch (error) {
    console.error('Failed to stop chat:', error)
    alert('Failed to stop chat')
  } finally {
    stopping.value = false
  }
}

const restartChat = async () => {
  if (!room.value) return
  if (!confirm('Start a new conversation session? Existing messages will be saved in history.')) return
  
  try {
    restarting.value = true
    await roomApi.restart(roomId)
    // Reload everything
    await loadData()
  } catch (error) {
    console.error('Failed to restart chat:', error)
    alert('Failed to restart chat')
  } finally {
    restarting.value = false
  }
}

const deleteRoom = async () => {
  if (!confirm('Are you sure you want to delete this room? This cannot be undone.')) return
  
  try {
    deleting.value = true
    await roomApi.delete(roomId)
    router.push('/')
  } catch (error) {
    console.error('Failed to delete room:', error)
    alert('Failed to delete room')
  } finally {
    deleting.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await loadData()
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<style>
.markdown-body p {
  margin-bottom: 0.5rem;
}
.markdown-body pre {
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 0.25rem;
  overflow-x: auto;
}
</style>
