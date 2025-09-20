<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">My Tasks</h1>
          <p class="page-subtitle">View and Create Tasks Here</p>
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
        
        <!-- Unassigned status card - only show for managers and directors -->
        <div v-if="isManagerOrDirector" class="stat-card" @click="activeFilter = 'unassigned'" :class="{ active: activeFilter === 'unassigned' }">
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
        
        <div class="stat-card" @click="activeFilter = 'ongoing'" :class="{ active: activeFilter === 'ongoing' }">
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
        
        <div class="stat-card" @click="activeFilter = 'under-review'" :class="{ active: activeFilter === 'under-review' }">
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
        
        <div class="stat-card" @click="activeFilter = 'completed'" :class="{ active: activeFilter === 'completed' }">
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
      <!-- Tasks -->
      <div class="tasks-container">

        <!-- if no tasks found -->
        <div v-if="filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-clipboard"></i>
          </div>
          <div class="empty-title">No tasks found. Create one now!</div>
          <p class="empty-subtitle">{{ getEmptyMessage() }}</p>
        </div>

        <div 
          v-for="(task, index) in filteredTasks" 
          :key="task.id"
          class="task-card"
          :class="{ completed: task.status === 'completed' }"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <!-- Main Task -->
          <div class="task-main" @click="navigateToTask(task.id)">
            <div class="task-content">
              <div class="task-header">
                <div class="task-title-section">
                  <h3 class="task-title" :class="{ completed: task.status === 'completed' }">
                    {{ task.name }}
                  </h3>
                  <div class="task-status" :class="task.status">
                    <i :class="getStatusIcon(task.status)"></i>
                    <span>{{ getStatusLabel(task.status) }}</span>
                  </div>
                </div>
                <div class="task-meta">
                  <div class="task-date">
                    <i class="bi bi-calendar3"></i>
                    <span>{{ formatDate(task.dueDate) }}</span>
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
                :class="{ completed: subtask.status === 'completed' }"
                :style="{ animationDelay: `${subIndex * 0.03}s` }"
                @click="navigateToTask(subtask.id)"
              >
                <div class="subtask-content">
                  <div class="subtask-header">
                    <div class="subtask-title" :class="{ completed: subtask.status === 'completed' }">
                      {{ subtask.name }}
                    </div>
                    <div class="task-status" :class="subtask.status">
                      <i :class="getStatusIcon(subtask.status)"></i>
                    </div>
                  </div>
                  <div class="subtask-date">
                    <i class="bi bi-calendar3"></i>
                    <span>{{ formatDate(subtask.dueDate) }}</span>
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
import SideNavbar from '../../components/SideNavbar.vue'
import "./taskview.css"

const activeFilter = ref('all')
const expandedTasks = ref([])
const userRole = ref('manager') // change back to ref('') after testing

// Get user role from localStorage on component mount
// onMounted(() => {
//   const storedRole = localStorage.getItem('userRole') || localStorage.getItem('role') || ''
//   userRole.value = storedRole.toLowerCase()
// })

// Check if user is manager or director
const isManagerOrDirector = computed(() => {
  return ['manager', 'director'].includes(userRole.value)
})

// const tasks = ref([]) // where the fetched data will be stored

// const userId = 2 // CHANGE THIS TO GET FROM LOCAL STORAGE (CODE BELOW)
// // const userId = localStorage.getItem("UID") // check the way user id is stored in table

// onMounted(() => {
//   fetch(`http://localhost:5002/tasks/user-task/${userId}`)
//     .then(response => {
//       if (!response.ok) {
//         throw new Error(`HTTP error! status: ${response.status}`)
//       }
//       return response.json()
//     })
//     .then(data => {
//       // API returns { "tasks": [ {...}, {...} ] }
//       tasks.value = data.tasks
//       console.log('Fetched tasks:', tasks.value)
//     })
//     .catch(error => {
//       console.error('Error fetching tasks:', error)
//     })
// })

const tasks = ref([
  {
    id: 1,
    name: 'Complete project proposal',
    dueDate: '2024-01-15',
    status: 'under-review',
    subtasks: [
      { id: 11, name: 'Research competitors', dueDate: '2024-01-12', status: 'completed' },
      { id: 12, name: 'Write executive summary', dueDate: '2024-01-14', status: 'under-review' },
      { id: 13, name: 'Create budget breakdown', dueDate: '2024-01-15', status: 'ongoing' }
    ]
  },
  {
    id: 2,
    name: 'Client meeting preparation',
    dueDate: '2024-01-08',
    status: 'completed',
    subtasks: [
      { id: 21, name: 'Prepare presentation slides', dueDate: '2024-01-07', status: 'completed' },
      { id: 22, name: 'Review client requirements', dueDate: '2024-01-08', status: 'completed' }
    ]
  },
  {
    id: 3,
    name: 'Review team performance',
    dueDate: '2024-01-10',
    status: 'completed',
    subtasks: []
  },
  {
    id: 4,
    name: 'Update website content',
    dueDate: '2024-01-20',
    status: 'ongoing',
    subtasks: [
      { id: 41, name: 'Write new blog post', dueDate: '2024-01-18', status: 'ongoing' },
      { id: 42, name: 'Update team page', dueDate: '2024-01-19', status: 'ongoing' }
    ]
  },
  {
    id: 5,
    name: 'Plan quarterly review',
    dueDate: '2024-01-25',
    status: 'ongoing',
    subtasks: []
  },
  {
    id: 6,
    name: 'Assign new developer tasks',
    dueDate: '2024-01-30',
    status: 'unassigned',
    subtasks: []
  },
  {
    id: 7,
    name: 'Review budget allocations',
    dueDate: '2024-02-01',
    status: 'unassigned',
    subtasks: []
  }
])

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(task => task.status === activeFilter.value)
  }
  
  return filtered.sort((a, b) => {
    if (a.status === 'completed' && b.status !== 'completed') return 1
    if (a.status !== 'completed' && b.status === 'completed') return -1
    return new Date(a.dueDate) - new Date(b.dueDate)
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

const navigateToTask = (taskId) => {
  console.log(`Navigating to task ${taskId}`)
  // Example: this.$router.push(`/tasks/${taskId}`)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
  })
}

const getStatusIcon = (status) => {
  const icons = {
    'ongoing': 'bi-play-circle',
    'under-review': 'bi-eye',
    'completed': 'bi-check-circle-fill',
    'unassigned': 'bi-person-dash'
  }
  return icons[status] || 'bi-circle'
}

const getStatusLabel = (status) => {
  const labels = {
    'ongoing': 'Ongoing',
    'under-review': 'Under Review',
    'completed': 'Completed',
    'unassigned': 'Unassigned'
  }
  return labels[status]
}

const getSubtaskProgress = (task) => {
  if (!task.subtasks || task.subtasks.length === 0) return 0
  const completed = task.subtasks.filter(subtask => subtask.status === 'completed').length
  return Math.round((completed / task.subtasks.length) * 100)
}

const getCompletedSubtasks = (task) => {
  if (!task.subtasks) return 0
  return task.subtasks.filter(subtask => subtask.status === 'completed').length
}

const getEmptyMessage = () => {
  const messages = {
    'all': 'Add some tasks to get started!',
    'ongoing': 'No tasks in progress.',
    'under-review': 'No tasks under review.',
    'completed': 'No completed tasks yet.',
    'unassigned': 'No unassigned tasks.'
  }
  return messages[activeFilter.value] || 'No tasks found.'
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'under-review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'unassigned').length)
</script>
