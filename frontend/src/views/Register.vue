<template>
  <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center bg-gradient-to-br from-purple-50 via-white to-indigo-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 px-4 py-12 sm:px-6 lg:px-8 transition-colors duration-300">
    <div class="max-w-md w-full space-y-8 bg-white/80 dark:bg-gray-900/60 backdrop-blur-xl p-8 sm:p-10 rounded-3xl shadow-2xl border border-white/20 dark:border-gray-800 transition-all duration-300 hover:shadow-3xl hover:-translate-y-1">
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-2xl shadow-lg flex items-center justify-center mb-6 transform -rotate-3 hover:rotate-0 transition-transform duration-300">
          <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
        </div>
        <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">
          Create Account
        </h2>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
          Join to build your personal AI workforce
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div class="relative group">
            <label for="username" class="sr-only">Username</label>
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-purple-500 dark:group-focus-within:text-purple-400 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              id="username"
              name="username"
              type="text"
              required
              v-model="username"
              class="appearance-none rounded-2xl relative block w-full pl-10 pr-4 py-3.5 border border-gray-200 dark:border-gray-700 placeholder-gray-400 dark:placeholder-gray-600 text-gray-900 dark:text-gray-100 bg-gray-50/50 dark:bg-gray-950/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 dark:focus:ring-purple-500/40 focus:border-purple-500 dark:focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 transition-all duration-200 sm:text-sm"
              placeholder="Username"
            />
          </div>
          <div class="relative group">
            <label for="email" class="sr-only">Email (Optional)</label>
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-purple-500 dark:group-focus-within:text-purple-400 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
              </svg>
            </div>
            <input
              id="email"
              name="email"
              type="email"
              v-model="email"
              class="appearance-none rounded-2xl relative block w-full pl-10 pr-4 py-3.5 border border-gray-200 dark:border-gray-700 placeholder-gray-400 dark:placeholder-gray-600 text-gray-900 dark:text-gray-100 bg-gray-50/50 dark:bg-gray-950/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 dark:focus:ring-purple-500/40 focus:border-purple-500 dark:focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 transition-all duration-200 sm:text-sm"
              placeholder="Email (Optional)"
            />
          </div>

          <div class="relative group">
            <label for="invitationCode" class="sr-only">Invitation Code</label>
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-purple-500 dark:group-focus-within:text-purple-400 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-11a1 1 0 10-2 0v2H7a1 1 0 100 2h2v2a1 1 0 102 0v-2h2a1 1 0 100-2h-2V7z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              id="invitationCode"
              name="invitationCode"
              type="text"
              required
              v-model="invitationCode"
              class="appearance-none rounded-2xl relative block w-full pl-10 pr-4 py-3.5 border border-gray-200 dark:border-gray-700 placeholder-gray-400 dark:placeholder-gray-600 text-gray-900 dark:text-gray-100 bg-gray-50/50 dark:bg-gray-950/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 dark:focus:ring-purple-500/40 focus:border-purple-500 dark:focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 transition-all duration-200 sm:text-sm"
              placeholder="Invitation Code"
            />
          </div>
          
          <div class="relative group">
            <label for="password" class="sr-only">Password</label>
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-purple-500 dark:group-focus-within:text-purple-400 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              required
              v-model="password"
              class="appearance-none rounded-2xl relative block w-full pl-10 pr-4 py-3.5 border border-gray-200 dark:border-gray-700 placeholder-gray-400 dark:placeholder-gray-600 text-gray-900 dark:text-gray-100 bg-gray-50/50 dark:bg-gray-950/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 dark:focus:ring-purple-500/40 focus:border-purple-500 dark:focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 transition-all duration-200 sm:text-sm"
              placeholder="Password"
            />
          </div>
          <div class="relative group">
            <label for="confirmPassword" class="sr-only">Confirm Password</label>
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400 dark:text-gray-500 group-focus-within:text-purple-500 dark:group-focus-within:text-purple-400 transition-colors" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
              </svg>
            </div>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              required
              v-model="confirmPassword"
              class="appearance-none rounded-2xl relative block w-full pl-10 pr-4 py-3.5 border border-gray-200 dark:border-gray-700 placeholder-gray-400 dark:placeholder-gray-600 text-gray-900 dark:text-gray-100 bg-gray-50/50 dark:bg-gray-950/50 focus:outline-none focus:ring-2 focus:ring-purple-500/20 dark:focus:ring-purple-500/40 focus:border-purple-500 dark:focus:border-purple-500 focus:bg-white dark:focus:bg-gray-900 transition-all duration-200 sm:text-sm"
              placeholder="Confirm Password"
            />
          </div>
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="group relative w-full flex justify-center py-3.5 px-4 border border-transparent text-sm font-bold rounded-2xl text-white bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 dark:focus:ring-offset-gray-900 transition-all duration-200 disabled:opacity-70 disabled:cursor-not-allowed shadow-lg hover:shadow-purple-500/30 transform hover:-translate-y-0.5 active:scale-95"
          >
            <span v-if="loading" class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ loading ? 'Creating Account...' : 'Sign Up' }}
          </button>
        </div>
        
        <div class="text-center">
            <p class="text-sm text-gray-600 dark:text-gray-400">
                Already have an account? 
                <router-link to="/login" class="font-semibold text-purple-600 dark:text-purple-400 hover:text-purple-500 dark:hover:text-purple-300 transition-colors">
                    Sign in
                </router-link>
            </p>
        </div>

        <div v-if="error" class="text-center text-sm text-red-500 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-xl border border-red-100 dark:border-red-800 animate-pulse">
           {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/services/api'

const username = ref('')
const email = ref('')
const invitationCode = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const router = useRouter()

const handleRegister = async () => {
  if (password.value.length < 6) {
      error.value = "Password must be at least 6 characters long"
      return
  }

  if (password.value !== confirmPassword.value) {
      error.value = "Passwords do not match"
      return
  }

  loading.value = true
  error.value = ''
  
  try {
    await authApi.register({
        username: username.value,
        password: password.value,
        email: email.value || undefined,
        invitation_code: invitationCode.value
    })
    
    // Auto login or redirect to login? Redirect to login for now.
    router.push('/login')
  } catch (err: any) {
    if (err.response && err.response.data && err.response.data.detail) {
      error.value = err.response.data.detail
    } else {
      error.value = 'Registration failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
