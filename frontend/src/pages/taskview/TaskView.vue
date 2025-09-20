<template>
  <div class="app-layout">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section ms-5">
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
        
        <div class="stat-card" @click="activeFilter = 'ongoing'" :class="{ active: activeFilter === 'ongoing' }">
          <div class="stat-content">
            <div class="stat-icon ongoing">
              <i class="bi bi-play-circle"></i>
            </div>
            <div class="stat-info">
              <div class="stat-number">{{ ongoingTasks }}</div>
              <div class="stat-title">In Progress</div>
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
              <div class="stat-title">Review</div>
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
              <div class="stat-title">Done</div>
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
    'completed': 'bi-check-circle-fill'
  }
  return icons[status] || 'bi-circle'
}

const getStatusLabel = (status) => {
  const labels = {
    'ongoing': 'In Progress',
    'under-review': 'Review',
    'completed': 'Done'
  }
  return labels[status] || 'Todo'
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
    'completed': 'No completed tasks yet.'
  }
  return messages[activeFilter.value] || 'No tasks found.'
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'under-review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'completed').length)
</script>

<style scoped>
/* Layout: make the page fill the viewport with sidebar */
.app-layout {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
}

.app-container {
  /* Use dynamic viewport height to avoid mobile browser UI issues */
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: 2rem;
  box-sizing: border-box;
  flex: 1;
  margin-left: 250px; /* Account for sidebar width */
}

.main-content {
  /* Take up remaining space and allow internal scrolling if needed */
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

/* Center main inner containers while keeping them responsive */
.header-content,
.stats-container,
.tasks-container {
  width: 100%;
  margin: 0 auto;
}

/* Header */
.header-section {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 0.25rem 0;
  letter-spacing: -0.01em;
}

.page-subtitle {
  font-size: 0.95rem;
  color: #6b7280;
  margin: 0;
  font-weight: 400;
}

/* Stats */
.stats-section {
  margin-bottom: 2rem;
}

.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  max-width: 800px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  cursor: pointer;
  transition: all 0.2s ease;
}

.stat-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-card.active {
  border-color: #3b82f6;
  background: #f8faff;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.stat-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.stat-icon.total { background: #f3f4f6; color: #374151; }
.stat-icon.ongoing { background: #fef3c7; color: #d97706; }
.stat-icon.under-review { background: #e0e7ff; color: #6366f1; }
.stat-icon.completed { background: #d1fae5; color: #059669; }

.stat-number {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1a1a1a;
  line-height: 1;
}

.stat-title {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 500;
}

/* Tasks */
.tasks-container {
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.task-card {
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  animation: slideIn 0.3s ease-out both;
}

.task-card.completed {
  opacity: 0.7;
}

.task-main {
  display: flex;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 1px solid transparent;
}

.task-main:hover {
  background: #f9fafb;
}

.task-main:hover .click-hint {
  opacity: 1;
  transform: translateX(0);
}

.task-content {
  flex: 1;
}

.task-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.task-title-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.task-title {
  font-size: 0.95rem;
  font-weight: 500;
  color: #1a1a1a;
  margin: 0;
  line-height: 1.4;
}

.task-title.completed {
  text-decoration: line-through;
  color: #9ca3af;
}

.task-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  white-space: nowrap;
}

.task-status.ongoing {
  background: #fef3c7;
  color: #d97706;
}

.task-status.under-review {
  background: #e0e7ff;
  color: #6366f1;
}

.task-status.completed {
  background: #d1fae5;
  color: #059669;
}

.task-meta {
  display: flex;
  align-items: center;
}

.task-date {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.task-actions {
  margin-left: 1rem;
}

.click-hint {
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s ease;
  color: #9ca3af;
  font-size: 0.8rem;
}

/* Subtasks Toggle */
.subtasks-toggle {
  padding: 0.75rem 1rem;
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
  cursor: pointer;
  transition: all 0.2s ease;
}

.subtasks-toggle:hover {
  background: #f3f4f6;
}

.toggle-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toggle-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: #6b7280;
}

.subtask-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.progress-bar {
  width: 40px;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #10b981;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.7rem;
  color: #9ca3af;
}

.toggle-icon {
  transition: transform 0.2s ease;
  color: #9ca3af;
}

.toggle-icon.expanded {
  transform: rotate(180deg);
}

/* Subtasks */
.subtasks-section {
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
}

.subtask {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  transition: all 0.2s ease;
  animation: slideInSubtask 0.3s ease-out both;
}

.subtask:last-child {
  border-bottom: none;
}

.subtask:hover {
  background: #f3f4f6;
}

.subtask:hover .subtask-action {
  opacity: 1;
  transform: translateX(0);
}

.subtask.completed {
  opacity: 0.6;
}

.subtask-content {
  flex: 1;
}

.subtask-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.subtask-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
  margin: 0;
}

.subtask-title.completed {
  text-decoration: line-through;
  color: #9ca3af;
}

.subtask-date {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

.subtask-action {
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.2s ease;
  color: #9ca3af;
  font-size: 0.7rem;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-title {
  font-size: 1rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.empty-subtitle {
  font-size: 0.85rem;
  margin: 0;
}

/* Animations */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideInSubtask {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Subtasks Transition */
.subtasks-enter-active,
.subtasks-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.subtasks-enter-from,
.subtasks-leave-to {
  max-height: 0;
  opacity: 0;
}

.subtasks-enter-to,
.subtasks-leave-from {
  max-height: 500px;
  opacity: 1;
}

/* Responsive */
@media (max-width: 768px) {
  .app-container {
    padding: 1rem;
    margin-left: 200px; /* Smaller sidebar width on mobile */
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .task-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .toggle-info {
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .app-container {
    margin-left: 0; /* Remove sidebar margin on small screens */
    padding: 1rem;
  }
  
  .stats-container {
    grid-template-columns: 1fr;
  }
  
  .subtask-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
