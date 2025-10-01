<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
          <i class="bi bi-arrow-clockwise spin"></i>
        </div>
        <p>Loading task details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <i class="bi bi-exclamation-triangle"></i>
        </div>
        <h3>Error Loading Task</h3>
        <p>{{ error }}</p>
        <button @click="goBack" class="btn btn-secondary">
          <i class="bi bi-arrow-left"></i>
          Go Back
        </button>
      </div>

      <!-- Task Details Content -->
      <div v-else-if="task" class="task-details-content">
        <!-- Breadcrumb Navigation -->
        <div class="breadcrumb-section">
          <nav class="breadcrumb-nav">
            <button @click="goBack" class="breadcrumb-item">
              <i class="bi bi-house"></i>
              Tasks
            </button>
            <i class="bi bi-chevron-right breadcrumb-separator"></i>
            <span v-if="project" class="breadcrumb-item">
              <div class="project-dot" :style="{ backgroundColor: project.color || '#6366f1' }"></div>
              {{ project.name }}
              <i class="bi bi-chevron-right breadcrumb-separator"></i>
            </span>
            <span v-if="parentTask" class="breadcrumb-item" @click="navigateToTask(parentTask.id)">
              {{ parentTask.task_name }}
              <i class="bi bi-chevron-right breadcrumb-separator"></i>
            </span>
            <span class="breadcrumb-current">{{ task.task_name }}</span>
          </nav>
        </div>

        <!-- Header Section -->
        <div class="header-section">
          <div class="header-content">
            <div class="task-header">
              <div class="task-icon-title">
                <div class="task-icon" :class="getTaskTypeClass()">
                  <i :class="getTaskTypeIcon()"></i>
                </div>
                <h1 class="page-title">{{ task.task_name }}</h1>
              </div>
              
              <div class="header-actions">
                <div class="task-status-badge" :class="getStatusClass(task.status)">
                  <i :class="getStatusIcon(task.status)"></i>
                  <span>{{ getStatusLabel(task.status) }}</span>
                </div>
                
                <div class="action-buttons">
                  <button 
                    v-if="canEditTask" 
                    @click="openEditPopup" 
                    class="btn btn-ghost"
                  >
                    <i class="bi bi-pencil"></i>
                    Edit
                  </button>
                  <button 
                    v-if="canAssignTask" 
                    @click="openAssignPopup" 
                    class="btn btn-primary"
                  >
                    <i class="bi bi-person-plus"></i>
                    Assign
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="main-content">
          <!-- Task Description -->
          <div class="content-block">
            <h3 class="block-title">
              <i class="bi bi-card-text"></i>
              Description
            </h3>
            <div class="block-content">
              <div class="description-content">
                <p v-if="task.description" class="description-text">{{ task.description }}</p>
                <p v-else class="description-placeholder">No description provided</p>
              </div>
            </div>
          </div>

          <!-- Properties Section -->
          <div class="content-block">
            <h3 class="block-title">
              <i class="bi bi-list-ul"></i>
              Properties
            </h3>
            <div class="block-content">
              <div class="properties-grid">
                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-flag"></i>
                    Status
                  </label>
                  <div class="property-value">
                    <div class="task-status-inline" :class="getStatusClass(task.status)">
                      <i :class="getStatusIcon(task.status)"></i>
                      <span>{{ getStatusLabel(task.status) }}</span>
                    </div>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-calendar3"></i>
                    Due Date
                  </label>
                  <div class="property-value">
                    <span class="date-value">{{ formatDate(task.due_date) }}</span>
                    <span v-if="task.due_date" class="date-relative">{{ getRelativeDate(task.due_date) }}</span>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-person"></i>
                    Owner
                  </label>
                  <div class="property-value">
                    <div v-if="task.owner" class="user-chip">
                      <div class="user-avatar">
                        <i class="bi bi-person-circle"></i>
                      </div>
                      <span>{{ task.owner }}</span>
                    </div>
                    <span v-else class="unassigned-text">Unassigned</span>
                  </div>
                </div>

                <div v-if="project" class="property-item">
                  <label class="property-label">
                    <i class="bi bi-folder"></i>
                    Project
                  </label>
                  <div class="property-value">
                    <div class="project-chip">
                      <div class="project-dot" :style="{ backgroundColor: project.color || '#6366f1' }"></div>
                      <span>{{ project.name }}</span>
                    </div>
                  </div>
                </div>

                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-clock"></i>
                    Created
                  </label>
                  <div class="property-value">
                    <span class="date-value">{{ formatDate(task.created_at) }}</span>
                  </div>
                </div>

                <div v-if="task.collaborators && task.collaborators.length > 0" class="property-item">
                  <label class="property-label">
                    <i class="bi bi-people"></i>
                    Collaborators
                  </label>
                  <div class="property-value">
                    <div class="collaborators-list">
                      <div v-for="collaborator in task.collaborators" :key="collaborator.id" class="user-chip">
                        <div class="user-avatar">
                          <i class="bi bi-person-circle"></i>
                        </div>
                        <span>{{ collaborator.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- PDF Attachments Section -->
          <div v-if="task.pdf_attachments && task.pdf_attachments.length > 0" class="content-block">
            <h3 class="block-title">
              <i class="bi bi-paperclip"></i>
              Attachments
            </h3>
            <div class="block-content">
              <div class="attachments-grid">
                <div 
                  v-for="attachment in task.pdf_attachments" 
                  :key="attachment.id || attachment.name"
                  class="attachment-card"
                  @click="openAttachment(attachment)"
                >
                  <div class="attachment-icon">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </div>
                  <div class="attachment-info">
                    <h4 class="attachment-name">{{ attachment.name || attachment.filename }}</h4>
                    <p class="attachment-meta">
                      <span v-if="attachment.size">{{ formatFileSize(attachment.size) }}</span>
                      <span v-if="attachment.uploaded_at">• {{ formatDate(attachment.uploaded_at) }}</span>
                    </p>
                  </div>
                  <div class="attachment-actions">
                    <button class="btn-icon" @click.stop="downloadAttachment(attachment)">
                      <i class="bi bi-download"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Subtasks Section -->
          <div v-if="task.subtasks && task.subtasks.length > 0" class="content-block">
            <h3 class="block-title">
              <i class="bi bi-diagram-3"></i>
              Subtasks
              <div class="subtasks-progress">
                <div class="progress-bar">
                  <div 
                    class="progress-fill" 
                    :style="{ width: `${getSubtaskProgress(task)}%` }"
                  ></div>
                </div>
                <span class="progress-text">{{ getCompletedSubtasks(task) }}/{{ task.subtasks.length }}</span>
              </div>
            </h3>
            <div class="block-content">
              <div class="subtasks-list">
                <div 
                  v-for="subtask in task.subtasks" 
                  :key="subtask.id"
                  class="subtask-item"
                  :class="{ completed: subtask.status === 'Completed' }"
                  @click="navigateToTask(subtask.id)"
                >
                  <div class="subtask-content">
                    <h4 class="subtask-title" :class="{ completed: subtask.status === 'Completed' }">
                      {{ subtask.task_name }}
                    </h4>
                    <div class="subtask-meta">
                      <div class="task-status-mini" :class="getStatusClass(subtask.status)">
                        {{ getStatusLabel(subtask.status) }}
                      </div>
                      <span v-if="subtask.due_date" class="subtask-date">
                        {{ formatDate(subtask.due_date) }}
                      </span>
                      <span v-if="subtask.owner" class="subtask-owner">
                        {{ subtask.owner }}
                      </span>
                    </div>
                  </div>
                  <div class="subtask-arrow">
                    <i class="bi bi-arrow-right"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Parent Task Reference -->
          <div v-if="parentTask" class="content-block">
            <h3 class="block-title">
              <i class="bi bi-arrow-up"></i>
              Parent Task
            </h3>
            <div class="block-content">
              <div class="parent-task-link" @click="navigateToTask(parentTask.id)">
                <div class="task-icon parent">
                  <i class="bi bi-list-task"></i>
                </div>
                <div class="parent-task-info">
                  <h4 class="parent-task-title">{{ parentTask.task_name }}</h4>
                  <p class="parent-task-meta">Parent Task</p>
                </div>
                <div class="parent-task-arrow">
                  <i class="bi bi-arrow-right"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Popup -->
    <EditPopup
      :isVisible="showEditPopup"
      :taskId="task?.id"
      :taskTitle="task?.task_name || ''"
      :currentOwner="task?.owner || ''"
      :userRole="currentUser.role"
      :isSubtask="!!task?.parent_task"
      :parentTaskId="task?.parent_task"
      :parentTaskTitle="parentTask?.task_name || ''"
      :teamMembers="teamMembers"
      @close="closeEditPopup"
      @update-success="updateSuccess"
    />

    <!-- Assign Popup -->
    <AssignPopup 
      :isVisible="showAssignPopup"
      :taskId="task?.id"
      :taskTitle="task?.task_name || ''"
      :currentOwner="task?.owner || ''"
      :userRole="currentUser.role"
      :isSubtask="!!task?.parent_task"
      :parentTaskId="task?.parent_task"
      :teamMembers="teamMembers"
      @close="closeAssignPopup"
      @assignment-success="handleAssignmentSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AssignPopup from '@/components/AssignPopup.vue'
import EditPopup from '@/components/EditPopup.vue'
import SideNavbar from '../../components/SideNavbar.vue'
import '../taskview/taskview.css'
import './taskdetails.css'

const route = useRoute()
const router = useRouter()

const task = ref(null)
const project = ref(null)
const parentTask = ref(null)
const loading = ref(true)
const error = ref(null)
const showEditPopup = ref(false)
const showAssignPopup = ref(false)

// Team members data for assign popup - replace with real data fetching as needed
const teamMembers = ref([
  { id: 1, name: 'John Manager', role: 'manager' },
  { id: 2, name: 'Jane Manager', role: 'manager' },
  { id: 3, name: 'Alice Staff', role: 'staff' },
  { id: 4, name: 'Bob Staff', role: 'staff' },
  { id: 5, name: 'Carol Staff', role: 'staff' }
])

// Get user info from localStorage
const getCurrentUser = () => {
  try {
    const userRole = localStorage.getItem('userRole') || ''
    const userId = localStorage.getItem('userId') || ''
    return { role: userRole, userId: userId }
  } catch (err) {
    return { role: '', userId: '' }
  }
}

const currentUser = getCurrentUser()

// Computed properties for permissions
const canEditTask = computed(() => {
  if (!task.value || !currentUser.userId) return false
  
  const currentUserId = String(currentUser.userId).trim()
  const taskOwnerId = String(task.value.owner_id).trim()
  const isTaskOwner = currentUserId === taskOwnerId && currentUserId !== ''
  const hasRolePermission = currentUser.role === 'manager' || currentUser.role === 'director'
  
  return isTaskOwner || hasRolePermission
})

// const canAssignTask = computed(() => {
//   if (!task.value || !currentUser.userId) return false
  
//   const currentUserId = String(currentUser.userId).trim()
//   const taskOwnerId = String(task.value.owner_id).trim()
//   const isTaskOwner = currentUserId === taskOwnerId && currentUserId !== ''
//   const hasRolePermission = currentUser.role === 'manager' || currentUser.role === 'director'
  
//   return isTaskOwner || hasRolePermission
// })

const canAssignTask = computed(() => {
  if (!task.value) return false
  
  return currentUser.role === 'manager' || currentUser.role === 'director'
})

// Watch for route parameter changes to reload task details
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    await fetchTaskDetails()
  }
}, { immediate: false })

onMounted(async () => {
  await fetchTaskDetails()
})

const fetchTaskDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const taskId = route.params.id
    
    // Reset current task data
    task.value = null
    project.value = null
    parentTask.value = null
    
    // Fetch task details
    const taskResponse = await fetch(`http://localhost:5002/tasks/${taskId}`)
    if (!taskResponse.ok) {
      throw new Error(`Failed to fetch task: ${taskResponse.status}`)
    }
    
    const taskData = await taskResponse.json()
    task.value = taskData.task || taskData

    // Fetch owner details using owner_id
    if (task.value.owner_id) {
      try {
        const ownerResponse = await fetch(`http://localhost:5003/users/${task.value.owner_id}`)
        if (ownerResponse.ok) {
          const responseData = await ownerResponse.json()
          const ownerData = responseData.data
          
          if (ownerData && (ownerData.name || ownerData.username || ownerData.email)) {
            task.value.owner = ownerData.name || ownerData.username || ownerData.email
          } else {
            task.value.owner = null
          }
        } else {
          task.value.owner = null
        }
      } catch (err) {
        task.value.owner = null
      }
    } else {
      task.value.owner = null
    }

    // Fetch subtask details if subtasks array contains IDs
    if (task.value.subtasks && task.value.subtasks.length > 0) {
      try {
        const subtaskPromises = task.value.subtasks.map(async (subtaskId) => {
          if (typeof subtaskId === 'object') {
            return subtaskId
          }
          
          const subtaskResponse = await fetch(`http://localhost:5002/tasks/${subtaskId}`)
          if (subtaskResponse.ok) {
            const subtaskData = await subtaskResponse.json()
            return subtaskData.task || subtaskData
          }
          return null
        })
        
        const subtaskResults = await Promise.all(subtaskPromises)
        task.value.subtasks = subtaskResults.filter(subtask => subtask !== null)
      } catch (err) {
        // Silently handle subtask fetch errors
      }
    }
    
    // Fetch parent task details if parent_task exists
    if (task.value.parent_task) {
      try {
        const parentResponse = await fetch(`http://localhost:5002/tasks/${task.value.parent_task}`)
        if (parentResponse.ok) {
          const parentData = await parentResponse.json()
          parentTask.value = parentData.task || parentData
        }
      } catch (err) {
        // Silently handle parent task fetch errors
      }
    }
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/tasks')
}

const navigateToTask = async (taskId) => {
  if (taskId) {
    await router.push({ name: 'task-detail', params: { id: taskId.toString() } })
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric',
    month: 'short', 
    day: 'numeric'
  })
}

const getRelativeDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = date - now
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 0) {
    return `${Math.abs(diffDays)} days overdue`
  } else if (diffDays === 0) {
    return 'Due today'
  } else if (diffDays === 1) {
    return 'Due tomorrow'
  } else {
    return `Due in ${diffDays} days`
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return ''
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Bytes'
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

const getStatusClass = (status) => {
  const statusClassMap = {
    'Ongoing': 'ongoing',
    'Under Review': 'under-review',
    'Completed': 'completed',
    'Unassigned': 'unassigned'
  }
  return statusClassMap[status] || 'unassigned'
}

const getStatusIcon = (status) => {
  const icons = {
    'Ongoing': 'bi-play-circle',
    'Under Review': 'bi-eye',
    'Completed': 'bi-check-circle-fill',
    'Unassigned': 'bi-person-dash'
  }
  return icons[status] || 'bi-circle'
}

const getStatusLabel = (status) => {
  const labels = {
    'Ongoing': 'Ongoing',
    'Under Review': 'Under Review',
    'Completed': 'Completed',
    'Unassigned': 'Unassigned'
  }
  return labels[status]
}

const getTaskTypeClass = () => {
  return task.value?.parent_task ? 'subtask' : 'task'
}

const getTaskTypeIcon = () => {
  return task.value?.parent_task ? 'bi-diagram-2' : 'bi-list-task'
}

const getSubtaskProgress = (task) => {
  if (!task.subtasks || task.subtasks.length === 0) return 0
  const completed = task.subtasks.filter(subtask => subtask.status === 'Completed').length
  return Math.round((completed / task.subtasks.length) * 100)
}

const getCompletedSubtasks = (task) => {
  if (!task.subtasks) return 0
  return task.subtasks.filter(subtask => subtask.status === 'Completed').length
}

const openAttachment = (attachment) => {
  if (attachment.url) {
    window.open(attachment.url, '_blank')
  }
}

const downloadAttachment = (attachment) => {
  if (attachment.download_url || attachment.url) {
    const link = document.createElement('a')
    link.href = attachment.download_url || attachment.url
    link.download = attachment.name || attachment.filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

// Assign popup methods
const openAssignPopup = () => {
  showAssignPopup.value = true
}

const closeAssignPopup = () => {
  showAssignPopup.value = false
}

const handleAssignmentSuccess = async (assignmentData) => {
  await fetchTaskDetails()
  closeAssignPopup()
}

// Edit popup methods
const openEditPopup = () => {
  showEditPopup.value = true
}

const closeEditPopup = () => {
  showEditPopup.value = false
}

const updateSuccess = async (assignmentData) => {
  await fetchTaskDetails()
  closeEditPopup()
}
</script>