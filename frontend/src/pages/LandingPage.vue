<!-- dummy sample, can change name later, this can be home page w all the user's tasks instead, just rmb to change all the names in router/index.js -->
<!-- idk how yall do it, mayb instead of this we can have one folder for one page then put one vue file and one css file in each folder -->

 <script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../components/SideNavbar.vue'
import { sessionState } from '../services/session'
import { logout } from '../services/auth'
import { notificationStore, userPreferencesService, notificationUtils } from '../services/notifications'
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
const showNotificationsPopup = ref(false)
const notificationsFilter = ref('all')
const notificationsSortBy = ref('newest')
const expandedPopupNotifications = ref([])
const greeting = computed(() => {
  const hour = now.value.getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

// Computed properties for popup notifications
const unreadCount = computed(() => notificationStore.unreadCount)
const totalCount = computed(() => notifications.value.length)
const readCount = computed(() => totalCount.value - unreadCount.value)

const filteredAndSortedNotifications = computed(() => {
  let filtered = notifications.value

  // Apply filter
  if (notificationsFilter.value === 'unread') {
    filtered = filtered.filter(n => !n.is_read)
  } else if (notificationsFilter.value === 'read') {
    filtered = filtered.filter(n => n.is_read)
  }

  // Apply sorting
  filtered = [...filtered].sort((a, b) => {
    const dateA = new Date(a.created_at)
    const dateB = new Date(b.created_at)
    
    if (notificationsSortBy.value === 'newest') {
      return dateB - dateA
    } else {
      return dateA - dateB
    }
  })

  return filtered
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
  // Use the notification utilities function for consistent title handling
  return notificationUtils.getNotificationTitle(notification)
}

function viewAllNotifications() {
  // Show the notifications popup modal
  showNotificationsPopup.value = true
}

function closeNotificationsPopup() {
  showNotificationsPopup.value = false
  expandedPopupNotifications.value = []
}

function togglePopupNotificationDetails(notification) {
  const index = expandedPopupNotifications.value.indexOf(notification.id)
  if (index > -1) {
    // Notification is being collapsed - mark as read now
    expandedPopupNotifications.value.splice(index, 1)
    if (!notification.is_read) {
      markAsRead(notification)
    }
  } else {
    // Notification is being expanded - don't mark as read yet
    expandedPopupNotifications.value.push(notification.id)
  }
}

async function markAsUnread(notification) {
  try {
    await notificationStore.markAsUnread(notification.id)
  } catch (error) {
    console.error('Failed to mark notification as unread:', error)
  }
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
            <button class="view-all-btn" @click="viewAllNotifications">
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

    <!-- Notifications Popup Modal -->
    <div v-if="showNotificationsPopup" class="notifications-popup-overlay" @click="closeNotificationsPopup">
      <div class="notifications-popup-modal" @click.stop>
        <!-- Popup Header -->
        <div class="popup-header">
          <div class="popup-title-section">
            <h2 class="popup-title">All Notifications</h2>
            <p class="popup-subtitle">View and manage all your notifications</p>
          </div>
          <button @click="closeNotificationsPopup" class="popup-close-btn">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <!-- Popup Content -->
        <div class="popup-content">
          <!-- Empty State -->
          <div v-if="notifications.length === 0" class="popup-empty-state">
            <div class="popup-empty-icon">
              <i class="bi bi-bell-slash"></i>
            </div>
            <h3>No notifications yet</h3>
            <p>You'll see notifications here when tasks are updated, assigned, or when you're added as a collaborator.</p>
          </div>

          <!-- Notifications List -->
          <div v-else class="popup-notifications-list">
            <!-- Filter and Sort Controls -->
            <div class="popup-controls">
              <div class="popup-filter-controls">
                <button 
                  @click="notificationsFilter = 'all'" 
                  :class="{ active: notificationsFilter === 'all' }"
                  class="popup-filter-btn"
                >
                  All ({{ totalCount }})
                </button>
                <button 
                  @click="notificationsFilter = 'unread'" 
                  :class="{ active: notificationsFilter === 'unread' }"
                  class="popup-filter-btn"
                >
                  Unread ({{ unreadCount }})
                </button>
                <button 
                  @click="notificationsFilter = 'read'" 
                  :class="{ active: notificationsFilter === 'read' }"
                  class="popup-filter-btn"
                >
                  Read ({{ readCount }})
                </button>
              </div>
              
              <div class="popup-sort-controls">
                <label for="popup-sort-select">Sort by:</label>
                <select id="popup-sort-select" v-model="notificationsSortBy" class="popup-sort-select">
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                </select>
              </div>
            </div>

            <!-- Notifications -->
            <div class="popup-notifications-grid">
              <div 
                v-for="notification in filteredAndSortedNotifications" 
                :key="notification.id"
                class="popup-notification-card"
                :class="{ 'unread': !notification.is_read, 'expanded': expandedPopupNotifications.includes(notification.id) }"
                @click="togglePopupNotificationDetails(notification)"
              >
                <div class="popup-notification-header">
                  <div class="popup-notification-icon">
                    <i :class="getNotificationIcon(notification.notification_type)" :style="{ color: getNotificationColor(notification.notification_type) }"></i>
                  </div>
                  
                  <div class="popup-notification-summary">
                    <div class="popup-notification-title">{{ getNotificationTitle(notification) }}</div>
                    <div class="popup-notification-time">{{ formatTime(notification.created_at) }}</div>
                  </div>

                  <div class="popup-notification-actions">
                    <div v-if="!notification.is_read" class="popup-unread-dot"></div>
                    <div class="popup-expand-icon">
                      <i :class="expandedPopupNotifications.includes(notification.id) ? 'bi bi-chevron-up' : 'bi bi-chevron-down'"></i>
                    </div>
                  </div>
                </div>

                <div v-if="expandedPopupNotifications.includes(notification.id)" class="popup-notification-details">
                  <div class="popup-notification-content">
                    <div class="popup-notification-text" v-html="formatNotificationText(notification.notification)"></div>
                  </div>
                  
                  <div class="popup-notification-footer">
                    <button 
                      v-if="!notification.is_read" 
                      @click.stop="markAsRead(notification)"
                      class="popup-mark-read-btn"
                    >
                      <i class="bi bi-check"></i>
                      Mark as Read
                    </button>
                    <button 
                      v-else 
                      @click.stop="markAsUnread(notification)"
                      class="popup-mark-unread-btn"
                    >
                      <i class="bi bi-arrow-counterclockwise"></i>
                      Mark as Unread
                    </button>
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

/* Notifications Popup Modal Styles */
.notifications-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.notifications-popup-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.popup-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.popup-title-section {
  flex: 1;
}

.popup-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 0.25rem 0;
}

.popup-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.popup-close-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.popup-close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.popup-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

.popup-empty-state {
  padding: 3rem 1.5rem;
  text-align: center;
}

.popup-empty-icon {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.popup-empty-state h3 {
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.popup-empty-state p {
  color: #6b7280;
  max-width: 400px;
  margin: 0 auto;
}

.popup-notifications-list {
  padding: 1.5rem;
}

.popup-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.popup-filter-controls {
  display: flex;
  gap: 0.5rem;
}

.popup-filter-btn {
  background: white;
  border: 1px solid #d1d5db;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s ease;
  color: black;
}

.popup-filter-btn:hover {
  background: #f3f4f6;
  border-color: #9ca3af;
  color: black;
}

.popup-filter-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
}

.popup-sort-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.popup-sort-controls label {
  font-size: 0.875rem;
  color: #374151;
}

.popup-sort-select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 0.5rem;
  font-size: 0.875rem;
  background: white;
}

.popup-notifications-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.popup-notification-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  overflow: hidden;
}

.popup-notification-card.unread:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.popup-notification-card.unread {
  background: #f8fafc;
  border-left: 4px solid #3b82f6;
}

.popup-notification-card.expanded {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.popup-notification-header {
  display: flex;
  align-items: center;
  padding: 1rem;
  gap: 0.75rem;
}

.popup-notification-icon {
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

.popup-notification-summary {
  flex: 1;
  min-width: 0;
}

.popup-notification-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.25rem;
}

.popup-notification-time {
  font-size: 0.8rem;
  color: #6b7280;
}

.popup-notification-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.popup-unread-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
  border-radius: 50%;
}

.popup-expand-icon {
  color: #6b7280;
  font-size: 0.8rem;
  transition: transform 0.2s ease;
}

.popup-notification-card.expanded .popup-expand-icon {
  transform: rotate(180deg);
}

.popup-notification-details {
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: 1rem;
}

.popup-notification-content {
  margin-bottom: 1rem;
}

.popup-notification-text {
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

.popup-notification-text strong {
  color: #1f2937;
  font-weight: 700;
}

.popup-notification-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.popup-mark-read-btn, .popup-mark-unread-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  transition: background 0.2s ease;
}

.popup-mark-read-btn:hover {
  background: #059669;
}

.popup-mark-unread-btn {
  background: #6b7280;
}

.popup-mark-unread-btn:hover {
  background: #4b5563;
}

/* Mobile responsiveness for popup */
@media (max-width: 768px) {
  .notifications-popup-modal {
    margin: 0.5rem;
    max-height: 95vh;
  }
  
  .popup-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .popup-controls {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .popup-filter-controls {
    justify-content: center;
  }
  
  .popup-sort-controls {
    justify-content: center;
  }
  
  .popup-notification-header {
    padding: 0.75rem;
  }
  
  .popup-notification-details {
    padding: 0.75rem;
  }
}
</style>
