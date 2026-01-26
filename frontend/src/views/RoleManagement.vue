<template>
  <div class="px-4 sm:px-0">
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-900">Role Management</h2>
      <button
        @click="openCreateModal"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Create New Role
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Loading roles...</p>
    </div>
    
    <div v-else-if="roles.length === 0" class="text-center py-12">
      <p class="text-gray-500">No roles found. Create one to get started!</p>
    </div>
    
    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="role in roles"
        :key="role.id"
        class="bg-white overflow-hidden shadow rounded-lg border border-gray-200"
      >
        <div class="px-4 py-5 sm:p-6">
          <div class="flex items-center mb-4">
            <div class="h-10 w-10 rounded-full bg-purple-100 flex items-center justify-center text-purple-600 font-bold text-xl mr-3">
              {{ role.name.charAt(0) }}
            </div>
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ role.name }}</h3>
              <p class="text-sm text-gray-500">{{ role.profession || 'Unknown Profession' }}</p>
            </div>
          </div>
          
          <div class="space-y-2 mb-4">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Gender/Age:</span>
              <span class="font-medium">{{ role.gender || '?' }} / {{ role.age || '?' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">Aggressiveness:</span>
              <span class="font-medium">{{ role.aggressiveness }}/10</span>
            </div>
            <div class="text-sm">
              <span class="text-gray-500 block mb-1">Personality:</span>
              <p class="text-gray-700 bg-gray-50 p-2 rounded text-xs line-clamp-3">{{ role.personality || 'None' }}</p>
            </div>
            <div class="text-xs text-gray-400 mt-2">
              Base Agent ID: {{ role.agent_id }}
            </div>
          </div>
          
          <div class="flex justify-end space-x-2">
            <button
              @click="editRole(role)"
              class="text-indigo-600 hover:text-indigo-900 text-sm font-medium"
            >
              Edit
            </button>
            <button
              @click="deleteRole(role.id)"
              class="text-red-600 hover:text-red-900 text-sm font-medium"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Create/Edit Role Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:max-w-lg sm:w-full sm:p-6">
        <div>
          <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">{{ isEditing ? 'Edit Role' : 'Create New Role' }}</h3>
          <form @submit.prevent="submitRole">
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Name</label>
                <input v-model="form.name" type="text" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
              </div>
              
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Gender</label>
                  <select v-model="form.gender" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
                    <option value="">Select...</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Non-binary">Non-binary</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Age</label>
                  <input v-model="form.age" type="text" placeholder="e.g. 25, 40s" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Profession</label>
                <input v-model="form.profession" type="text" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">Base Agent (LLM Config)</label>
                <select v-model="form.agent_id" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2">
                  <option v-if="agents.length === 0" value="" disabled>No agents available. Create one first.</option>
                  <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                    {{ agent.name }} ({{ agent.provider }}/{{ agent.model_name }})
                  </option>
                </select>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Personality</label>
                <textarea v-model="form.personality" rows="3" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2" placeholder="Describe the personality (e.g. cheerful, grumpy, sarcastic...)"></textarea>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-gray-700">Aggressiveness ({{ form.aggressiveness }}/10)</label>
                <div class="flex items-center space-x-2">
                    <span class="text-xs text-gray-500">Peaceful</span>
                    <input v-model.number="form.aggressiveness" type="range" min="1" max="10" step="1" class="flex-grow">
                    <span class="text-xs text-gray-500">Hostile</span>
                </div>
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
