<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Schedule</h1>
          <p class="page-subtitle">View your tasks and deadlines</p>
        </div>
      </div>

      <!-- Calendar Controls -->
      <div class="calendar-controls">
        <div class="view-toggle">
          <button 
            v-for="view in views" 
            :key="view.value"
            @click="currentView = view.value"
            :class="['view-btn', { active: currentView === view.value }]"
          >
            <i :class="view.icon"></i>
            {{ view.label }}
          </button>
        </div>
        
        <div class="date-navigation">
          <button @click="previousPeriod" class="nav-btn">
            <i class="bi bi-chevron-left"></i>
          </button>
          <h2 class="current-period">{{ currentPeriodTitle }}</h2>
          <button @click="nextPeriod" class="nav-btn">
            <i class="bi bi-chevron-right"></i>
          </button>
        </div>
        
        <div class="today-btn">
          <button @click="goToToday" class="today-button">
            <i class="bi bi-calendar-check"></i>
            Today
          </button>
          <!-- <button @click="fetchTasks" class="refresh-button" :disabled="loading">
            <i class="bi bi-arrow-clockwise" :class="{ 'spinning': loading }"></i>
            Refresh
          </button> -->
        </div>
      </div>

      <!-- Calendar Content -->
      <div class="calendar-container">
        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>Loading your tasks...</p>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="!loading && tasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-calendar-x"></i>
          </div>
          <h3>No tasks found</h3>
          <p>You don't have any tasks scheduled yet.</p>
        </div>
        <!-- Calendar Views -->
        <div v-else>
          <!-- Daily View -->
          <div v-if="currentView === 'day'" class="daily-view">
          <div class="day-header">
            <h3>{{ formatDate(currentDate, 'EEEE, MMMM d, yyyy') }}</h3>
            <div class="day-stats">
              <span class="task-count">{{ getTasksForDate(currentDate).length }} tasks</span>
            </div>
          </div>
          
          <div class="day-timeline">
            <div v-for="hour in 24" :key="hour" class="time-slot">
              <div class="time-label">{{ formatHour(hour - 1) }}</div>
              <div class="time-content">
                <div 
                  v-for="task in getTasksForDateAndHour(currentDate, hour - 1)" 
                  :key="task.id"
                  class="task-event"
                  :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                  @click="selectTask(task)"
                >
                  <div class="task-title">{{ task.task_name }}</div>
                  <div class="task-meta">
                    <div class="task-status-badge" :class="getTaskStatusClass(task.status)">
                      {{ task.status }}
                    </div>
                    <div class="task-time">{{ formatTime(task.due_date) }}</div>
                  </div>
                  <button 
                    v-if="isTaskOverdue(task)" 
                    class="reschedule-btn" 
                    @click.stop="openRescheduleModal(task)"
                  >
                    Reschedule
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Weekly View -->
        <div v-if="currentView === 'week'" class="weekly-view">
          <div class="week-header">
            <div class="day-header" v-for="day in weekDays" :key="day.date">
              <div class="day-name">{{ formatDate(day.date, 'EEE') }}</div>
              <div class="day-number" :class="{ today: isToday(day.date) }">
                {{ formatDate(day.date, 'd') }}
              </div>
              <div class="day-tasks-count">{{ getTasksForDate(day.date).length }}</div>
            </div>
          </div>
          
          <div class="week-grid">
            <div v-for="day in weekDays" :key="day.date" class="day-column">
              <div 
                v-for="task in getTasksForDate(day.date)" 
                :key="task.id"
                class="task-item"
                :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                @click="onTaskClick(task, $event)"
              >
                <div class="task-title">{{ task.task_name }}</div>
                <div class="task-status-badge" :class="getTaskStatusClass(task.status)">
                  {{ task.status }}
                </div>
                <div class="task-time">{{ formatTime(task.due_date) }}</div>
                <button 
                  v-if="isTaskOverdue(task)" 
                  class="reschedule-btn" 
                  @click.stop="openRescheduleModal(task)"
                >
                Reschedule
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Monthly View -->
        <div v-if="currentView === 'month'" class="monthly-view">
          <div class="month-grid">
            <div 
              v-for="day in monthDays" 
              :key="day.date" 
              class="month-day"
              :class="{ 
                'other-month': !day.isCurrentMonth,
                'today': isToday(day.date),
                'has-tasks': getTasksForDate(day.date).length > 0
              }"
              @click="selectDate(day.date)"
            >
              <div class="day-number">{{ formatDate(day.date, 'd') }}</div>
              <div class="day-tasks">
                <div 
                  v-for="task in getTasksForDate(day.date)" 
                  :key="task.id"
                  class="task-box"
                  :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                  :title="`${task.task_name} - ${task.status}`"
                >
                  <div class="task-box-name">{{ task.task_name }}</div>
                  <div class="task-box-status">{{ task.status }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Task Details Modal -->
      <div v-if="selectedTask" class="task-modal-overlay" @click="selectedTaskForDetails = null">
        <div class="task-modal" @click.stop>
          <div class="modal-header">
            <h3>{{ selectedTask.task_name }}</h3>
            <button @click="closeTaskModal" class="close-btn">
              <i class="bi bi-x"></i>
            </button>
          </div>
          <div class="modal-content">
            <div class="task-details">
              <div class="detail-row">
                <span class="label">Status:</span>
                <span class="value" :class="getTaskStatusClass(selectedTask.status)">
                  {{ selectedTask.status }}
                </span>
              </div>
              <div class="detail-row">
                <span class="label">Type:</span>
                <span class="value">{{ selectedTask.type || 'N/A' }}</span>
              </div>
              <div class="detail-row" v-if="selectedTask.project_id">
                <span class="label">Project ID:</span>
                <span class="value">{{ selectedTask.project_id }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Due Date:</span>
                <span class="value">{{ formatDate(selectedTask.due_date, 'EEEE, MMMM d, yyyy') }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Time:</span>
                <span class="value">{{ formatTime(selectedTask.due_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="label">Description:</span>
                <span class="value">{{ selectedTask.description || 'No description' }}</span>
              </div>
              <div class="detail-row" v-if="selectedTask.collaborators && selectedTask.collaborators.length > 0">
                <span class="label">Collaborators:</span>
                <span class="value">{{ selectedTask.collaborators.join(', ') }}</span>
              </div>
              <div class="detail-row" v-if="selectedTask.attachments && selectedTask.attachments.length > 0">
                <span class="label">Attachments:</span>
                <span class="value">
                  <div v-for="attachment in selectedTask.attachments" :key="attachment.name">
                    {{ attachment.name }}
                  </div>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <!-- Reschedule Modal -->
      <div v-if="showRescheduleModal" class="modal-overlay">
        <div class="modal-content">
          <h3>Reschedule Task</h3>
          <p><strong>{{ selectedTaskForReschedule?.task_name }}</strong></p>

          <label for="newDueDate">New Due Date:</label>
          <input id="newDueDate" type="datetime-local" v-model="newDueDate" class="date-picker" :min="todayString" />

          <div class="modal-actions">
            <button class="confirm-btn" @click="confirmReschedule">Save</button>
            <button class="cancel-btn" @click="closeRescheduleModal">Cancel</button>
          </div>
        </div>
      </div>
      <!-- Success Popup -->
      <div v-if="successMessage" class="success-popup">
        {{ successMessage }}
      </div>

      <!-- Error Popup -->
      <div v-if="errorMessage" class="error-popup">
        <span>{{ errorMessage }}</span>
        <button class="close-btn" @click="errorMessage = ''">&times;</button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import SideNavbar from '../../components/SideNavbar.vue'
import { sessionState } from '../../services/session.js'

// Reactive data
const currentView = ref('week')
const currentDate = ref(new Date())
const selectedTask = ref(null)
const tasks = ref([])
const loading = ref(false)
const selectedTaskForDetails = ref(null)
const selectedTaskForReschedule = ref(null)

// Calendar views configuration
const views = [
  { value: 'day', label: 'Day', icon: 'bi bi-calendar-day' },
  { value: 'week', label: 'Week', icon: 'bi bi-calendar-week' },
  { value: 'month', label: 'Month', icon: 'bi bi-calendar-month' }
]

// Computed properties
const currentPeriodTitle = computed(() => {
  switch (currentView.value) {
    case 'day':
      return formatDate(currentDate.value, 'EEEE, MMMM d, yyyy')
    case 'week':
      const weekStart = getWeekStart(currentDate.value)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      return `${formatDate(weekStart, 'MMM d')} - ${formatDate(weekEnd, 'MMM d, yyyy')}`
    case 'month':
      return formatDate(currentDate.value, 'MMMM yyyy')
    default:
      return ''
  }
})

const weekDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value)
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(weekStart)
    date.setDate(weekStart.getDate() + i)
    return { date }
  })
})

const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  // Calculate start date - beginning of the week containing the first day of the month
  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  
  // Calculate end date - end of the week containing the last day of the month
  const endDate = new Date(lastDay)
  endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()))
  
  // Calculate total weeks needed to show the complete month
  const totalWeeks = Math.ceil((endDate - startDate) / (7 * 24 * 60 * 60 * 1000))
  const totalDays = totalWeeks * 7
  
  const days = []
  const current = new Date(startDate)
  
  // Generate the exact number of days needed (either 35 for 5 weeks or 42 for 6 weeks)
  for (let i = 0; i < totalDays; i++) {
    const dayDate = new Date(current)
    days.push({
      date: dayDate,
      isCurrentMonth: current.getMonth() === month
    })
    current.setDate(current.getDate() + 1)
  }
  
  return days
})

// Methods
const formatDate = (date, format = 'yyyy-MM-dd') => {
  if (!date) return ''
  
  const d = new Date(date)
  const options = {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Singapore'
  }
  
  if (format === 'EEEE, MMMM d, yyyy') {
    return d.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      timeZone: 'Asia/Singapore'
    })
  } else if (format === 'EEE') {
    return d.toLocaleDateString('en-US', { weekday: 'short', timeZone: 'Asia/Singapore' })
  } else if (format === 'd') {
    return d.getDate().toString()
  } else if (format === 'MMM d') {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'Asia/Singapore' })
  } else if (format === 'MMMM yyyy') {
    return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric', timeZone: 'Asia/Singapore' })
  }
  
  return d.toLocaleDateString('en-US', { timeZone: 'Asia/Singapore' })
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit',
    timeZone: 'Asia/Singapore'
  })
}

const formatHour = (hour) => {
  return `${hour.toString().padStart(2, '0')}:00`
}

const getWeekStart = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day
  return new Date(d.setDate(diff))
}

const isToday = (date) => {
  const today = new Date()
  const d = new Date(date)
  return d.toDateString() === today.toDateString()
}

const getTasksForDate = (date) => {
  if (!date || !tasks.value || !Array.isArray(tasks.value) || !tasks.value.length) return []
  
  // Convert the target date to Singapore timezone and get YYYY-MM-DD
  const targetDate = new Date(date)
  const targetDateString = targetDate.toLocaleDateString('en-CA', { 
    timeZone: 'Asia/Singapore' 
  }) // en-CA gives YYYY-MM-DD format
  
  const filteredTasks = tasks.value.filter(task => {
    if (!task.due_date) return false
    try {
      // Convert task due date to Singapore timezone and get YYYY-MM-DD
      const taskDate = new Date(task.due_date)
      const taskDateString = taskDate.toLocaleDateString('en-CA', { 
        timeZone: 'Asia/Singapore' 
      })
      return taskDateString === targetDateString
    } catch (error) {
      console.warn('Error parsing task date:', task.due_date, error)
      return false
    }
  })
  
  return filteredTasks.sort((a, b) => {
    const timeA = new Date(a.due_date).getTime()
    const timeB = new Date(b.due_date).getTime()
    return timeA - timeB})
}

const getTasksForDateAndHour = (date, hour) => {
  const dayTasks = getTasksForDate(date)
  return dayTasks.filter(task => {
    if (!task.due_date) return false
    const taskDate = new Date(task.due_date)
    // Get the hour in Singapore timezone
    const singaporeHour = parseInt(taskDate.toLocaleTimeString('en-US', { 
      timeZone: 'Asia/Singapore',
      hour12: false,
      hour: '2-digit'
    }))
    return singaporeHour === hour
  })
}

const getTaskStatusClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'unassigned': return 'status-unassigned'
    case 'ongoing': return 'status-ongoing'
    case 'under review': return 'status-under-review'
    case 'completed': return 'status-completed'
    default: return 'status-default'
  }
}

const isTaskOverdue = (task) => {
  if (!task.due_date) return false
  
  const now = new Date()
  const due = new Date(task.due_date)
  return due < now && task.status?.toLowerCase() !== 'completed'
}

const onTaskClick = (task, event) => {
  // If the click came from the Reschedule button, do nothing
  if (event.target.closest('.reschedule-btn')) return;

  // Otherwise, open task details modal
  selectTask(task)
}

const selectTask = (task) => {
  selectedTask.value = task
}

const closeTaskModal = () => {
  selectedTask.value = null
}

const selectDate = (date) => {
  currentDate.value = new Date(date)
  currentView.value = 'day'
}

const previousPeriod = () => {
  const newDate = new Date(currentDate.value)
  switch (currentView.value) {
    case 'day':
      newDate.setDate(newDate.getDate() - 1)
      break
    case 'week':
      newDate.setDate(newDate.getDate() - 7)
      break
    case 'month':
      newDate.setMonth(newDate.getMonth() - 1)
      break
  }
  currentDate.value = newDate
}

const nextPeriod = () => {
  const newDate = new Date(currentDate.value)
  switch (currentView.value) {
    case 'day':
      newDate.setDate(newDate.getDate() + 1)
      break
    case 'week':
      newDate.setDate(newDate.getDate() + 7)
      break
    case 'month':
      newDate.setMonth(newDate.getMonth() + 1)
      break
  }
  currentDate.value = newDate
}

const goToToday = () => {
  currentDate.value = new Date()
}

const fetchTasks = async () => {
  loading.value = true
  
  try {
    // Get user ID from session
    const userId = sessionState.userid
    if (!userId) {
      console.warn('No user ID found in session')
      tasks.value = []
      return
    }
    
    // Fetch tasks directly from API endpoint
    const response = await fetch(`http://127.0.0.1:5002/tasks/user-task/${userId}`, {
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      const msg = await response.text().catch(() => response.statusText)
      throw new Error(msg || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    console.log('API Response:', data)
    
    if (data && data.tasks && data.tasks.data) {
      const allTasks = []
      
      // Process parent tasks and their subtasks
      data.tasks.data.forEach(parentTask => {
        // Add parent task
        allTasks.push(parentTask)
        
        // Add subtasks if they exist
        if (parentTask.subtasks && Array.isArray(parentTask.subtasks)) {
          parentTask.subtasks.forEach(subtask => {
            allTasks.push(subtask)
          })
        }
      })
      
      tasks.value = allTasks
      console.log('Loaded tasks:', allTasks.length, 'total tasks')
      
      // Debug timezone handling
      allTasks.forEach(task => {
        if (task.due_date) {
          const taskDate = new Date(task.due_date)
          const sgDateString = taskDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Singapore' })
          const sgTimeString = taskDate.toLocaleTimeString('en-US', { timeZone: 'Asia/Singapore' })
          console.log(`Task "${task.task_name}": UTC ${task.due_date} -> SG ${sgDateString} ${sgTimeString}`)
        }
      })
    } else {
      console.warn('Unexpected API response format:', data)
      tasks.value = []
    }
  } catch (error) {
    console.error('Error fetching tasks:', error)
    tasks.value = []
  } finally {
    loading.value = false
  }
}

// Modal state
const showRescheduleModal = ref(false)
const newDueDate = ref('')
const todayString = ref(new Date().toISOString().split('T')[0])
const successMessage = ref('')
const errorMessage = ref('')

const openRescheduleModal = (task) => {
  selectedTaskForReschedule.value = task
  newDueDate.value = task.due_date ? task.due_date.split('T')[0] : todayString.value
  showRescheduleModal.value = true
}

const closeRescheduleModal = () => {
  showRescheduleModal.value = false
  selectedTaskForReschedule.value = null
  newDueDate.value = ''
}

const showSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => {
    successMessage.value = ''
  }, 3000) // auto-hide after 3s
}

const showError = (msg) => {
  errorMessage.value = msg
  setTimeout(() => {
    errorMessage.value = ''
  }, 5000) // auto-hide after 5s
}


const confirmReschedule = async () => {
  if (!newDueDate.value) {
    showError('Please select a new due date.')
    return
  }
  if (newDueDate.value < todayString.value) {
    showError('Cannot reschedule to a date before today.');
    return;
  }

  try {
    const localDate = new Date(newDueDate.value)
      // Convert to ISO string in UTC
    const utcDateString = localDate.toISOString() // format: "2025-10-07T02:45:00.000Z"
    const payload = {
      task_id: selectedTaskForReschedule.value.id,
      due_date: utcDateString
    }

    const res = await fetch('http://127.0.0.1:5002/tasks/update', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()

    if (data.Code === 200) {
      selectedTaskForReschedule.value.due_date = newDueDate.value
      showSuccess('Task rescheduled successfully!')
    } else {
      showError(`Failed to reschedule: ${data.Message}`)
    }
  } catch (err) {
    console.error(err)
    showError('Error rescheduling task.')
  } finally {
    closeRescheduleModal()
  }
}

// Lifecycle
onMounted(() => {
  fetchTasks()
})

// Watch for userid changes
watch(() => sessionState.userid, (newUserId) => {
  if (newUserId) {
    fetchTasks()
  }
})

// Simple debug function
window.debugCalendar = {
  getTasksForDate: (dateString) => {
    const date = new Date(dateString)
    return getTasksForDate(date)
  },
  goToDate: (dateString) => {
    const date = new Date(dateString)
    currentDate.value = date
    console.log(`Navigated to: ${date.toDateString()}`)
  }
}
</script>

<style scoped>
@import './scheduleview.css';
</style>
