<template>
  <div class="px-4 sm:px-0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-900">Agent Management</h2>
      <button
        @click="openCreateModal"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Create New Agent
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Loading agents...</p>
    </div>
    
    <div v-else-if="agents.length === 0" class="text-center py-12">
      <p class="text-gray-500">No agents found. Create one to get started!</p>
    </div>
    
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="bg-white overflow-hidden shadow rounded-lg border border-gray-200"
      >
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center mb-4">
            <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 font-bold text-xl mr-3">
              {{ agent.name.charAt(0) }}
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ agent.name }}</h3>
              <p class="text-sm text-gray-500">{{ agent.provider }} / {{ agent.model_name }}</p>
            </div>
          </div>
          
          <div class="mb-4">
            <h4 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">System Prompt</h4>
            <p class="text-sm text-gray-700 line-clamp-3 bg-gray-50 p-2 rounded">{{ agent.system_prompt }}</p>
          </div>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="editAgent(agent)"
              class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
            >
              Edit
            </button>
            <button
              @click="deleteAgent(agent.id)"
              class="text-red-600 hover:text-red-900 text-sm font-medium"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Agent Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:max-w-lg sm:w-full sm:p-6">
        <div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">{{ isEditing ? 'Edit Agent' : 'Create New Agent' }}</h3>
          <form @submit.prevent="submitAgent">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Name</label>
                <input v-model="form.name" type="text" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Provider</label>
                  <select v-model="form.provider" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
                    <option value="openai">OpenAI</option>
                    <option value="deepseek">DeepSeek</option>
                    <option value="google">Google (Gemini)</option>
                    <option value="ollama">Ollama</option>
                    <option value="chatanywhere">ChatAnywhere (Free)</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Model Name</label>
                  <input v-model="form.model_name" type="text" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">API Key (Optional)</label>
                <input v-model="form.api_key_config" type="password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2" placeholder="Leave empty to use system default">
                <p class="mt-1 text-xs text-gray-500">If provided, this key will be used instead of the system default.</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">System Prompt</label>
                <textarea v-model="form.system_prompt" rows="3" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2" placeholder="Describe the agent's personality..."></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Temperature ({{ form.temperature }})</label>
                <input v-model.number="form.temperature" type="range" min="0" max="2" step="0.1" class="mt-1 block w-full">
              </div>
            </div>
            
            <div class="mt-5 sm:mt-6 flex justify-end space-x-3">
              <button type="button" @click="showCreateModal = false" class="inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:text-sm">
                Cancel
              </button>
              <button type="submit" class="inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none sm:text-sm">
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

const defaultSystemPrompt = "You are a participant in a group chat. Your responses should be concise, casual, and conversational, mimicking how humans type in a group chat (e.g., lowercase, slang, emojis if appropriate). Keep messages short. Only provide longer, detailed explanations if the topic strictly requires it or if explicitly asked. Engage naturally with others."

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
