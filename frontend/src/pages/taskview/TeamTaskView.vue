<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Team Tasks</h1>
          <p class="page-subtitle">View Tasks for Your Team</p>
        </div>
      </div>
      
    <!-- Stats Section -->
    <div class="stats-section">
      <div class="stats-container">
        <div class="stat-card" @click="activeFilter = 'all'" :class="{ active: activeFilter === 'all' }">
          <div class="stat-content">
            <div class="stat-icon total">
              <i class="bi bi-list-task"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ totalTasks }}</div>
              <div class="stat-title">Total</div>
            </div>
          </div>
        </div>

        <div class="stat-card" @click="activeFilter = 'Unassigned'" :class="{ active: activeFilter === 'Unassigned' }">
          <div class="stat-content">
            <div class="stat-icon unassigned">
              <i class="bi bi-person-dash"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ unassignedTasks }}</div>
              <div class="stat-title">Unassigned</div>
            </div>
          </div>
        </div>
        
        <div class="stat-card" @click="activeFilter = 'Ongoing'" :class="{ active: activeFilter === 'Ongoing' }">
          <div class="stat-content">
            <div class="stat-icon ongoing">
              <i class="bi bi-play-circle"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ ongoingTasks }}</div>
              <div class="stat-title">Ongoing</div>
            </div>
          </div>
        </div>
        
        <div class="stat-card" @click="activeFilter = 'Under Review'" :class="{ active: activeFilter === 'Under Review' }">
          <div class="stat-content">
            <div class="stat-icon under-review">
              <i class="bi bi-eye"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ underReviewTasks }}</div>
              <div class="stat-title">Under Review</div>
            </div>
          </div>
        </div>
        
        <div class="stat-card" @click="activeFilter = 'Completed'" :class="{ active: activeFilter === 'Completed' }">
          <div class="stat-content">
            <div class="stat-icon completed">
              <i class="bi bi-check-circle-fill"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ completedTasks }}</div>
              <div class="stat-title">Completed</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Sort Controls -->
      <div class="sort-controls">
        <div class="sort-container">
          <label for="sortBy">Sort by:</label>
          <select id="sortBy" v-model="sortBy" class="sort-dropdown">
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="name">Task Name</option>
          </select>
          <button 
            @click="toggleSortOrder" 
            class="sort-order-btn"
            :title="sortOrder === 'asc' ? 'Sort Descending' : 'Sort Ascending'"
          >
            <i :class="sortOrder === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down'"></i>
          </button>
        </div>
      </div>
      
      <!-- Tasks -->
      <div class="tasks-container">

        <!-- Loading state -->
        <div v-if="isLoadingTasks" class="loading-state">
          <div class="loading-spinner">
            <i class="bi bi-arrow-clockwise spin"></i>
          </div>
          <p class="loading-text">Loading team tasks...</p>
        </div>

        <!-- if no tasks found -->
        <div v-else-if="!isLoadingTasks && filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-clipboard"></i>
          </div>
          <div class="empty-title">No tasks found :(</div>
          <p class="empty-subtitle">{{ getEmptyMessage() }}</p>
        </div>

        <div 
          v-else
          v-for="(task, index) in filteredTasks" 
          :key="task.id"
          class="task-card"
          :class="{ completed: task.status === 'Completed' }"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <!-- Main Task -->
          <div class="task-main" @click="navigateToTask(task.id)">
            <div class="task-content">
              <div class="task-header">
                <div class="task-title-section">
                  <h3 class="task-title" :class="{ completed: task.status === 'Completed' }">
                    {{ task.task_name }}
                  </h3>
                  <div class="task-badges">
                    <div class="task-status" :class="getStatusClass(task.status)">
                      <i :class="getStatusIcon(task.status)"></i>
                      <span>{{ getStatusLabel(task.status) }}</span>
                    </div>
                    <div class="task-priority" :class="getPriorityClass(task.priority)">
                      <i class="bi bi-flag-fill"></i>
                      <span>{{ task.priority }}</span>
                    </div>
                  </div>
                </div>
                <div class="task-people">
                  <div v-if="task.owner_id" class="task-owner">
                    <i class="bi bi-person-fill"></i>
                    <span class="owner-label">Owner:</span>
                    <span class="owner-name">{{ getUserName(task.owner_id) }}</span>
                  </div>
                  <div v-if="task.collaborators && task.collaborators.length > 0" class="task-collaborators">
                    <i class="bi bi-people-fill"></i>
                    <span class="collab-label">Collaborators:</span>
                    <span class="collab-names">
                      {{ task.collaborators.slice(0, 2).map(id => getUserName(id)).join(', ') }}
                      <span v-if="task.collaborators.length > 2" class="more-collabs">
                        +{{ task.collaborators.length - 2 }} more
                      </span>
                    </span>
                  </div>
                </div>
                <div class="task-meta">
                  <div class="task-date">
                    <i class="bi bi-calendar3"></i>
                    <span>{{ formatDate(task.due_date) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <div class="click-hint">
                <i class="bi bi-arrow-right"></i>
              </div>
            </div>
          </div>

          <!-- Subtasks Toggle -->
          <div 
            v-if="task.subtasks && task.subtasks.length > 0" 
            class="subtasks-toggle"
            @click="toggleSubtasks(task.id)"
          >
            <div class="toggle-content">
              <div class="toggle-info">
                <i class="bi bi-diagram-3"></i>
                <span>{{ task.subtasks.length }} subtask{{ task.subtasks.length !== 1 ? 's' : '' }}</span>
                <div class="subtask-progress">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: `${getSubtaskProgress(task)}%` }"
                    ></div>
                  </div>
                  <span class="progress-text">{{ getCompletedSubtasks(task) }}/{{ task.subtasks.length }}</span>
                </div>
              </div>
              <div class="toggle-icon" :class="{ expanded: expandedTasks.includes(task.id) }">
                <i class="bi bi-chevron-down"></i>
              </div>
            </div>
          </div>

          <!-- Subtasks -->
          <transition name="subtasks">
            <div v-if="task.subtasks && task.subtasks.length > 0 && expandedTasks.includes(task.id)" class="subtasks-section">
              <div 
                v-for="(subtask, subIndex) in task.subtasks" 
                :key="subtask.id"
                class="subtask"
                :class="{ completed: subtask.status === 'Completed' }"
                :style="{ animationDelay: `${subIndex * 0.03}s` }"
                @click="navigateToTask(subtask.id)"
              >
                <div class="subtask-content">
                  <div class="subtask-header">
                    <div class="subtask-title" :class="{ completed: subtask.status === 'Completed' }">
                      {{ subtask.task_name }}
                    </div>
                    <div class="task-status" :class="getStatusClass(subtask.status)">
                      <i :class="getStatusIcon(subtask.status)"></i>
                    </div>
                  </div>
                  <div class="subtask-meta">
                    <div class="subtask-date">
                      <i class="bi bi-calendar3"></i>
                      <span>{{ formatDate(subtask.due_date) }}</span>
                    </div>
                    <div v-if="subtask.owner_id" class="subtask-owner">
                      <i class="bi bi-person"></i>
                      <span>{{ getUserName(subtask.owner_id) }}</span>
                    </div>
                  </div>
                </div>
                <div class="subtask-action">
                  <i class="bi bi-arrow-right"></i>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../../components/SideNavbar.vue'
import { getCurrentUserData } from '../../services/session.js'
import "../taskview/taskview.css"

const activeFilter = ref('all')
const sortBy = ref('due_date')
const sortOrder = ref('asc')
const expandedTasks = ref([])
const userRole = ref('')
const userId = ref(null)
const teamId = ref(null)

const tasks = ref([])
const users = ref({})
const isLoadingTasks = ref(false)

// Get user data from session
onMounted(async () => {
  const userData = getCurrentUserData()
  userRole.value = userData.role?.toLowerCase() || ''
  userId.value = parseInt(userData.userid) || null
  
  console.log('Team Task View - User data from session:', userData)
  
  // Get user's team_id
  if (userId.value) {
    try {
      const response = await fetch(`http://localhost:5003/users/${userId.value}`)
      if (response.ok) {
        const data = await response.json()
        teamId.value = data.data?.team_id
        console.log('User team_id:', teamId.value)
        
        if (teamId.value) {
          await fetchTeamTasks()
        }
      }
    } catch (error) {
      console.error('Error fetching user details:', error)
    }
  }
})

// Function to fetch user details by userid
const fetchUserDetails = async (userid) => {
  if (!userid) return null
  if (users.value[userid]) {
    return users.value[userid]
  }
  
  try {
    const response = await fetch(`http://localhost:5003/users/${userid}`)
    if (response.ok) {
      const data = await response.json()
      const user = data.data
      if (user) {
        users.value[userid] = user
        return user
      }
    }
  } catch (error) {
    console.error(`Error fetching user ${userid}:`, error)
  }
  return null
}

// Function to get user names for display
const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || `User ${userid}`
}

// Function to fetch all users mentioned in tasks
const fetchTaskUsers = async () => {
  const userIds = new Set()
  
  tasks.value.forEach(task => {
    if (task.owner_id) userIds.add(task.owner_id)
    if (task.collaborators) {
      task.collaborators.forEach(id => userIds.add(id))
    }
    if (task.subtasks) {
      task.subtasks.forEach(subtask => {
        if (subtask.owner_id) userIds.add(subtask.owner_id)
        if (subtask.collaborators) {
          subtask.collaborators.forEach(id => userIds.add(id))
        }
      })
    }
  })
  
  const fetchPromises = Array.from(userIds).map(userid => fetchUserDetails(userid))
  await Promise.all(fetchPromises)
}

// Fetch team tasks
const fetchTeamTasks = async () => {
  if (!teamId.value) return
  
  isLoadingTasks.value = true
  
  try {
    const response = await fetch(`http://localhost:5002/tasks/team/${teamId.value}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    tasks.value = data.data || []
    console.log('Fetched team tasks:', tasks.value)
    
    await fetchTaskUsers()
  } catch (error) {
    console.error('Error fetching team tasks:', error)
    tasks.value = []
  } finally {
    isLoadingTasks.value = false
  }
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(task => task.status === activeFilter.value)
  }
  
  return filtered.sort((a, b) => {
    if (sortBy.value !== 'status') {
      if (a.status === 'Completed' && b.status !== 'Completed') return 1
      if (a.status !== 'Completed' && b.status === 'Completed') return -1
    }
    
    let comparison = 0
    
    switch (sortBy.value) {
      case 'due_date':
        comparison = new Date(a.due_date) - new Date(b.due_date)
        break
      case 'priority':
        comparison = parseInt(b.priority) - parseInt(a.priority)
        break
      case 'status':
        const statusOrder = { 'Unassigned': 0, 'Ongoing': 1, 'Under Review': 2, 'Completed': 3 }
        comparison = statusOrder[a.status] - statusOrder[b.status]
        break
      case 'name':
        comparison = a.task_name.localeCompare(b.task_name)
        break
      default:
        comparison = new Date(a.due_date) - new Date(b.due_date)
    }
    
    return sortOrder.value === 'asc' ? comparison : -comparison
  })
})

const toggleSubtasks = (taskId) => {
  const index = expandedTasks.value.indexOf(taskId)
  if (index > -1) {
    expandedTasks.value.splice(index, 1)
  } else {
    expandedTasks.value.push(taskId)
  }
}

const router = useRouter()

const navigateToTask = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-SG', { 
    timeZone: 'Asia/Singapore',
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
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
  return status
}

const getPriorityClass = (priority) => {
  const level = parseInt(priority)
  if (level >= 8) return 'priority-high'
  if (level >= 5) return 'priority-medium'
  return 'priority-low'
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

const getEmptyMessage = () => {
  const messages = {
    'all': 'No team tasks found.',
    'Ongoing': 'No ongoing team tasks.',
    'Under Review': 'No team tasks under review.',
    'Completed': 'No completed team tasks.',
    'Unassigned': 'No unassigned team tasks.'
  }
  return messages[activeFilter.value] || 'No team tasks found.'
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'Ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'Under Review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'Completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'Unassigned').length)
</script>