import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import AgentManagement from '@/views/AgentManagement.vue'
import RoomConfiguration from '@/views/RoomConfiguration.vue'
import RoleManagement from '@/views/RoleManagement.vue'
import ChatRoom from '@/views/ChatRoom.vue'
import Playground from '@/views/Playground.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
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
    path: '/chat',
    name: 'Playground',
    component: Playground,
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

// Auth Guard
router.beforeEach((to, _from, next) => {
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)
  const loggedIn = localStorage.getItem('token')

  if (authRequired && !loggedIn) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else {
    next()
  }
})

export default router
