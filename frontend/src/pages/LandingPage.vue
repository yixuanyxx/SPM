<!-- dummy sample, can change name later, this can be home page w all the user's tasks instead, just rmb to change all the names in router/index.js -->
<!-- idk how yall do it, mayb instead of this we can have one folder for one page then put one vue file and one css file in each folder -->

 <script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../components/SideNavbar.vue'
import NotificationDropdown from '../components/NotificationDropdown.vue'
import { sessionState } from '../services/session'
import { logout } from '../services/auth'
import { notificationStore, userPreferencesService } from '../services/notifications'
import './taskview/taskview.css'

const router = useRouter()
const now = ref(new Date())
const tasks = ref([])
const loading = ref(false)
const userId = localStorage.getItem('spm_userid')
const API_TASKS = 'http://localhost:5002'
const API_USERS = 'http://127.0.0.1:5003'
const userName = ref('')
const showNotificationDropdown = ref(false)
const unreadCount = ref(0)
const userPreferences = ref({ in_app: true, email: true })
const inAppNotifications = ref([])

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

onMounted(async () => {
  const timer = setInterval(() => (now.value = new Date()), 60000)
  // cleanup
  window.addEventListener('beforeunload', () => clearInterval(timer))
  if (userId) {
    fetchTasks()
    fetchUserName()
    await initializeNotifications()
  }
})

async function onLogout() {
  try {
    console.log('Logging out...');
    await logout();
    console.log('Logout successful, redirecting to login...');
    router.push({ name: 'Login' });
  } catch (error) {
    console.error('Logout failed:', error);
    // Still redirect to login even if logout fails
    router.push({ name: 'Login' });
  }
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

async function initializeNotifications() {
  try {
    // Initialize notification store
    await notificationStore.init(userId)
    unreadCount.value = notificationStore.unreadCount
    
    // Get user preferences
    const userData = await userPreferencesService.getUserData(userId)
    userPreferences.value = userData?.data?.notification_preferences || { in_app: true, email: true }
    
    // Load in-app notifications if enabled
    if (userPreferences.value.in_app) {
      loadInAppNotifications()
    }
    
    // Set up periodic refresh for notifications (every 30 seconds)
    setInterval(async () => {
      try {
        await notificationStore.refresh(userId)
        unreadCount.value = notificationStore.unreadCount
        if (userPreferences.value.in_app) {
          loadInAppNotifications()
        }
      } catch (error) {
        console.error('Failed to refresh notifications:', error)
      }
    }, 30000)
    
  } catch (error) {
    console.error('Failed to initialize notifications:', error)
  }
}

function loadInAppNotifications() {
  // Show only recent unread notifications for in-app display
  const unreadNotifications = notificationStore.notifications.filter(n => !n.is_read)
  inAppNotifications.value = unreadNotifications.slice(0, 3) // Show max 3 recent notifications
}

function toggleNotificationDropdown() {
  showNotificationDropdown.value = !showNotificationDropdown.value
}

function closeNotificationDropdown() {
  showNotificationDropdown.value = false
}

async function dismissInAppNotification(notificationId) {
  try {
    await notificationStore.markAsRead(notificationId)
    loadInAppNotifications() // Refresh in-app notifications
    unreadCount.value = notificationStore.unreadCount
  } catch (error) {
    console.error('Failed to dismiss notification:', error)
  }
}

// Utility functions for notifications
function formatTime(timestamp) {
  const date = new Date(timestamp)
  const now = new Date()
  const diffInMinutes = Math.floor((now - date) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Just now'
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours}h ago`
  
  const diffInDays = Math.floor(diffInHours / 24)
  if (diffInDays < 7) return `${diffInDays}d ago`
  
  return date.toLocaleDateString()
}

function getNotificationIcon(type) {
  const iconMap = {
    'task_assigned': 'bi-person-check',
    'task_updated': 'bi-pencil-square',
    'general': 'bi-info-circle',
    'system': 'bi-gear'
  }
  return iconMap[type] || 'bi-bell'
}

function getNotificationColor(type) {
  const colorMap = {
    'task_assigned': '#10b981', // green
    'task_updated': '#f59e0b',  // amber
    'general': '#3b82f6',       // blue
    'system': '#6b7280'         // gray
  }
  return colorMap[type] || '#3b82f6'
}
</script>

<template>
  <div class="app-layout ms-2">
    <SideNavbar />

    <div class="app-container">
      <div class="header-section">
        <div class="header-content">
          <div class="header-left">
            <h1 class="page-title">Welcome</h1>
            <p class="page-subtitle">Your hub for tasks, schedule, and projects</p>
          </div>
          <div class="header-right">
            <button class="notification-bell" @click="toggleNotificationDropdown">
              <i class="bi bi-bell"></i>
              <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </button>
          </div>
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

        <!-- In-app notifications (if enabled) -->
        <div v-if="userPreferences.in_app" class="tasks-container" style="margin-top: 1rem;">
          <div class="in-app-notifications">
            <div class="notifications-header">
              <h4 class="notifications-title">
                <i class="bi bi-bell-fill me-2"></i>
                New Notifications
              </h4>
            </div>
            
            <!-- Show notifications if they exist -->
            <div v-if="inAppNotifications.length > 0" class="notifications-list">
              <div 
                v-for="notification in inAppNotifications" 
                :key="notification.id"
                class="in-app-notification-item"
              >
                <div class="notification-icon">
                  <i :class="getNotificationIcon(notification.notification_type)" :style="{ color: getNotificationColor(notification.notification_type) }"></i>
                </div>
                <div class="notification-content">
                  <div class="notification-message">{{ notification.notification }}</div>
                  <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                </div>
                <button @click="dismissInAppNotification(notification.id)" class="dismiss-btn">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
            
            <!-- Show "no new notifications" message if no notifications -->
            <div v-else class="no-notifications">
              <div class="no-notifications-content">
                <i class="bi bi-bell-slash"></i>
                <span>No new notifications</span>
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

    <!-- Notification Dropdown -->
    <NotificationDropdown 
      :show="showNotificationDropdown" 
      :userId="userId" 
      @close="closeNotificationDropdown" 
    />
  </div>
</template>

<style scoped>
/* Header modifications */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  width: 100%;
}

.header-left {
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  margin-top: 0.5rem;
}

/* Notification Bell */
.notification-bell {
  position: relative;
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1.2rem;
  color: #6b7280;
}

.notification-bell:hover {
  border-color: #3b82f6;
  color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

/* In-app Notifications */
.in-app-notifications {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #bae6fd;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.notifications-header {
  padding: 1rem 1.25rem;
  background: rgba(59, 130, 246, 0.05);
  border-bottom: 1px solid #bae6fd;
}

.notifications-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1e40af;
  display: flex;
  align-items: center;
}

.notifications-list {
  padding: 0.5rem 0;
}

.in-app-notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  transition: background-color 0.2s ease;
  position: relative;
}

.in-app-notification-item:hover {
  background: rgba(59, 130, 246, 0.05);
}

.in-app-notification-item:not(:last-child) {
  border-bottom: 1px solid rgba(186, 230, 253, 0.5);
}

.notification-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 50%;
  font-size: 0.9rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 0.9rem;
  line-height: 1.4;
  color: #1e40af;
  margin-bottom: 0.25rem;
  font-weight: 500;
}

.notification-time {
  font-size: 0.8rem;
  color: #64748b;
}

.dismiss-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.in-app-notification-item:hover .dismiss-btn {
  opacity: 1;
}

.dismiss-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* No notifications message */
.no-notifications {
  padding: 1.5rem;
  text-align: center;
}

.no-notifications-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  color: #9ca3af;
}

.no-notifications-content i {
  font-size: 2rem;
  opacity: 0.6;
}

.no-notifications-content span {
  font-size: 0.9rem;
  font-weight: 500;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .header-right {
    align-self: flex-end;
    margin-top: 0;
  }
  
  .notification-bell {
    width: 44px;
    height: 44px;
    font-size: 1.1rem;
  }
  
  .in-app-notification-item {
    padding: 0.75rem 1rem;
  }
  
  .dismiss-btn {
    opacity: 1; /* Always show on mobile */
  }
}

@media (max-width: 640px) {
  .notification-bell {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }
  
  .notifications-header {
    padding: 0.75rem 1rem;
  }
  
  .notifications-title {
    font-size: 0.9rem;
  }
}
</style>
