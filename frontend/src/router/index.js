import { createRouter, createWebHistory } from 'vue-router'

const LandingPage  = () => import('../pages/LandingPage.vue')
const TaskView = () => import('../pages/taskview/TaskView.vue')
const TaskDetail = () => import('../pages/taskdetails/TaskDetails.vue')

const routes = [
  { path: '/', name: 'landing', component: LandingPage },

  {
    path: '/tasks/:id',  // new route with dynamic segment
    name: 'task-detail', 
    component: TaskDetail,
    props: true  // allows route params to be passed as props to the component
    // ,meta: { requiresAuth: true }
  },
  
  { path: '/tasks',  // change to '/tasks/:id'
    name: 'task-view', 
    component: TaskView 
    // ,meta: { requiresAuth: true }
  }
]

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() { return { top: 0 } }
})
