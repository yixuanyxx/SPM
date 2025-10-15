<template>
    <div class="project-app-layout ms-2">
      <!-- Side Navigation -->
      <SideNavbar />
      
      <!-- Main Content Area -->
      <div class="project-app-container">
        <!-- Header Section -->
        <div class="project-header-section">
          <div class="header-content">
            <h1 class="project-view-page-title">My Projects</h1>
            <p class="project-view-page-subtitle">View and manage your project collaborations</p>
          </div>
          <button class="create-project-btn" @click="showCreateModal = true">
            <i class="bi bi-plus-lg"></i>
            Create New Project
          </button>
        </div>

        <div class="content-wrapper">

          <!-- Main Content -->
          <div class="project-main-content">
            <!-- if no projects found -->
            <div v-if="projects.length === 0" class="empty-state">
              <div class="empty-icon">
                <i class="bi bi-folder"></i>
              </div>
              <div class="empty-title">No projects found</div>
              <p class="empty-subtitle">Create your first project to get started!</p>
            </div>

            <div v-else class="project-view-projects-grid">
              <!-- Dynamic Project Cards -->
              <div v-for="project in projects" 
                   :key="project.id" 
                   class="project-card"
                   :class="{ 'drag-over': isDraggingOver === project.id }"
                   @click="handleCardClick(project)"
                   @dragover.prevent="handleDragOver($event, project)"
                   @dragleave="handleDragLeave(project)"
                   @drop="handleDrop($event, project)">
  
                <div class="project-header">
                  <div class="project-icon">
                    <i class="bi bi-folder-fill"></i>
                  </div>
                  <div class="project-info">
                    <h3 class="project-name mt-3">{{ project.proj_name }}</h3>
                  </div>
                </div>
                
                <div class="project-meta">
                  <div class="meta-item">
                    <i class="bi bi-person-fill"></i>
                    <span>Owner: {{ getUserName(project.owner_id) }}</span>
                  </div>
                  <div class="meta-item" v-if="project.collaborators">
                    <i class="bi bi-people-fill"></i>
                    <span>{{ getProjectMemberCount(project) }} members</span>
                  </div>
                  <div class="meta-item" v-if="project.created_at">
                    <i class="bi bi-calendar3"></i>
                    <span>Created {{ formatDate(project.created_at) }}</span>
                  </div>
                </div>

                <!-- Keep your existing My Tasks section -->
                <div class="my-tasks">
                  <div class="tasks-header">
                    <span class="tasks-title">My Tasks</span>
                  </div>
                  <div v-if="getMyTasks(project.tasks).length === 0" class="no-tasks">
                    No tasks assigned
                  </div>
                  <div v-else class="project-task-list">
                    <div v-for="task in getMyTasks(project.tasks)" 
                         :key="task.id" 
                         class="project-task-item">
                      <div class="project-task-content">
                        <span class="project-task-name">{{ task.task_name }}</span>
                      </div>
                      <span :class="['project-status-badge', `project-status-${task.status.toLowerCase()}`]">
                        {{ task.status }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Workload View Button -->
                <div class="project-actions">
                  <button 
                    class="btn-primary edit-project-btn" 
                    @click.stop="navigateToWorkload(project)"
                  >
                    <i class="bi bi-bar-chart"></i>
                    View Workload
                  </button>
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
        
          <div class="unassigned-tasks-sidebar">
            <div class="sidebar-header">
              <h2>Unassigned Tasks</h2>
              <p class="sidebar-subtitle">Tasks without project assignment</p>
            </div>
            
            <div class="tasks-container">
              <div v-if="unassignedTasks.length === 0" class="no-tasks-message">
                No unassigned tasks found
              </div>
              <div v-else class="tasks-list">
                <div v-for="task in unassignedTasks" 
                     :key="task.id" 
                     class="unassigned-task-item"
                     draggable="true"
                     @dragstart="handleDragStart($event, task)"
                     @click="navigateToTask(task.id)">
                  <div class="project-task-content">
                    <span class="project-task-name">{{ task.task_name }}</span>
                    <span :class="['project-status-badge', `project-status-${task.status.toLowerCase()}`]">
                      {{ task.status }}
                    </span>
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
import { ref, computed, onMounted } from 'vue'
import SideNavbar from '../../components/SideNavbar.vue'
import { enhancedNotificationService } from '../../services/notifications.js'
import '../projectview/projectview.css'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const projects = ref([])
const showCreateModal = ref(false)
const userId = localStorage.getItem("spm_userid")
const unassignedTasks = ref([])

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
    
    if (data.data && Array.isArray(data.data)) {
      const projectsWithTasks = await Promise.all(
        data.data.map(async (project) => {
          // Fetch owner details first
          await fetchUserDetails(project.owner_id)
          
          try {
            const taskResponse = await fetch(`http://localhost:5002/tasks/project/${project.id}`)
            const taskData = await taskResponse.json()
            project.tasks = taskData.data || taskData.tasks || []
          } catch (error) {
            console.error(`Error fetching tasks for project ${project.id}:`, error)
            project.tasks = []
          }
          return project
        })
      )
      
      projects.value = projectsWithTasks
    } else {
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
      const createdProject = data.data
      if (createdProject) {
        projects.value.push(createdProject)
      }
      
      // Trigger notifications for collaborators
      if (payload.collaborators && payload.collaborators.length > 0) {
        await triggerProjectCollaboratorNotifications(
          createdProject.id,
          payload.collaborators,
          createdProject.proj_name
        )
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

// Trigger notifications for collaborators when a project is created
const triggerProjectCollaboratorNotifications = async (projectId, collaboratorIds, projectName) => {
  if (!collaboratorIds || collaboratorIds.length === 0) {
    console.log('No collaborators to notify for project')
    return
  }
  
  try {
    const currentUserName = localStorage.getItem('spm_username') || 'System'
    console.log(`Sending project notifications to ${collaboratorIds.length} collaborators for project ${projectId}`)
    
    const result = await enhancedNotificationService.triggerProjectCollaboratorAdditionNotification(
      projectId,
      collaboratorIds,
      projectName,
      currentUserName
    )
    
    console.log(`✅ Project notifications sent successfully to ${collaboratorIds.length} collaborators`)
    console.log('Notification result:', result)
    
  } catch (error) {
    console.error('❌ Failed to send project collaborator notifications:', error)
    // Don't throw error to avoid breaking the main project creation flow
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

const fetchUnassignedTasks = async () => {
  try {
    const response = await fetch(`http://localhost:5002/tasks/user-task/${userId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    console.log('Raw API response:', JSON.stringify(data, null, 2)) 

    
    // Check data structure and get the tasks array
    let tasks = []
    if (data.data) {
      tasks = Array.isArray(data.data) ? data.data : [data.data]
    } 
    // else if (data.data) {
    //   tasks = Array.isArray(data.data) ? data.data : [data.data]
    // } else if (Array.isArray(data)) {
    //   tasks = data
    // } else {
    //   tasks = [data] // If it's a single task object
    // }
    
    console.log('Processed tasks array:', tasks) // Debug processed array

    // Filter unassigned tasks
    unassignedTasks.value = tasks.filter(task => {
      console.log('Checking task:', {
        id: task.id,
        name: task.task_name,
        project_id: task.project_id
      }) // Debug each task's relevant fields
      
      // Check all possible cases for an unassigned task
      const isUnassigned = task.project_id === null || 
                          task.project_id === undefined || 
                          task.project_id === 0 || 
                          task.project_id === "" || 
                          !task.hasOwnProperty('project_id')
                          
      console.log(`Task ${task.id} is unassigned: ${isUnassigned}`) // Debug result
      return isUnassigned
    })

    console.log('Final unassigned tasks:', unassignedTasks.value) // Debug final result
  } catch (error) {
    console.error('Error in fetchUnassignedTasks:', error)
    unassignedTasks.value = []
  }
}

// Make sure to call both fetches on mount
onMounted(async () => {
  console.log('Component mounted, userId:', userId) // Debug userId
  await Promise.all([
    fetchProjects(),
    fetchUnassignedTasks()
  ])
})

const navigateToTask = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

const navigateToWorkload = (project) => {
  router.push(`/tasks/projects?projectId=${project.id}`)
}


const handleDragStart = (event, task) => {
  event.dataTransfer.setData('taskId', task.id.toString())
}

const handleDrop = async (event, project) => {
  const taskId = event.dataTransfer.getData('taskId')
  isDraggingOver.value = null // Reset drag state
  
  try {
    // Update task with new project_id
    const response = await fetch(`http://localhost:5002/tasks/update`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        task_id: parseInt(taskId),
        project_id: project.id,
        collaborators: [parseInt(userId)] // Ensure current user is a collaborator
      })
    })

    if (!response.ok) {
      throw new Error('Failed to update task')
    }

    // Fetch updated task details
    const taskResponse = await fetch(`http://localhost:5002/tasks/${taskId}`)
    const taskData = await taskResponse.json()
    const updatedTask = taskData.data || taskData

    // Update the project's tasks array
    if (!project.tasks) {
      project.tasks = []
    }
    project.tasks.push(updatedTask)

    // Refresh lists
    await Promise.all([
      fetchProjects(),
      fetchUnassignedTasks()
    ])
  } catch (error) {
    console.error('Error updating task:', error)
    alert('Failed to assign task to project')
  }
}

const isDraggingOver = ref(null)

const handleDragOver = (event, project) => {
  event.preventDefault()
  isDraggingOver.value = project.id
}

const handleDragLeave = (project) => {
  if (isDraggingOver.value === project.id) {
    isDraggingOver.value = null
  }
}

// Add this with your other refs
const users = ref({})

// Add this method to your existing methods
const getProjectMemberCount = (project) => {
  let count = 1 // Owner
  if (project.collaborators && Array.isArray(project.collaborators)) {
    count += project.collaborators.length
  }
  return count
}

// Add this with your other methods
const fetchUserDetails = async (userid) => {
  if (!userid) return null
  if (users.value[userid]) return users.value[userid]
  
  try {
    const response = await fetch(`http://localhost:5003/users/${userid}`)
    if (response.ok) {
      const data = await response.json()
      const user = data.data || data
      if (user) {
        users.value[userid] = user
        return user
      }
    }
  } catch (error) {
    console.error(`Error fetching user ${userid}:`, error)
  }
  return null
}

const getUserName = (userid) => {
  const user = users.value[userid]
  return user?.name || 'Unknown User'
}

// Add this with your other methods
const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-SG', { 
    timeZone: 'Asia/Singapore',
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}
</script>