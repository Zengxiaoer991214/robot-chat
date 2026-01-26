import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import AgentManagement from '@/views/AgentManagement.vue'
import RoomConfiguration from '@/views/RoomConfiguration.vue'
import RoleManagement from '@/views/RoleManagement.vue'
import ChatRoom from '@/views/ChatRoom.vue'

const routes = [
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

export default router
