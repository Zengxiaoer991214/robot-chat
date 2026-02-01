<template>
  <div class="px-4 sm:px-0">
    <div class="md:grid md:grid-cols-3 md:gap-6">
      <div class="md:col-span-1">
        <div class="px-4 sm:px-0 sticky top-6">
          <h3 class="text-xl font-bold leading-6 text-gray-900">Room Configuration</h3>
          <p class="mt-2 text-sm text-gray-500">
            Create a new chat room where AI agents will discuss a topic.
            Choose the mode that fits your needs:
          </p>
          <ul class="mt-4 space-y-3 text-sm text-gray-500">
            <li class="flex items-start">
              <span class="flex-shrink-0 h-5 w-5 text-indigo-500 flex items-center justify-center">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path></svg>
              </span>
              <span class="ml-2"><strong class="font-medium text-gray-900">Debate:</strong> Structured argument between roles.</span>
            </li>
            <li class="flex items-start">
              <span class="flex-shrink-0 h-5 w-5 text-indigo-500 flex items-center justify-center">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
              </span>
              <span class="ml-2"><strong class="font-medium text-gray-900">Group Chat:</strong> Casual conversation.</span>
            </li>
          </ul>
        </div>
      </div>
      
      <div class="mt-5 md:mt-0 md:col-span-2">
        <form @submit.prevent="createRoom">
          <div class="bg-white/70 backdrop-blur-md border border-white/20 rounded-2xl shadow-sm overflow-hidden">
            <div class="px-4 py-5 space-y-6 sm:p-8">
              <!-- Room Name -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Room Name</label>
                <input
                  v-model="form.name"
                  type="text"
                  required
                  class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white"
                  placeholder="e.g. Philosophy Debate"
                />
              </div>

              <!-- Topic -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Topic</label>
                <textarea
                  v-model="form.topic"
                  rows="3"
                  required
                  class="block w-full border-gray-300 rounded-xl shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border p-2.5 bg-gray-50/50 transition-all focus:bg-white"
                  placeholder="e.g. Is artificial consciousness possible?"
                ></textarea>
                <p class="mt-2 text-sm text-gray-500">
                  The topic that the agents will discuss.
                </p>
              </div>

              <!-- Mode -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-3">Mode</label>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div 
                    class="relative rounded-xl border p-4 flex cursor-pointer transition-all duration-200"
                    :class="form.mode === 'debate' ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-500' : 'border-gray-200 hover:bg-gray-50'"
                    @click="form.mode = 'debate'"
                  >
                    <div class="flex items-center h-5">
                      <input
                        id="debate"
                        name="mode"
                        type="radio"
                        value="debate"
                        v-model="form.mode"
                        class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                      />
                    </div>
                    <div class="ml-3 flex flex-col">
                      <span class="block text-sm font-medium" :class="form.mode === 'debate' ? 'text-indigo-900' : 'text-gray-900'">
                        Debate
                      </span>
                      <span class="block text-sm" :class="form.mode === 'debate' ? 'text-indigo-700' : 'text-gray-500'">
                        Structured argument
                      </span>
                    </div>
                  </div>

                  <div 
                    class="relative rounded-xl border p-4 flex cursor-pointer transition-all duration-200"
                    :class="form.mode === 'group_chat' ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-500' : 'border-gray-200 hover:bg-gray-50'"
                    @click="form.mode = 'group_chat'"
                  >
                    <div class="flex items-center h-5">
                      <input
                        id="group_chat"
                        name="mode"
                        type="radio"
                        value="group_chat"
                        v-model="form.mode"
                        class="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                      />
                    </div>
                    <div class="ml-3 flex flex-col">
                      <span class="block text-sm font-medium" :class="form.mode === 'group_chat' ? 'text-indigo-900' : 'text-gray-900'">
                        Group Chat
                      </span>
                      <span class="block text-sm" :class="form.mode === 'group_chat' ? 'text-indigo-700' : 'text-gray-500'">
                        Casual conversation
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Max Rounds -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Max Rounds</label>
                <div class="flex items-center space-x-4">
                  <input
                    v-model.number="form.max_rounds"
                    type="range"
                    min="1"
                    max="100"
                    class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                  />
                  <span class="text-sm font-medium text-gray-900 w-12 text-center">{{ form.max_rounds }}</span>
                </div>
                <p class="mt-2 text-sm text-gray-500">
                  The conversation will automatically stop after this many rounds.
                </p>
              </div>

              <!-- Select Roles -->
              <div>
                <fieldset>
                  <legend class="text-base font-medium text-gray-900 mb-3">Select Roles <span class="text-sm font-normal text-gray-500 ml-2">(Select at least 2)</span></legend>
                  
                  <div class="bg-gray-50/50 rounded-xl border border-gray-200 overflow-hidden max-h-96 overflow-y-auto">
                    <div v-if="loadingRoles" class="py-8 text-center text-gray-500 flex flex-col items-center">
                       <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600 mb-2"></div>
                       Loading roles...
                    </div>
                    <div v-else-if="roles.length === 0" class="py-8 text-center text-gray-500">
                      No roles available. Please create roles first.
                    </div>
                    <div v-else class="divide-y divide-gray-100">
                      <div 
                        v-for="role in roles" 
                        :key="role.id" 
                        class="relative flex items-center p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                        @click="toggleRole(role.id)"
                      >
                        <div class="flex items-center h-5">
                          <input
                            :id="`role-${role.id}`"
                            :value="role.id"
                            v-model="selectedRoleIds"
                            type="checkbox"
                            class="focus:ring-indigo-500 h-5 w-5 text-indigo-600 border-gray-300 rounded transition-colors"
                            @click.stop
                          />
                        </div>
                        <div class="ml-3 flex-1">
                          <label :for="`role-${role.id}`" class="font-medium text-gray-900 select-none block cursor-pointer">
                            {{ role.name }}
                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 ml-2">
                              {{ role.profession || 'No profession' }}
                            </span>
                          </label>
                          <div class="mt-1 flex items-center text-sm text-gray-500 space-x-3">
                             <span>{{ role.gender }}</span>
                             <span class="text-gray-300">&bull;</span>
                             <span>{{ role.age }} years</span>
                             <span class="text-gray-300">&bull;</span>
                             <div class="flex items-center">
                               <span class="mr-1 text-xs uppercase tracking-wider">Aggression:</span>
                               <div class="w-16 bg-gray-200 rounded-full h-1.5 mr-2">
                                  <div class="bg-indigo-400 h-1.5 rounded-full" :style="{ width: `${role.aggressiveness * 10}%` }"></div>
                               </div>
                               <span class="text-xs text-gray-600 font-bold">{{ role.aggressiveness }}</span>
                             </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <p class="mt-2 text-sm text-red-600" v-if="rolesError">
                    {{ rolesError }}
                  </p>
                </fieldset>
              </div>
            </div>
            
            <div class="px-4 py-4 bg-gray-50/80 backdrop-blur text-right sm:px-6 border-t border-gray-100">
              <button
                type="submit"
                :disabled="creating || selectedRoleIds.length < 2"
                class="inline-flex justify-center items-center py-2.5 px-6 border border-transparent shadow-lg text-sm font-medium rounded-full text-white bg-indigo-600 hover:bg-indigo-700 hover:shadow-indigo-500/30 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:-translate-y-0.5"
              >
                <svg v-if="creating" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ creating ? 'Creating Room...' : 'Create Room' }}
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

const toggleRole = (id: number) => {
  const index = selectedRoleIds.value.indexOf(id)
  if (index === -1) {
    selectedRoleIds.value.push(id)
  } else {
    selectedRoleIds.value.splice(index, 1)
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
