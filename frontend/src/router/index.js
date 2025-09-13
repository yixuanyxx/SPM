import { createRouter, createWebHistory } from 'vue-router'

const LandingPage  = () => import('../pages/LandingPage.vue')

const routes = [
  { path: '/', name: 'landing', component: LandingPage },
]

export default createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() { return { top: 0 } }
})
