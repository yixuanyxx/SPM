<template>
  <div class="notification-dropdown" v-if="show">
    <div class="dropdown-overlay" @click="$emit('close')"></div>
    <div class="dropdown-content" :class="{ 'mobile': isMobile }">
      <div class="dropdown-header">
        <h4 class="dropdown-title">
          <i class="bi bi-bell me-2"></i>
          Notifications
          <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }}</span>
        </h4>
        <button @click="$emit('close')" class="close-btn">
          <i class="bi bi-x"></i>
        </button>
      </div>

      <div class="dropdown-body">
        <div v-if="loading && notifications.length === 0" class="loading-state">
          <div class="spinner"></div>
          <p>Loading...</p>
        </div>

        <div v-else-if="error" class="error-state">
          <i class="bi bi-exclamation-triangle"></i>
          <p>{{ error }}</p>
        </div>

        <div v-else-if="notifications.length === 0" class="empty-state">
          <i class="bi bi-bell-slash"></i>
          <p>No notifications</p>
        </div>

        <div v-else class="notifications-list">
          <div 
            v-for="notification in recentNotifications" 
            :key="notification.id"
            class="notification-item"
            :class="{ 'unread': !notification.is_read }"
            @click="markAsRead(notification)"
          >
            <div class="notification-icon">
              <i :class="getNotificationIcon(notification.notification_type)" :style="{ color: getNotificationColor(notification.notification_type) }"></i>
            </div>
            
            <div class="notification-content">
              <div class="notification-message">{{ truncateText(notification.notification, 80) }}</div>
              <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
            </div>

            <div v-if="!notification.is_read" class="unread-dot"></div>
          </div>
        </div>
      </div>

      <div v-if="notifications.length > 0" class="dropdown-footer">
        <div class="footer-actions">
          <button v-if="unreadCount > 0" @click="markAllAsRead" class="btn-link">
            Mark all as read
          </button>
          <button @click="viewAll" class="btn-primary">
            View all notifications
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { notificationStore, notificationUtils } from '../services/notifications'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  userId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['close'])

const router = useRouter()
const loading = ref(false)
const error = ref(null)
const isMobile = ref(window.innerWidth <= 640)

const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)
const recentNotifications = computed(() => notifications.value.slice(0, 5))

// Handle window resize
const handleResize = () => {
  isMobile.value = window.innerWidth <= 640
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

watch(() => props.show, async (newShow) => {
  if (newShow && props.userId) {
    await refreshNotifications()
  }
})

async function refreshNotifications() {
  if (!props.userId) return
  
  loading.value = true
  error.value = null
  
  try {
    await notificationStore.refresh(props.userId)
  } catch (err) {
    error.value = err.message || 'Failed to load notifications'
  } finally {
    loading.value = false
  }
}

async function markAsRead(notification) {
  if (!notification.is_read) {
    try {
      await notificationStore.markAsRead(notification.id)
    } catch (err) {
      console.error('Failed to mark as read:', err)
    }
  }
}

async function markAllAsRead() {
  const unreadNotifications = notifications.value.filter(n => !n.is_read)
  
  try {
    await Promise.all(
      unreadNotifications.map(notification => 
        notificationStore.markAsRead(notification.id)
      )
    )
  } catch (err) {
    console.error('Failed to mark all as read:', err)
  }
}

function viewAll() {
  router.push({ name: 'Landing' })
  emit('close')
}

function formatTime(timestamp) {
  return notificationUtils.formatTime(timestamp)
}

function getNotificationIcon(type) {
  return notificationUtils.getNotificationIcon(type)
}

function getNotificationColor(type) {
  return notificationUtils.getNotificationColor(type)
}

function truncateText(text, maxLength) {
  return notificationUtils.truncateText(text, maxLength)
}
</script>

<style scoped>
.notification-dropdown {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 2000;
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}

.dropdown-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
}

.dropdown-content {
  position: relative;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  width: 380px;
  max-height: 500px;
  margin: 80px 2rem 0 auto;
  margin-right: calc(250px + 2rem);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dropdown-content.mobile {
  width: calc(100vw - 2rem);
  max-width: 400px;
  margin: 80px 1rem 0 1rem;
}

.dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}

.dropdown-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #1a1a1a;
}

.unread-badge {
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 0.5rem;
}

.close-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
}

.close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.dropdown-body {
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
}

.notifications-list {
  padding: 0.5rem 0;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  transition: background-color 0.2s ease;
  position: relative;
}

.notification-item:hover {
  background: #fafafa;
}

.notification-item.unread {
  background: #f8faff;
}

.notification-icon {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 0.8rem;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 0.85rem;
  line-height: 1.4;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.75rem;
  color: #6b7280;
}

.unread-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  background: #3b82f6;
  border-radius: 50%;
  margin-top: 0.5rem;
}

.dropdown-footer {
  border-top: 1px solid #f3f4f6;
  padding: 0.75rem 1.25rem;
  background: #fafafa;
}

.footer-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-link:hover {
  background: #f0f9ff;
  color: #1d4ed8;
}

.btn-primary {
  background: #3b82f6;
  border: none;
  color: white;
  font-size: 0.8rem;
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: #2563eb;
}

/* Loading, Error, and Empty States */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1.25rem;
  text-align: center;
}

.loading-state .spinner {
  width: 24px;
  height: 24px;
  border: 2px solid #f3f4f6;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 0.75rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.error-state i,
.empty-state i {
  font-size: 1.5rem;
  color: #9ca3af;
  margin-bottom: 0.75rem;
}

.error-state p,
.empty-state p {
  margin: 0;
  color: #6b7280;
  font-size: 0.85rem;
}

/* Mobile adjustments */
@media (max-width: 640px) {
  .dropdown-content {
    margin: 70px 1rem 0 1rem;
    width: calc(100vw - 2rem);
    max-width: none;
  }
  
  .dropdown-header {
    padding: 0.75rem 1rem;
  }
  
  .dropdown-title {
    font-size: 0.9rem;
  }
  
  .notification-item {
    padding: 0.75rem 1rem;
  }
  
  .footer-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .btn-primary {
    width: 100%;
    text-align: center;
  }
}
</style>
