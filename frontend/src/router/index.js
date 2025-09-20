import { createRouter, createWebHistory } from 'vue-router'

const LandingPage  = () => import('../pages/LandingPage.vue')
const TaskView = () => import('../pages/taskview/TaskView.vue')
const UpdateTasks = () => import('../pages/update_tasks/UpdateTask.vue')

const routes = [
  { path: '/', name: 'landing', component: LandingPage },
  
  { path: '/tasks',  // change to '/tasks/:id'
    name: 'task-view', 
    component: TaskView 
    // ,meta: { requiresAuth: true }
  },

  { path: '/updatetask',
    name: 'update-task', 
    component: UpdateTasks 
  }
  
]

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() { return { top: 0 } }
})
