<template>
  <div id="app" class="min-h-screen font-sans antialiased selection:bg-indigo-500 selection:text-white">
    <nav class="sticky top-0 z-50 bg-white/70 backdrop-blur-lg border-b border-white/20 shadow-sm transition-all duration-300">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <!-- Mobile Back Button -->
            <button 
              v-if="route.path !== '/'"
              @click="router.back()"
              class="mr-2 -ml-2 p-2 rounded-full text-gray-500 hover:bg-gray-100/50 hover:text-gray-900 transition-colors focus:outline-none sm:hidden active:scale-95"
              aria-label="Back"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <div class="flex-shrink-0 flex items-center gap-2 cursor-pointer transition-transform hover:scale-105" @click="router.push('/')">
              <div class="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg shadow-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 truncate max-w-[150px] sm:max-w-none">AI Group Chat</h1>
            </div>
            <div class="hidden sm:ml-8 sm:flex sm:space-x-8">
              <router-link
                to="/"
                class="border-transparent text-gray-500 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
                active-class="border-indigo-500 text-indigo-600"
              >
                Dashboard
              </router-link>
              <router-link
                to="/agents"
                class="border-transparent text-gray-500 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
                active-class="border-indigo-500 text-indigo-600"
              >
                Agents
              </router-link>
              <router-link
                to="/roles"
                class="border-transparent text-gray-500 hover:text-gray-900 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
                active-class="border-indigo-500 text-indigo-600"
              >
                Roles
              </router-link>
            </div>
          </div>
          
          <!-- Mobile Menu Button -->
          <div class="flex items-center sm:hidden">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-500 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 transition-colors"
              aria-expanded="false"
            >
              <span class="sr-only">Open main menu</span>
              <!-- Icon when menu is closed -->
              <svg v-if="!mobileMenuOpen" class="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <!-- Icon when menu is open -->
              <svg v-else class="block h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile Menu -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform opacity-0 scale-95"
        enter-to-class="transform opacity-100 scale-100"
        leave-active-class="transition duration-100 ease-in"
        leave-from-class="transform opacity-100 scale-100"
        leave-to-class="transform opacity-0 scale-95"
      >
        <div v-if="mobileMenuOpen" class="sm:hidden bg-white/95 backdrop-blur-xl border-b border-gray-200 shadow-lg absolute w-full z-50">
          <div class="pt-2 pb-4 space-y-1 px-2">
            <router-link
              to="/"
              class="block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors"
              active-class="bg-indigo-50 border-indigo-500 text-indigo-700"
              exact-active-class="bg-indigo-50 border-indigo-500 text-indigo-700"
              :class="[$route.path === '/' ? '' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
              @click="mobileMenuOpen = false"
            >
              Dashboard
            </router-link>
            <router-link
              to="/agents"
              class="block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors"
              active-class="bg-indigo-50 border-indigo-500 text-indigo-700"
              :class="[$route.path.startsWith('/agents') ? '' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
              @click="mobileMenuOpen = false"
            >
              Agents
            </router-link>
            <router-link
              to="/roles"
              class="block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors"
              active-class="bg-indigo-50 border-indigo-500 text-indigo-700"
              :class="[$route.path.startsWith('/roles') ? '' : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700']"
              @click="mobileMenuOpen = false"
            >
              Roles
            </router-link>
          </div>
        </div>
      </transition>
    </nav>

    <main class="py-6 sm:px-6 lg:px-8 transition-all duration-500 ease-out">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const mobileMenuOpen = ref(false)
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
