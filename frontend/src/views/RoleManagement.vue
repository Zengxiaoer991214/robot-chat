<template>
  <div class="px-4 sm:px-0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-900">Role Management</h2>
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
      <p class="mt-2 text-gray-500">Loading roles...</p>
    </div>
    
    <div v-else-if="roles.length === 0" class="text-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-gray-100 shadow-sm">
      <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900">No roles yet</h3>
      <p class="mt-1 text-gray-500">Create roles (personas) to participate in chats.</p>
    </div>
    
    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="role in roles"
        :key="role.id"
        class="group relative bg-white/70 backdrop-blur-md border border-white/20 rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
      >
        <div class="flex items-center mb-4">
          <div class="h-12 w-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-md mr-4">
            {{ role.name.charAt(0) }}
          </div>
          <div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ role.name }}</h3>
            <p class="text-sm text-gray-500">{{ role.profession || 'Unknown Profession' }}</p>
          </div>
        </div>
        
        <div class="space-y-3 mb-4">
          <div class="flex justify-between text-sm items-center p-2 bg-gray-50/50 rounded-xl">
            <span class="text-gray-500 text-xs uppercase tracking-wider font-semibold">Profile</span>
            <span class="font-medium text-gray-900">{{ role.gender || '?' }} / {{ role.age || '?' }}</span>
          </div>
          
          <div class="flex flex-col space-y-1 p-2 bg-gray-50/50 rounded-xl">
             <div class="flex justify-between text-sm items-center">
                <span class="text-gray-500 text-xs uppercase tracking-wider font-semibold">Aggressiveness</span>
                <span class="font-medium text-gray-900">{{ role.aggressiveness }}/10</span>
             </div>
             <div class="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                <div class="bg-indigo-500 h-1.5 rounded-full" :style="{ width: `${role.aggressiveness * 10}%` }"></div>
             </div>
          </div>

          <div class="text-sm">
            <span class="text-gray-400 text-xs uppercase tracking-wider font-semibold block mb-1.5">Personality</span>
            <div class="text-gray-600 bg-gray-50/80 p-3 rounded-xl border border-gray-100 text-xs leading-relaxed line-clamp-3">
              {{ role.personality || 'No personality description provided.' }}
            </div>
          </div>
          
          <div class="text-xs text-gray-400 flex items-center justify-end">
            <span class="bg-gray-100 px-2 py-1 rounded-lg">Agent ID: {{ role.agent_id }}</span>
          </div>
        </div>
        
        <div class="flex justify-end space-x-2 pt-4 border-t border-gray-100/50">
          <button
            @click="editRole(role)"
            class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-colors"
            title="Edit"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 00-2 2h11a2 2 0 00-2-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
          <button
            @click="deleteRole(role.id)"
            class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors"
            title="Delete"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Role Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-900/50 backdrop-blur-sm flex items-center justify-center z-50 transition-all">
      <div class="bg-white rounded-3xl px-4 pt-5 pb-4 text-left overflow-hidden shadow-2xl transform transition-all sm:max-w-lg sm:w-full sm:p-8 border border-gray-100">
        <div>
          <h3 class="text-2xl font-bold text-gray-900 mb-6">{{ isEditing ? 'Edit Role' : 'Create New Role' }}</h3>
          <form @submit.prevent="submitRole">
            <div class="space-y-5">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                <input v-model="form.name" type="text" required class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white">
              </div>
              
              <div class="grid grid-cols-2 gap-5">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Gender</label>
                  <select v-model="form.gender" class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white">
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Non-binary">Non-binary</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Age</label>
                  <input v-model="form.age" type="text" placeholder="e.g. 25, 40s" class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white">
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Profession</label>
                <input v-model="form.profession" type="text" class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Base Agent (LLM Config)</label>
                <select v-model="form.agent_id" required class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white">
                  <option v-if="agents.length === 0" value="" disabled>No agents available. Create one first.</option>
                  <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                    {{ agent.name }} ({{ agent.provider }}/{{ agent.model_name }})
                  </option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Personal Experience / Personality</label>
                <textarea v-model="form.personality" rows="4" class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white" placeholder="Describe the character's background..."></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Aggressiveness ({{ form.aggressiveness }}/10)</label>
                <div class="flex items-center space-x-3 bg-gray-50/50 p-3 rounded-xl border border-gray-200">
                    <span class="text-xs text-gray-500 font-medium uppercase">Peaceful</span>
                    <input v-model.number="form.aggressiveness" type="range" min="1" max="10" step="1" class="flex-grow h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600">
                    <span class="text-xs text-gray-500 font-medium uppercase">Hostile</span>
                </div>
              </div>
            </div>
            
            <div class="mt-8 flex justify-end space-x-3">
              <button type="button" @click="showCreateModal = false" class="inline-flex justify-center rounded-xl border border-gray-300 shadow-sm px-5 py-2.5 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none transition-colors">
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
