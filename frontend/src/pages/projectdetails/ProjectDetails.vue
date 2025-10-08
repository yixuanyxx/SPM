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
        <div class="header-section">
          <div class="header-content">
            <div class="projectdetails-header">
              <div class="title-section">
                <div class="title-row">
                  <h1 class="page-title">{{ project.proj_name }}</h1>
                  <div class="project-id">Project ID: #{{ project.id }}</div>
                </div>
              </div>
              <div class="header-actions">
                <button 
                  class="btn-primary edit-project-btn" 
                  @click="showEditModal = true"
                >
                  <i class="bi bi-pencil"></i>
                  Edit Project
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
                <div class="info-item">
                  <label>Owner:</label>
                  <span>{{ project.owner_id }}</span>
                </div>
                <div class="info-item">
                  <label>Collaborators:</label>
                  <div class="collaborators-list">
                    <div v-for="collab in filterCollaborators(project)" 
                         :key="collab" 
                         class="collaborator-chip">
                      {{ collab }}
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
                <div class="progress-bar">
                  <div class="progress-fill" 
                       :style="{ width: `${calculateProgress(project.tasks)}%` }">
                  </div>
                </div>
                <span class="progress-text">
                  {{ getCompletedTasksCount(project.tasks) }}/{{ (project.tasks || []).length }}
                </span>
              </div>
            </h3>
            <div class="block-content">
              <div v-if="!project.tasks || project.tasks.length === 0" 
                   class="no-tasks">
                No tasks in this project
              </div>
              <div v-else class="tasks-list">
                <div v-for="task in project.tasks" 
                     :key="task.id"
                     class="task-item"
                     @click="navigateToTask(task.id)">
                  <div class="task-content">
                    <h4 class="task-name">{{ task.task_name }}</h4>
                    <div class="task-meta">
                      <span :class="['status-badge', `status-${task.status.toLowerCase()}`]">
                        {{ task.status }}
                      </span>
                    </div>
                  </div>
                  <div class="task-arrow">
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
                <button @click="submitNewTask">Create</button>
                <button @click="showCreateModal = false">Cancel</button>
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



          <!-- Add the edit modal -->
          <div v-if="showEditModal" class="modal-overlay">
            <div class="modal-content">
              <div class="modal-header">
                <h2>Edit Project</h2>
                <button class="close-btn" @click="showEditModal = false">
                  <i class="bi bi-x"></i>
                </button>
              </div>

              <div class="form-group">
                <label>Project Name*</label>
                <input v-model="editedProject.proj_name" required />
              </div>

              <div class="form-group">
                <label>Collaborators</label>
                <div class="autocomplete">
                  <input 
                    type="text"
                    v-model="collaboratorQuery"
                    placeholder="Search users by email..."
                    @input="searchUsers"
                  />
                  
                  <ul v-if="collaboratorSuggestions.length > 0" class="suggestions-list">
                    <li 
                      v-for="user in collaboratorSuggestions" 
                      :key="user.id"
                      @click="addCollaborator(user)"
                      class="suggestion-item"
                    >
                      {{ user.email }}
                    </li>
                  </ul>
                </div>

                <div class="selected-collaborators">
                  <div 
                    v-for="collab in editedProject.collaborators" 
                    :key="collab.id"
                    class="collaborator-chip"
                  >
                    {{ collab.email }}
                    <button 
                      class="remove-collab-btn"
                      @click="removeCollaborator(collab)"
                    >
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="modal-actions">
                <button 
                  class="submit-btn" 
                  @click="updateProject"
                  :disabled="!isFormValid"
                >
                  Update Project
                </button>
                <button 
                  class="cancel-btn" 
                  @click="showEditModal = false"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
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
import '../projectdetails/projectdetails.css'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const collaboratorQuery = ref('')
const selectedCollaborators = ref([])
const collaboratorSuggestions = ref([])
const newTaskFile = ref(null)
const showErrorPopup = ref(false)
const errorMessage = ref('')
const userId = ref(getCurrentUserData().userid)
const userRole = ref(getCurrentUserData().role?.toLowerCase())

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

// Add the edited project data
const editedProject = ref({
  proj_name: '',
  collaborators: [],
})

onMounted(async () => {
  await fetchProjectDetails()
})

const fetchProjectDetails = async () => {
  try {
    loading.value = true
    error.value = null
    
    const projectId = route.params.id
    
    // Fetch project details
    const projectResponse = await fetch(`http://localhost:5001/projects/${projectId}`)
    if (!projectResponse.ok) {
      throw new Error(`Failed to fetch project: ${projectResponse.status}`)
    }
    const projectData = await projectResponse.json()
    
    // Fetch tasks for this project
    try {
      const tasksResponse = await fetch(`http://localhost:5002/tasks/project/${projectId}`)
      const tasksData = await tasksResponse.json()
      
      // Combine project and tasks data
      project.value = {
        ...(projectData.data || projectData),
        tasks: tasksData.data || tasksData.tasks || []
      }
    } catch (taskError) {
      // If tasks fetch fails, still show project with empty tasks array
      console.warn('Failed to fetch tasks:', taskError)
      project.value = {
        ...(projectData.data || projectData),
        tasks: []
      }
    }
    
    // Set edited project data
    editedProject.value = {
      proj_name: project.value.proj_name,
      collaborators: project.value.collaborators || [],
    }
    
    console.log('Project with tasks:', project.value)
    
  } catch (err) {
    error.value = err.message
    console.error('Error fetching project details:', err)
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
      showCreateModal.value = false
      
      // Reset form
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
      newTaskFile.value = null
    } else {
      throw new Error(data.Message || 'Failed to create task')
    }
  } catch (error) {
    errorMessage.value = error.message
    showErrorPopup.value = true
  }
}

const isFormValid = computed(() => {
  return editedProject.value.proj_name.trim() !== ''
})

const initializeEditForm = () => {
  editedProject.value = {
    proj_name: project.value.proj_name,
    collaborators: [...(project.value.collaborators || [])]
  }
}

const searchUsers = async () => {
  if (!collaboratorQuery.value) {
    collaboratorSuggestions.value = []
    return
  }

  try {
    const response = await fetch(
      `http://localhost:5003/users/search?email=${encodeURIComponent(collaboratorQuery.value)}`
    )
    if (!response.ok) throw new Error('Failed to fetch users')
    
    const data = await response.json()
    collaboratorSuggestions.value = data.data || []
  } catch (error) {
    console.error('Error searching users:', error)
    collaboratorSuggestions.value = []
  }
}

const updateProject = async () => {
  try {
    const response = await fetch(`http://localhost:5001/projects/update`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        project_id: project.value.id,
        proj_name: editedProject.value.proj_name,
        collaborators: editedProject.value.collaborators.map(c => 
          typeof c === 'object' ? c.id || c.userid : c
        )
      })
    })

    if (!response.ok) {
      throw new Error('Failed to update project')
    }

    // Refresh project details
    await fetchProjectDetails()
    showEditModal.value = false

    // Show success message
    // You can add a success notification here if needed
  } catch (error) {
    console.error('Error updating project:', error)
    errorMessage.value = error.message
    showErrorPopup.value = true
  }
}

// Initialize edit form when edit modal is shown
watch(() => showEditModal.value, (newValue) => {
  if (newValue) {
    initializeEditForm()
  }
})
</script>