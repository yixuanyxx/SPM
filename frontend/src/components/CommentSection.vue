<template>
  <div class="comments-section">
    <!-- Comments Header -->
    <div class="comments-header">
      <h3 class="comments-title">
        <i class="bi bi-chat-dots"></i>
        {{ comments.length }} {{ comments.length === 1 ? 'Comment' : 'Comments' }}
      </h3>
    </div>

    <!-- Add Comment Form -->
    <div class="add-comment-container">
      <img 
        :src="getUserAvatar(currentUserId)" 
        :alt="getCurrentUserName()"
        class="user-avatar-small"
      />
      <div class="comment-input-wrapper">
        <div class="mention-input-container">
          <input
            ref="commentInput"
            v-model="newComment"
            type="text"
            placeholder="Add a comment... (use @ to mention users)"
            class="comment-input"
            @focus="showCommentForm = true"
            @input="handleInput"
            @keydown="handleKeydown"
            :class="{ 'input-focused': showCommentForm }"
          />
          <!-- Mention suggestions dropdown -->
          <div 
            v-if="showMentionSuggestions && mentionSuggestions.length > 0"
            class="mention-suggestions"
          >
            <div 
              v-for="(user, index) in mentionSuggestions"
              :key="user.userid"
              @click="selectMention(user)"
              :class="['mention-suggestion', { active: selectedMentionIndex === index }]"
            >
              <img 
                :src="getUserAvatar(user.userid, user.name)" 
                :alt="user.name"
                class="mention-avatar"
              />
              <div class="mention-info">
                <div class="mention-name">{{ user.name }}</div>
                <div class="mention-username">@{{ user.username }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-if="showCommentForm" class="comment-form-actions">
          <button 
            @click="cancelComment"
            class="btn-cancel"
          >
            Cancel
          </button>
          <button 
            @click="submitComment"
            :disabled="!newComment.trim() || isSubmitting"
            class="btn-comment"
          >
            {{ isSubmitting ? 'Posting...' : 'Comment' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Comments List -->
    <div class="comments-list">
      <div 
        v-for="comment in comments" 
        :key="comment.id"
        class="comment-thread"
      >
        <!-- Main Comment -->
        <div class="comment">
          <img 
            :src="getUserAvatar(comment.user_id, comment.user_name)" 
            :alt="comment.user_name"
            class="comment-avatar"
          />
          
          <div class="comment-body">
            <div class="comment-content">
              <div class="comment-header">
                <span class="comment-author">{{ comment.user_name }}</span>
                <span class="comment-role" v-if="comment.user_role">
                  {{ capitalizeRole(comment.user_role) }}
                </span>
                <span class="comment-timestamp">{{ formatCommentTime(comment.created_at) }}</span>
                <span class="comment-edited" v-if="isCommentEdited(comment)">
                  (edited)
                </span>
              </div>

              <div class="comment-text-container">
                <p class="comment-text" v-html="formatCommentText(comment.content)"></p>
              </div>
            </div>

            <div class="action-menu">
              <button 
                v-if="canEditComment(comment.user_id)"
                @click="editComment(comment)"
                class="menu-btn"
                title="Edit"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button 
                v-if="canDeleteComment(comment.user_id)"
                @click="deleteComment(comment.id)"
                class="menu-btn delete"
                title="Delete"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Comments State -->
    <div v-if="comments.length === 0 && !isLoading" class="no-comments">
      <i class="bi bi-chat-left"></i>
      <p>No comments yet. Be the first to comment!</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <p>Loading comments...</p>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteConfirm" class="dialog-overlay">
      <div class="dialog-container">
        <div class="dialog-content">
          <div class="dialog-header">
            <i class="bi bi-exclamation-triangle-fill warning-icon"></i>
            <h4>Delete Comment</h4>
          </div>
          <p>Are you sure you want to delete this comment? This action cannot be undone.</p>
          <div class="dialog-actions">
            <button 
              class="btn-secondary"
              @click="cancelDelete"
            >
              Cancel
            </button>
            <button 
              class="btn-danger"
              @click="confirmDelete"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { getCurrentUserData } from '../services/session.js'

const props = defineProps({
  taskId: {
    type: [String, Number],
    required: true
  },
  taskOwnerId: {
    type: [String, Number],
    required: true
  }
})

const emit = defineEmits(['comments-updated'])

// Configuration
const COMMENTS_API_URL = import.meta.env.VITE_COMMENTS_API_URL || 'http://localhost:5008'
const USERS_API_URL = import.meta.env.VITE_USERS_API_URL || 'http://localhost:5003'

// User data
const userData = getCurrentUserData()
const currentUserId = ref(parseInt(userData.userid) || null)
const currentUserRole = ref(userData.role?.toLowerCase() || '')
const currentUserEmail = ref(userData.email || '')

// State
const comments = ref([])
const users = ref({})
const showCommentForm = ref(false)
const isSubmitting = ref(false)
const newComment = ref('')
const isLoading = ref(false)
const editingCommentId = ref(null)
const deleteConfirmationId = ref(null)
const showDeleteConfirm = ref(false)

// Mention functionality
const commentInput = ref(null)
const showMentionSuggestions = ref(false)
const mentionSuggestions = ref([])
const selectedMentionIndex = ref(-1)
const mentionStartPosition = ref(-1)
const mentionQuery = ref('')

// Toast state
const toast = ref({
  show: false,
  message: '',
  type: 'success' // 'success' or 'error'
})

// Show toast notification
const showToast = (message, type = 'success', duration = 3000) => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, duration)
}

// Extract username from email
const extractUsernameFromEmail = (email) => {
  if (!email) return 'Unknown'
  const atIndex = email.indexOf('@')
  return atIndex > 0 ? email.substring(0, atIndex) : email
}

// Fetch comments for the current task
const fetchComments = async () => {
  if (!props.taskId) return
  
  isLoading.value = true
  try {
    const response = await fetch(`${COMMENTS_API_URL}/comments/task/${props.taskId}`)
    
    if (!response.ok) {
      if (response.status === 404) {
        comments.value = []
        return
      }
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data && data.data) {
      comments.value = data.data
      emit('comments-updated', comments.value)
    }
  } catch (error) {
    console.error('Error fetching comments:', error)
    comments.value = []
  } finally {
    isLoading.value = false
  }
}

// Submit new comment
const submitComment = async () => {
  if (!newComment.value.trim()) {
    showToast('Please enter a comment', 'error')
    return
  }
  
  if (!props.taskId) {
    showToast('Error: No task ID', 'error')
    return
  }

  isSubmitting.value = true

  try {
    const username = extractUsernameFromEmail(currentUserEmail.value)
    
    const commentData = {
      task_id: parseInt(props.taskId),
      user_id: currentUserId.value,
      user_name: username,
      user_role: currentUserRole.value,
      content: newComment.value.trim()
    }

    // If editing existing comment
    if (editingCommentId.value) {
      const response = await fetch(
        `${COMMENTS_API_URL}/comments/${editingCommentId.value}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ content: newComment.value.trim() })
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.Message || `HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data && data.data) {
        const index = comments.value.findIndex(c => c.id === editingCommentId.value)
        if (index !== -1) {
          comments.value[index] = data.data
        }
        emit('comments-updated', comments.value)
        showToast('Comment updated successfully', 'success')
      }
      editingCommentId.value = null
    } else {
      // Create new comment
      const response = await fetch(
        `${COMMENTS_API_URL}/comments/create`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(commentData)
        }
      )
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Error creating comment:', errorData)
        throw new Error(errorData.Message || `HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      
      if (data && data.data) {
        comments.value.unshift(data.data)
        emit('comments-updated', comments.value)
        showToast('Comment posted successfully', 'success')
      }
    }

    newComment.value = ''
    showCommentForm.value = false
  } catch (error) {
    console.error('Error submitting comment:', error)
    showToast('Failed to post comment. Please try again.', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Cancel comment
const cancelComment = () => {
  newComment.value = ''
  showCommentForm.value = false
  editingCommentId.value = null
  hideMentionSuggestions()
}

// Edit comment
const editComment = (comment) => {
  newComment.value = comment.content
  showCommentForm.value = true
  editingCommentId.value = comment.id
}

// Delete comment
const deleteComment = async (commentId) => {
  // Open confirmation dialog
  deleteConfirmationId.value = commentId
  showDeleteConfirm.value = true
}

// Confirm delete
const confirmDelete = async () => {
  if (!deleteConfirmationId.value) return

  try {
    const response = await fetch(
      `${COMMENTS_API_URL}/comments/${deleteConfirmationId.value}`,
      {
        method: 'DELETE'
      }
    )
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    comments.value = comments.value.filter(c => c.id !== deleteConfirmationId.value)
    emit('comments-updated', comments.value)
    showToast('Comment deleted successfully', 'success')
  } catch (error) {
    console.error('Error deleting comment:', error)
    showToast('Failed to delete comment. Please try again.', 'error')
  } finally {
    showDeleteConfirm.value = false
    deleteConfirmationId.value = null
  }
}

// Cancel delete
const cancelDelete = () => {
  showDeleteConfirm.value = false
  deleteConfirmationId.value = null
}

// Mention functionality methods
const handleInput = (event) => {
  const value = event.target.value
  const cursorPosition = event.target.selectionStart
  
  // Check if user is typing @mention
  const lastAtIndex = value.lastIndexOf('@', cursorPosition - 1)
  
  if (lastAtIndex !== -1) {
    // Check if there's no space between @ and cursor
    const textAfterAt = value.substring(lastAtIndex + 1, cursorPosition)
    if (!textAfterAt.includes(' ')) {
      mentionStartPosition.value = lastAtIndex
      mentionQuery.value = textAfterAt
      
      if (textAfterAt.length >= 0) {
        searchUsers(mentionQuery.value)
      }
      return
    }
  }
  
  // Hide suggestions if not in mention mode
  hideMentionSuggestions()
}

const handleKeydown = (event) => {
  if (!showMentionSuggestions.value || mentionSuggestions.value.length === 0) {
    return
  }
  
  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      selectedMentionIndex.value = Math.min(
        selectedMentionIndex.value + 1,
        mentionSuggestions.value.length - 1
      )
      break
    case 'ArrowUp':
      event.preventDefault()
      selectedMentionIndex.value = Math.max(selectedMentionIndex.value - 1, 0)
      break
    case 'Enter':
      event.preventDefault()
      if (selectedMentionIndex.value >= 0) {
        selectMention(mentionSuggestions.value[selectedMentionIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      hideMentionSuggestions()
      break
  }
}

const searchUsers = async (query) => {
  if (!query || query.length < 1) {
    mentionSuggestions.value = []
    showMentionSuggestions.value = false
    return
  }
  
  try {
    const response = await fetch(`${USERS_API_URL}/users/search?q=${encodeURIComponent(query)}&limit=5`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data && data.data) {
      mentionSuggestions.value = data.data
      showMentionSuggestions.value = true
      selectedMentionIndex.value = 0
    } else {
      mentionSuggestions.value = []
      showMentionSuggestions.value = false
    }
  } catch (error) {
    console.error('Error searching users:', error)
    mentionSuggestions.value = []
    showMentionSuggestions.value = false
  }
}

const selectMention = (user) => {
  if (!user) return
  
  const beforeMention = newComment.value.substring(0, mentionStartPosition.value)
  const afterMention = newComment.value.substring(mentionStartPosition.value + 1 + mentionQuery.value.length)
  
  newComment.value = beforeMention + `@${user.username}` + afterMention
  
  hideMentionSuggestions()
  
  // Focus back to input and position cursor after mention
  setTimeout(() => {
    if (commentInput.value) {
      const newPosition = beforeMention.length + user.username.length + 2 // +2 for @
      commentInput.value.focus()
      commentInput.value.setSelectionRange(newPosition, newPosition)
    }
  }, 0)
}

const hideMentionSuggestions = () => {
  showMentionSuggestions.value = false
  mentionSuggestions.value = []
  selectedMentionIndex.value = -1
  mentionStartPosition.value = -1
  mentionQuery.value = ''
}

// Check if comment has been edited
const isCommentEdited = (comment) => {
  if (!comment.created_at || !comment.updated_at) return false
  const createdTime = new Date(comment.created_at).getTime()
  const updatedTime = new Date(comment.updated_at).getTime()
  return updatedTime - createdTime > 1000 // More than 1 second difference
}

// Get user avatar
const getUserAvatar = (userId, userName) => {
  if (userId === currentUserId.value && currentUserEmail.value) {
    const username = extractUsernameFromEmail(currentUserEmail.value)
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(username)}&background=random&size=36`
  }
  
  // For other users, use the userName parameter if provided
  if (userName) {
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(userName)}&background=random&size=36`
  }
  
  const user = users.value[userId]
  const name = user?.name || user?.email
  
  const displayName = name 
    ? (name.includes('@') ? extractUsernameFromEmail(name) : name)
    : `User ${userId}`
  
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=random&size=36`
}

// Get current user name
const getCurrentUserName = () => {
  return extractUsernameFromEmail(currentUserEmail.value)
}

// Format comment time
const formatCommentTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  if (diffDays < 365) return date.toLocaleDateString('en-SG', { month: 'short', day: 'numeric' })
  
  return date.toLocaleDateString('en-SG', { month: 'short', day: 'numeric', year: 'numeric' })
}

// Format comment text
const formatCommentText = (text) => {
  return text.replace(
    /@(\w+)/g,
    '<span class="mention">@$1</span>'
  )
}

// Check if user can edit comment
const canEditComment = (userId) => {
  return currentUserId.value === userId
}

// Check if user can delete comment
const canDeleteComment = (userId) => {
  return currentUserId.value === userId || currentUserRole.value === 'admin'
}

// Capitalize role
const capitalizeRole = (role) => {
  return role.charAt(0).toUpperCase() + role.slice(1)
}

// Fetch comments when component mounts
onMounted(() => {
  fetchComments()
})

// Watch for taskId changes
watch(() => props.taskId, (newTaskId) => {
  if (newTaskId) {
    fetchComments()
  }
})
</script>

<style scoped>
.comments-section {
  margin-top: 2rem;
  padding: 1.5rem 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  position: relative;
}

.comments-header {
  margin-bottom: 2rem;
  padding-bottom: 0;
}

.comments-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #030303;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comments-title i {
  font-size: 1.8rem;
  color: #065fd4;
}

.add-comment-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #f0f2f5 100%);
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  align-items: flex-start;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  margin-top: 0.6rem;
}

.comment-input-wrapper {
  flex: 1;
}

.comment-input {
  width: 100%;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 0.75rem 0;
  font-size: 0.95rem;
  outline: none;
  background: transparent;
  transition: all 0.2s;
  color: #030303;
}

.comment-input::placeholder {
  color: #9ca3af;
}

.comment-input:focus {
  border-bottom-color: #065fd4;
  background: rgba(255, 255, 255, 0.5);
}

.comment-form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.75rem;
  justify-content: flex-end;
}

.btn-cancel,
.btn-comment {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: transparent;
  color: #030303;
}

.btn-cancel:hover {
  background: #f0f0f0;
}

.btn-comment {
  background: #065fd4;
  color: white;
}

.btn-comment:hover:not(:disabled) {
  background: #0d47a1;
}

.btn-comment:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-thread {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.comment {
  display: flex;
  gap: 1rem;
  padding: 1rem 0;
  align-items: center;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  flex-shrink: 0;
  margin-top: 0.25rem;
}

.comment-body {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.comment-content {
  flex: 1;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.comment-author {
  font-weight: 500;
  color: #030303;
  font-size: 0.9rem;
}

.comment-role {
  font-size: 0.75rem;
  background: #f0f0f0;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  color: #606060;
}

.comment-timestamp {
  font-size: 0.85rem;
  color: #606060;
}

.comment-edited {
  font-size: 0.85rem;
  color: #999;
  font-style: italic;
}

.comment-text-container {
  margin-bottom: 0.5rem;
}

.comment-text {
  margin: 0;
  color: #030303;
  font-size: 0.9rem;
  line-height: 1.4;
  word-wrap: break-word;
}

.mention {
  color: #065fd4;
  font-weight: 500;
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.action-menu {
  display: flex;
  gap: 0.25rem;
  margin-left: auto;
}

.menu-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #606060;
  padding: 0.25rem;
  font-size: 0.85rem;
  transition: color 0.2s;
}

.menu-btn:hover {
  color: #030303;
}

.menu-btn.delete:hover {
  color: #ff4444;
}

.no-comments {
  text-align: center;
  padding: 2rem;
  color: #606060;
  font-size: 0.95rem;
}

.no-comments i {
  font-size: 3rem;
  margin-bottom: 1rem;
  display: block;
  opacity: 0.6;
  color: #9ca3af;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #606060;
  font-size: 0.95rem;
}

.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.9rem;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  background-color: #10b981;
}

.toast.error {
  background-color: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Delete Confirmation Dialog Styles */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
  animation: fadeIn 0.2s ease-out;
}

.dialog-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: slideInDialog 0.3s ease-out;
}

.dialog-content {
  text-align: center;
}

.dialog-header {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.dialog-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.warning-icon {
  font-size: 2rem;
  color: #f59e0b;
}

.dialog-content p {
  color: #4b5563;
  margin-bottom: 1.5rem;
  font-size: 0.975rem;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  background-color: white;
  color: #4b5563;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover {
  background-color: #f3f4f6;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background-color: #dc2626;
}

@keyframes slideInDialog {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Mention functionality styles */
.mention-input-container {
  position: relative;
  width: 100%;
}

.mention-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
  margin-top: 2px;
}

.mention-suggestion {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background-color 0.2s;
}

.mention-suggestion:last-child {
  border-bottom: none;
}

.mention-suggestion:hover,
.mention-suggestion.active {
  background-color: #f8fafc;
}

.mention-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 0.75rem;
  flex-shrink: 0;
}

.mention-info {
  flex: 1;
  min-width: 0;
}

.mention-name {
  font-weight: 500;
  color: #1f2937;
  font-size: 0.9rem;
  margin-bottom: 0.125rem;
}

.mention-username {
  color: #6b7280;
  font-size: 0.8rem;
}
</style>