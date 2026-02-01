<template>
  <div class="h-[calc(100vh-7rem)] flex flex-col md:flex-row gap-4 md:gap-6 p-2 md:p-4 max-w-7xl mx-auto relative">
    
    <!-- Mobile Header (Visible only on mobile) -->
    <div class="md:hidden flex-shrink-0 flex justify-between items-center bg-white/80 backdrop-blur-md p-3 rounded-xl border border-gray-100 shadow-sm z-10">
      <div class="min-w-0 flex-1 mr-2">
        <h2 class="font-bold text-gray-900 truncate">{{ room?.name || 'Chat Room' }}</h2>
        <div class="flex items-center text-xs text-gray-500">
          <span :class="statusColorClass(room?.status || '')" class="inline-block w-2 h-2 rounded-full mr-1.5"></span>
          {{ room?.status }} • {{ room?.current_rounds }}/{{ room?.max_rounds }}
        </div>
      </div>
      <button 
        @click="mobileSidebarOpen = true"
        class="p-2 text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </button>
    </div>

    <!-- Sidebar (Agents & Info) - Desktop: Static, Mobile: Modal Overlay -->
    <div 
      class="flex-shrink-0 flex flex-col gap-4 transition-all duration-300"
      :class="[
        mobileSidebarOpen ? 'fixed inset-0 z-50 bg-gray-50/95 backdrop-blur-sm p-4 overflow-y-auto' : 'hidden md:flex w-full md:w-80'
      ]"
    >
      <!-- Mobile Close Button -->
      <div class="md:hidden flex justify-end mb-2">
        <button 
          @click="mobileSidebarOpen = false"
          class="p-2 text-gray-500 hover:text-gray-900 bg-white rounded-full shadow-sm"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Room Info Card -->
      <div class="bg-white/80 backdrop-blur-md shadow-sm border border-gray-100 rounded-2xl p-5 transition-all hover:shadow-md">
        <div v-if="loadingRoom" class="text-center py-4 text-gray-400 animate-pulse">Loading room...</div>
        <template v-else-if="room">
          <div class="mb-4">
            <h2 class="text-xl font-semibold text-gray-900 tracking-tight">{{ room.name }}</h2>
            <p class="text-sm text-gray-500 mt-1 font-medium">{{ room.topic }}</p>
          </div>

          <div class="flex items-center justify-between mb-6 bg-gray-50/50 p-3 rounded-xl border border-gray-100">
            <div class="flex items-center gap-2">
              <span class="relative flex h-2.5 w-2.5">
                <span v-if="room.status === 'running'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span :class="statusColorClass(room.status)" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
              </span>
              <span class="text-xs font-semibold uppercase tracking-wider text-gray-600">{{ room.status }}</span>
            </div>
            <span class="text-xs font-mono text-gray-400 bg-white px-2 py-1 rounded-md shadow-sm border border-gray-100">
              {{ room.current_rounds }} / {{ room.max_rounds }}
            </span>
          </div>

          <!-- Controls -->
          <div class="space-y-3">
            <button
              v-if="room.status !== 'running'"
              @click="startChat"
              :disabled="starting || room.current_rounds >= room.max_rounds"
              class="group w-full flex items-center justify-center py-2.5 px-4 rounded-xl shadow-sm text-sm font-medium text-white bg-[#007AFF] hover:bg-[#0062CC] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-95"
            >
              <span v-if="starting" class="mr-2">
                <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              {{ room.status === 'finished' ? 'Finished' : (starting ? 'Starting...' : 'Start Chat') }}
            </button>
            
            <button
              v-if="room.status === 'running'"
              @click="stopChat"
              :disabled="stopping"
              class="group w-full flex items-center justify-center py-2.5 px-4 rounded-xl shadow-sm text-sm font-medium text-white bg-[#FF3B30] hover:bg-[#D70015] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 transition-all active:scale-95"
            >
              <span v-if="stopping" class="mr-2">
                <svg class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </span>
              {{ stopping ? 'Pausing...' : 'Pause Chat' }}
            </button>

            <div class="grid grid-cols-2 gap-3 pt-2">
              <button
                @click="restartChat"
                :disabled="restarting || starting || stopping"
                class="flex items-center justify-center py-2 px-3 border border-gray-200 rounded-xl shadow-sm text-xs font-medium text-gray-700 bg-white hover:bg-gray-50 hover:border-gray-300 focus:outline-none transition-colors"
              >
                Restart
              </button>
              <button
                @click="deleteRoom"
                :disabled="deleting"
                class="flex items-center justify-center py-2 px-3 border border-gray-200 rounded-xl shadow-sm text-xs font-medium text-red-600 bg-white hover:bg-red-50 hover:border-red-200 focus:outline-none transition-colors"
              >
                Delete
              </button>
            </div>
            
            <button
              @click="router.push('/')"
              class="w-full flex items-center justify-center py-2 px-4 rounded-xl text-sm font-medium text-gray-500 hover:text-gray-900 hover:bg-gray-100 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </template>
      </div>

      <!-- Roles List -->
      <div class="bg-white/80 backdrop-blur-md shadow-sm border border-gray-100 rounded-2xl p-5 flex-1 overflow-hidden flex flex-col min-h-[200px]">
        <h3 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-1">Participants</h3>
        <div class="overflow-y-auto pr-2 -mr-2 space-y-1 custom-scrollbar">
          <div v-if="room" v-for="role in room.roles" :key="role.id" class="group flex items-center p-2 rounded-xl hover:bg-gray-50 transition-colors cursor-default">
            <div class="relative">
              <div class="h-10 w-10 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold shadow-sm ring-2 ring-white">
                {{ role.name.charAt(0) }}
              </div>
              <div class="absolute -bottom-1 -right-1 bg-white rounded-full p-0.5" v-if="activeRoleId === role.id">
                 <div class="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></div>
              </div>
            </div>
            <div class="ml-3 min-w-0">
              <p class="text-sm font-semibold text-gray-900 truncate">{{ role.name }}</p>
              <p class="text-xs text-gray-500 truncate">{{ role.profession || 'Participant' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Area -->
    <div class="flex-1 bg-white/90 backdrop-blur-sm shadow-sm border border-gray-100 rounded-2xl flex flex-col h-full overflow-hidden relative">
      <!-- Chat Header (optional context) -->
      <div class="absolute top-0 left-0 right-0 h-6 bg-gradient-to-b from-white/90 to-transparent z-10 pointer-events-none"></div>

      <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar scroll-smooth" ref="chatContainer">
        <div v-if="loadingMessages" class="flex flex-col items-center justify-center h-full text-gray-400 space-y-3">
           <svg class="animate-spin h-8 w-8 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
           </svg>
           <p class="text-sm font-medium">Loading conversation...</p>
        </div>
        
        <div v-else-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
          <div class="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
            </svg>
          </div>
          <p class="text-sm">No messages yet. Start the chat to begin!</p>
        </div>
        
        <transition-group name="message-fade">
          <div v-for="msg in messages" :key="msg.id" class="flex flex-col">
            <!-- System Message -->
            <div v-if="!msg.role_id && !msg.agent_id" class="flex justify-center my-4">
              <span class="bg-gray-100/80 backdrop-blur-sm border border-gray-200 text-gray-500 text-xs px-3 py-1.5 rounded-full shadow-sm font-medium">
                {{ msg.content }}
              </span>
            </div>
            
            <!-- Role Message -->
            <div v-else class="flex space-x-3 max-w-[85%] md:max-w-[75%]" :class="msg.role === 'user' ? 'ml-auto justify-end' : ''">
              <!-- Avatar (Left) -->
              <div class="flex-shrink-0 flex flex-col justify-end" v-if="msg.role !== 'user'">
                <div class="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-bold text-xs shadow-sm ring-2 ring-white">
                  {{ getRoleName(msg.role_id).charAt(0) }}
                </div>
              </div>

              <!-- Message Content -->
              <div class="flex flex-col" :class="msg.role === 'user' ? 'items-end' : 'items-start'">
                <div class="flex items-baseline space-x-2 mb-1" :class="msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''">
                  <span class="text-xs font-semibold text-gray-900">{{ msg.role === 'user' ? 'You' : getRoleName(msg.role_id) }}</span>
                  <span class="text-[10px] text-gray-400">{{ formatDate(msg.created_at) }}</span>
                </div>
                
                <div 
                  class="px-4 py-2.5 shadow-sm text-sm leading-relaxed markdown-body break-words"
                  :class="[
                    msg.role === 'user' 
                      ? 'bg-[#007AFF] text-white rounded-2xl rounded-tr-sm' 
                      : 'bg-[#F2F2F7] text-gray-900 rounded-2xl rounded-tl-sm'
                  ]"
                  v-html="renderMarkdown(msg.content)"
                ></div>
              </div>

              <!-- Avatar (Right - User) -->
              <div class="flex-shrink-0 flex flex-col justify-end" v-if="msg.role === 'user'">
                <div class="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold text-xs shadow-sm ring-2 ring-white">
                  U
                </div>
              </div>
            </div>
          </div>
        </transition-group>
      </div>
      
      <!-- Connection Status Footer -->
      <div class="absolute bottom-4 right-6 z-10 transition-opacity duration-500" :class="connected ? 'opacity-0 hover:opacity-100' : 'opacity-100'">
        <div class="flex items-center space-x-1.5 bg-white/90 backdrop-blur px-2 py-1 rounded-full shadow-sm border border-gray-100">
          <span class="relative flex h-2 w-2">
            <span :class="connected ? 'bg-green-500' : 'bg-red-500'" class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"></span>
            <span :class="connected ? 'bg-green-500' : 'bg-red-500'" class="relative inline-flex rounded-full h-2 w-2"></span>
          </span>
          <span class="text-[10px] font-medium text-gray-500">{{ connected ? 'Live' : 'Offline' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
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
const mobileSidebarOpen = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
let socket: WebSocket | null = null

// Active role highlight (simulated for now)
const activeRoleId = computed(() => {
  if (messages.value.length > 0) {
    const lastMsg = messages.value[messages.value.length - 1]
    return lastMsg.role_id
  }
  return null
})

// Helper to get role name
const getRoleName = (roleId?: number | null) => {
  if (!roleId) return 'System'
  const role = room.value?.roles.find((r: Role) => r.id === roleId)
  return role ? role.name : 'Unknown Role'
}

// Status color helper
const statusColorClass = (status: string) => {
  switch (status) {
    case 'running': return 'bg-green-500'
    case 'finished': return 'bg-gray-500'
    default: return 'bg-yellow-500'
  }
}

// Format date
const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// Render markdown
const renderMarkdown = (content: string) => {
  return marked(content)
}

// Scroll to bottom
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTo({
      top: chatContainer.value.scrollHeight,
      behavior: 'smooth'
    })
  }
}

// Load initial data
const loadData = async () => {
  try {
    const roomData = await roomApi.getById(roomId)
    room.value = roomData
    loadingRoom.value = false
    
    const msgsData = await roomApi.getMessages(roomId, roomData.session_id)
    messages.value = msgsData
    loadingMessages.value = false
    scrollToBottom()
  } catch (error) {
    console.error('Failed to load room data:', error)
    // Removed alert for cleaner UX
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
        const msg: Message = {
          id: msgData.id || Date.now(),
          room_id: roomId,
          role_id: msgData.role_id || undefined,
          content: msgData.content || '',
          role: (msgData.role as 'user' | 'assistant' | 'system') || (msgData.role_id ? 'assistant' : 'system'),
          sender_name: msgData.sender_name || msgData.agent_name,
          created_at: msgData.created_at || new Date().toISOString()
        }

        if (!messages.value.find((m: Message) => m.id === msg.id)) {
          messages.value.push(msg)
          scrollToBottom()
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
  } finally {
    starting.value = false
  }
}

const stopChat = async () => {
  if (!room.value) return
  try {
    stopping.value = true
    await roomApi.stop(roomId)
    room.value.status = 'idle'
  } catch (error) {
    console.error('Failed to stop chat:', error)
  } finally {
    stopping.value = false
  }
}

const restartChat = async () => {
  if (!room.value) return
  if (!confirm('Start a new conversation session?')) return
  
  try {
    restarting.value = true
    await roomApi.restart(roomId)
    await loadData()
  } catch (error) {
    console.error('Failed to restart chat:', error)
  } finally {
    restarting.value = false
  }
}

const deleteRoom = async () => {
  if (!confirm('Delete this room?')) return
  
  try {
    deleting.value = true
    await roomApi.delete(roomId)
    router.push('/')
  } catch (error) {
    console.error('Failed to delete room:', error)
  } finally {
    deleting.value = false
  }
}

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

<style scoped>
/* Markdown Styles override for chat */
:deep(.markdown-body) {
  background-color: transparent !important;
  font-family: inherit !important;
  font-size: 0.95rem;
}
:deep(.markdown-body p) {
  margin-bottom: 0.5rem;
}
:deep(.markdown-body p:last-child) {
  margin-bottom: 0;
}
:deep(.markdown-body pre) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.75rem;
  border-radius: 0.5rem;
  margin: 0.5rem 0;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.3);
  border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(156, 163, 175, 0.5);
}

/* Message Transitions */
.message-fade-enter-active,
.message-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}
.message-fade-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}
.message-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
