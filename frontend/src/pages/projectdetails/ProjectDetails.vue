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
        <p>Loading project details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <div class="error-icon">
          <i class="bi bi-exclamation-triangle"></i>
        </div>
        <h3>Error Loading Project</h3>
        <p>{{ error }}</p>
        <button @click="goBack" class="btn btn-secondary">
          <i class="bi bi-arrow-left"></i>
          Go Back
        </button>
      </div>

      <!-- Project Details Content -->
      <div v-else-if="project" class="project-details-content">
        <!-- Breadcrumb Navigation -->
        <div class="breadcrumb-section">
          <nav class="breadcrumb-nav">
            <button @click="goBack" class="breadcrumb-item">
              <i class="bi bi-house"></i>
              Projects
            </button>
            <i class="bi bi-chevron-right breadcrumb-separator"></i>
            <span class="breadcrumb-current">{{ project.proj_name }}</span>
          </nav>
        </div>

        <!-- Header Section -->
        <div class="project-details-header-section">
          <div class="header-content">
            <div class="projectdetails-header">
              <div class="project-details-title-section">
                <div class="project-details-title-row">
                  <h1 class="project-details-page-title">{{ project.proj_name }}</h1>
                  <div class="project-id">Project ID: #{{ project.id }}</div>
                </div>
              </div>
              <div class="project-details-header-actions">
                <button 
                  class="btn btn-primary" 
                  @click="navigateToWorkload"
                >
                  <i class="bi bi-bar-chart"></i>
                  View Workload
                </button>
                <button 
                  class="btn btn-ghost" 
                  @click="openEditProject"
                >
                  <i class="bi bi-pencil"></i>
                  Edit
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="maindetails-content">
          <!-- Project Details -->
          <div class="content-block">
            <h3 class="block-title">Project Information</h3>
            <div class="block-content">
              <div class="info-grid">
                <div class="property-item">
                  <label class="property-label">
                    <i class="bi bi-person"></i>
                    Owner
                  </label>
                  <div class="property-value">
                    <div class="user-chip">
                      <div class="user-avatar">
                        <i class="bi bi-person-circle"></i>
                      </div>
                      <span>{{ getUserName(project.owner_id) }}</span>
                    </div>
                  </div>
                </div>

                <div v-if="project.collaborators && project.collaborators.length > 0" 
                     class="property-item">
                  <label class="property-label">
                    <i class="bi bi-people"></i>
                    Collaborators
                  </label>
                  <div class="property-value">
                    <div class="collaborators-list">
                      <div v-for="collaboratorId in filterCollaborators(project)" 
                           :key="collaboratorId" 
                           class="user-chip">
                        <div class="user-avatar">
                          <i class="bi bi-person-circle"></i>
                        </div>
                        <span>{{ getUserName(collaboratorId) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Project Tasks -->
          <div class="content-block">
            <h3 class="block-title">
              <i class="bi bi-list-task"></i>
              Tasks
              <div class="tasks-progress">
                <div class="project-details-progress-bar">
                  <div class="project-details-progress-fill" 
                       :style="{ width: `${calculateProgress(project.tasks)}%` }">
                  </div>
                </div>
                <span class="project-details-progress-text">
                  {{ getCompletedTasksCount(project.tasks) }}/{{ (project.tasks || []).length }}
                </span>
              </div>
            </h3>
            <div class="block-content">
              <div v-if="!project.tasks || project.tasks.length === 0" 
                   class="no-tasks">
                No tasks in this project
              </div>
              <div v-else class="project-details-tasks-list">
                <div v-for="task in project.tasks" 
                     :key="task.id"
                     class="project-details-task-item"
                     @click="navigateToTask(task.id)">
                  <div class="project-details-task-content">
                    <h4 class="project-details-task-name">{{ task.task_name }}</h4>
                    <div class="project-details-task-meta">
                      <span :class="['project-details-status-badge', `project-details-status-${task.status.toLowerCase().replace(' ', '-')}`]">
                        {{ task.status }}
                      </span>
                    </div>
                  </div>
                  <div class="project-details-task-arrow">
                    <i class="bi bi-arrow-right"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Create Task Section -->
          <div class="create-task-section">
            <button class="create-task-btn" @click="showCreateModal = true">
              <i class="bi bi-plus-lg"></i>
              Add Task
            </button>
          </div>

          <!-- Create Task Modal -->
          <div v-if="showCreateModal" class="popup-overlay" @click.self="handleCloseCreateTask">
            <div class="popup-container">
              <!-- Header -->
              <div class="popup-header">
                <h3>Create New Task for {{ project.proj_name }}</h3>
                <button class="close-btn" @click="handleCloseCreateTask">&times;</button>
              </div>

              <div class="popup-content">
                <form @submit.prevent="submitNewTask">
                  <!-- Task Name -->
                  <div class="form-group">
                    <label for="task_name">Task Name<span class="required">*</span></label>
                    <input
                      type="text"
                      id="task_name"
                      v-model="newTask.task_name"
                      :disabled="isCreatingTask"
                      :class="{ 'input-error': showErrors && !newTask.task_name }"
                      placeholder="Enter task name..."
                      class="form-input"
                    />
                  </div>

                  <!-- Description -->
                  <div class="form-group">
                    <label for="description">Description<span class="required">*</span></label>
                    <textarea
                      id="description"
                      v-model="newTask.description"
                      rows="3"
                      :disabled="isCreatingTask"
                      :class="{ 'input-error': showErrors && !newTask.description }"
                      placeholder="Enter task description..."
                    ></textarea>
                  </div>

                  <!-- Due Date -->
                  <div class="form-group">
                    <label for="due_date">Due Date<span class="required">*</span></label>
                    <input
                      type="datetime-local"
                      id="due_date"
                      v-model="newTask.due_date"
                      :disabled="isCreatingTask"
                      :class="{ 'input-error': showErrors && !newTask.due_date }"
                      :min="getTodayDateTime()"
                      class="form-input"
                    />
                  </div>

                  <!-- Reminder Intervals -->
                  <div class="form-group">
                    <label for="reminder_intervals">Reminder Intervals</label>
                    <input
                      type="text"
                      id="reminder_intervals"
                      v-model="newTask.reminder_intervals"
                      :disabled="isCreatingTask"
                      placeholder="e.g., 7, 3, 1"
                      class="form-input"
                    />
                    <div class="field-hint">
                      Default: 7, 3, 1 days before due date. Enter comma-separated numbers (e.g., 10, 5, 2)
                    </div>
                  </div>

                  <!-- Status -->
                  <div class="form-group">
                    <label for="status">Status</label>
                    <select
                      id="status"
                      v-model="newTask.status"
                      :disabled="isCreatingTask"
                      class="form-select"
                    >
                      <option v-if="userRole === 'manager' || userRole === 'director'" value="Unassigned">Unassigned</option>
                      <option value="Ongoing">Ongoing</option>
                      <option value="Under Review">Under Review</option>
                      <option value="Completed">Completed</option>
                    </select>
                  </div>

                  <!-- Priority Slider -->
                  <div class="form-group">
                    <label for="priority">Priority Level: {{ newTask.priority }}</label>
                    <div class="priority-slider-wrapper">
                      <input
                        id="priority"
                        type="range"
                        min="1"
                        max="10"
                        v-model="newTask.priority"
                        :disabled="isCreatingTask"
                        class="priority-slider"
                      />
                      <div class="priority-range-labels">
                        <span>1 - Least Important</span>
                        <span>10 - Most Important</span>
                      </div>
                    </div>
                  </div>

                  <!-- Collaborators -->
                  <div class="form-group">
                    <label>Collaborators (emails)</label>
                    <div class="autocomplete">
                      <input 
                        type="text"
                        v-model="collaboratorQuery"
                        placeholder="Type email..."
                        class="form-input"
                        :disabled="isCreatingTask"
                      />

                      <ul v-if="collaboratorSuggestions.length > 0" class="suggestions-list">
                        <li 
                          v-for="user in collaboratorSuggestions" 
                          :key="user.userid"
                          @click="addCollaborator(user)"
                          class="suggestion-item"
                        >
                          {{ user.email }}
                        </li>
                      </ul>

                      <div class="selected-collaborators">
                        <span 
                          v-for="(user, index) in selectedCollaborators" 
                          :key="index"
                          :class="['selected-email', { 'creator-locked': user.isCreator }]"
                        >
                          {{ user.email }}
                          <i 
                            v-if="user.isCreator"
                            class="bi bi-lock-fill"
                            title="Task creator (cannot be removed)"
                          ></i>
                          <i 
                            v-else
                            class="bi bi-x" 
                            @click="removeCollaborator(user)"
                          ></i>
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Attachment -->
                  <div class="form-group">
                    <label>Attach PDF</label>
                    <input
                      type="file"
                      @change="handleFileUpload"
                      accept="application/pdf"
                      :disabled="isCreatingTask"
                      class="file-input"
                    />
                    <span class="file-hint">Only PDF files allowed</span>
                  </div>

                  <!-- Recurrence Type -->
                  <div class="form-group">
                    <label for="recurrence_type">Recurrence</label>
                    <select 
                      id="recurrence_type" 
                      v-model="newTask.recurrence_type" 
                      :disabled="isCreatingTask" 
                      class="form-select"
                    >
                      <option :value="null">-- None --</option>
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="bi-weekly">Bi-Weekly</option>
                      <option value="monthly">Monthly</option>
                      <option value="yearly">Yearly</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>

                  <!-- Custom Interval -->
                  <div v-if="newTask.recurrence_type === 'custom'" class="form-group">
                    <label for="recurrence_interval_days">Repeat Every (Days)<span class="required">*</span></label>
                    <input
                      type="number"
                      id="recurrence_interval_days"
                      v-model.number="newTask.recurrence_interval_days"
                      min="1"
                      placeholder="Enter number of days (e.g. 10)"
                      :disabled="isCreatingTask"
                      :required="newTask.recurrence_type === 'custom'"
                      class="form-input"
                    />
                  </div>

                  <!-- Recurrence End Date -->
                  <div v-if="newTask.recurrence_type !== null" class="form-group">
                    <label for="recurrence_end_date">Recurrence End Date</label>
                    <input
                      type="datetime-local"
                      id="recurrence_end_date"
                      v-model="newTask.recurrence_end_date"
                      :disabled="isCreatingTask"
                      :min="getTodayDateTime()"
                      class="form-input"
                    />
                  </div>

                  <!-- Actions -->
                  <div class="form-actions">
                    <button 
                      type="submit" 
                      :disabled="isCreatingTask"
                      class="btn-primary"
                    >
                      <i class="bi bi-plus-circle" v-if="!isCreatingTask"></i>
                      <i class="bi bi-arrow-repeat spin" v-else></i>
                      {{ isCreatingTask ? 'Creating...' : 'Create Task' }}
                    </button>
                    <button 
                      type="button" 
                      @click="handleCloseCreateTask" 
                      :disabled="isCreatingTask"
                      class="btn-secondary"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- Success Popup -->
          <div v-if="taskSuccessMessage" class="success-popup">
            <i class="bi bi-check-circle-fill"></i> {{ taskSuccessMessage }}
          </div>

          <!-- Error Popup -->
          <div v-if="taskErrorMessage" class="error-popup">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <span>{{ taskErrorMessage }}</span>
            <button class="close-btn" @click="taskErrorMessage = ''">&times;</button>
          </div>

          <!-- Edit Project Component -->
          <EditProject
            :isVisible="showEditProject"
            :projectId="project?.id"
            :currentProjectName="project?.proj_name || ''"
            :currentCollaborators="project?.collaborators || []"
            @close="closeEditProject"
            @update-success="handleProjectUpdate"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCurrentUserData } from '../../services/session.js'
import SideNavbar from '../../components/SideNavbar.vue'
import EditProject from '../../components/EditProject.vue'
import '../projectdetails/projectdetails.css'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)
const showEditProject = ref(false)
const newTaskFile = ref(null)
const showErrorPopup = ref(false)
const errorMessage = ref('')
const userId = ref(getCurrentUserData().userid)
const userRole = ref(getCurrentUserData().role?.toLowerCase())
const users = ref({}) // Add this with your other refs

// Create Task Modal Variables
const collaboratorQuery = ref('')
const collaboratorSuggestions = ref([])
const selectedCollaborators = ref([])
const isCreatingTask = ref(false)

// Add the new task form data
const newTask = ref({
  owner_id: userId.value,
  task_name: '',
  description: '',
  type: 'parent',
  status: (userRole.value === 'manager' || userRole.value === 'director') ? 'Unassigned' : 'Ongoing',
  due_date: '',
  priority: 5,
  recurrence_type: null,
  recurrence_end_date: null,
  recurrence_interval_days: null,
  reminder_intervals: ''
})

// Add these refs
const showErrors = ref(false)
const taskSuccessMessage = ref('')
const taskErrorMessage = ref('')
const currentUserData = ref(getCurrentUserData())
const userEmail = ref(currentUserData.value.email || '')
const allUsers = ref([])

onMounted(async () => {
  await fetchProjectDetails()
})

// Watch for route parameter changes to reload project details
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    await fetchProjectDetails()
  }
}, { immediate: false })

const fetchProjectDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const projectId = route.params.id
    
    // Validate project ID
    if (!projectId || isNaN(projectId)) {
      throw new Error('Invalid project ID')
    }
    
    // Fetch project details
    const projectResponse = await fetch(`http://localhost:5001/projects/${projectId}`)
    if (!projectResponse.ok) {
      if (projectResponse.status === 404) {
        throw new Error('Project not found')
      } else if (projectResponse.status === 500) {
        throw new Error('Server error - project may not exist')
      } else {
        throw new Error(`Failed to fetch project: ${projectResponse.status}`)
      }
    }
    const projectData = await projectResponse.json()
    
    // Validate project data
    if (!projectData || (!projectData.data && !projectData.proj_name)) {
      throw new Error('Invalid project data received')
    }
    
    // Get initial project data
    project.value = {
      ...(projectData.data || projectData),
      tasks: []
    }
    
    // Ensure required fields exist
    if (!project.value.proj_name) {
      throw new Error('Project name is missing')
    }

    // Fetch all user details
    await fetchProjectUsers()
    
    // Fetch tasks for this project
    try {
      const tasksResponse = await fetch(`http://localhost:5002/tasks/project/${projectId}`)
      const tasksData = await tasksResponse.json()
      project.value.tasks = tasksData.data || tasksData.tasks || []
    } catch (taskError) {
      console.warn('Failed to fetch tasks:', taskError)
      project.value.tasks = []
    }
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/projects')
}

const navigateToTask = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const navigateToWorkload = () => {
  router.push(`/tasks/projects?projectId=${project.value.id}`)
}

const filterCollaborators = (project) => {
  if (!project.collaborators) return []
  return project.collaborators.filter(collab => collab !== project.owner_id)
}

const calculateProgress = (tasks) => {
  if (!tasks || tasks.length === 0) return 0
  const completed = tasks.filter(task => task.status === 'Completed').length
  return Math.round((completed / tasks.length) * 100)
}

const getCompletedTasksCount = (tasks) => {
  if (!tasks) return 0
  return tasks.filter(task => task.status === 'Completed').length
}

// Add this helper method
const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || 'Unknown User'
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file && file.type === "application/pdf") {
    newTaskFile.value = file
    taskErrorMessage.value = ''
  } else {
    taskErrorMessage.value = "Only PDF files are allowed"
    event.target.value = null
    newTaskFile.value = null
    setTimeout(() => {
      taskErrorMessage.value = ''
    }, 3000)
  }
}

const addCollaborator = (user) => {
  if (!selectedCollaborators.value.find(u => u.userid === user.userid)) {
    selectedCollaborators.value.push(user)
  }
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
}

const removeCollaborator = (user) => {
  if (user.isCreator) {
    taskErrorMessage.value = "Cannot remove task creator from collaborators"
    setTimeout(() => {
      taskErrorMessage.value = ''
    }, 2000)
    return
  }
  selectedCollaborators.value = selectedCollaborators.value.filter(u => u.userid !== user.userid)
}

// Watch for collaborator query changes
watch(collaboratorQuery, async (query) => {
  if (!query) {
    collaboratorSuggestions.value = []
    return
  }

  try {
    const res = await fetch(`http://localhost:5003/users/search?q=${encodeURIComponent(query)}`)
    if (!res.ok) throw new Error('Failed to fetch user emails')
    const data = await res.json()
    
    // Filter out already selected collaborators
    collaboratorSuggestions.value = (data.data || []).filter(user => 
      !selectedCollaborators.value.some(c => c.userid === user.userid)
    )
  } catch (err) {
    console.error(err)
    collaboratorSuggestions.value = []
  }
})

const getTodayDateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
}

// Update submitNewTask with comprehensive validation
const submitNewTask = async () => {
  // Validation
  if (!newTask.value.task_name?.trim() || !newTask.value.description?.trim() || !newTask.value.due_date) {
    showErrors.value = true
    taskErrorMessage.value = "Please fill out all required fields: Task Name, Description, and Due Date."
    return
  }

  // Validate due date is not in the past
  const selectedDate = new Date(newTask.value.due_date)
  const now = new Date()
  if (selectedDate < now) {
    taskErrorMessage.value = "Due date cannot be in the past. Please select today or a future date."
    return
  }

  // Validate recurrence end date if set
  if (newTask.value.recurrence_type && newTask.value.recurrence_end_date) {
    const endDate = new Date(newTask.value.recurrence_end_date)
    const startDate = new Date(newTask.value.due_date)
    if (endDate < startDate) {
      taskErrorMessage.value = "Recurrence end date cannot be before the task's due date."
      return
    }
  }

  // Validate custom recurrence interval
  if (
    newTask.value.recurrence_type === "custom" &&
    (!newTask.value.recurrence_interval_days || newTask.value.recurrence_interval_days < 1)
  ) {
    taskErrorMessage.value = "Please enter a valid recurrence interval (in days) for custom recurrence."
    return
  }

  isCreatingTask.value = true
  taskErrorMessage.value = ''
  taskSuccessMessage.value = ''

  try {
    const endpoint = (userRole.value === 'manager' || userRole.value === 'director')
      ? 'http://localhost:5002/tasks/manager-task/create'
      : 'http://localhost:5002/tasks/staff-task/create'

    const formData = new FormData()
    
    // Add task data
    formData.append('owner_id', newTask.value.owner_id)
    formData.append('task_name', newTask.value.task_name)
    formData.append('description', newTask.value.description)
    formData.append('type', 'parent')
    formData.append('status', newTask.value.status)
    formData.append('priority', newTask.value.priority)
    formData.append('project_id', project.value.id)

    // Add due date in UTC
    if (newTask.value.due_date) {
      const localDate = new Date(newTask.value.due_date)
      const utcDateString = localDate.toISOString()
      formData.append('due_date', utcDateString)
    }

    // Add collaborators
    const collaboratorIds = selectedCollaborators.value.map(user => parseInt(user.userid))
    if (userRole.value === 'staff' && !collaboratorIds.includes(newTask.value.owner_id)) {
      collaboratorIds.push(newTask.value.owner_id)
    }
    if (collaboratorIds.length > 0) {
      formData.append('collaborators', collaboratorIds.join(','))
    }

    // Add file if present
    if (newTaskFile.value) {
      formData.append('attachment', newTaskFile.value)
    }

    // Add reminder intervals
    if (newTask.value.reminder_intervals && newTask.value.reminder_intervals.trim()) {
      formData.append('reminder_intervals', newTask.value.reminder_intervals.trim())
    }

    // Add recurrence data
    if (newTask.value.recurrence_type) {
      formData.append('recurrence_type', newTask.value.recurrence_type)

      if (newTask.value.recurrence_end_date) {
        const endUTC = new Date(newTask.value.recurrence_end_date).toISOString()
        formData.append('recurrence_end_date', endUTC)
      } else {
        formData.append('recurrence_end_date', '')
      }
      
      if (newTask.value.recurrence_type === 'custom' && newTask.value.recurrence_interval_days) {
        formData.append('recurrence_interval_days', newTask.value.recurrence_interval_days)
      }
    } else {
      formData.append('recurrence_type', 'None')
      formData.append('recurrence_end_date', '')
    }

    console.log('Creating task in project:', project.value.id)

    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData
    })

    const data = await response.json()

    if (response.ok && data.Code === 201) {
      // Show success message
      taskSuccessMessage.value = 'Task created successfully!'
      
      // Update project collaborators with task collaborators
      if (collaboratorIds.length > 0) {
        await updateProjectCollaborators(collaboratorIds)
      }
      
      // Wait a moment for the success message to be visible
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Refresh project details to show the new task
      await fetchProjectDetails()
      
      // Reset form and close modal
      resetCreateTaskForm()
      showCreateModal.value = false
      
      // Clear success message after modal closes
      setTimeout(() => {
        taskSuccessMessage.value = ''
      }, 500)
      
    } else {
      throw new Error(data.Message || 'Failed to create task')
    }
  } catch (error) {
    console.error('Error creating task:', error)
    taskErrorMessage.value = error.message || 'Failed to create task'
  } finally {
    isCreatingTask.value = false
  }
}

// Edit Project methods
const openEditProject = () => {
  showEditProject.value = true
}

const closeEditProject = () => {
  showEditProject.value = false
}

const handleProjectUpdate = async (updateData) => {
  // Refresh project details to show updated data
  await fetchProjectDetails()
  closeEditProject()
}

// Create Task Modal Methods
const resetCreateTaskForm = () => {
  const defaultStatus = (userRole.value === 'manager' || userRole.value === 'director') ? 'Unassigned' : 'Ongoing'
  
  newTask.value = {
    owner_id: userId.value,
    task_name: '',
    description: '',
    type: 'parent',
    status: defaultStatus,
    due_date: '',
    priority: 5,
    recurrence_type: null,
    recurrence_end_date: null,
    recurrence_interval_days: null,
    reminder_intervals: ''
  }
  
  // Reset collaborators - only add creator for STAFF
  if (userRole.value === 'staff' && userEmail.value && userId.value) {
    selectedCollaborators.value = [{
      userid: userId.value,
      email: userEmail.value,
      isCreator: true
    }]
  } else {
    selectedCollaborators.value = []
  }
  
  newTaskFile.value = null
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
  taskErrorMessage.value = ''
  taskSuccessMessage.value = ''
  showErrors.value = false
}

const closeCreateTaskModal = () => {
  showCreateModal.value = false
  resetCreateTaskForm()
}

// Add updateProjectCollaborators method
const updateProjectCollaborators = async (taskCollaboratorIds) => {
  if (!taskCollaboratorIds || taskCollaboratorIds.length === 0) return

  try {
    const projectCollaborators = project.value.collaborators || []
    const projectOwnerId = parseInt(project.value.owner_id)
    
    const projectCollaboratorsSet = new Set(
      projectCollaborators.map(collab => parseInt(collab))
    )
    
    const newCollaborators = taskCollaboratorIds.filter(
      collabId => {
        const id = parseInt(collabId)
        return !projectCollaboratorsSet.has(id) && id !== projectOwnerId
      }
    )

    console.log('Task collaborators:', taskCollaboratorIds)
    console.log('Project collaborators:', projectCollaborators)
    console.log('New collaborators to add:', newCollaborators)

    if (newCollaborators.length > 0) {
      const updateResponse = await fetch(`http://localhost:5001/projects/update`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          project_id: project.value.id,
          collaborators: [...projectCollaborators, ...newCollaborators]
        })
      })

      if (!updateResponse.ok) {
        throw new Error('Failed to update project collaborators')
      }

      console.log('Project collaborators updated successfully')
      
      await Promise.all(newCollaborators.map(id => fetchUserDetails(id)))
    }
  } catch (error) {
    console.error('Error updating project collaborators:', error)
  }
}

// Update the fetchProjectUsers function
const fetchProjectUsers = async () => {
  const userIds = new Set()
  
  // Collect all unique user IDs from project
  if (project.value.owner_id) userIds.add(project.value.owner_id)
  if (project.value.collaborators) {
    project.value.collaborators.forEach(id => userIds.add(id))
  }
  
  // Fetch user details for all unique IDs
  const fetchPromises = Array.from(userIds).map(userid => fetchUserDetails(userid))
  const results = await Promise.all(fetchPromises)
  console.log(`Fetched ${results.filter(r => r !== null).length} users out of ${userIds.size}`)
}

// Update the fetchUserDetails function
const fetchUserDetails = async (userid) => {
  if (!userid) return null
  if (users.value[userid]) {
    return users.value[userid] // Return cached user
  }
  
  try {
    console.log(`Fetching user details for userid: ${userid}`)
    const response = await fetch(`http://localhost:5003/users/${userid}`)
    if (response.ok) {
      const data = await response.json()
      console.log(`User data received for ${userid}:`, data)
      const user = data.data
      if (user) {
        users.value[userid] = user
        console.log(`Cached user ${userid}:`, user)
        return user
      }
    } else {
      console.error(`Failed to fetch user ${userid}: ${response.status}`)
    }
  } catch (error) {
    console.error(`Error fetching user ${userid}:`, error)
  }
  return null
}

// Watch for modal opening to reset form
watch(showCreateModal, (newValue) => {
  if (newValue) {
    resetCreateTaskForm()
  }
})

// Initialize collaborators on mount
onMounted(async () => {
  await fetchProjectDetails()
  
  // Auto-add creator for staff when component mounts
  if (userRole.value === 'staff' && userEmail.value && userId.value) {
    selectedCollaborators.value = [{
      userid: userId.value,
      email: userEmail.value,
      isCreator: true
    }]
  }
})
</script>