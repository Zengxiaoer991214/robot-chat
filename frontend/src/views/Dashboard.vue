<template>
  <div class="px-4 sm:px-0">
    <h2 class="text-3xl font-bold text-gray-900 mb-6">Dashboard</h2>
    
    <div class="mb-6">
      <router-link
        to="/rooms/new"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
      >
        Create New Room
      </router-link>
    </div>

    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Loading rooms...</p>
    </div>

    <div v-else-if="rooms.length === 0" class="text-center py-12">
      <p class="text-gray-500">No rooms yet. Create your first room to get started!</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="room in rooms"
        :key="room.id"
        class="bg-white overflow-hidden shadow rounded-lg hover:shadow-md transition-shadow cursor-pointer"
        @click="goToRoom(room.id)"
      >
        <div class="px-4 py-5 sm:p-6">
          <h3 class="text-lg font-medium text-gray-900 mb-2">{{ room.name }}</h3>
          <p class="text-sm text-gray-500 mb-3">{{ room.topic }}</p>
          <div class="flex justify-between items-center">
            <span :class="statusClass(room.status)" class="px-2 py-1 text-xs rounded-full">
              {{ room.status }}
            </span>
            <span class="text-sm text-gray-500">
              {{ room.current_rounds }}/{{ room.max_rounds }} rounds
            </span>
          </div>
          <div class="mt-3 flex items-center">
            <span class="text-xs text-gray-500 mr-2">Agents:</span>
            <span class="text-xs font-medium">{{ room.agents.length }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { roomApi } from '@/services/api'
import type { Room } from '@/types'

const router = useRouter()
const rooms = ref<Room[]>([])
const loading = ref(true)

const loadRooms = async () => {
  try {
    rooms.value = await roomApi.getAll()
  } catch (error) {
    console.error('Failed to load rooms:', error)
  } finally {
    loading.value = false
  }
}

const goToRoom = (id: number) => {
  router.push(`/rooms/${id}`)
}

const statusClass = (status: string) => {
  switch (status) {
    case 'running':
      return 'bg-green-100 text-green-800'
    case 'finished':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-yellow-100 text-yellow-800'
  }
}

onMounted(() => {
  loadRooms()
})
</script>
