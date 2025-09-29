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
              <h1 class="page-title">{{ project.proj_name }}</h1>
              <div class="project-id">Project ID: #{{ project.id }}</div>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SideNavbar from '../../components/SideNavbar.vue'
import '../projectdetails/projectdetails.css'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const loading = ref(true)
const error = ref(null)

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
</script>