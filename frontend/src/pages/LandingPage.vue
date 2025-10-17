<!-- dummy sample, can change name later, this can be home page w all the user's tasks instead, just rmb to change all the names in router/index.js -->
<!-- idk how yall do it, mayb instead of this we can have one folder for one page then put one vue file and one css file in each folder -->

 <script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../components/SideNavbar.vue'
import { sessionState } from '../services/session'
import { logout } from '../services/auth'
import { notificationStore, userPreferencesService } from '../services/notifications'
import './taskview/taskview.css'

const router = useRouter()
const now = ref(new Date())
const loading = ref(false)
const userId = localStorage.getItem('spm_userid')
const API_TASKS = 'http://localhost:5002'
const API_USERS = 'http://127.0.0.1:5003'
const userName = ref('')
const userPreferences = ref({ in_app: true, email: true })

const notifications = computed(() => notificationStore.notifications)
const recentNotifications = computed(() => notifications.value.slice(0, 5)) // Show up to 5 notifications
const expandedNotifications = ref([])
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
    fetchUserName()
    await initializeNotifications()
    // Also load notifications immediately to ensure they're available
    await loadNotifications()
  }
})

async function onLogout() {
  try {
    console.log('Logging out...');
    await logout();
    console.log('Logout successful, redirecting to login...');
    // Force navigation to login page
    await router.push({ name: 'Login' });
    // Force reload to ensure clean state
    window.location.href = '/login';
  } catch (error) {
    console.error('Logout failed:', error);
    // Still redirect to login even if logout fails
    await router.push({ name: 'Login' });
    window.location.href = '/login';
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

async function loadNotifications() {
  try {
    loading.value = true
    await notificationStore.refresh(userId)
  } catch (error) {
    console.error('Failed to load notifications:', error)
  } finally {
    loading.value = false
  }
}

async function initializeNotifications() {
  try {
    // Initialize notification store
    await notificationStore.init(userId)
    
    // Get user preferences
    const userData = await userPreferencesService.getUserData(userId)
    userPreferences.value = userData?.data?.notification_preferences || { in_app: true, email: true }
    
    // Set up periodic refresh for notifications (every 30 seconds)
    setInterval(async () => {
      try {
        await notificationStore.refresh(userId)
      } catch (error) {
        console.error('Failed to refresh notifications:', error)
      }
    }, 30000)
    
  } catch (error) {
    console.error('Failed to initialize notifications:', error)
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

function truncateText(text, maxLength = 100) {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

async function markAsRead(notification) {
  try {
    await notificationStore.markAsRead(notification.id)
  } catch (error) {
    console.error('Failed to mark notification as read:', error)
  }
}

function toggleNotificationDetails(notification) {
  const index = expandedNotifications.value.indexOf(notification.id)
  if (index > -1) {
    expandedNotifications.value.splice(index, 1)
  } else {
    expandedNotifications.value.push(notification.id)
    // Auto-mark as read when banner is opened
    if (!notification.is_read) {
      markAsRead(notification)
    }
  }
}

function formatNotificationText(text) {
  // Convert markdown-style bold (**text**) to HTML bold
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
}

function getNotificationTitle(notification) {
  // Extract title from notification content
  const content = notification.notification
  if (content.includes('Task Update Summary')) {
    return 'Task Updated'
  } else if (content.includes('assigned')) {
    return 'Task Assigned'
  } else if (content.includes('transferred')) {
    return 'Task Ownership Transferred'
  }
  return 'Notification'
}

function viewAllNotifications() {
  // Navigate to a dedicated notifications page or show all notifications
  // For now, we'll just show all notifications in the current view
  console.log('View all notifications clicked')
  // You can implement navigation to a dedicated notifications page here
  // this.$router.push('/notifications')
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


        <!-- Latest Notifications -->
        <div class="tasks-container" style="margin-top: 1rem;">
          <div class="notifications-header">
            <h3 class="notifications-heading">Latest Notifications</h3>
            <button v-if="notifications.length > 5" class="view-all-btn" @click="viewAllNotifications">
              <i class="bi bi-list-ul"></i> View All Notifications
            </button>
          </div>
          <div v-if="loading" class="empty-state" style="padding: 1rem;">
            <p class="empty-subtitle">Loading notifications…</p>
          </div>
          <div v-else>
            <div v-if="notifications.length === 0" class="empty-state" style="padding: 1rem;">
              <p class="empty-subtitle">No notifications yet.</p>
            </div>
            <div v-else>
              <div 
                v-for="notification in recentNotifications" 
                :key="notification.id"
                class="notification-banner"
                :class="{ 'unread': !notification.is_read, 'expanded': expandedNotifications.includes(notification.id) }"
                @click="toggleNotificationDetails(notification)"
              >
                <div class="notification-header">
                  <div class="notification-icon">
                    <i :class="getNotificationIcon(notification.notification_type)" :style="{ color: getNotificationColor(notification.notification_type) }"></i>
                  </div>
                  
                  <div class="notification-summary">
                    <div class="notification-title">{{ getNotificationTitle(notification) }}</div>
                    <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                  </div>

                  <div class="notification-actions">
                    <div v-if="!notification.is_read" class="unread-dot"></div>
                    <div class="expand-icon">
                      <i :class="expandedNotifications.includes(notification.id) ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
                    </div>
                  </div>
                </div>

                <div v-if="expandedNotifications.includes(notification.id)" class="notification-details">
                  <div class="notification-content">
                    <div class="notification-text" v-html="formatNotificationText(notification.notification)"></div>
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

/* Notifications Header */
.notifications-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.notifications-heading {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  letter-spacing: -0.025em;
}

.view-all-btn {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.view-all-btn:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.view-all-btn i {
  font-size: 0.8rem;
}
.notification-banner {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.notification-banner.unread:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.notification-banner.unread {
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
}

.notification-banner.expanded {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.notification-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  gap: 0.75rem;
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

.notification-summary {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.8rem;
  color: #6b7280;
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
}

.expand-icon {
  color: #6b7280;
  font-size: 0.8rem;
  transition: transform 0.2s ease;
}

.notification-banner.expanded .expand-icon {
  transform: rotate(180deg);
}

.notification-details {
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: 1rem;
}

.notification-content {
  margin-bottom: 0;
}

.notification-text {
  font-family: inherit;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
  margin: 0;
  background: white;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.notification-text strong {
  color: #1f2937;
  font-weight: 700;
}


/* Mobile responsiveness */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .notification-banner {
    margin-bottom: 0.5rem;
  }
  
  .notification-header {
    padding: 0.75rem;
  }
  
  .notification-details {
    padding: 0.75rem;
  }
}
</style>
