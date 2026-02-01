<template>
  <div class="px-4 sm:px-0">
    <!-- Header with Flexbox -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
      <h2 class="text-3xl font-bold tracking-tight text-gray-900">Dashboard</h2>
      
      <router-link
        to="/rooms/new"
        class="inline-flex items-center px-5 py-2.5 text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-full shadow-lg hover:shadow-indigo-500/30 transition-all duration-200 ease-in-out transform hover:-translate-y-0.5"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create New Room
      </router-link>
    </div>

    <div v-if="loading" class="flex justify-center items-center py-20">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
    </div>

    <div v-else-if="rooms.length === 0" class="text-center py-20 bg-white/50 backdrop-blur-sm rounded-3xl border border-gray-100 shadow-sm">
      <div class="mx-auto h-12 w-12 text-gray-400 mb-4">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-gray-900">No rooms yet</h3>
      <p class="mt-1 text-gray-500">Get started by creating your first chat room.</p>
    </div>

    <div v-else class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="room in rooms"
        :key="room.id"
        class="group relative bg-white/70 backdrop-blur-md border border-white/20 rounded-2xl p-6 shadow-sm hover:shadow-xl transition-all duration-300 cursor-pointer hover:-translate-y-1"
        @click="goToRoom(room.id)"
      >
        <div class="flex justify-between items-start mb-4">
          <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-md">
            {{ room.name.charAt(0).toUpperCase() }}
          </div>
          <span :class="statusClass(room.status)" class="px-2.5 py-1 text-xs font-medium rounded-full border">
            {{ room.status }}
          </span>
        </div>
        
        <h3 class="text-xl font-bold text-gray-900 mb-2 line-clamp-1 group-hover:text-indigo-600 transition-colors">{{ room.name }}</h3>
        <p class="text-sm text-gray-500 mb-4 line-clamp-2 min-h-[2.5rem]">{{ room.topic }}</p>
        
        <div class="flex items-center justify-between pt-4 border-t border-gray-100/50">
          <div class="flex items-center space-x-4 text-xs text-gray-500">
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              {{ room.roles.length }}
            </div>
            <div class="flex items-center">
              <svg class="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ room.current_rounds }}/{{ room.max_rounds }}
            </div>
          </div>
          
          <button 
            @click.stop="deleteRoom(room.id)"
            class="text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full hover:bg-red-50"
            title="Delete Room"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
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

const deleteRoom = async (id: number) => {
  if (!confirm('Are you sure you want to delete this room? All history will be lost.')) return
  
  try {
    await roomApi.delete(id)
    // Remove from list immediately
    rooms.value = rooms.value.filter((r: Room) => r.id !== id)
  } catch (error) {
    console.error('Failed to delete room:', error)
    alert('Failed to delete room')
  }
}

const statusClass = (status: string) => {
  switch (status) {
    case 'running':
      return 'bg-green-50 text-green-700 border-green-200'
    case 'finished':
      return 'bg-gray-100 text-gray-700 border-gray-200'
    default:
      return 'bg-amber-50 text-amber-700 border-amber-200'
  }
}

onMounted(() => {
  loadRooms()
})
</script>