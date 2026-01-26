<template>
  <div class="px-4 sm:px-0">
    <div class="md:grid md:grid-cols-3 md:gap-6">
      <div class="md:col-span-1">
        <div class="px-4 sm:px-0">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Room Configuration</h3>
          <p class="mt-1 text-sm text-gray-600">
            Create a new chat room where AI agents will discuss a topic.
          </p>
        </div>
      </div>
      
      <div class="mt-5 md:mt-0 md:col-span-2">
        <form @submit.prevent="createRoom">
          <div class="shadow sm:rounded-md sm:overflow-hidden">
            <div class="px-4 py-5 bg-white space-y-6 sm:p-6">
              <!-- Room Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700">Room Name</label>
                <div class="mt-1">
                  <input
                    v-model="form.name"
                    type="text"
                    required
                    class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                    placeholder="e.g. Philosophy Debate"
                  />
                </div>
              </div>

              <!-- Topic -->
              <div>
                <label class="block text-sm font-medium text-gray-700">Topic</label>
                <div class="mt-1">
                  <textarea
                    v-model="form.topic"
                    rows="3"
                    required
                    class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                    placeholder="e.g. Is artificial consciousness possible?"
                  ></textarea>
                </div>
                <p class="mt-2 text-sm text-gray-500">
                  The topic that the agents will discuss.
                </p>
              </div>

              <!-- Mode -->
              <div>
                <label class="block text-sm font-medium text-gray-700">Mode</label>
                <div class="mt-2 space-y-4 sm:flex sm:items-center sm:space-y-0 sm:space-x-10">
                  <div class="flex items-center">
                    <input
                      id="debate"
                      name="mode"
                      type="radio"
                      value="debate"
                      v-model="form.mode"
                      class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                    />
                    <label for="debate" class="ml-3 block text-sm font-medium text-gray-700">
                      Debate
                    </label>
                  </div>
                  <div class="flex items-center">
                    <input
                      id="group_chat"
                      name="mode"
                      type="radio"
                      value="group_chat"
                      v-model="form.mode"
                      class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                    />
                    <label for="group_chat" class="ml-3 block text-sm font-medium text-gray-700">
                      Group Chat
                    </label>
                  </div>
                </div>
                <p class="mt-2 text-sm text-gray-500">
                  Debate: Structured argument between roles. Group Chat: Casual conversation between roles.
                </p>
              </div>

              <!-- Max Rounds -->
              <div>
                <label class="block text-sm font-medium text-gray-700">Max Rounds</label>
                <div class="mt-1">
                  <input
                    v-model.number="form.max_rounds"
                    type="number"
                    min="1"
                    max="100"
                    required
                    class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                  />
                </div>
                <p class="mt-2 text-sm text-gray-500">
                  The conversation will automatically stop after this many rounds.
                </p>
              </div>

              <!-- Select Roles -->
              <div>
                <fieldset>
                  <legend class="text-base font-medium text-gray-900">Select Roles</legend>
                  <div class="mt-4 border-t border-b border-gray-200 divide-y divide-gray-200 max-h-60 overflow-y-auto">
                    <div v-if="loadingRoles" class="py-4 text-center text-gray-500">
                      Loading roles...
                    </div>
                    <div v-else-if="roles.length === 0" class="py-4 text-center text-gray-500">
                      No roles available. Please create roles first.
                    </div>
                    <div v-else v-for="role in roles" :key="role.id" class="relative flex items-start py-4">
                      <div class="min-w-0 flex-1 text-sm">
                        <label :for="`role-${role.id}`" class="font-medium text-gray-700 select-none block">
                          {{ role.name }}
                          <span class="text-gray-500 font-normal">({{ role.profession || 'No profession' }})</span>
                        </label>
                        <p class="text-gray-500 truncate">
                           {{ role.gender }} | {{ role.age }} | Aggressiveness: {{ role.aggressiveness }}/10
                        </p>
                      </div>
                      <div class="ml-3 flex items-center h-5">
                        <input
                          :id="`role-${role.id}`"
                          :value="role.id"
                          v-model="selectedRoleIds"
                          type="checkbox"
                          class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
                        />
                      </div>
                    </div>
                  </div>
                  <p class="mt-2 text-sm text-red-600" v-if="rolesError">
                    {{ rolesError }}
                  </p>
                </fieldset>
              </div>
            </div>
            
            <div class="px-4 py-3 bg-gray-50 text-right sm:px-6">
              <button
                type="submit"
                :disabled="creating || selectedRoleIds.length < 2"
                class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {{ creating ? 'Creating...' : 'Create Room' }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { roomApi, roleApi } from '@/services/api'
import type { Role, CreateRoomRequest } from '@/types'

const router = useRouter()
const roles = ref<Role[]>([])
const loadingRoles = ref(true)
const creating = ref(false)
const rolesError = ref('')

const form = reactive<Omit<CreateRoomRequest, 'role_ids'>>({
  name: '',
  topic: '',
  max_rounds: 20,
  mode: 'debate'
})

const selectedRoleIds = ref<number[]>([])

const loadRoles = async () => {
  try {
    loadingRoles.value = true
    roles.value = await roleApi.getAll()
  } catch (error) {
    console.error('Failed to load roles:', error)
  } finally {
    loadingRoles.value = false
  }
}

const createRoom = async () => {
  if (selectedRoleIds.value.length < 2) {
    rolesError.value = 'Please select at least 2 roles'
    return
  }
  
  try {
    creating.value = true
    rolesError.value = ''
    
    const roomData: CreateRoomRequest = {
      ...form,
      role_ids: selectedRoleIds.value
    }
    
    const room = await roomApi.create(roomData)
    router.push(`/rooms/${room.id}`)
  } catch (error) {
    console.error('Failed to create room:', error)
    alert('Failed to create room')
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadRoles()
})
</script>
