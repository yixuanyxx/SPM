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
        <button class="create-task-btn" @click="showCreateModal = true">
            <i class="bi bi-plus-lg"></i>
            Create New Task
        </button>
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
        <div v-if="isManagerOrDirector" class="stat-card" @click="activeFilter = 'Unassigned'" :class="{ active: activeFilter === 'Unassigned' }">
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
      <!-- Tasks -->
      <div class="tasks-container">

        <!-- if no tasks found -->
        <div v-if="filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-clipboard"></i>
          </div>
          <div class="empty-title">No tasks found :(</div>
          <p class="empty-subtitle">{{ getEmptyMessage() }}</p>
        </div>

        <div 
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
                  <div class="task-status" :class="getStatusClass(task.status)">
                    <i :class="getStatusIcon(task.status)"></i>
                    <span>{{ getStatusLabel(task.status) }}</span>
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
                  <div class="subtask-date">
                    <i class="bi bi-calendar3"></i>
                    <span>{{ formatDate(subtask.due_date) }}</span>
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
    <!-- Create Task Modal -->
    <div v-if="showCreateModal" class="modal-overlay">
      <div class="modal-content">
        <h2>Create New Task</h2>

        <label>Task Name* </label>
        <input v-model="newTask.task_name" placeholder="Enter task name" :class="{ 'input-error': newTask.task_name.trim() === '' }" required/>

        <label>Description* </label>
        <textarea v-model="newTask.description" placeholder="Enter description" :class="{ 'input-error': newTask.description.trim() === '' }" required></textarea>

        <label>Due Date* </label>
        <input type="date" v-model="newTask.due_date" :class="{ 'input-error': newTask.due_date.trim() === '' }" required/>

        <label>Status</label>
        <select v-model="newTask.status">
          <option v-if="isManagerOrDirector" value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>

        <label>Project ID</label>
        <input type="text" v-model="newTask.project_id" placeholder="Enter project ID" />

        <label>Collaborators (comma-separated)</label>
        <input type="text" v-model="newTask.collaborators" placeholder="e.g., 101,102,103" />

        <label>Subtask IDs (comma-separated)</label>
        <input type="text" v-model="newTask.subtasks" placeholder="e.g., 201,202" />

        <div class="modal-actions">
          <button @click="submitNewTask" :disabled="!isFormValid" :class="{ 'btn-disabled': !isFormValid }">
            Create
          </button>
          <button @click="showCreateModal = false">Cancel</button>
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
import "./taskview.css"

const activeFilter = ref('all')
const expandedTasks = ref([])
const userRole = ref('')
const showCreateModal = ref(false);

// Get user role from localStorage on component mount
// onMounted(() => {
//   const storedRole = localStorage.getItem('userRole') || localStorage.getItem('role') || ''
//   userRole.value = storedRole.toLowerCase()
// })

// Check if user is manager or director
const isManagerOrDirector = computed(() => {
  return ['manager', 'director'].includes(userRole.value)
})

const tasks = ref([]) // where the fetched data will be stored

// const userId = 101 // CHANGE THIS TO GET FROM LOCAL STORAGE (CODE BELOW)
const userId = localStorage.getItem("spm_userid") // check the way user id is stored in table

onMounted(() => {
  fetch(`http://localhost:5002/tasks/user-task/${userId}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      return response.json()
    })
    .then(data => {
      // API returns { "tasks": [ {...}, {...} ] }
      tasks.value = data.tasks.data
      console.log('Fetched tasks:', tasks.value)
    })
    .catch(error => {
      console.error('Error fetching tasks:', error)
    })
})

const newTask = ref({
  owner_id: userId,
  task_name: '',
  description: '',
  type: 'parent',
  due_date: '',
  status: 'Ongoing',
  project_id: '',
  collaborators: '',
  parent_task: '',
  subtasks: ''
})

const isFormValid = computed(() => {
  return newTask.value.task_name.trim() !== '' &&
         newTask.value.description.trim() !== '' &&
         newTask.value.due_date.trim() !== ''   
})

// send POST to backend
const submitNewTask = async () => {
  if (!newTask.value.task_name || !newTask.value.description || !newTask.value.due_date) {
    alert('Please fill out all required fields: Task Name, Description, and Due Date.')
    return
  }
  try {
    let endpoint = userRole.value === 'manager'
      ? 'http://localhost:5002/tasks/manager-task/create'
      : 'http://localhost:5002/tasks/staff-task/create'

    // convert comma-separated strings to arrays where needed
    const payload = {
      ...newTask.value,
      collaborators: newTask.value.collaborators
        ? newTask.value.collaborators.split(',').map(id => id.trim())
        : [],
      subtasks: newTask.value.subtasks
        ? newTask.value.subtasks.split(',').map(id => id.trim())
        : []
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (response.ok && data.Code === 201) {
      tasks.value.push(data.data)
      // reset form
      newTask.value = {
        owner_id: userId,
        task_name: '',
        description: '',
        type: 'parent',
        due_date: '',
        status: 'Unassigned',
        project_id: '',
        collaborators: '',
        parent_task: '',
        subtasks: ''
      }
      showCreateModal.value = false
    } else {
      alert('Failed: ' + data.Message)
    }
  } catch (err) {
    console.error(err)
    alert('Error creating task')
  }
}

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(task => task.status === activeFilter.value)
  }
  
  return filtered.sort((a, b) => {
    if (a.status === 'Completed' && b.status !== 'Completed') return 1
    if (a.status !== 'Completed' && b.status === 'Completed') return -1
    return new Date(a.due_date) - new Date(b.due_date)
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
  console.log(`Navigating to task ${taskId}`)
  router.push(`/tasks/${taskId}`)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
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
  const labels = {
    'Ongoing': 'Ongoing',
    'Under Review': 'Under Review',
    'Completed': 'Completed',
    'Unassigned': 'Unassigned'
  }
  return labels[status]
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
    'all': 'Add some tasks to get started!',
    'Ongoing': 'No tasks in progress.',
    'Under Review': 'No tasks under review.',
    'Completed': 'No completed tasks yet.',
    'Unassigned': 'No unassigned tasks.'
  }
  return messages[activeFilter.value] || 'No tasks found.'
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'Ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'Under Review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'Completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'Unassigned').length)
</script>