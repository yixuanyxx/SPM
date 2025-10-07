// Task notification utilities
// This file provides helper functions to trigger notifications when tasks are assigned or updated

import { enhancedNotificationService } from '../services/notifications'

/**
 * Trigger notification when a task is assigned to a user
 * @param {number} taskId - The ID of the task
 * @param {number} assignedUserId - The ID of the user assigned to the task
 * @param {string} assignerName - The name of the person assigning the task
 * @param {string} taskName - The name of the task (optional, for better UX)
 */
export async function notifyTaskAssignment(taskId, assignedUserId, assignerName, taskName = '') {
  try {
    console.log(`Triggering task assignment notification: Task ${taskId} assigned to user ${assignedUserId} by ${assignerName}`)
    
    const result = await enhancedNotificationService.triggerTaskAssignmentNotification(
      taskId, 
      assignedUserId, 
      assignerName
    )
    
    console.log('Task assignment notification sent:', result)
    return result
  } catch (error) {
    console.error('Failed to send task assignment notification:', error)
    // Don't throw error to avoid breaking the main task assignment flow
    return { status: 500, error: error.message }
  }
}

/**
 * Trigger notification when a task status is updated
 * @param {number} taskId - The ID of the task
 * @param {number[]} collaboratorIds - Array of user IDs to notify (task collaborators)
 * @param {string} oldStatus - The previous status
 * @param {string} newStatus - The new status
 * @param {string} updaterName - The name of the person updating the task
 */
export async function notifyTaskStatusUpdate(taskId, collaboratorIds, oldStatus, newStatus, updaterName) {
  try {
    console.log(`Triggering task status update notification: Task ${taskId} status changed from ${oldStatus} to ${newStatus} by ${updaterName}`)
    
    const result = await enhancedNotificationService.triggerTaskUpdateNotification(
      taskId,
      collaboratorIds,
      'status',
      oldStatus,
      newStatus,
      updaterName
    )
    
    console.log('Task status update notification sent:', result)
    return result
  } catch (error) {
    console.error('Failed to send task status update notification:', error)
    return { status: 500, error: error.message }
  }
}

/**
 * Trigger notification when a task due date is updated
 * @param {number} taskId - The ID of the task
 * @param {number[]} collaboratorIds - Array of user IDs to notify (task collaborators)
 * @param {string} oldDueDate - The previous due date
 * @param {string} newDueDate - The new due date
 * @param {string} updaterName - The name of the person updating the task
 */
export async function notifyTaskDueDateUpdate(taskId, collaboratorIds, oldDueDate, newDueDate, updaterName) {
  try {
    console.log(`Triggering task due date update notification: Task ${taskId} due date changed from ${oldDueDate} to ${newDueDate} by ${updaterName}`)
    
    const result = await enhancedNotificationService.triggerTaskUpdateNotification(
      taskId,
      collaboratorIds,
      'due_date',
      oldDueDate,
      newDueDate,
      updaterName
    )
    
    console.log('Task due date update notification sent:', result)
    return result
  } catch (error) {
    console.error('Failed to send task due date update notification:', error)
    return { status: 500, error: error.message }
  }
}

/**
 * Trigger notification when a task description is updated
 * @param {number} taskId - The ID of the task
 * @param {number[]} collaboratorIds - Array of user IDs to notify (task collaborators)
 * @param {string} updaterName - The name of the person updating the task
 */
export async function notifyTaskDescriptionUpdate(taskId, collaboratorIds, updaterName) {
  try {
    console.log(`Triggering task description update notification: Task ${taskId} description updated by ${updaterName}`)
    
    const result = await enhancedNotificationService.triggerTaskUpdateNotification(
      taskId,
      collaboratorIds,
      'description',
      null,
      null,
      updaterName
    )
    
    console.log('Task description update notification sent:', result)
    return result
  } catch (error) {
    console.error('Failed to send task description update notification:', error)
    return { status: 500, error: error.message }
  }
}

/**
 * Example usage in a task component:
 * 
 * import { notifyTaskAssignment, notifyTaskStatusUpdate } from '@/utils/taskNotifications'
 * 
 * // When assigning a task
 * async function assignTask(taskId, userId) {
 *   // ... your task assignment logic ...
 *   
 *   // Trigger notification
 *   await notifyTaskAssignment(taskId, userId, currentUserName, taskName)
 * }
 * 
 * // When updating task status
 * async function updateTaskStatus(taskId, newStatus) {
 *   const oldStatus = task.status
 *   
 *   // ... your task update logic ...
 *   
 *   // Trigger notification to all collaborators
 *   await notifyTaskStatusUpdate(taskId, task.collaborators, oldStatus, newStatus, currentUserName)
 * }
 */
