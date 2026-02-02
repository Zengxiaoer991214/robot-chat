<template>
  <div class="px-4 sm:px-0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white">Role Management</h2>
      <button
        @click="openCreateModal"
        class="inline-flex items-center px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-full shadow-lg hover:shadow-indigo-500/30 transition-all duration-200 ease-in-out transform hover:-translate-y-0.5"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create New Role
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-2 text-gray-500 dark:text-gray-400">Loading roles...</p>
    </div>
    
    <div v-else-if="roles.length === 0" class="text-center py-20 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-3xl border border-gray-100 dark:border-gray-700 shadow-sm">
      <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900 dark:text-white">No roles yet</h3>
      <p class="mt-1 text-gray-500 dark:text-gray-400">Create roles (personas) to participate in chats.</p>
    </div>
    
    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div
        v-for="role in roles"
        :key="role.id"
        class="group relative bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm hover:shadow-lg transition-all duration-300 border border-gray-100 dark:border-gray-700 flex flex-col h-full"
      >
        <div class="flex items-start mb-4">
          <div class="h-10 w-10 rounded-full bg-gray-100 dark:bg-gray-700 flex items-center justify-center text-gray-600 dark:text-gray-300 font-bold text-lg mr-3 flex-shrink-0">
            {{ role.name.charAt(0) }}
          </div>
          <div class="flex-grow min-w-0">
            <h3 class="text-base font-semibold text-gray-900 dark:text-white truncate pr-1">{{ role.name }}</h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ role.profession || 'Unknown' }}</p>
          </div>
          <div class="flex-shrink-0 ml-2">
             <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200">
               {{ role.gender ? role.gender.charAt(0) : '?' }}/{{ role.age || '?' }}
             </span>
          </div>
        </div>
        
        <div class="space-y-3 flex-grow">
          <!-- Aggressiveness -->
          <div>
             <div class="flex justify-between text-xs items-center mb-1">
                <span class="text-gray-400 dark:text-gray-500 font-medium">Aggressiveness</span>
                <span class="text-gray-600 dark:text-gray-300 font-medium">{{ role.aggressiveness }}/10</span>
             </div>
             <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-1">
                <div class="bg-gray-800 dark:bg-gray-200 h-1 rounded-full transition-all duration-500" :style="{ width: `${role.aggressiveness * 10}%` }"></div>
             </div>
          </div>

          <!-- Personality -->
          <div class="mt-2">
            <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-3 leading-relaxed">
              {{ role.personality || 'No description.' }}
            </p>
          </div>
        </div>
        
        <div class="flex justify-between items-center mt-4 pt-3 border-t border-gray-50 dark:border-gray-700/50">
           <span class="text-[10px] text-gray-300 dark:text-gray-600">ID: {{ role.agent_id }}</span>
           <div class="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <button
                @click="editRole(role)"
                class="p-1.5 text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md transition-colors"
            >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 00-2 2h11a2 2 0 00-2-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
            </button>
            <button
                @click="deleteRole(role.id)"
                class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-md transition-colors"
            >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
            </button>
           </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Role Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center z-50 transition-all">
      <div class="bg-white dark:bg-gray-800 rounded-3xl px-4 pt-5 pb-4 text-left overflow-hidden shadow-2xl transform transition-all sm:max-w-lg sm:w-full sm:p-8 border border-gray-100 dark:border-gray-700">
        <div>
          <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">{{ isEditing ? 'Edit Role' : 'Create New Role' }}</h3>
          <form @submit.prevent="submitRole">
            <div class="space-y-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
                <input v-model="form.name" type="text" required class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
              </div>
              
              <div class="grid grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Gender</label>
                  <select v-model="form.gender" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Non-binary">Non-binary</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Age</label>
                  <input v-model="form.age" type="text" placeholder="e.g. 25, 40s" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Profession</label>
                <input v-model="form.profession" type="text" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Base Agent (LLM Config)</label>
                <select v-model="form.agent_id" required class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700">
                  <option v-if="agents.length === 0" value="" disabled>No agents available. Create one first.</option>
                  <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                    {{ agent.name }} ({{ agent.provider }}/{{ agent.model_name }})
                  </option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Personal Experience / Personality</label>
                <textarea v-model="form.personality" rows="4" class="block w-full border-gray-300 dark:border-gray-600 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 dark:bg-gray-700/50 dark:text-white transition-all focus:bg-white dark:focus:bg-gray-700" placeholder="Describe the character's background..."></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Aggressiveness ({{ form.aggressiveness }}/10)</label>
                <div class="flex items-center space-x-3 bg-gray-50/50 dark:bg-gray-700/50 p-3 rounded-xl border border-gray-200 dark:border-gray-600">
                    <span class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase">Peaceful</span>
                    <input v-model.number="form.aggressiveness" type="range" min="1" max="10" step="1" class="flex-grow h-2 bg-gray-200 dark:bg-gray-600 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                    <span class="text-xs text-gray-500 dark:text-gray-400 font-medium uppercase">Hostile</span>
                </div>
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
import { ref, onMounted, reactive } from 'vue'
import { roleApi, agentApi } from '@/services/api'
import type { Role, Agent, CreateRoleRequest } from '@/types'

const roles = ref<Role[]>([])
const agents = ref<Agent[]>([])
const loading = ref(true)
const showCreateModal = ref(false)
const isEditing = ref(false)
const editingId = ref<number | null>(null)

const form = reactive<CreateRoleRequest>({
  name: '',
  gender: '',
  age: '',
  profession: '',
  personality: '',
  aggressiveness: 5,
  agent_id: 0
})

const loadData = async () => {
  try {
    loading.value = true
    const [rolesData, agentsData] = await Promise.all([
      roleApi.getAll(),
      agentApi.getAll()
    ])
    roles.value = rolesData
    agents.value = agentsData
    
    // Set default agent_id if available and not set
    if (agentsData.length > 0 && form.agent_id === 0) {
      form.agent_id = agentsData[0].id
    }
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  isEditing.value = false
  editingId.value = null
  form.name = ''
  form.gender = ''
  form.age = ''
  form.profession = ''
  form.personality = ''
  form.aggressiveness = 5
  if (agents.value.length > 0) {
      form.agent_id = agents.value[0].id
  }
  showCreateModal.value = true
}

const editRole = (role: Role) => {
  isEditing.value = true
  editingId.value = role.id
  form.name = role.name
  form.gender = role.gender
  form.age = role.age
  form.profession = role.profession
  form.personality = role.personality
  form.aggressiveness = role.aggressiveness
  form.agent_id = role.agent_id
  showCreateModal.value = true
}

const submitRole = async () => {
  try {
    if (isEditing.value && editingId.value) {
      await roleApi.update(editingId.value, form)
    } else {
      await roleApi.create(form)
    }
    await loadData()
    showCreateModal.value = false
  } catch (error) {
    console.error('Failed to save role:', error)
    alert('Failed to save role')
  }
}

const deleteRole = async (id: number) => {
  if (!confirm('Are you sure you want to delete this role?')) return
  
  try {
    await roleApi.delete(id)
    await loadData()
  } catch (error) {
    console.error('Failed to delete role:', error)
    alert('Failed to delete role')
  }
}

onMounted(loadData)
</script>
