<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">My Personal Tasks</h1>
          <p class="page-subtitle">View and Create Your Personal Tasks</p>
        </div>
        <div class="header-actions">
          <div class="header-right-actions">
            <button v-if="canCreateTask" @click="openCreateTask" class="create-task-btn">
              <i class="bi bi-plus-lg"></i>
              Create New Task
            </button>
          </div>
        </div>
        
        <CreateNewTaskForm 
          :isVisible="isCreateTaskVisible"
          @close="isCreateTaskVisible = false"
          @task-created="handleTaskCreated"
        />
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
      <!-- Sort Controls -->
      <div class="sort-controls">
        <div class="sort-container">
          <label for="sortBy">Sort by:</label>
          <select id="sortBy" v-model="sortBy" class="sort-dropdown">
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
            <option value="status">Status</option>
            <option value="name">Task Name</option>
          </select>
          <button 
            @click="toggleSortOrder" 
            class="sort-order-btn"
            :title="sortOrder === 'asc' ? 'Sort Descending' : 'Sort Ascending'"
          >
            <i :class="sortOrder === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down'"></i>
          </button>
        </div>
      </div>
      
      <!-- Tasks -->
      <div class="tasks-container">

        <!-- Loading state -->
        <div v-if="isLoadingTasks || !hasInitialized" class="loading-state">
          <div class="loading-spinner">
            <i class="bi bi-arrow-clockwise spin"></i>
          </div>
          <p class="loading-text">Loading your tasks...</p>
        </div>

        <!-- if no tasks found - only show when fully loaded and tasks array is truly empty -->
        <div v-else-if="hasInitialized && !isLoadingTasks && tasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-clipboard"></i>
          </div>
          <div class="empty-title">No tasks found :(</div>
          <p class="empty-subtitle">{{ getEmptyMessage() }}</p>
        </div>

        <!-- if tasks exist but filtered results are empty -->
        <div v-else-if="hasInitialized && !isLoadingTasks && tasks.length > 0 && filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-funnel"></i>
          </div>
          <div class="empty-title">No tasks match your filter</div>
          <p class="empty-subtitle">Try adjusting your filter settings to see more tasks.</p>
        </div>

        <div 
          v-else
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
                  <div class="task-badges">
                    <div class="task-status" :class="getStatusClass(task.status)">
                      <i :class="getStatusIcon(task.status)"></i>
                      <span>{{ getStatusLabel(task.status) }}</span>
                    </div>
                    <div class="task-priority" :class="getPriorityClass(task.priority)">
                      <i class="bi bi-flag-fill"></i>
                      <span>{{ task.priority }}</span>
                    </div>
                    <!-- Overdue/Due Soon indicators -->
                    <div v-if="isTaskOverdue(task)" class="task-overdue">
                      <i class="bi bi-exclamation-triangle-fill"></i>
                      <span>Overdue</span>
                    </div>
                    <div v-else-if="isTaskDueSoon(task)" class="task-due-soon">
                      <i class="bi bi-clock-fill"></i>
                      <span>Due Soon</span>
                    </div>
                    <!-- New Create Subtask Button -->
                    <button 
                      class="create-subtask-btn" 
                      @click.stop="openSubtaskModal(task)"
                      title="Create subtasks"
                    >
                    <i class="bi bi-plus-lg"></i>
                  </button>
                </div>
              </div>
                <div class="task-people">
                  <div v-if="task.owner_id" class="task-owner">
                    <i class="bi bi-person-fill"></i>
                    <span class="owner-label">Owner:</span>
                    <span class="owner-name">{{ getUserName(task.owner_id) }}</span>
                  </div>
                  <div v-if="task.collaborators && task.collaborators.length > 0" class="task-collaborators">
                    <i class="bi bi-people-fill"></i>
                    <span class="collab-label">Collaborators:</span>
                    <span class="collab-names">
                      {{ task.collaborators.slice(0, 2).map(id => getUserName(id)).join(', ') }}
                      <span v-if="task.collaborators.length > 2" class="more-collabs">
                        +{{ task.collaborators.length - 2 }} more
                      </span>
                    </span>
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
                  <div class="subtask-meta">
                    <div class="subtask-date">
                      <i class="bi bi-calendar3"></i>
                      <span>{{ formatDate(subtask.due_date) }}</span>
                    </div>
                    <div v-if="subtask.owner_id" class="subtask-owner">
                      <i class="bi bi-person"></i>
                      <span>{{ getUserName(subtask.owner_id) }}</span>
                    </div>
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
<!-- Subtask Creation Modal -->
<teleport to="body">
  <div v-if="isSubtaskModalVisible" class="modal-overlay" @click="closeSubtaskModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="modal-title-section">
          <h2>Create Subtask</h2>
        </div>
        <button @click="closeSubtaskModal" class="modal-close-btn">
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
      
      <div class="modal-body">
        <SubtaskForm 
          v-model="currentSubtasks"
          :parent-task="selectedTask"
        />
      </div>
      
      <div class="modal-footer">
        <button @click="closeSubtaskModal" class="btn-modal-cancel">
          Cancel
        </button>
        <button @click="saveSubtasks" class="btn-modal-save">
          <i class="bi bi-check-lg"></i>
          Save Subtasks
        </button>
      </div>
    </div>
  </div>
</teleport>
</div>
</template>

<script setup>
import { ref, computed, onMounted,watch } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../../components/SideNavbar.vue'
import CreateNewTaskForm from '../../components/CreateNewTask.vue'
import SubtaskForm from '../../components/CreateSubtask.vue'
import { getCurrentUserData } from '../../services/session.js'
import { enhancedNotificationService } from '../../services/notifications.js'
import "./taskview.css"

const activeFilter = ref('all')
const sortBy = ref('due_date')
const sortOrder = ref('asc')
const expandedTasks = ref([])
const userRole = ref('')
const userId = ref(null)
const showCreateModal = ref(false);
const errorMessage = ref('')
const showErrorPopup = ref(false)

onMounted(() => {
  const userData = getCurrentUserData()
  userRole.value = userData.role?.toLowerCase() || ''
  userId.value = parseInt(userData.userid) || null
  
  console.log('User data from session:', userData)
  console.log('Fetching projects for userId:', userId.value)

  // Only fetch data if userId is available
  if (userId.value) {
    isLoadingTasks.value = true // Start loading
    
    fetch(`http://localhost:5002/tasks/user-task/${userId.value}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        return response.json()
      })
      .then(async data => {
        // API returns { "tasks": [ {...}, {...} ] }
        tasks.value = data.tasks.data
        console.log('Fetched tasks:', tasks.value)
        
        // Fetch user details for all users mentioned in tasks - wait for completion
        await fetchTaskUsers()
      })
      .catch(error => {
        console.error('Error fetching tasks:', error)
      })
      .finally(() => {
        isLoadingTasks.value = false // End loading
      })

    // Fetch projects owned by user
    fetch(`http://localhost:5001/projects/owner/${userId.value}`)
      .then(response => {
        if (!response.ok) {
          if (response.status === 404) {
            console.warn('No projects found for this user')
            userProjects.value = []
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        return response.json()
      })
      .then(data => {
      const allProjects = data.data || []
      // filter projects where user is owner or in collaborators
      userProjects.value = allProjects.filter(project => {
        const collabs = project.collaborators || []
        return project.owner_id == userId.value || collabs.includes(Number(userId.value))
      })
      console.log('Filtered projects for dropdown:', userProjects.value)
      })
      .catch(error => console.error('Error fetching projects:', error))
  }
})

// Check if user is manager or director
const isManagerOrDirector = computed(() => {
  return ['manager', 'director'].includes(userRole.value)
})

const tasks = ref([]) // where the fetched data will be stored
const userProjects = ref([])
const showSuccessMessage = ref(false)
const users = ref({}) // Store user information lookup { userid: { name, email, ... } }
const isLoadingTasks = ref(true) // Loading state for tasks - start as true
const hasInitialized = ref(false) // Track if component has been initialized

// Function to fetch user details by userid
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

// Function to get user names for display
const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || `Invalid user`
}

// Function to fetch all users mentioned in tasks
const fetchTaskUsers = async () => {
  const userIds = new Set()
  
  // Collect all unique user IDs from tasks
  tasks.value.forEach(task => {
    if (task.owner_id) userIds.add(task.owner_id)
    if (task.collaborators) {
      task.collaborators.forEach(id => userIds.add(id))
    }
    // Also check subtasks
    if (task.subtasks) {
      task.subtasks.forEach(subtask => {
        if (subtask.owner_id) userIds.add(subtask.owner_id)
        if (subtask.collaborators) {
          subtask.collaborators.forEach(id => userIds.add(id))
        }
      })
    }
  })
  
  console.log(`Found user IDs to fetch:`, Array.from(userIds))
  
  // Only fetch users we don't already have cached
  const uncachedUserIds = Array.from(userIds).filter(userid => !users.value[userid])
  
  if (uncachedUserIds.length > 0) {
    console.log(`Fetching ${uncachedUserIds.length} new users:`, uncachedUserIds)
    // Fetch user details for all unique IDs that aren't cached
    const fetchPromises = uncachedUserIds.map(userid => fetchUserDetails(userid))
    const results = await Promise.all(fetchPromises)
    console.log(`Fetched ${results.filter(r => r !== null).length} new users out of ${uncachedUserIds.length}`)
  }
}

// Helper function to fetch user details for a specific task
const fetchTaskSpecificUsers = async (taskData) => {
  const userIds = new Set()
  
  // Collect user IDs from the specific task
  if (taskData.owner_id) userIds.add(taskData.owner_id)
  if (taskData.collaborators) {
    taskData.collaborators.forEach(id => userIds.add(id))
  }
  if (taskData.subtasks) {
    taskData.subtasks.forEach(subtask => {
      if (subtask.owner_id) userIds.add(subtask.owner_id)
      if (subtask.collaborators) {
        subtask.collaborators.forEach(id => userIds.add(id))
      }
    })
  }
  
  // Only fetch users we don't already have cached
  const uncachedUserIds = Array.from(userIds).filter(userid => !users.value[userid])
  
  if (uncachedUserIds.length > 0) {
    console.log(`Fetching users for new task:`, uncachedUserIds)
    const fetchPromises = uncachedUserIds.map(userid => fetchUserDetails(userid))
    await Promise.all(fetchPromises)
  }
}

onMounted(() => {
  const userData = getCurrentUserData()
  userRole.value = userData.role?.toLowerCase() || ''
  userId.value = parseInt(userData.userid) || null
  
  console.log('User data from session:', userData)
  console.log('Fetching projects for userId:', userId.value)

  // Only fetch data if userId is available
  if (userId.value) {
    isLoadingTasks.value = true // Start loading
    
    fetch(`http://localhost:5002/tasks/user-task/${userId.value}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        return response.json()
      })
      .then(async data => {
        // API returns { "tasks": [ {...}, {...} ] }
        tasks.value = data.data
        console.log('Fetched tasks:', tasks.value)
        
        // Fetch user details for all users mentioned in tasks - wait for completion
        await fetchTaskUsers()
      })
      .catch(error => {
        console.error('Error fetching tasks:', error)
      })
      .finally(() => {
        isLoadingTasks.value = false // End loading
        hasInitialized.value = true // Mark as fully initialized
      })

    // Fetch projects owned by user
    fetch(`http://localhost:5001/projects/owner/${userId.value}`)
      .then(response => {
        if (!response.ok) {
          if (response.status === 404) {
            console.warn('No projects found for this user')
            userProjects.value = []
            return
          }
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        return response.json()
      })
      .then(data => {
      const allProjects = data.data || []
      // filter projects where user is owner or in collaborators
      userProjects.value = allProjects.filter(project => {
        const collabs = project.collaborators || []
        return project.owner_id == userId.value || collabs.includes(Number(userId.value))
      })
      console.log('Filtered projects for dropdown:', userProjects.value)
      })
      .catch(error => console.error('Error fetching projects:', error))
  }
})

const collaboratorQuery = ref('');
const selectedCollaborators = ref([]);
const collaboratorSuggestions = ref([]);

const addCollaborator = (user) => {
  if (!selectedCollaborators.value.find(u => u.id === user.id)) {
    selectedCollaborators.value.push(user)
  }
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
};

const removeCollaborator = (user) => {
  selectedCollaborators.value = selectedCollaborators.value.filter(u => u.id !== user.id);
};

// fetch suggestions whenever the query changes
watch(collaboratorQuery, async (query) => {
  if (!query) {
    collaboratorSuggestions.value = [];
    return;
  }

  try {
    const res = await fetch(`http://localhost:5003/users/search?email=${encodeURIComponent(query)}`);
    if (!res.ok) throw new Error('Failed to fetch user emails');
    const data = await res.json();
    collaboratorSuggestions.value = data.data || [];
  } catch (err) {
    console.error(err);
    collaboratorSuggestions.value = [];
  }
});

// Computed property to determine if user can create tasks
const canCreateTask = computed(() => {
  return userRole.value === "manager" || userRole.value === "director" || userRole.value === "staff";
});

// Popup visibility state
const isCreateTaskVisible = ref(false);

function openCreateTask() {
  console.log("Clicked create task button!");
  isCreateTaskVisible.value = true;
}

const handleTaskCreated = async (newTaskData) => {
  tasks.value.push(newTaskData)
  isCreateTaskVisible.value = false
  
  // Fetch user details specifically for the newly created task
  await fetchTaskSpecificUsers(newTaskData)
  
  showSuccessMessage.value = true
  setTimeout(() => {
    showSuccessMessage.value = false
  }, 3000)
}

// Add these refs
const isSubtaskModalVisible = ref(false)
const selectedTask = ref(null)
const currentSubtasks = ref([])

// Add these methods
const openSubtaskModal = (task) => {
  selectedTask.value = task
  currentSubtasks.value = [] // Reset subtasks
  isSubtaskModalVisible.value = true
}

const closeSubtaskModal = () => {
  isSubtaskModalVisible.value = false
  selectedTask.value = null
  currentSubtasks.value = []
}

const saveSubtasks = async () => {
  if (currentSubtasks.value.length === 0) {
    alert('Please add at least one subtask')
    return
  }
  
  try {
    // Here you would make API calls to save the subtasks
    // For now, we'll just add them to the parent task locally
    if (selectedTask.value) {
      if (!selectedTask.value.subtasks) {
        selectedTask.value.subtasks = []
      }
      selectedTask.value.subtasks.push(...currentSubtasks.value)
    }
    
    console.log('Saving subtasks:', currentSubtasks.value)
    closeSubtaskModal()
    
    // Fetch user details for the newly created subtasks
    await fetchTaskUsers()
    
    // Show success message
  } catch (error) {
    console.error('Error saving subtasks:', error)
    alert('Failed to save subtasks')
  }
}

// const newTaskFile = ref(null)
// const handleFileUpload = (event) => {
//   const file = event.target.files[0]
//   if (file && file.type === "application/pdf") {
//     newTaskFile.value = file
//   } else {
//     alert("Only PDF files are allowed")
//     event.target.value = null
//     newTaskFile.value = null
//   }
// }

// const newTask = ref({
//   owner_id: null, // Will be set when userId is available
//   task_name: '',
//   description: '',
//   type: 'parent',
//   due_date: '',
//   priority: '5',
//   status: 'Ongoing',
//   project_id: '',
//   collaborators: '',
//   parent_task: '',
//   subtasks: [], 
// })

// // Watch for userId changes and update newTask.owner_id
// watch(userId, (newUserId) => {
//   if (newUserId) {
//     newTask.value.owner_id = newUserId
//   }
// }, { immediate: true })

// const isFormValid = computed(() => {
//   return newTask.value.task_name.trim() !== '' &&
//          newTask.value.description.trim() !== '' &&
//          newTask.value.due_date.trim() !== ''   
// })

// // send POST to backend
// const submitNewTask = async () => {
//   if (!newTask.value.task_name || !newTask.value.description || !newTask.value.due_date) {
//     alert('Please fill out all required fields: Task Name, Description, and Due Date.')
//     return
//   }
//   try {
//     // Directors and managers use the manager endpoint (owner only, no auto-collaborator addition)
//     // Staff uses the staff endpoint (automatically adds owner as collaborator)
//     let endpoint = (userRole.value === 'manager' || userRole.value === 'director')
//       ? 'http://localhost:5002/tasks/manager-task/create'
//       : 'http://localhost:5002/tasks/staff-task/create'

//     // Use FormData to handle file uploads properly
//     const formData = new FormData()
    
//     // Add all task fields to FormData
//     formData.append('owner_id', newTask.value.owner_id)
//     formData.append('task_name', newTask.value.task_name)
//     formData.append('description', newTask.value.description)
//     formData.append('type', newTask.value.type)
//     formData.append('due_date', newTask.value.due_date)
//     formData.append('priority', newTask.value.priority)
//     formData.append('status', newTask.value.status)
    
//     if (newTask.value.project_id) {
//       formData.append('project_id', newTask.value.project_id)
//     }
    
//     if (newTask.value.parent_task) {
//       formData.append('parent_task', newTask.value.parent_task)
//     }
    
//     // Add collaborators as comma-separated string with role-based logic
//     const collaboratorIds = selectedCollaborators.value.map(user => parseInt(user.userid))
    
//     // Role-based owner inclusion in collaborators:
//     // - Staff: Include owner as collaborator
//     // - Manager/Director: Owner only, NOT in collaborators
//     if (userRole.value === 'staff') {
//       // For staff, ensure owner is always included in collaborators
//       if (!collaboratorIds.includes(newTask.value.owner_id)) {
//         collaboratorIds.push(newTask.value.owner_id)
//         console.log('Added staff owner to collaborators')
//       }
//     }
    
//     // Only append collaborators if there are any
//     if (collaboratorIds.length > 0) {
//       const collaboratorString = collaboratorIds.join(',')
//       console.log('Appending collaborators string:', collaboratorString)
//       formData.append('collaborators', collaboratorString)
//     } else {
//       console.log('No collaborators to append - skipping collaborators field entirely')
//     }
  
//     // Add subtasks - send as JSON if backend expects subtask objects
//     if (newTask.value.subtasks && newTask.value.subtasks.length > 0) {
//       formData.append('subtasks', JSON.stringify(newTask.value.subtasks))
//     }
    
//     // Add the actual file for upload
//     if (newTaskFile.value) {
//       formData.append('attachment', newTaskFile.value)
//     }

//     const response = await fetch(endpoint, {
//       method: 'POST',
//       body: formData  // Don't set Content-Type header - browser will set it automatically with boundary
//     })

//     const data = await response.json()

//     if (response.ok && data.Code === 201) {
//       tasks.value.push(data.data)
//       // reset form
//       newTask.value = {
//         owner_id: userId.value,
//         task_name: '',
//         description: '',
//         type: 'parent',
//         due_date: '',
//         priority: '5',
//         status: 'Ongoing',
//         project_id: '',
//         collaborators: '',
//         parent_task: '',
//         subtasks: [],
//       }
//       selectedCollaborators.value = []
//       newTaskFile.value = null
//       // Clear the file input element
//       const fileInput = document.querySelector('input[type="file"]')
//       if (fileInput) {
//         fileInput.value = ''
//       }
//       showCreateModal.value = false
//       showSuccessMessage.value = true
//       setTimeout(() => {
//         showSuccessMessage.value = false
//       }, 3000)
//     } else {
//       alert('Failed: ' + data.Message)
//     }
//   } catch (err) {
//     console.error(err)
//     alert('Error creating task')
//   }
// }

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

// Trigger notifications for collaborators when a task is created
const triggerCollaboratorNotifications = async (taskId, collaborators) => {
  if (!collaborators || collaborators.length === 0) {
    console.log('No collaborators to notify')
    return
  }
  
  try {
    const currentUserName = localStorage.getItem('spm_username') || 'System'
    console.log(`Sending notifications to ${collaborators.length} collaborators for task ${taskId}`)
    
    // Send notifications to all collaborators
    const notificationPromises = collaborators.map(collaborator => {
      console.log(`Triggering notification for collaborator: ${collaborator.userid} (${collaborator.email})`)
      return enhancedNotificationService.triggerTaskAssignmentNotification(
        taskId,
        collaborator.userid,
        currentUserName
      )
    })
    
    const results = await Promise.all(notificationPromises)
    console.log(`✅ Notifications sent successfully to ${collaborators.length} collaborators`)
    console.log('Notification results:', results)
    
  } catch (error) {
    console.error('❌ Failed to send collaborator notifications:', error)
    // Don't throw error to avoid breaking the main task creation flow
  }
}

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(task => task.status === activeFilter.value)
  }
  
  return filtered.sort((a, b) => {
    // Always keep completed tasks at the bottom if not sorting by status
    if (sortBy.value !== 'status') {
      if (a.status === 'Completed' && b.status !== 'Completed') return 1
      if (a.status !== 'Completed' && b.status === 'Completed') return -1
    }
    
    let comparison = 0
    
    switch (sortBy.value) {
      case 'due_date':
        comparison = new Date(a.due_date) - new Date(b.due_date)
        break
      case 'priority':
        comparison = parseInt(b.priority) - parseInt(a.priority) // Higher priority first by default
        break
      case 'status':
        const statusOrder = { 'Unassigned': 0, 'Ongoing': 1, 'Under Review': 2, 'Completed': 3 }
        comparison = statusOrder[a.status] - statusOrder[b.status]
        break
      case 'name':
        comparison = a.task_name.localeCompare(b.task_name)
        break
      default:
        comparison = new Date(a.due_date) - new Date(b.due_date)
    }
    
    return sortOrder.value === 'asc' ? comparison : -comparison
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
  if (!dateString) return 'No date'
  
  const date = new Date(dateString)
  
  return date.toLocaleDateString(undefined, { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
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

const getPriorityClass = (priority) => {
  const level = parseInt(priority)
  if (level >= 8) return 'priority-high'
  if (level >= 5) return 'priority-medium'
  return 'priority-low'
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

// Utility functions for overdue and due soon tasks
const isTaskOverdue = (task) => {
  if (!task.due_date || task.status === 'Completed') return false
  const dueDate = new Date(task.due_date)
  const now = new Date()
  return dueDate < now
}

const isTaskDueSoon = (task) => {
  if (!task.due_date || task.status === 'Completed') return false
  const dueDate = new Date(task.due_date)
  const now = new Date()
  const timeDiff = dueDate.getTime() - now.getTime()
  const daysDiff = timeDiff / (1000 * 3600 * 24)
  return daysDiff > 0 && daysDiff <= 3 // Due within 3 days
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'Ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'Under Review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'Completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'Unassigned').length)
</script>