import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import AgentManagement from '@/views/AgentManagement.vue'
import RoomConfiguration from '@/views/RoomConfiguration.vue'
import RoleManagement from '@/views/RoleManagement.vue'
import ChatRoom from '@/views/ChatRoom.vue'
import Login from '@/views/Login.vue'
import axios from 'axios'
import { getApiBaseUrl } from '@/services/config'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/agents',
    name: 'AgentManagement',
    component: AgentManagement,
  },
  {
    path: '/roles',
    name: 'RoleManagement',
    component: RoleManagement,
  },
  {
    path: '/rooms/new',
    name: 'RoomConfiguration',
    component: RoomConfiguration,
  },
  {
    path: '/rooms/:id',
    name: 'ChatRoom',
    component: ChatRoom,
    props: true,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

const API_BASE_URL = getApiBaseUrl()

// Auth Guard
router.beforeEach(async (to, _from, next) => {
  if (to.path === '/login') {
    next()
    return
  }

  const isAuthenticated = localStorage.getItem('isAuthenticated')
  if (isAuthenticated === 'true') {
    next()
    return
  }

  try {
    // Check if auth is required
    const response = await axios.get(`${API_BASE_URL}/auth/status`)
    if (response.data.required) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      // Auth not required, mark as authenticated to skip future checks
      localStorage.setItem('isAuthenticated', 'true')
      next()
    }
  } catch (error) {
    console.error('Error checking auth status:', error)
    // If backend is down or error, assume we can proceed or show error
    // For now, let's proceed but maybe backend will block 401 later
    next()
  }
})

export default router
