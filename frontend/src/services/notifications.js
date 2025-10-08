// Notification service for API calls
const NOTIFICATION_API = 'http://127.0.0.1:5006';
const USER_API = 'http://127.0.0.1:5003';

// Helper function for API requests
async function request(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  });
  
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(msg || `HTTP ${res.status}`);
  }
  
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

// Notification API functions
export const notificationService = {
  // Get all notifications for a user
  async getUserNotifications(userId) {
    return await request(`${NOTIFICATION_API}/notifications/user/${userId}`);
  },

  // Get unread notifications for a user
  async getUnreadNotifications(userId) {
    return await request(`${NOTIFICATION_API}/notifications/user/${userId}/unread`);
  },

  // Get unread count for a user
  async getUnreadCount(userId) {
    return await request(`${NOTIFICATION_API}/notifications/user/${userId}/unread-count`);
  },

  // Get a specific notification
  async getNotification(notificationId) {
    return await request(`${NOTIFICATION_API}/notifications/${notificationId}`);
  },

  // Mark notification as read
  async markAsRead(notificationId) {
    return await request(`${NOTIFICATION_API}/notifications/${notificationId}/read`, {
      method: 'PUT'
    });
  },

  // Mark notification as unread
  async markAsUnread(notificationId) {
    return await request(`${NOTIFICATION_API}/notifications/${notificationId}/unread`, {
      method: 'PUT'
    });
  },

  // Delete a notification
  async deleteNotification(notificationId) {
    return await request(`${NOTIFICATION_API}/notifications/${notificationId}`, {
      method: 'DELETE'
    });
  },

  // Create a notification (mainly for testing)
  async createNotification(notificationData) {
    return await request(`${NOTIFICATION_API}/notifications/create`, {
      method: 'POST',
      body: JSON.stringify(notificationData)
    });
  }
};

// User preferences API functions
export const userPreferencesService = {
  // Update notification preferences
  async updateNotificationPreferences(userId, preferences) {
    return await request(`${USER_API}/users/${userId}/notification-preferences`, {
      method: 'PUT',
      body: JSON.stringify(preferences)
    });
  },

  // Get user data (includes notification preferences)
  async getUserData(userId) {
    return await request(`${USER_API}/users/${userId}`);
  }
};

// Utility functions for notification formatting
export const notificationUtils = {
  // Format notification time
  formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInMinutes = Math.floor((now - date) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return date.toLocaleDateString();
  },

  // Get notification icon based on type
  getNotificationIcon(type) {
    const iconMap = {
      'task_assigned': 'bi-person-check',
      'task_updated': 'bi-pencil-square',
      'general': 'bi-info-circle',
      'system': 'bi-gear'
    };
    return iconMap[type] || 'bi-bell';
  },

  // Get notification color based on type
  getNotificationColor(type) {
    const colorMap = {
      'task_assigned': '#10b981', // green
      'task_updated': '#f59e0b',  // amber
      'general': '#3b82f6',       // blue
      'system': '#6b7280'         // gray
    };
    return colorMap[type] || '#3b82f6';
  },

  // Truncate notification text
  truncateText(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  }
};

// Reactive notification store (simple state management)
export const notificationStore = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,

  // Initialize store with user notifications
  async init(userId) {
    if (!userId) return;
    
    this.loading = true;
    this.error = null;
    
    try {
      const [notificationsRes, unreadCountRes] = await Promise.all([
        notificationService.getUserNotifications(userId),
        notificationService.getUnreadCount(userId)
      ]);
      
      this.notifications = notificationsRes.data || [];
      this.unreadCount = unreadCountRes.data?.unread_count || 0;
    } catch (error) {
      console.error('Failed to initialize notification store:', error);
      this.error = error.message;
      this.notifications = [];
      this.unreadCount = 0;
    } finally {
      this.loading = false;
    }
  },

  // Refresh notifications
  async refresh(userId) {
    await this.init(userId);
  },

  // Mark notification as read and update store
  async markAsRead(notificationId) {
    try {
      await notificationService.markAsRead(notificationId);
      
      // Update local state
      const notification = this.notifications.find(n => n.id === notificationId);
      if (notification && !notification.is_read) {
        notification.is_read = true;
        this.unreadCount = Math.max(0, this.unreadCount - 1);
      }
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
      throw error;
    }
  },

  // Mark notification as unread and update store
  async markAsUnread(notificationId) {
    try {
      await notificationService.markAsUnread(notificationId);
      
      // Update local state
      const notification = this.notifications.find(n => n.id === notificationId);
      if (notification && notification.is_read) {
        notification.is_read = false;
        this.unreadCount += 1;
      }
    } catch (error) {
      console.error('Failed to mark notification as unread:', error);
      throw error;
    }
  },

  // Delete notification and update store
  async deleteNotification(notificationId) {
    try {
      await notificationService.deleteNotification(notificationId);
      
      // Update local state
      const index = this.notifications.findIndex(n => n.id === notificationId);
      if (index > -1) {
        const notification = this.notifications[index];
        if (!notification.is_read) {
          this.unreadCount = Math.max(0, this.unreadCount - 1);
        }
        this.notifications.splice(index, 1);
      }
    } catch (error) {
      console.error('Failed to delete notification:', error);
      throw error;
    }
  }
};

// Enhanced notification service that respects user preferences
export const enhancedNotificationService = {
  // Send notification based on user preferences
  async sendNotificationWithPreferences(userId, notificationData) {
    try {
      // Get user preferences
      const userData = await userPreferencesService.getUserData(userId);
      const preferences = userData?.data?.notification_preferences || { in_app: true, email: true };
      
      const results = [];
      
      // Send in-app notification if enabled
      if (preferences.in_app) {
        const inAppResult = await notificationService.createNotification({
          userid: userId,
          notification: notificationData.message,
          notification_type: notificationData.type || 'general',
          related_task_id: notificationData.related_task_id || null
        });
        results.push({ type: 'in_app', result: inAppResult });
        
        // Update local store if initialized
        if (notificationStore.notifications.length > 0) {
          await notificationStore.refresh(userId);
        }
      }
      
      // Send email notification if enabled
      if (preferences.email && userData?.data?.email) {
        // This would be handled by the backend notification trigger service
        // The frontend doesn't directly send emails
        results.push({ type: 'email', result: { status: 200, message: 'Email will be sent by backend' } });
      }
      
      return { status: 200, message: 'Notifications sent based on preferences', results };
    } catch (error) {
      console.error('Failed to send notification with preferences:', error);
      throw error;
    }
  },

  // Trigger task assignment notification
  async triggerTaskAssignmentNotification(taskId, assignedUserId, assignerName = 'System') {
    try {
      const response = await fetch('http://127.0.0.1:5006/notifications/triggers/task-assignment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: taskId,
          assigned_user_id: assignedUserId,
          assigner_name: assignerName
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to trigger task assignment notification:', error);
      throw error;
    }
  },

  // Trigger task ownership transfer notification
  async triggerTaskOwnershipTransferNotification(taskId, newOwnerId, previousOwnerName = 'System') {
    try {
      const response = await fetch('http://127.0.0.1:5006/notifications/triggers/task-ownership-transfer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          task_id: taskId,
          new_owner_id: newOwnerId,
          previous_owner_name: previousOwnerName
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to trigger task ownership transfer notification:', error);
      throw error;
    }
  },

  // Trigger task update notification
  async triggerTaskUpdateNotification(taskId, userIds, updateType, oldValue, newValue, updaterName = 'System') {
    try {
      let endpoint = '';
      let payload = {
        task_id: taskId,
        user_ids: userIds,
        updater_name: updaterName
      };

      switch (updateType) {
        case 'status':
          endpoint = 'task-status-change';
          payload.old_status = oldValue;
          payload.new_status = newValue;
          break;
        case 'due_date':
          endpoint = 'task-due-date-change';
          payload.old_due_date = oldValue;
          payload.new_due_date = newValue;
          break;
        case 'description':
          endpoint = 'task-description-change';
          break;
        default:
          throw new Error(`Unknown update type: ${updateType}`);
      }

      const response = await fetch(`http://127.0.0.1:5006/notifications/triggers/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Failed to trigger task update notification:', error);
      throw error;
    }
  }
};
