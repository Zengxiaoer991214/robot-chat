<template>
  <div class="h-[calc(100vh-4rem)] flex overflow-hidden">
    <!-- Sidebar (History) -->
    <div 
      class="w-64 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 transform"
      :class="[showSidebar ? 'translate-x-0' : '-translate-x-full absolute z-20 h-full md:relative md:translate-x-0 md:w-64', showSidebarMobile ? 'translate-x-0 absolute z-20 h-full shadow-xl' : '']"
    >
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h2 class="font-semibold text-gray-700 dark:text-gray-200">Chat History</h2>
        <button @click="createNewChat" class="p-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded-lg text-gray-600 dark:text-gray-400" title="New Chat">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
        </button>
      </div>
      
      <div class="flex-1 overflow-y-auto p-2 space-y-1">
        <div 
          v-for="session in sessions" 
          :key="session.id"
          @click="loadSession(session)"
          class="p-3 rounded-xl cursor-pointer transition-colors group relative"
          :class="currentSessionId === session.id ? 'bg-white dark:bg-gray-800 shadow-sm border border-indigo-100 dark:border-indigo-900' : 'hover:bg-gray-100 dark:hover:bg-gray-800'"
        >
          <div class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate pr-6">{{ session.title || 'New Chat' }}</div>
          <div class="text-xs text-gray-400 mt-1">{{ formatDate(session.updated_at) }}</div>
          
          <button 
            @click.stop="deleteSession(session.id)" 
            class="absolute right-2 top-3 opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 transition-opacity"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
          </button>
        </div>
        
        <div v-if="sessions.length === 0" class="text-center text-gray-400 text-sm py-8">
          No history yet
        </div>
      </div>
    </div>

    <!-- Mobile Overlay -->
    <div v-if="showSidebarMobile" @click="showSidebarMobile = false" class="fixed inset-0 bg-black/20 z-10 md:hidden"></div>

    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col h-full w-full bg-white dark:bg-gray-900 relative">
      <!-- Header -->
      <div class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800 p-4 flex items-center justify-between z-10">
        <div class="flex items-center gap-2">
          <button @click="showSidebarMobile = !showSidebarMobile" class="md:hidden p-2 -ml-2 text-gray-500 dark:text-gray-400">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
          </button>
          
          <div class="flex flex-col md:flex-row gap-2 md:items-center">
            <!-- Agent Selector -->
            <select v-model="selectedAgentId" class="text-sm border-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 py-1.5 pl-2 pr-8">
              <option :value="null" disabled>Select Agent</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                {{ agent.name }} ({{ agent.model_name }})
              </option>
            </select>
            
            <!-- Role Selector -->
            <select v-model="selectedRoleId" class="text-sm border-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 py-1.5 pl-2 pr-8">
              <option :value="null">Default Persona</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- Messages -->
      <div 
        ref="messagesContainer"
        class="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth"
      >
        <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400">
          <div class="bg-indigo-50 dark:bg-indigo-900/20 p-4 rounded-full mb-4">
            <svg class="w-8 h-8 text-indigo-500 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
          </div>
          <p class="text-lg font-medium text-gray-900 dark:text-gray-100">How can I help you today?</p>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Select an agent and start chatting.</p>
        </div>

        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          class="flex gap-4 max-w-3xl mx-auto w-full"
          :class="msg.role === 'user' ? 'flex-row-reverse' : ''"
        >
          <!-- Avatar -->
          <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" 
            :class="msg.role === 'user' ? 'bg-indigo-100 dark:bg-indigo-900' : 'bg-emerald-100 dark:bg-emerald-900'">
            <span v-if="msg.role === 'user'" class="text-xs font-bold text-indigo-600 dark:text-indigo-300">You</span>
            <span v-else class="text-xs font-bold text-emerald-600 dark:text-emerald-300">AI</span>
          </div>

          <!-- Content -->
          <div class="flex flex-col gap-1 max-w-[85%]">
            <div class="text-xs text-gray-400 px-1" :class="msg.role === 'user' ? 'text-right' : ''">
              {{ msg.role === 'user' ? 'You' : (selectedRole?.name || 'Assistant') }}
            </div>
            
            <div 
              class="rounded-2xl px-5 py-3 shadow-sm"
              :class="[
                msg.role === 'user' 
                  ? 'bg-indigo-600 text-white rounded-tr-none' 
                  : 'bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-100 rounded-tl-none'
              ]"
            >
              <!-- Image Display -->
              <div v-if="msg.image_url" class="mb-3">
                <img :src="msg.image_url" class="max-w-full rounded-lg border border-white/20 dark:border-gray-600" alt="Uploaded image" />
              </div>

              <!-- Text Content -->
              <div v-if="msg.role === 'user'" class="whitespace-pre-wrap text-sm leading-relaxed">{{ msg.content }}</div>
              <div 
                v-else
                class="prose prose-sm max-w-none prose-indigo dark:prose-invert prose-p:leading-relaxed prose-pre:bg-gray-800 prose-pre:text-gray-100"
                v-html="renderMarkdown(msg.content)"
              ></div>
            </div>
          </div>
        </div>

        <div v-if="loading" class="flex gap-4 max-w-3xl mx-auto w-full">
           <div class="w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center shrink-0">
            <span class="text-xs font-bold text-emerald-600 dark:text-emerald-300">AI</span>
          </div>
          <div class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl rounded-tl-none px-5 py-4 shadow-sm">
            <div class="flex space-x-1.5">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
        <div class="max-w-3xl mx-auto relative">
          <!-- Image Preview -->
          <div v-if="selectedImagePreview" class="absolute bottom-full left-0 mb-2 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-100 dark:border-gray-700 flex items-start gap-2">
            <img :src="selectedImagePreview" class="h-20 w-20 object-cover rounded-md" />
            <button @click="clearImage" class="text-gray-400 hover:text-red-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>

          <form @submit.prevent="sendMessage" class="relative flex items-end gap-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-2 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:border-transparent transition-all">
            <!-- Upload Button -->
            <button 
              type="button" 
              @click="triggerFileInput"
              class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-xl transition-colors shrink-0"
              title="Upload Image"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
            </button>
            <input 
              ref="fileInput"
              type="file" 
              accept="image/*" 
              class="hidden"
              @change="handleFileUpload"
            >

            <textarea 
              v-model="inputMessage" 
              rows="1"
              @keydown.enter.prevent="handleEnter"
              placeholder="Type your message..." 
              class="block w-full border-0 bg-transparent p-2 focus:ring-0 text-sm dark:text-gray-100 resize-none max-h-32 placeholder-gray-500 dark:placeholder-gray-400"
              style="min-height: 40px;"
            ></textarea>

            <button 
              type="submit" 
              :disabled="loading || (!inputMessage.trim() && !selectedImage)"
              class="p-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-colors shadow-sm shrink-0"
            >
              <svg class="w-5 h-5 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
          <div class="text-center text-xs text-gray-400 mt-2">
            AI can make mistakes. Consider checking important information.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { agentApi, roleApi, chatSessionApi } from '@/services/api'
import { getApiBaseUrl } from '@/services/config'
import type { Agent, Role } from '@/types'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const API_BASE_URL = getApiBaseUrl()

// State
const sessions = ref<any[]>([])
const currentSessionId = ref<number | null>(null)
const agents = ref<Agent[]>([])
const roles = ref<Role[]>([])
const selectedAgentId = ref<number | null>(null)
const selectedRoleId = ref<number | null>(null)
const messages = ref<any[]>([])
const inputMessage = ref('')
const loading = ref(false)
const showSidebar = ref(true)
const showSidebarMobile = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedImage = ref<string | null>(null)
const selectedImagePreview = ref<string | null>(null)

const selectedRole = computed(() => roles.value.find(r => r.id === selectedRoleId.value))

// Markdown
const renderMarkdown = (content: string) => {
  if (!content) return ''
  const rawHtml = marked.parse(content, { breaks: true, gfm: true }) as string
  return DOMPurify.sanitize(rawHtml)
}

// Format Date
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }).format(date)
}

// Scroll
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Lifecycle
onMounted(async () => {
  await Promise.all([loadAgentsRoles(), loadSessions()])
  if (sessions.value.length > 0) {
    loadSession(sessions.value[0])
  }
})

// Logic
const loadAgentsRoles = async () => {
  try {
    const [agentsData, rolesData] = await Promise.all([
      agentApi.getAll(),
      roleApi.getAll()
    ])
    agents.value = agentsData
    roles.value = rolesData
    if (agents.value.length > 0) selectedAgentId.value = agents.value[0].id
  } catch (e) {
    console.error(e)
  }
}

const loadSessions = async () => {
  try {
    sessions.value = await chatSessionApi.getAll()
  } catch (e) {
    console.error(e)
  }
}

const loadSession = async (session: any) => {
  currentSessionId.value = session.id
  selectedAgentId.value = session.agent_id
  selectedRoleId.value = session.role_id
  showSidebarMobile.value = false
  
  try {
    messages.value = await chatSessionApi.getMessages(session.id)
    scrollToBottom()
  } catch (e) {
    console.error(e)
  }
}

const createNewChat = () => {
  currentSessionId.value = null
  messages.value = []
  inputMessage.value = ''
  selectedImage.value = null
  selectedImagePreview.value = null
  showSidebarMobile.value = false
}

const deleteSession = async (id: number) => {
  if (!confirm('Delete this chat?')) return
  try {
    await chatSessionApi.delete(id)
    sessions.value = sessions.value.filter(s => s.id !== id)
    if (currentSessionId.value === id) {
      createNewChat()
    }
  } catch (e) {
    console.error(e)
  }
}

// Image Upload
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    const reader = new FileReader()
    
    reader.onload = (e) => {
      const result = e.target?.result as string
      selectedImage.value = result // Base64 full string
      selectedImagePreview.value = result
    }
    
    reader.readAsDataURL(file)
  }
}

const clearImage = () => {
  selectedImage.value = null
  selectedImagePreview.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const handleEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    sendMessage()
  }
}

// Send Message
const sendMessage = async () => {
  if ((!inputMessage.value.trim() && !selectedImage.value) || !selectedAgentId.value || loading.value) return

  const userMsg = inputMessage.value.trim()
  const userImage = selectedImage.value
  
  // Optimistic UI update
  messages.value.push({ 
    role: 'user', 
    content: userMsg,
    image_url: userImage
  })
  
  inputMessage.value = ''
  clearImage()
  loading.value = true
  scrollToBottom()

  try {
    const payload = {
      agent_id: selectedAgentId.value,
      role_id: selectedRoleId.value,
      session_id: currentSessionId.value,
      message: userMsg || (userImage ? "Sent an image" : ""), // Fallback text
      image: userImage,
      history: [], // We rely on DB now
      stream: true
    }

    const response = await fetch(`${API_BASE_URL}/chat/completion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)

    // Create placeholder for assistant
    messages.value.push({ role: 'assistant', content: '' })
    const assistantMsgIndex = messages.value.length - 1
    
    if (!response.body) throw new Error('Response body is null')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let done = false

    while (!done) {
      const { value, done: doneReading } = await reader.read()
      done = doneReading
      if (value) {
        const chunk = decoder.decode(value, { stream: true })
        messages.value[assistantMsgIndex].content += chunk
        scrollToBottom()
      }
    }
    
    // Refresh sessions list to update timestamp/title or add new session
    await loadSessions()
    
    // If this was a new session, update currentSessionId to the latest one
    if (!currentSessionId.value && sessions.value.length > 0) {
      currentSessionId.value = sessions.value[0].id
    }

  } catch (error) {
    console.error('Chat failed:', error)
    messages.value.push({ role: 'system', content: 'Error: Failed to get response.' })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}
</script>

<style scoped>
/* Custom scrollbar for webkit */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>