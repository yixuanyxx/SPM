<!-- dummy sample, can change name later, this can be home page w all the user's tasks instead, just rmb to change all the names in router/index.js -->
<!-- idk how yall do it, mayb instead of this we can have one folder for one page then put one vue file and one css file in each folder -->

 <script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../components/SideNavbar.vue'
import { sessionState } from '../services/session'
import { logout } from '../services/auth'
import './taskview/taskview.css'

const router = useRouter()
const now = ref(new Date())
const tasks = ref([])
const loading = ref(false)
const userId = localStorage.getItem('spm_userid')
const API_TASKS = 'http://localhost:5002'
const API_USERS = 'http://127.0.0.1:5003'
const userName = ref('')

const upcomingTasks = computed(() => {
  const list = Array.isArray(tasks.value) ? tasks.value.slice() : []
  return list
    .filter(t => !!t?.due_date)
    .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
    .slice(0, 5)
})
const greeting = computed(() => {
  const hour = now.value.getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

onMounted(() => {
  const timer = setInterval(() => (now.value = new Date()), 60000)
  // cleanup
  window.addEventListener('beforeunload', () => clearInterval(timer))
  if (userId) {
    fetchTasks()
    fetchUserName()
  }
})

async function onLogout() {
  await logout()
  router.push({ name: 'Login' })
}

async function fetchTasks() {
  try {
    loading.value = true
    const res = await fetch(`${API_TASKS}/tasks/user-task/${userId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    tasks.value = data?.tasks?.data || []
  } catch (e) {
    console.error('Failed to load tasks:', e)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

async function fetchUserName() {
  try {
    const res = await fetch(`${API_USERS}/users/${userId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    userName.value = data?.data?.name || ''
  } catch (e) {
    console.error('Failed to load user name:', e)
    userName.value = ''
  }
}
</script>

<template>
  <div class="app-layout ms-2">
    <SideNavbar />

    <div class="app-container">
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Welcome</h1>
          <p class="page-subtitle">Your hub for tasks, schedule, and projects</p>
        </div>
      </div>

      <div class="main-content">
        <div class="tasks-container">
          <div class="empty-state" style="padding-top: 0;">
            <div class="empty-icon">
              <i class="bi bi-emoji-smile"></i>
            </div>
            <div class="empty-title">{{ greeting }}, {{ userName || sessionState.user?.user_metadata?.name || 'there' }} 👋</div>
            <p class="empty-subtitle">Stay on top of your tasks, deadlines, and team collaboration.</p>
          </div>

          <div class="stats-section">
            <div class="stats-container">
              <div class="stat-card" @click="router.push('/tasks')">
                <div class="stat-content">
                  <div class="stat-icon ongoing">
                    <i class="bi bi-list-task"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">Tasks</div>
                    <div class="stat-title">View your tasks</div>
                  </div>
                </div>
              </div>

              <div class="stat-card" @click="router.push('/schedule')">
                <div class="stat-content">
                  <div class="stat-icon under-review">
                    <i class="bi bi-calendar3"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">Schedule</div>
                    <div class="stat-title">See upcoming events</div>
                  </div>
                </div>
              </div>

              <div class="stat-card" @click="router.push('/projects')">
                <div class="stat-content">
                  <div class="stat-icon completed">
                    <i class="bi bi-folder"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">Projects</div>
                    <div class="stat-title">Browse projects</div>
                  </div>
                </div>
              </div>

              <div class="stat-card" @click="router.push({ name: 'AccountSettings' })">
                <div class="stat-content">
                  <div class="stat-icon total">
                    <i class="bi bi-person-circle"></i>
                  </div>
                  <div class="stat-info">
                    <div class="stat-number">Account</div>
                    <div class="stat-title">Manage profile</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming tasks summary -->
        <div class="tasks-container" style="margin-top: 1rem;">
          <h3 class="page-subtitle" style="color:#374151; margin-bottom: 0.5rem;">Upcoming Tasks</h3>
          <div v-if="loading" class="empty-state" style="padding: 1rem;">
            <p class="empty-subtitle">Loading tasks…</p>
          </div>
          <div v-else>
            <div v-if="upcomingTasks.length === 0" class="empty-state" style="padding: 1rem;">
              <p class="empty-subtitle">No upcoming tasks.</p>
            </div>
            <div v-else>
              <div 
                v-for="(task, index) in upcomingTasks" 
                :key="task.id" 
                class="task-card" 
                :style="{ animationDelay: `${index * 0.05}s` }"
              >
                <div class="task-main" @click="router.push(`/tasks/${task.id}`)">
                  <div class="task-content">
                    <div class="task-header">
                      <div class="task-title-section">
                        <h3 class="task-title">{{ task.task_name }}</h3>
                        <div class="task-status" :class="{ ongoing: task.status==='Ongoing', completed: task.status==='Completed', 'under-review': task.status==='Under Review' }">
                          <i class="bi" :class="{ 'bi-play-circle': task.status==='Ongoing', 'bi-check-circle-fill': task.status==='Completed', 'bi-eye': task.status==='Under Review' }"></i>
                          <span>{{ task.status }}</span>
                        </div>
                      </div>
                      <div class="task-meta">
                        <div class="task-date">
                          <i class="bi bi-calendar3"></i>
                          <span>{{ new Date(task.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="task-actions">
                    <div class="click-hint">
                      <i class="bi bi-arrow-right"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* No component-scoped styles needed; using TaskView theme from imported CSS */
</style>
