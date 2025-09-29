<template>
    <div class="app-layout ms-2">
      <!-- Side Navigation -->
      <SideNavbar />
      
      <!-- Main Content Area -->
      <div class="app-container">
        <!-- Header Section -->
        <div class="header-section">
          <div class="header-content">
            <h1 class="page-title">My Projects</h1>
            <p class="page-subtitle">View and manage your project collaborations</p>
          </div>
          <button class="create-project-btn" @click="showCreateModal = true">
            <i class="bi bi-plus-lg"></i>
            Create New Project
          </button>
        </div>

        <!-- Main Content -->
        <div class="main-content">
          <!-- if no projects found -->
          <div v-if="projects.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="bi bi-folder"></i>
            </div>
            <div class="empty-title">No projects found</div>
            <p class="empty-subtitle">Create your first project to get started!</p>
          </div>

          <div v-else class="projects-grid">
            <!-- Dynamic Project Cards -->
            <div v-for="project in projects" 
                 :key="project.id" 
                 class="project-card" 
                 @click="handleCardClick(project)">
              <div class="project-header">
                <h3 class="project-title">{{ project.proj_name }}</h3>
                <span class="project-id">Project ID: {{ project.id }}</span>

              </div>
  
              <div class="project-meta">
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-person"></i>
                  </div>
                  <span>Project Owner: <span class="owner-name">{{project.owner_id || 'Unknown'}}</span></span>
                </div>
                <div class="meta-item">
                  <div class="meta-icon">
                    <i class="bi bi-people"></i>
                  </div>
                  <span>Collaborators:</span>
                  <div class="collaborators">
                    <div v-for="(collab, index) in filterCollaborators(project)" 
                        :key="index" 
                        class="avatar">
                      {{ getInitials(collab.name || collab.toString()) }}
                    </div>
                    <div v-if="filterCollaborators(project).length > 3" 
                        class="avatar more-collaborators">
                      +{{ filterCollaborators(project).length - 3 }}
                    </div>
                  </div>
                </div>
              </div>
  
              <div class="progress-section">
                <div class="progress-bar">
                  <div class="progress-fill" 
                       :style="{ width: calculateProgress(project.tasks) + '%' }">
                  </div>
                </div>
                <div class="progress-text">
                  {{ getCompletedTasksCount(project.tasks) }} of {{ (project.tasks || []).length }} tasks completed
                </div>
              </div>

              

              <div class="my-tasks">
                <div class="tasks-header">
                  <span class="tasks-title">My Tasks</span>
                </div>
                <div v-if="getMyTasks(project.tasks).length === 0" class="no-tasks">
                  No tasks assigned
                </div>
                <div v-else class="task-list">
                  <div v-for="task in getMyTasks(project.tasks)" 
                      :key="task.id" 
                      class="task-item">
                    <div class="task-content">
                      <span class="task-name">{{ task.task_name }}</span>
                    </div>
                    <span :class="['status-badge', `status-${task.status.toLowerCase()}`]">
                      {{ task.status }}
                    </span>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      <!-- Create Project Modal -->
      <div v-if="showCreateModal" class="modal-overlay">
        <div class="modal-content">
          <h2>Create New Project</h2>

          <label>Project Name* </label>
          <input v-model="newProject.proj_name" placeholder="Enter project name" :class="{ 'input-error': newProject.proj_name.trim() === '' }" required/>

          <label>Collaborators (comma-separated user IDs)</label>
          <input type="text" v-model="newProject.collaborators" placeholder="e.g., 101,102,103" />

          <label>Tasks (comma-separated task IDs)</label>
          <input type="text" v-model="newProject.tasks" placeholder="e.g., 201,202" />

          <div class="modal-actions">
            <button @click="submitNewProject" :disabled="!isFormValid" :class="{ 'btn-disabled': !isFormValid }">
              Create
            </button>
            <button @click="showCreateModal = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>
</template>
  
<script setup>
import { ref, computed, onMounted } from 'vue'
import SideNavbar from '../../components/SideNavbar.vue'
import '../projectview/projectview.css'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const projects = ref([])
const showCreateModal = ref(false)
const userId = localStorage.getItem("spm_userid")

// New project form data
const newProject = ref({
  owner_id: userId,
  proj_name: '',
  collaborators: '',
  tasks: ''
})

// Form validation
const isFormValid = computed(() => {
  return newProject.value.proj_name.trim() !== ''
})

// Methods
const fetchProjects = async () => {
  try {
    const response = await fetch(`http://localhost:5001/projects/user/${userId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    console.log('Initial project data:', data) // Debug log
    
    if (data.data && Array.isArray(data.data)) {
      const projectsWithTasks = await Promise.all(
        data.data.map(async (project) => {
          try {
            const taskResponse = await fetch(`http://localhost:5002/tasks/project/${project.id}`)
            const taskData = await taskResponse.json()
            console.log(`Tasks for project ${project.id}:`, taskData) // Debug log
            
            // Check if taskData has a data property
            project.tasks = taskData.data || taskData.tasks || []
            return project
          } catch (error) {
            console.error(`Error fetching tasks for project ${project.id}:`, error)
            project.tasks = []
            return project
          }
        })
      )
      
      projects.value = projectsWithTasks
      console.log('Final projects with tasks:', projects.value) // Debug log
    } else {
      console.warn('No projects data found in response:', data) // Debug log
      projects.value = []
    }
  } catch (error) {
    console.error('Error fetching projects:', error)
    projects.value = []
  }
}

// Make sure to call fetchProjects on component mount
onMounted(() => {
  fetchProjects()
})

// Submit new project
const submitNewProject = async () => {
  if (!newProject.value.proj_name.trim()) {
    alert('Please fill out the required field: Project Name.')
    return
  }

  try {
    // Convert comma-separated strings to arrays where needed
    const payload = {
      ...newProject.value,
      collaborators: newProject.value.collaborators
        ? newProject.value.collaborators.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
        : [],
      tasks: newProject.value.tasks
        ? newProject.value.tasks.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id))
        : []
    }

    const response = await fetch('http://localhost:5001/projects/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (response.ok && data.status === 201) {
      // Add the new project to the list
      if (data.data) {
        projects.value.push(data.data)
      }
      
      // Reset form
      newProject.value = {
        owner_id: userId,
        proj_name: '',
        collaborators: '',
        tasks: ''
      }
      
      showCreateModal.value = false
      alert('Project created successfully!')
      
      // Refresh the projects list
      fetchProjects()
    } else {
      alert('Failed to create project: ' + (data.error || data.message || 'Unknown error'))
    }
  } catch (err) {
    console.error('Error creating project:', err)
    alert('Error creating project. Please try again.')
  }
}

const getInitials = (name) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
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

const handleCardClick = (project) => {
  router.push(`/projects/${project.id}`)
}

const getMyTasks = (tasks) => {
  if (!tasks) return []
  return tasks.filter(task => {
    // Check if the current user is assigned to this task
    return task.collaborators && task.collaborators.includes(parseInt(userId))
  })
}

const filterCollaborators = (project) => {
  if (!project.collaborators) return []
  return (project.collaborators || [])
    .filter(collab => {
      // Convert both to numbers for comparison
      const collabId = typeof collab === 'object' ? collab.id : parseInt(collab)
      return collabId !== parseInt(project.owner_id)
    })
    .slice(0, 3) // Keep only first 3 collaborators for display
}

</script>