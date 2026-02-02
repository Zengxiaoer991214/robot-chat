<template>
  <div class="px-4 sm:px-0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white">Agent Management</h2>
      <button
        @click="openCreateModal"
        class="inline-flex items-center px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-full shadow-lg hover:shadow-indigo-500/30 transition-all duration-200 ease-in-out transform hover:-translate-y-0.5"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create New Agent
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-gray-500 dark:text-gray-400">Loading agents...</p>
    </div>
    
    <div v-else-if="agents.length === 0" class="text-center py-20 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-3xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white">No agents yet</h3>
      <p class="mt-1 text-gray-500 dark:text-gray-400">Create your first AI agent to get started.</p>
    </div>
    
    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="group relative bg-white/70 dark:bg-gray-800 backdrop-blur-md border border-white/20 dark:border-gray-700 rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
      >
        <div class="flex items-center mb-4">
          <div class="h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-md mr-4">
            {{ agent.name.charAt(0) }}
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{{ agent.name }}</h3>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 dark:bg-indigo-900/30 text-indigo-800 dark:text-indigo-300">
              {{ agent.provider }}
            </span>
          </div>
        </div>
        
        <div class="mb-4">
          <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">System Prompt</h4>
          <div class="text-sm text-gray-600 dark:text-gray-300 bg-gray-50/80 dark:bg-gray-700/50 p-3 rounded-xl border border-gray-100 dark:border-gray-600 line-clamp-3">
            {{ agent.system_prompt }}
          </div>
        </div>
        
        <div class="flex justify-between items-center pt-4 border-t border-gray-100/50 dark:border-gray-700/50">
          <span class="text-xs text-gray-400 font-mono">{{ agent.model_name }}</span>
          <div class="flex space-x-2">
            <button
              @click="editAgent(agent)"
              class="p-2 text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 rounded-xl transition-colors"
              title="Edit"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 00-2 2h11a2 2 0 00-2-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              @click="deleteAgent(agent.id)"
              class="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors"
              title="Delete"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Agent Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center z-50 transition-all">
      <div class="bg-white dark:bg-gray-800 rounded-3xl px-4 pt-5 pb-4 text-left overflow-hidden shadow-2xl transform transition-all sm:max-w-lg sm:w-full sm:p-8 border border-gray-100 dark:border-gray-700">
        <div>
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">{{ isEditing ? 'Edit Agent' : 'Create New Agent' }}</h3>
          <form @submit.prevent="submitAgent">
            <div class="space-y-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
                <input v-model="form.name" type="text" required class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
              </div>
              
              <div class="grid grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Provider</label>
                  <select v-model="form.provider" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
                    <option value="openai">OpenAI</option>
                    <option value="deepseek">DeepSeek</option>
                    <option value="google">Google (Gemini)</option>
                    <option value="ollama">Ollama</option>
                    <option value="chatanywhere">ChatAnywhere (Free)</option>
                    <option value="dashscope">Aliyun DashScope (BaiLian)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Model Name</label>
                  <select v-if="form.provider === 'dashscope'" v-model="form.model_name" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
                    <option value="qwen-turbo">Qwen-Turbo</option>
                    <option value="qwen-plus">Qwen-Plus</option>
                    <option value="qwen-max">Qwen-Max</option>
                    <option value="qwen-long">Qwen-Long</option>
                    <option value="qwen-vl-plus">Qwen-VL-Plus (Vision)</option>
                    <option value="qwen-vl-max">Qwen-VL-Max (Vision)</option>
                  </select>
                  <input v-else v-model="form.model_name" type="text" required class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">API Key (Optional)</label>
                <input v-model="form.api_key_config" type="password" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700" placeholder="Leave empty to use system default">
                <p class="mt-1.5 text-xs text-gray-500 dark:text-gray-400">If provided, this key will be used instead of the system default.</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">System Prompt</label>
                <textarea v-model="form.system_prompt" rows="3" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700" placeholder="Describe the agent's personality..."></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Temperature ({{ form.temperature }})</label>
                <input v-model.number="form.temperature" type="range" min="0" max="2" step="0.1" class="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-indigo-600">
              </div>
            </div>
            
            <div class="mt-8 flex justify-end space-x-3">
              <button type="button" @click="showCreateModal = false" class="inline-flex justify-center rounded-xl border border-gray-300 dark:border-gray-600 shadow-sm px-5 py-2.5 bg-white dark:bg-gray-700 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none transition-colors">
                Cancel
              </button>
              <button type="submit" class="inline-flex justify-center rounded-xl border border-transparent shadow-sm px-5 py-2.5 bg-indigo-600 text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none transition-colors">
                {{ isEditing ? 'Update' : 'Create' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import { agentApi } from '@/services/api'
import type { Agent, CreateAgentRequest } from '@/types'

const agents = ref<Agent[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const defaultSystemPrompt = ""

const form = reactive<CreateAgentRequest>({
  name: '',
  provider: 'openai',
  model_name: 'gpt-3.5-turbo',
  system_prompt: defaultSystemPrompt,
  temperature: 0.7,
  api_key_config: ''
})

// Update default model name when provider changes
watch(() => form.provider, (newProvider: string) => {
  if (isEditing.value) return // Don't change model name when editing existing agent
  
  switch (newProvider) {
    case 'openai':
      form.model_name = 'gpt-3.5-turbo'
      break
    case 'deepseek':
      form.model_name = 'deepseek-chat'
      break
    case 'google':
      form.model_name = 'gemini-2.0-flash-exp'
      break
    case 'ollama':
      form.model_name = 'llama3'
      break
    case 'chatanywhere':
      form.model_name = 'gpt-3.5-turbo'
      break
    case 'dashscope':
      form.model_name = 'qwen-plus'
      break
  }
})

const loadAgents = async () => {
  try {
    loading.value = true
    agents.value = await agentApi.getAll()
  } catch (error) {
    console.error('Failed to load agents:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.name = ''
  form.provider = 'openai'
  form.model_name = 'gpt-3.5-turbo'
  form.system_prompt = defaultSystemPrompt
  form.temperature = 0.7
  form.api_key_config = ''
  showCreateModal.value = true
}

const editAgent = (agent: Agent) => {
  isEditing.value = true
  editingId.value = agent.id
  form.name = agent.name
  form.provider = agent.provider
  form.model_name = agent.model_name
  form.system_prompt = agent.system_prompt
  form.temperature = agent.temperature
  form.api_key_config = '' // Don't show existing key
  showCreateModal.value = true
}

const submitAgent = async () => {
  try {
    if (isEditing.value && editingId.value) {
      await agentApi.update(editingId.value, form)
    } else {
      await agentApi.create(form)
    }
    showCreateModal.value = false
    await loadAgents()
  } catch (error) {
    console.error('Failed to save agent:', error)
    alert('Failed to save agent')
  }
}

const deleteAgent = async (id: number) => {
  if (!confirm('Are you sure you want to delete this agent?')) return
  
  try {
    await agentApi.delete(id)
    await loadAgents()
  } catch (error) {
    console.error('Failed to delete agent:', error)
    alert('Failed to delete agent')
  }
}

onMounted(() => {
  loadAgents()
})
</script>
