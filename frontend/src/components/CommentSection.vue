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
        <input
          v-model="newComment"
          type="text"
          placeholder="Add a comment..."
          class="comment-input"
          @focus="showCommentForm = true"
          :class="{ 'input-focused': showCommentForm }"
        />
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

    <!-- Sort Options -->
    <div class="sort-container">
      <button class="sort-btn active">Top comments</button>
      <button class="sort-btn">Newest first</button>
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
            :src="getUserAvatar(comment.user_id)" 
            :alt="comment.user_name"
            class="comment-avatar"
          />
          
          <div class="comment-body">
            <div class="comment-header">
              <span class="comment-author">{{ comment.user_name }}</span>
              <span class="comment-role" v-if="comment.user_role">
                {{ capitalizeRole(comment.user_role) }}
              </span>
              <span class="comment-timestamp">{{ formatCommentTime(comment.created_at) }}</span>
            </div>

            <div class="comment-text-container">
              <p class="comment-text" v-html="formatCommentText(comment.content)"></p>
            </div>

            <div class="comment-actions">
              <button class="action-btn like-btn" title="Like">
                <i class="bi bi-hand-thumbs-up"></i>
              </button>
              <button class="action-btn dislike-btn" title="Dislike">
                <i class="bi bi-hand-thumbs-down"></i>
              </button>
              <div class="action-menu">
                <button 
                  v-if="canEditComment(comment.user_id)"
                  @click="editComment(comment)"
                  class="menu-btn"
                >
                  <i class="bi bi-pencil"></i>
                </button>
                <button 
                  v-if="canDeleteComment(comment.user_id)"
                  @click="deleteComment(comment.id)"
                  class="menu-btn delete"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
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
  console.log('=== SUBMIT COMMENT CLICKED ===')
  console.log('New comment value:', newComment.value)
  console.log('Task ID:', props.taskId)
  
  if (!newComment.value.trim()) {
    console.error('Comment is empty!')
    alert('Please enter a comment')
    return
  }
  
  if (!props.taskId) {
    console.error('No task ID provided!')
    alert('Error: No task ID')
    return
  }

  isSubmitting.value = true

  try {
    const username = extractUsernameFromEmail(currentUserEmail.value)
    
    console.log('Current user data:', {
      userId: currentUserId.value,
      email: currentUserEmail.value,
      username: username,
      role: currentUserRole.value
    })
    
    const commentData = {
      task_id: parseInt(props.taskId),
      user_id: currentUserId.value,
      user_name: username,
      user_role: currentUserRole.value,
      content: newComment.value.trim()
    }

    console.log('Submitting comment data:', commentData)
    console.log('API URL:', COMMENTS_API_URL)

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
        // Update comment in local array
        const index = comments.value.findIndex(c => c.id === editingCommentId.value)
        if (index !== -1) {
          comments.value[index] = data.data
        }
        emit('comments-updated', comments.value)
      }
      editingCommentId.value = null
    } else {
      // Create new comment
      console.log('Creating comment with data:', commentData)
      
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
      
      console.log('Response status:', response.status)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        console.error('Error creating comment:', errorData)
        throw new Error(errorData.Message || `HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Comment created successfully:', data)
      
      if (data && data.data) {
        // Add new comment to the beginning of the array
        comments.value.unshift(data.data)
        emit('comments-updated', comments.value)
        console.log('Comment added to list. Total comments:', comments.value.length)
      }
    }

    newComment.value = ''
    showCommentForm.value = false
  } catch (error) {
    console.error('Error submitting comment:', error)
    alert('Failed to post comment. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}

// Cancel comment
const cancelComment = () => {
  newComment.value = ''
  showCommentForm.value = false
  editingCommentId.value = null
}

// Edit comment
const editComment = (comment) => {
  newComment.value = comment.content
  showCommentForm.value = true
  editingCommentId.value = comment.id
}

// Delete comment
const deleteComment = async (commentId) => {
  if (!confirm('Delete this comment?')) return

  try {
    const response = await fetch(
      `${COMMENTS_API_URL}/comments/${commentId}`,
      {
        method: 'DELETE'
      }
    )
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    // Remove comment from local array
    comments.value = comments.value.filter(c => c.id !== commentId)
    emit('comments-updated', comments.value)
  } catch (error) {
    console.error('Error deleting comment:', error)
    alert('Failed to delete comment. Please try again.')
  }
}

// Get user avatar
const getUserAvatar = (userId) => {
  const user = users.value[userId]
  const name = user?.name || user?.email || 'Unknown'
  const displayName = name.includes('@') ? extractUsernameFromEmail(name) : name
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=random&size=32`
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

.sort-container {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  padding: 1rem 0;
  border-bottom: 1px solid #e5e5e5;
}

.sort-btn {
  padding: 0.5rem 0;
  border: none;
  background: transparent;
  color: #030303;
  font-size: 0.9rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.sort-btn.active {
  border-bottom-color: #030303;
  font-weight: 500;
}

.sort-btn:hover {
  color: #606060;
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

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #606060;
  font-size: 0.9rem;
  padding: 0.25rem 0.5rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.action-btn:hover {
  color: #030303;
}

.action-btn i {
  font-size: 0.9rem;
}

.like-btn:hover {
  color: #065fd4;
}

.dislike-btn:hover {
  color: #ff4444;
}

.action-menu {
  margin-left: auto;
  display: flex;
  gap: 0.25rem;
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
</style>