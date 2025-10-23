<template>
  <div class="notifications-container">
    <div class="notifications-header">
      <h3 class="notifications-title">
        <i class="bi bi-bell me-2"></i>
        Notifications
        <span v-if="unreadCount > 0" class="unread-badge">{{ unreadCount }}</span>
      </h3>
      <div class="notifications-actions">
        <button 
          v-if="unreadCount > 0" 
          @click="markAllAsRead" 
          class="btn-link"
          :disabled="loading"
        >
          Mark all as read
        </button>
        <button @click="refreshNotifications" class="btn-refresh" :disabled="loading">
          <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
        </button>
      </div>
    </div>

    <div v-if="loading && notifications.length === 0" class="loading-state">
      <div class="spinner"></div>
      <p>Loading notifications...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <i class="bi bi-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="refreshNotifications" class="secondary-button">Try Again</button>
    </div>

    <div v-else-if="notifications.length === 0" class="empty-state">
      <i class="bi bi-bell-slash"></i>
      <h4>No notifications yet</h4>
      <p>You'll see notifications here when you receive them.</p>
    </div>

    <div v-else class="notifications-list">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        class="notification-item"
        :class="{ 'unread': !notification.is_read }"
      >
        <div class="notification-icon">
          <i :class="getNotificationIcon(notification.notification_type)" :style="{ color: getNotificationColor(notification.notification_type) }"></i>
        </div>
        
        <div class="notification-content">
          <div class="notification-message">{{ notification.notification }}</div>
          <div class="notification-meta">
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
            <span v-if="notification.notification_type !== 'general'" class="notification-type">
              {{ formatNotificationType(notification.notification_type) }}
            </span>
          </div>
        </div>

        <div class="notification-actions">
          <button 
            @click="toggleReadStatus(notification)"
            class="btn-action"
            :title="notification.is_read ? 'Mark as unread' : 'Mark as read'"
          >
            <i :class="notification.is_read ? 'bi-envelope' : 'bi-envelope-open'"></i>
          </button>
          <button 
            @click="deleteNotification(notification.id)"
            class="btn-action btn-delete"
            title="Delete notification"
          >
            <i class="bi bi-trash"></i>
          </button>
        </div>
      </div>
    </div>

    <div v-if="notifications.length > 0" class="notifications-footer">
      <p class="text-muted">{{ notifications.length }} notification{{ notifications.length !== 1 ? 's' : '' }} total</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { notificationStore, notificationUtils } from '../services/notifications'

const props = defineProps({
  userId: {
    type: [String, Number],
    required: true
  },
  maxHeight: {
    type: String,
    default: '400px'
  }
})

const loading = ref(false)
const error = ref(null)

const notifications = computed(() => notificationStore.notifications)
const unreadCount = computed(() => notificationStore.unreadCount)

onMounted(async () => {
  if (props.userId) {
    await refreshNotifications()
  }
})

watch(() => props.userId, async (newUserId) => {
  if (newUserId) {
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

async function toggleReadStatus(notification) {
  try {
    if (notification.is_read) {
      await notificationStore.markAsUnread(notification.id)
    } else {
      await notificationStore.markAsRead(notification.id)
    }
  } catch (err) {
    console.error('Failed to toggle read status:', err)
  }
}

async function deleteNotification(notificationId) {
  if (!confirm('Are you sure you want to delete this notification?')) return
  
  try {
    await notificationStore.deleteNotification(notificationId)
  } catch (err) {
    console.error('Failed to delete notification:', err)
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

function formatTime(timestamp) {
  return notificationUtils.formatTime(timestamp)
}

function getNotificationIcon(type) {
  return notificationUtils.getNotificationIcon(type)
}

function getNotificationColor(type) {
  return notificationUtils.getNotificationColor(type)
}

function formatNotificationType(type) {
  return notificationUtils.formatNotificationType(type)
}
</script>

<style scoped>
.notifications-container {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.notifications-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}

.notifications-title {
  display: flex;
  align-items: center;
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
}

.unread-badge {
  background: #ef4444;
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  margin-left: 0.5rem;
}

.notifications-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-link:hover:not(:disabled) {
  background: #f0f9ff;
  color: #1d4ed8;
}

.btn-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 1rem;
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

.btn-refresh:hover:not(:disabled) {
  background: #f3f4f6;
  color: #374151;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.notifications-list {
  max-height: v-bind(maxHeight);
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s ease;
}

.notification-item:hover {
  background: #fafafa;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item.unread {
  background: #f8faff;
  border-left: 3px solid #3b82f6;
}

.notification-icon {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f3f4f6;
  border-radius: 50%;
  font-size: 0.9rem;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 0.9rem;
  line-height: 1.4;
  color: #1a1a1a;
  margin-bottom: 0.25rem;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.notification-type {
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.notification-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.notification-item:hover .notification-actions {
  opacity: 1;
}

.btn-action {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
}

.btn-action:hover {
  background: #f3f4f6;
  color: #374151;
}

.btn-delete:hover {
  background: #fef2f2;
  color: #dc2626;
}

.notifications-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #f3f4f6;
  background: #fafafa;
  text-align: center;
}

.text-muted {
  color: #6b7280;
  font-size: 0.8rem;
  margin: 0;
}

/* Loading, Error, and Empty States */
.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1.25rem;
  text-align: center;
}

.loading-state .spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

.error-state i,
.empty-state i {
  font-size: 2rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.error-state h4,
.empty-state h4 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1.1rem;
}

.error-state p,
.empty-state p {
  margin: 0 0 1rem 0;
  color: #6b7280;
  font-size: 0.9rem;
}

.secondary-button {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-button:hover {
  background: #e5e7eb;
  border-color: #9ca3af;
}

/* Responsive */
@media (max-width: 640px) {
  .notifications-header {
    padding: 0.75rem 1rem;
  }
  
  .notifications-title {
    font-size: 1rem;
  }
  
  .notification-item {
    padding: 0.75rem 1rem;
  }
  
  .notification-actions {
    opacity: 1; /* Always show on mobile */
  }
}
</style>
