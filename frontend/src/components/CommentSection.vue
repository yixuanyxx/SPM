<template>
  <div class="comments-section">
    <!-- Comments Header -->
    <div class="comments-header">
      <h3 class="comments-title">
        <i class="bi bi-chat-dots"></i>
        Comments {{ comments.length > 0 ? `(${comments.length})` : '' }}
      </h3>
      <button 
        type="button"
        @click="toggleCommentForm"
        class="add-comment-btn"
      >
        <i class="bi bi-plus-lg"></i>
        {{ showCommentForm ? 'Cancel' : 'Add Comment' }}
      </button>
    </div>

    <!-- Add Comment Form -->
    <div v-if="showCommentForm" class="comment-form">
      <div class="comment-input-wrapper">
        <div class="user-avatar">
          <img 
            :src="getUserAvatar(currentUserId)" 
            :alt="getCurrentUserName()"
            class="avatar-img"
          />
        </div>
        <div class="comment-input-area">
          <textarea
            v-model="newComment"
            placeholder="Add a comment... (mention @username to notify)"
            rows="3"
            class="comment-textarea"
            :class="{ 'input-error': showErrors && !newComment.trim() }"
          ></textarea>
          <div v-if="showErrors && !newComment.trim()" class="error-message">
            <i class="bi bi-exclamation-circle"></i>
            Please enter a comment
          </div>
        </div>
      </div>

      <!-- Mentioned Users (if any) -->
      <div v-if="mentionedUsers.length > 0" class="mentioned-users">
        <span class="mentioned-label">Will notify:</span>
        <span 
          v-for="user in mentionedUsers" 
          :key="user.userid"
          class="mentioned-user-tag"
        >
          {{ user.name }}
          <button 
            type="button"
            @click="removeMention(user.userid)"
            class="remove-mention"
          >
            ×
          </button>
        </span>
      </div>

      <div class="comment-actions">
        <button 
          type="button"
          @click="submitComment"
          :disabled="isSubmitting"
          class="btn-submit-comment"
        >
          <span v-if="isSubmitting" class="spinner"></span>
          <i v-else class="bi bi-send"></i>
          {{ isSubmitting ? 'Posting...' : 'Post Comment' }}
        </button>
        <button 
          type="button"
          @click="cancelComment"
          class="btn-cancel-comment"
        >
          Cancel
        </button>
      </div>
    </div>

    <!-- Comments List -->
    <div v-if="comments.length > 0" class="comments-list">
      <div 
        v-for="comment in comments" 
        :key="comment.id"
        class="comment-item"
      >
        <!-- Comment Header -->
        <div class="comment-header">
          <div class="comment-user-info">
            <img 
              :src="getUserAvatar(comment.user_id)" 
              :alt="comment.user_name"
              class="comment-avatar"
            />
            <div class="comment-user-details">
              <span class="comment-user-name">{{ comment.user_name }}</span>
              <span class="comment-role" v-if="comment.user_role">
                {{ capitalizeRole(comment.user_role) }}
              </span>
            </div>
          </div>
          <span class="comment-time">{{ formatCommentTime(comment.created_at) }}</span>
        </div>

        <!-- Comment Content -->
        <div class="comment-content">
          <p class="comment-text" v-html="formatCommentText(comment.content)"></p>
        </div>

        <!-- Comment Actions -->
        <div class="comment-actions-footer">
          <button 
            v-if="canEditComment(comment.user_id)"
            type="button"
            @click="editComment(comment)"
            class="action-btn edit-btn"
            title="Edit comment"
          >
            <i class="bi bi-pencil"></i>
            Edit
          </button>
          <button 
            v-if="canDeleteComment(comment.user_id)"
            type="button"
            @click="deleteComment(comment.id)"
            class="action-btn delete-btn"
            title="Delete comment"
          >
            <i class="bi bi-trash"></i>
            Delete
          </button>
          <button 
            type="button"
            @click="replyToComment(comment)"
            class="action-btn reply-btn"
          >
            <i class="bi bi-reply"></i>
            Reply
          </button>
        </div>

        <!-- Replies -->
        <div v-if="comment.replies && comment.replies.length > 0" class="comment-replies">
          <div 
            v-for="reply in comment.replies" 
            :key="reply.id"
            class="reply-item"
          >
            <div class="reply-header">
              <img 
                :src="getUserAvatar(reply.user_id)" 
                :alt="reply.user_name"
                class="reply-avatar"
              />
              <div class="reply-user-info">
                <span class="reply-user-name">{{ reply.user_name }}</span>
                <span class="reply-time">{{ formatCommentTime(reply.created_at) }}</span>
              </div>
            </div>
            <p class="reply-text" v-html="formatCommentText(reply.content)"></p>
            <div class="reply-actions">
              <button 
                v-if="canEditComment(reply.user_id)"
                type="button"
                @click="editReply(reply, comment.id)"
                class="small-action-btn"
              >
                <i class="bi bi-pencil"></i> Edit
              </button>
              <button 
                v-if="canDeleteComment(reply.user_id)"
                type="button"
                @click="deleteReply(reply.id, comment.id)"
                class="small-action-btn"
              >
                <i class="bi bi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Comments State -->
    <div v-else-if="!showCommentForm" class="no-comments">
      <i class="bi bi-chat-left"></i>
      <p>No comments yet. Be the first to comment!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getCurrentUserData } from '../services/session.js'

const props = defineProps({
  taskId: {
    type: [String, Number],
    required: true
  },
  taskOwnerId: {
    type: [String, Number],
    required: true
  },
  comments: {
    type: Array,
    default: () => []
  },
  users: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['add-comment', 'edit-comment', 'delete-comment', 'reply-comment'])

const userData = getCurrentUserData()
const currentUserId = ref(parseInt(userData.userid) || null)
const currentUserRole = ref(userData.role?.toLowerCase() || '')

const showCommentForm = ref(false)
const showErrors = ref(false)
const isSubmitting = ref(false)
const newComment = ref('')
const mentionedUsers = ref([])
const editingCommentId = ref(null)

const toggleCommentForm = () => {
  if (showCommentForm.value) {
    cancelComment()
  } else {
    showCommentForm.value = true
    showErrors.value = false
  }
}

const submitComment = async () => {
  if (!newComment.value.trim()) {
    showErrors.value = true
    return
  }

  isSubmitting.value = true

  try {
    const commentData = {
      task_id: props.taskId,
      user_id: currentUserId.value,
      user_name: userData.username,
      user_role: currentUserRole.value,
      content: newComment.value,
      mentioned_user_ids: mentionedUsers.value.map(u => u.userid),
      created_at: new Date().toISOString(),
      replies: []
    }

    // Add to parent component
    emit('add-comment', commentData)

    // Reset form
    newComment.value = ''
    mentionedUsers.value = []
    showCommentForm.value = false
    showErrors.value = false
  } catch (error) {
    console.error('Error submitting comment:', error)
  } finally {
    isSubmitting.value = false
  }
}

const cancelComment = () => {
  newComment.value = ''
  mentionedUsers.value = []
  showCommentForm.value = false
  showErrors.value = false
  editingCommentId.value = null
}

const editComment = (comment) => {
  newComment.value = comment.content
  editingCommentId.value = comment.id
  showCommentForm.value = true
  showErrors.value = false
  // Parse existing mentions from content
  extractMentions(comment.content)
}

const deleteComment = (commentId) => {
  if (confirm('Are you sure you want to delete this comment?')) {
    emit('delete-comment', commentId)
  }
}

const replyToComment = (comment) => {
  newComment.value = `@${comment.user_name} `
  editingCommentId.value = comment.id
  showCommentForm.value = true
}

const editReply = (reply, parentCommentId) => {
  newComment.value = reply.content
  editingCommentId.value = `${parentCommentId}-${reply.id}`
  showCommentForm.value = true
}

const deleteReply = (replyId, commentId) => {
  if (confirm('Are you sure you want to delete this reply?')) {
    emit('delete-comment', { parentId: commentId, replyId })
  }
}

const removeMention = (userId) => {
  mentionedUsers.value = mentionedUsers.value.filter(u => u.userid !== userId)
}

const extractMentions = (text) => {
  const mentionRegex = /@(\w+)/g
  const matches = text.matchAll(mentionRegex)
  mentionedUsers.value = []
  
  for (const match of matches) {
    const username = match[1]
    const user = Object.values(props.users).find(u => u.name === username)
    if (user && !mentionedUsers.value.find(u => u.userid === user.userid)) {
      mentionedUsers.value.push(user)
    }
  }
}

const getUserAvatar = (userId) => {
  // Return initials-based avatar or placeholder
  const user = props.users[userId]
  if (user?.name) {
    const initials = user.name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
    return `https://ui-avatars.com/api/?name=${encodeURIComponent(user.name)}&background=random`
  }
  return 'https://ui-avatars.com/api/?name=Unknown&background=gray'
}

const getCurrentUserName = () => {
  return userData.username || 'You'
}

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
  
  return date.toLocaleDateString('en-SG', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatCommentText = (text) => {
  // Convert @mentions to highlighted spans
  return text.replace(
    /@(\w+)/g,
    '<span class="mention">@$1</span>'
  )
}

const canEditComment = (userId) => {
  return currentUserId.value === userId
}

const canDeleteComment = (userId) => {
  return currentUserId.value === userId || currentUserRole.value === 'admin'
}

const capitalizeRole = (role) => {
  return role.charAt(0).toUpperCase() + role.slice(1)
}
</script>

<style scoped>
.comments-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #e5e7eb;
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.comments-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.comments-title i {
  color: #3b82f6;
}

.add-comment-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.add-comment-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.comment-form {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
}

.comment-input-wrapper {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.user-avatar {
  flex-shrink: 0;
}

.avatar-img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e5e7eb;
}

.comment-input-area {
  flex: 1;
}

.comment-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  transition: all 0.2s;
}

.comment-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.comment-textarea.input-error {
  border-color: #dc2626;
  background-color: #fee2e2;
}

.error-message {
  margin-top: 0.5rem;
  color: #dc2626;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.mentioned-users {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.mentioned-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.mentioned-user-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #dbeafe;
  color: #1e40af;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.remove-mention {
  background: none;
  border: none;
  color: #1e40af;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
  line-height: 1;
}

.remove-mention:hover {
  opacity: 0.7;
}

.comment-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-submit-comment,
.btn-cancel-comment {
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-submit-comment {
  background: #10b981;
  color: white;
  flex: 1;
}

.btn-submit-comment:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(16, 185, 129, 0.3);
}

.btn-submit-comment:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel-comment {
  background: #e5e7eb;
  color: #374151;
  flex: 1;
}

.btn-cancel-comment:hover {
  background: #d1d5db;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.comment-item {
  padding: 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.comment-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: #d1d5db;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.comment-user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e5e7eb;
}

.comment-user-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.comment-user-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.9rem;
}

.comment-role {
  font-size: 0.75rem;
  color: #6b7280;
  background: #f3f4f6;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  width: fit-content;
}

.comment-time {
  font-size: 0.875rem;
  color: #9ca3af;
}

.comment-content {
  margin: 0.75rem 0 0.75rem 3rem;
}

.comment-text {
  margin: 0;
  color: #374151;
  font-size: 0.95rem;
  line-height: 1.5;
}

.mention {
  color: #3b82f6;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.1);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.comment-actions-footer {
  display: flex;
  gap: 1rem;
  margin-left: 3rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f3f4f6;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  color: #6b7280;
  padding: 0;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.action-btn:hover {
  color: #374151;
}

.edit-btn:hover {
  color: #3b82f6;
}

.delete-btn:hover {
  color: #ef4444;
}

.reply-btn:hover {
  color: #10b981;
}

.comment-replies {
  margin-top: 1rem;
  margin-left: 3rem;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reply-item {
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.reply-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #e5e7eb;
}

.reply-user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.reply-user-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 0.875rem;
}

.reply-time {
  font-size: 0.75rem;
  color: #9ca3af;
}

.reply-text {
  margin: 0;
  color: #374151;
  font-size: 0.875rem;
  line-height: 1.5;
}

.reply-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.small-action-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
  color: #6b7280;
  padding: 0;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.small-action-btn:hover {
  color: #374151;
}

.no-comments {
  text-align: center;
  padding: 2rem;
  color: #9ca3af;
}

.no-comments i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
  opacity: 0.5;
}

.no-comments p {
  margin: 0;
  font-size: 0.95rem;
}
</style>