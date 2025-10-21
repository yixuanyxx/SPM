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
          <div v-if="showCreateModal" class="modal-overlay">
            <div class="modal-content">
              <h2>Create New Task for {{ project.proj_name }}</h2>

              <label>Task Name* </label>
              <input v-model="newTask.task_name" placeholder="Enter task name" required/>

              <label>Description* </label>
              <textarea v-model="newTask.description" placeholder="Enter description" required></textarea>

              <label>Due Date* </label>
              <input type="datetime-local" v-model="newTask.due_date" required/>

              <div class="form-group mt-4">
                <label for="priority">Priority Level: {{ newTask.priority }}</label>
                <div class="priority-slider-container">
                  <input
                    id="priority"
                    type="range"
                    min="1"
                    max="10"
                    v-model="newTask.priority"
                    class="priority-slider"
                  />
                </div>
              </div>

              <label>Status</label>
              <select v-model="newTask.status">
                <option value="Unassigned">Unassigned</option>
                <option value="Ongoing">Ongoing</option>
                <option value="Under Review">Under Review</option>
                <option value="Completed">Completed</option>
              </select>

              <label>Collaborators (emails)</label>
              <div class="autocomplete">
                <input 
                  type="text"
                  v-model="collaboratorQuery"
                  placeholder="Type email..."
                />

                <ul v-if="collaboratorSuggestions.length > 0" class="suggestions-list">
                  <li 
                    v-for="user in collaboratorSuggestions" 
                    :key="user.id"
                    @click="addCollaborator(user)"
                  >
                    {{ user.email }}
                  </li>
                </ul>

                <div class="selected-collaborators">
                  <span 
                    v-for="user in selectedCollaborators" 
                    :key="user.id" 
                    class="selected-email"
                  >
                    {{ user.email }} <i class="bi bi-x" @click="removeCollaborator(user)"></i>
                  </span>
                </div>
              </div>

              <label>Attach PDF</label>
              <input type="file" @change="handleFileUpload" accept="application/pdf" />

              <div class="modal-actions">
                <button @click="submitNewTask" :disabled="isCreatingTask">
                  <i v-if="isCreatingTask" class="bi bi-arrow-repeat spin"></i>
                  {{ isCreatingTask ? 'Creating...' : 'Create' }}
                </button>
                <button @click="closeCreateTaskModal" :disabled="isCreatingTask">Cancel</button>
              </div>

              <!-- Error Popup -->
              <div v-if="showErrorPopup" class="error-popup">
                <p>{{ errorMessage }}</p>
                <button @click="showErrorPopup = false" class="btn-close">
                  <i class="bi bi-x"></i>
                </button>
              </div>
            </div>
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
  due_date: '',
  priority: '5',
  status: 'Ongoing',
  project_id: '', // Will be set automatically
  collaborators: [],
})


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

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file && file.type === "application/pdf") {
    newTaskFile.value = file
    errorMessage.value = ''
  } else {
    errorMessage.value = "Only PDF files are allowed"
    showErrorPopup.value = true
    event.target.value = null
    newTaskFile.value = null
  }
}

const addCollaborator = (user) => {
  if (!selectedCollaborators.value.find(u => u.id === user.id)) {
    selectedCollaborators.value.push(user)
  }
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
}

const removeCollaborator = (user) => {
  selectedCollaborators.value = selectedCollaborators.value.filter(u => u.id !== user.id)
}

// Watch for collaborator query changes
watch(collaboratorQuery, async (query) => {
  if (!query) {
    collaboratorSuggestions.value = []
    return
  }

  try {
    const res = await fetch(`http://localhost:5003/users/search?email=${encodeURIComponent(query)}`)
    if (!res.ok) throw new Error('Failed to fetch user emails')
    const data = await res.json()
    collaboratorSuggestions.value = data.data || []
  } catch (err) {
    console.error(err)
    collaboratorSuggestions.value = []
  }
})

const submitNewTask = async () => {
  if (!newTask.value.task_name || !newTask.value.description || !newTask.value.due_date) {
    errorMessage.value = 'Please fill out all required fields'
    showErrorPopup.value = true
    return
  }

  isCreatingTask.value = true
  try {
    const endpoint = (userRole.value === 'manager' || userRole.value === 'director')
      ? 'http://localhost:5002/tasks/manager-task/create'
      : 'http://localhost:5002/tasks/staff-task/create'

    const formData = new FormData()
    
    // Add task data
    Object.keys(newTask.value).forEach(key => {
      if (key === 'project_id') {
        formData.append(key, project.value.id) // Use current project ID
      } else {
        formData.append(key, newTask.value[key])
      }
    })

    // Add collaborators
    const collaboratorIds = selectedCollaborators.value.map(user => user.userid)
    if (userRole.value === 'staff' && !collaboratorIds.includes(userId.value)) {
      collaboratorIds.push(userId.value)
    }
    if (collaboratorIds.length > 0) {
      formData.append('collaborators', collaboratorIds.join(','))
    }

    // Add file if present
    if (newTaskFile.value) {
      formData.append('attachment', newTaskFile.value)
    }

    const response = await fetch(endpoint, {
      method: 'POST',
      body: formData
    })

    const data = await response.json()

    if (response.ok && data.Code === 201) {
      // Refresh project details to show new task
      await fetchProjectDetails()
      closeCreateTaskModal()
    } else {
      throw new Error(data.Message || 'Failed to create task')
    }
  } catch (error) {
    errorMessage.value = error.message
    showErrorPopup.value = true
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
  newTask.value = {
    owner_id: userId.value,
    task_name: '',
    description: '',
    type: 'parent',
    due_date: '',
    priority: '5',
    status: 'Ongoing',
    project_id: '',
    collaborators: [],
  }
  selectedCollaborators.value = []
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
  newTaskFile.value = null
  errorMessage.value = ''
  showErrorPopup.value = false
  isCreatingTask.value = false
}

const closeCreateTaskModal = () => {
  showCreateModal.value = false
  resetCreateTaskForm()
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


// Add this helper method
const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || 'Unknown User'
}
</script>