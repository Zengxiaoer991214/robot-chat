<template>
  <div class="h-[calc(100vh-4rem)] flex overflow-hidden">
    <!-- Mobile Sidebar Backdrop -->
    <div v-if="showSidebarMobile" @click="showSidebarMobile = false" class="fixed inset-0 bg-gray-900/50 z-30 md:hidden backdrop-blur-sm transition-opacity"></div>

    <!-- Sidebar (History) -->
    <div 
      class="bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col transition-all duration-300 z-40 h-full"
      :class="[
        // Mobile: Absolute, slide logic
        'absolute inset-y-0 left-0 shadow-2xl md:shadow-none',
        showSidebarMobile ? 'translate-x-0' : '-translate-x-full',
        
        // Desktop: Relative (Flex Item), toggle logic
        'md:static md:inset-auto',
        showSidebar ? 'md:translate-x-0 md:w-64' : 'md:w-0 md:-translate-x-full md:overflow-hidden md:border-r-0',
        
        // Base width for mobile (always 64 when shown)
        'w-64'
      ]"
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

    <!-- Mobile Config Overlay -->
    <div v-if="showConfigMobile" class="fixed inset-0 z-50 md:hidden">
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity" @click="showConfigMobile = false"></div>
      <div class="absolute bottom-0 left-0 right-0 bg-white dark:bg-gray-900 rounded-t-3xl p-6 space-y-6 transition-transform transform translate-y-0">
        <div class="w-12 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full mx-auto mb-2"></div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Chat Configuration</h3>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Agent</label>
            <select v-model="selectedAgentId" class="w-full text-base border-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 rounded-xl focus:ring-indigo-500 focus:border-indigo-500 py-3 px-4">
              <option :value="null" disabled>Select Agent</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                {{ agent.name }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Persona</label>
            <select v-model="selectedRoleId" class="w-full text-base border-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 rounded-xl focus:ring-indigo-500 focus:border-indigo-500 py-3 px-4">
              <option :value="null">Default Persona</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
            </select>
          </div>
        </div>
        
        <button @click="showConfigMobile = false" class="w-full py-3.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl transition-colors">
          Done
        </button>
      </div>
    </div>

    <!-- Main Chat Area -->
    <main class="flex-1 flex flex-col h-full w-full bg-white dark:bg-gray-900 relative min-w-0">
      <!-- Header -->
      <div class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-800 p-3 md:p-4 flex items-center justify-between z-10 sticky top-0">
        <!-- Left: Sidebar Toggle -->
        <button @click="showSidebarMobile = !showSidebarMobile" class="md:hidden p-2 -ml-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-full transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
        </button>
        
        <!-- Center: Title / Selectors -->
        <div class="flex-1 flex justify-center md:justify-start md:ml-4">
          <!-- Mobile Title (Click to Open Config) -->
          <button @click="showConfigMobile = true" class="md:hidden flex items-center gap-1.5 px-3 py-1.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
            <span class="font-semibold text-gray-900 dark:text-white truncate max-w-[160px]">{{ selectedAgent?.name || 'Select Agent' }}</span>
            <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </button>
          
          <!-- Desktop Selectors -->
          <div class="hidden md:flex items-center gap-3">
             <select v-model="selectedAgentId" class="text-sm border-0 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 py-2 pl-3 pr-8 font-medium cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              <option :value="null" disabled>Select Agent</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                {{ agent.name }}
              </option>
            </select>
            
            <select v-model="selectedRoleId" class="text-sm border-0 bg-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 rounded-lg focus:ring-0 py-2 pl-2 pr-8 cursor-pointer transition-colors">
              <option :value="null">Default Persona</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
            </select>
          </div>
        </div>

        <!-- Right: New Chat (Mobile) / Actions -->
        <div class="flex items-center gap-2">
           <button @click="createNewChat" class="md:hidden p-2 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/30 rounded-full transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div 
        ref="messagesContainer"
        class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 scroll-smooth"
      >
        <div v-if="messages.length === 0" class="h-full flex flex-col items-center justify-center text-gray-400 p-8 text-center">
          <div class="bg-indigo-50 dark:bg-indigo-900/20 p-5 rounded-3xl mb-6 shadow-sm">
            <svg class="w-10 h-10 text-indigo-500 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
          </div>
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">Welcome Back</h3>
          <p class="text-gray-500 dark:text-gray-400 max-w-xs">Select an agent above to start a new conversation.</p>
        </div>

        <div 
          v-for="(msg, index) in messages" 
          :key="index"
          class="flex gap-3 max-w-4xl mx-auto w-full group"
          :class="msg.role === 'user' ? 'flex-row-reverse' : ''"
        >
          <!-- Avatar (Hidden for user in mobile to save space? Keep for now but make small) -->
          <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm" 
            :class="msg.role === 'user' ? 'bg-indigo-600 text-white order-1 hidden sm:flex' : 'bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700'">
            <span v-if="msg.role === 'user'" class="text-xs font-bold">You</span>
            <span v-else class="text-xs font-bold text-emerald-600 dark:text-emerald-400">AI</span>
          </div>

          <!-- Content -->
          <div class="flex flex-col gap-1 max-w-[85%] md:max-w-[75%]">
            <div 
              class="rounded-3xl px-5 py-3.5 shadow-sm text-[15px] leading-relaxed relative"
              :class="[
                msg.role === 'user' 
                  ? 'bg-indigo-600 text-white rounded-br-md' 
                  : 'bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 text-gray-800 dark:text-gray-100 rounded-bl-md'
              ]"
            >
              <!-- Image Display -->
              <div v-if="msg.image_url" class="mb-3 -mx-2 -mt-2">
                <img :src="msg.image_url" class="max-w-full rounded-2xl border border-white/10" alt="Uploaded image" />
              </div>

              <!-- Text Content -->
              <div v-if="msg.role === 'user'" class="whitespace-pre-wrap">{{ msg.content }}</div>
              <div 
                v-else
                class="prose prose-sm max-w-none prose-indigo dark:prose-invert prose-p:leading-relaxed prose-pre:bg-gray-900 prose-pre:rounded-xl prose-pre:p-4"
                v-html="renderMarkdown(msg.content)"
              ></div>
            </div>
            
            <!-- Timestamp / Status (Optional) -->
            <!-- <div class="text-[10px] text-gray-300 px-2 opacity-0 group-hover:opacity-100 transition-opacity" :class="msg.role === 'user' ? 'text-right' : ''">
              Just now
            </div> -->
          </div>
        </div>

        <div v-if="loading" class="flex gap-3 max-w-4xl mx-auto w-full">
           <div class="w-8 h-8 rounded-full bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 flex items-center justify-center shrink-0 shadow-sm">
            <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">AI</span>
          </div>
          <div class="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-3xl rounded-bl-md px-5 py-4 shadow-sm">
            <div class="flex space-x-1.5">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-3 md:p-4 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t border-gray-100 dark:border-gray-800 sticky bottom-0 z-20">
        <div class="max-w-3xl mx-auto relative">
          <!-- Image Preview -->
          <div v-if="selectedImagePreview" class="absolute bottom-full left-0 mb-3 p-2 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 flex items-start gap-2 animate-fade-in-up">
            <img :src="selectedImagePreview" class="h-24 w-24 object-cover rounded-xl" />
            <button @click="clearImage" class="p-1 bg-gray-100 dark:bg-gray-700 rounded-full text-gray-500 hover:text-red-500">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
          </div>

          <form @submit.prevent="sendMessage" class="relative flex items-end gap-2 bg-gray-100 dark:bg-gray-800/50 border border-transparent focus-within:bg-white dark:focus-within:bg-gray-800 focus-within:border-indigo-500/30 focus-within:shadow-lg focus-within:ring-4 focus-within:ring-indigo-500/10 rounded-[2rem] p-1.5 transition-all duration-300">
            <!-- Upload Button -->
            <button 
              type="button" 
              @click="triggerFileInput"
              class="p-2.5 text-gray-400 hover:text-indigo-600 hover:bg-white dark:hover:bg-gray-700 rounded-full transition-all shrink-0"
              title="Upload Image"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
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
              placeholder="Message..." 
              class="block w-full border-0 bg-transparent p-2.5 focus:ring-0 text-[15px] dark:text-gray-100 resize-none max-h-32 placeholder-gray-500 dark:placeholder-gray-400"
              style="min-height: 44px;"
            ></textarea>

            <button 
              type="submit" 
              :disabled="loading || (!inputMessage.trim() && !selectedImage)"
              class="p-2.5 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 disabled:opacity-50 disabled:hover:bg-indigo-600 transition-all shadow-md shrink-0 mb-0.5 mr-0.5 group"
            >
              <svg class="w-5 h-5 transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          </form>
          <div class="text-center text-[10px] text-gray-400 mt-2 opacity-60">
            AI can make mistakes.
          </div>
        </div>
      </div>
    </main>
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
const showConfigMobile = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const selectedImage = ref<string | null>(null)
const selectedImagePreview = ref<string | null>(null)

const selectedAgent = computed(() => agents.value.find(a => a.id === selectedAgentId.value))

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

    const token = localStorage.getItem('token')
    const headers: HeadersInit = { 
      'Content-Type': 'application/json' 
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE_URL}/chat/completion`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    })

    if (response.status === 401) {
       localStorage.removeItem('token')
       localStorage.removeItem('isAuthenticated')
       window.location.href = '/login'
       throw new Error('Unauthorized')
    }

    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)

    // Create placeholder for assistant
    messages.value.push({ role: 'assistant', content: '' })
    const assistantMsgIndex = messages.value.length - 1
    loading.value = false // Stop loading indicator once we start receiving
    
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