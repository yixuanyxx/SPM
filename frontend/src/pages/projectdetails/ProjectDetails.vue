<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
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

          <!-- Create Task Modal Component -->
          <CreateNewTask
            :isVisible="showCreateModal"
            :projectId="project?.id"
            @close="handleCloseCreateTask"
            @task-created="handleTaskCreated"
          />

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
import CreateNewTask from '../../components/CreateNewTask.vue'
import '../projectdetails/projectdetails.css'

const route = useRoute()
const router = useRouter()

const project = ref(null)
const loading = ref(true)
const error = ref(null)
const showCreateModal = ref(false)
const showEditProject = ref(false)
const showErrorPopup = ref(false)
const errorMessage = ref('')
const userId = ref(getCurrentUserData().userid)
const userRole = ref(getCurrentUserData().role?.toLowerCase())
const users = ref({})

onMounted(async () => {
  await fetchProjectDetails()
})

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
    
    if (!projectId || isNaN(projectId)) {
      throw new Error('Invalid project ID')
    }
    
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
    
    if (!projectData || (!projectData.data && !projectData.proj_name)) {
      throw new Error('Invalid project data received')
    }
    
    project.value = {
      ...(projectData.data || projectData),
      tasks: []
    }
    
    if (!project.value.proj_name) {
      throw new Error('Project name is missing')
    }

    await fetchProjectUsers()
    
    try {
      const tasksResponse = await fetch(`http://localhost:5002/tasks/project/${projectId}`)
      const tasksData = await tasksResponse.json()
      project.value.tasks = tasksData.data || tasksData.tasks || []
    } catch (taskError) {
      console.warn('Failed to fetch tasks:', taskError)
      project.value.tasks = []
    }
    
    await syncAllTaskCollaborators()
    
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

// Task Creation Handlers
const handleCloseCreateTask = () => {
  showCreateModal.value = false
}

const handleTaskCreated = async (newTask) => {
  console.log('Task created:', newTask)
  
  // Extract collaborator IDs from the created task
  let collaboratorIds = []
  if (newTask.collaborators) {
    if (Array.isArray(newTask.collaborators)) {
      collaboratorIds = newTask.collaborators.map(id => parseInt(id))
    } else if (typeof newTask.collaborators === 'string') {
      collaboratorIds = newTask.collaborators.split(',').map(id => parseInt(id.trim()))
    }
  }
  
  // Update project collaborators with task collaborators
  if (collaboratorIds.length > 0) {
    await updateProjectCollaborators(collaboratorIds)
  }
  
  // Refresh project details to show the new task and updated collaborators
  await fetchProjectDetails()
  
  // Close the modal
  showCreateModal.value = false
}

// Edit Project methods
const openEditProject = () => {
  showEditProject.value = true
}

const closeEditProject = () => {
  showEditProject.value = false
}

const handleProjectUpdate = async (updateData) => {
  await fetchProjectDetails()
  closeEditProject()
}

// User management
const fetchProjectUsers = async () => {
  const userIds = new Set()
  
  if (project.value.owner_id) userIds.add(project.value.owner_id)
  if (project.value.collaborators) {
    project.value.collaborators.forEach(id => userIds.add(id))
  }
  
  const fetchPromises = Array.from(userIds).map(userid => fetchUserDetails(userid))
  const results = await Promise.all(fetchPromises)
  console.log(`Fetched ${results.filter(r => r !== null).length} users out of ${userIds.size}`)
}

const fetchUserDetails = async (userid) => {
  if (!userid) return null
  if (users.value[userid]) {
    return users.value[userid]
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

const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || 'Unknown User'
}

// Project collaborator management
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

const syncAllTaskCollaborators = async () => {
  if (!project.value.tasks || project.value.tasks.length === 0) return

  try {
    const allTaskCollaborators = new Set()
    
    project.value.tasks.forEach(task => {
      if (task.collaborators) {
        task.collaborators.forEach(collab => allTaskCollaborators.add(parseInt(collab)))
      }
      if (task.owner_id) {
        allTaskCollaborators.add(parseInt(task.owner_id))
      }
    })

    const projectCollaborators = project.value.collaborators || []
    const projectOwnerId = parseInt(project.value.owner_id)
    
    const projectCollaboratorsSet = new Set(
      projectCollaborators.map(collab => parseInt(collab))
    )

    const newCollaborators = Array.from(allTaskCollaborators).filter(
      collabId => !projectCollaboratorsSet.has(collabId) && collabId !== projectOwnerId
    )

    console.log('All task collaborators:', Array.from(allTaskCollaborators))
    console.log('Missing project collaborators:', newCollaborators)

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
        throw new Error('Failed to sync project collaborators')
      }

      console.log('All task collaborators synced with project')
      
      project.value.collaborators = [...projectCollaborators, ...newCollaborators]
      
      await Promise.all(newCollaborators.map(id => fetchUserDetails(id)))
    }
  } catch (error) {
    console.error('Error syncing task collaborators:', error)
  }
}
</script>