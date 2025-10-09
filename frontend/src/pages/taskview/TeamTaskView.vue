<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Team's Workload</h1>
          <p class="page-subtitle">Monitor and manage your team's task distribution</p>
        </div>
        <div class="header-actions">
          <div class="header-right-actions">
            <button 
              class="view-toggle-btn" 
              :class="{ active: viewMode === 'members' }"
              @click="viewMode = 'members'"
            >
              <i class="bi bi-people-fill"></i>
              Member View
            </button>
            <button 
              class="view-toggle-btn" 
              :class="{ active: viewMode === 'tasks' }"
              @click="viewMode = 'tasks'"
            >
              <i class="bi bi-list-task"></i>
              Task View
            </button>
          </div>
        </div>
      </div>
      
    <!-- Stats Section -->
    <div class="stats-section" :class="{ 'stats-section-member': viewMode === 'members' }">
      <div class="stats-container">
        <!-- Member View Stats -->
        <div v-if="viewMode === 'members'" class="workload-stats">
          <div class="stat-card workload-stat" @click="workloadFilter = 'all'" :class="{ active: workloadFilter === 'all' }">
            <div class="stat-content">
              <div class="stat-icon members">
                <i class="bi bi-people"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ teamMembers.filter(m => m.userid !== userId).length }}</div>
                <div class="stat-title">All Members</div>
              </div>
            </div>
          </div>

          <div class="stat-card workload-light" @click="workloadFilter = 'low'" :class="{ active: workloadFilter === 'low' }">
            <div class="stat-content">
              <div class="stat-icon light">
                <i class="bi bi-circle"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ lightLoadMembers }}</div>
                <div class="stat-title">Light Load</div>
              </div>
            </div>
          </div>

          <div class="stat-card workload-moderate" @click="workloadFilter = 'moderate'" :class="{ active: workloadFilter === 'moderate' }">
            <div class="stat-content">
              <div class="stat-icon moderate">
                <i class="bi bi-circle-half"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ moderateLoadMembers }}</div>
                <div class="stat-title">Moderate Load</div>
              </div>
            </div>
          </div>

          <div class="stat-card workload-heavy" @click="workloadFilter = 'high'" :class="{ active: workloadFilter === 'high' }">
            <div class="stat-content">
              <div class="stat-icon heavy">
                <i class="bi bi-circle-fill"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ heavyLoadMembers }}</div>
                <div class="stat-title">Heavy Load</div>
              </div>
            </div>
          </div>

          <div class="stat-card overload-stat" @click="workloadFilter = 'overload'" :class="{ active: workloadFilter === 'overload' }">
            <div class="stat-content">
              <div class="stat-icon overload">
                <i class="bi bi-exclamation-triangle-fill"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ overloadedMembers }}</div>
                <div class="stat-title">Over Load</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Task View Stats -->
        <div v-else class="task-stats">
          <div class="stat-card" @click="activeFilter = 'all'" :class="{ active: activeFilter === 'all' }">
            <div class="stat-content">
              <div class="stat-icon total">
                <i class="bi bi-list-task"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ selectedTaskMember ? memberTaskStats.total : totalTasks }}</div>
                <div class="stat-title">Total</div>
              </div>
            </div>
          </div>

          <div class="stat-card" @click="activeFilter = 'Unassigned'" :class="{ active: activeFilter === 'Unassigned' }">
            <div class="stat-content">
              <div class="stat-icon unassigned">
                <i class="bi bi-person-dash"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ selectedTaskMember ? memberTaskStats.unassigned : unassignedTasks }}</div>
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
                <div class="stat-number">{{ selectedTaskMember ? memberTaskStats.ongoing : ongoingTasks }}</div>
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
                <div class="stat-number">{{ selectedTaskMember ? memberTaskStats.underReview : underReviewTasks }}</div>
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
                <div class="stat-number">{{ selectedTaskMember ? memberTaskStats.completed : completedTasks }}</div>
                <div class="stat-title">Completed</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="main-content" :class="{ 'main-content-member': viewMode === 'members' }">

      
      <!-- Member View -->
      <div v-if="viewMode === 'members'" class="members-view">
        <!-- Filter Controls for Member View -->
        <div class="sort-controls">
          <div class="sort-container">
            <div class="filter-group ms-4">
              <label for="memberFilter">Filter by member:</label>
              <select id="memberFilter" v-model="selectedMember" class="filter-dropdown">
                <option value="">All Members</option>
                <option v-for="member in teamMembers.filter(m => m.userid !== userId)" :key="member.userid" :value="member.userid">
                  {{ member.name }}
                </option>
              </select>
            </div>
            
            <div class="workload-legend me-4">
              <span class="legend-item low">
                <div class="legend-color low"></div>
                Light
              </span>
              <span class="legend-item moderate">
                <div class="legend-color moderate"></div>
                Moderate
              </span>
              <span class="legend-item high">
                <div class="legend-color high"></div>
                Heavy
              </span>
              <span class="legend-item overload">
                <div class="legend-color overload"></div>
                Overloaded
              </span>
            </div>
          </div>
        </div>

        <!-- Loading State for Member View -->
        <div v-if="isLoadingTasks" class="loading-state">
          <div class="loading-spinner">
            <i class="bi bi-arrow-clockwise spin"></i>
          </div>
          <p class="loading-text">Loading team members and tasks...</p>
        </div>

        <!-- Empty State for No Members -->
        <div v-else-if="teamMembers.length === 0 && !isLoadingTasks" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-people"></i>
          </div>
          <div class="empty-title">No team members found</div>
          <p class="empty-subtitle">No team members found in this team.</p>
        </div>

        <!-- Empty State for No Filtered Members -->
        <div v-else-if="filteredMembers.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-people"></i>
          </div>
          <div class="empty-title">No team members match filter</div>
          <p class="empty-subtitle">Try adjusting your filter criteria.</p>
        </div>

        <!-- Member Cards -->
        <div v-else class="members-container">
          <div 
            v-for="(member, index) in filteredMembers" 
            :key="member.userid"
            class="member-card"
            :class="getWorkloadClass(member)"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <div class="member-header">
              <div class="member-info">
                <div class="member-avatar">
                  <i class="bi bi-person-circle"></i>
                </div>
                <div class="member-details">
                  <h3 class="member-name">{{ member.name }}</h3>
                  <p class="member-role">{{ member.role || 'Team Member' }}</p>
                  <p class="member-email">{{ member.email }}</p>
                </div>
              </div>
              <div class="workload-indicator" :class="getWorkloadClass(member)">
                <div class="workload-level">{{ getWorkloadLevel(member) }}</div>
                <div class="task-count">{{ getMemberTasks(member.userid).length }} tasks</div>
              </div>
            </div>

            <div class="member-tasks-summary">
              <div class="task-breakdown">
                <div class="breakdown-item ongoing">
                  <span class="breakdown-count">{{ getMemberTasksByStatus(member.userid, 'Ongoing').length }}</span>
                  <span class="breakdown-label">Ongoing</span>
                </div>
                <div class="breakdown-item under-review">
                  <span class="breakdown-count">{{ getMemberTasksByStatus(member.userid, 'Under Review').length }}</span>
                  <span class="breakdown-label">Review</span>
                </div>
                <div class="breakdown-item completed">
                  <span class="breakdown-count">{{ getMemberTasksByStatus(member.userid, 'Completed').length }}</span>
                  <span class="breakdown-label">Done</span>
                </div>
              </div>
              
              <div class="priority-breakdown">
                <div class="priority-item high" v-if="getMemberHighPriorityTasks(member.userid) > 0">
                  <i class="bi bi-flag-fill"></i>
                  <span>{{ getMemberHighPriorityTasks(member.userid) }} high priority</span>
                </div>
                <div class="upcoming-tasks" v-if="getMemberUpcomingTasks(member.userid) > 0">
                  <i class="bi bi-clock"></i>
                  <span>{{ getMemberUpcomingTasks(member.userid) }} due soon</span>
                </div>
              </div>
            </div>

            <div class="member-actions">
              <button class="view-tasks-btn" @click="viewMemberTasks(member.userid)">
                <i class="bi bi-eye"></i>
                View Tasks
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Task View -->
      <div v-else class="tasks-view">

        <!-- Sort Controls -->
        <div class="sort-controls">
          <div class="sort-container">
            <label for="sortBy">Sort by:</label>
            <select id="sortBy" v-model="sortBy" class="sort-dropdown">
              <option value="due_date">Due Date</option>
              <option value="priority">Priority</option>
              <option value="status">Status</option>
              <option value="name">Task Name</option>
              <option value="owner">Assignee</option>
            </select>
            <button 
              @click="toggleSortOrder" 
              class="sort-order-btn"
              :title="sortOrder === 'asc' ? 'Sort Descending' : 'Sort Ascending'"
            >
              <i :class="sortOrder === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down'"></i>
            </button>
            
            <div class="filter-group">
              <label for="memberTaskFilter">Filter by member:</label>
              <select id="memberTaskFilter" v-model="selectedTaskMember" class="filter-dropdown">
                <option value="">All Members</option>
                <option v-for="member in teamMembers.filter(m => m.userid !== userId)" :key="member.userid" :value="member.userid">
                  {{ member.name }}
                </option>
              </select>
            </div>
          </div>
        </div>
      
      <!-- Tasks -->
      <div class="tasks-container">

        <!-- Loading state -->
        <div v-if="isLoadingTasks" class="loading-state">
          <div class="loading-spinner">
            <i class="bi bi-arrow-clockwise spin"></i>
          </div>
          <p class="loading-text">Loading team tasks...</p>
        </div>

        <!-- if no tasks found -->
        <div v-else-if="!isLoadingTasks && filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-clipboard"></i>
          </div>
          <div class="empty-title">No tasks found :(</div>
          <p class="empty-subtitle">{{ getEmptyMessage() }}</p>
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
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../../components/SideNavbar.vue'
import { getCurrentUserData } from '../../services/session.js'
import "../taskview/taskview.css"

const activeFilter = ref('all')
const sortBy = ref('due_date')
const sortOrder = ref('asc')
const expandedTasks = ref([])
const userRole = ref('')
const userId = ref(null)
const teamId = ref(null)
const viewMode = ref('members')
const selectedMember = ref('')
const selectedTaskMember = ref('')
const workloadFilter = ref('all')

const tasks = ref([])
const users = ref({})
const teamMembers = ref([])
const isLoadingTasks = ref(false)

// Get user data from session
onMounted(async () => {
  const userData = getCurrentUserData()
  userRole.value = userData.role?.toLowerCase() || ''
  userId.value = parseInt(userData.userid) || null
  
  console.log('Team Task View - User data from session:', userData)
  
  // Get user's team_id
  if (userId.value) {
    try {
      const response = await fetch(`http://localhost:5003/users/${userId.value}`)
      if (response.ok) {
        const data = await response.json()
        teamId.value = data.data?.team_id
        console.log('User team_id:', teamId.value)
        
        if (teamId.value) {
          await Promise.all([
            fetchTeamTasks(),
            fetchTeamMembers()
          ])
        } else {
          console.log('No team ID found for user')
        }
      } else {
        console.error('Failed to fetch user details:', response.status)
      }
    } catch (error) {
      console.error('Error fetching user details:', error)
    }
  } else {
    console.log('No user ID found in session')
  }
})

// Function to fetch team members
const fetchTeamMembers = async () => {
  if (!teamId.value) {
    console.log('No team ID available')
    return
  }
  
  console.log('Fetching team members for team:', teamId.value)
  
  try {
    // Use the correct endpoint to get users by team ID
    const response = await fetch(`http://localhost:5003/users/team/${teamId.value}`)
    if (response.ok) {
      const data = await response.json()
      teamMembers.value = data.data || []
      console.log('Fetched team members:', teamMembers.value.length, teamMembers.value)
    } else {
      console.error('Failed to fetch team members:', response.status)
      teamMembers.value = []
    }
  } catch (error) {
    console.error('Error fetching team members:', error)
    teamMembers.value = []
  }
}

// Function to fetch user details by userid
const fetchUserDetails = async (userid) => {
  if (!userid) return null
  if (users.value[userid]) {
    return users.value[userid]
  }
  
  try {
    const response = await fetch(`http://localhost:5003/users/${userid}`)
    if (response.ok) {
      const data = await response.json()
      const user = data.data
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

// Function to get user names for display
const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || `User ${userid}`
}

// Function to fetch all users mentioned in tasks
const fetchTaskUsers = async () => {
  const userIds = new Set()
  
  tasks.value.forEach(task => {
    if (task.owner_id) userIds.add(task.owner_id)
    if (task.collaborators) {
      task.collaborators.forEach(id => userIds.add(id))
    }
    if (task.subtasks) {
      task.subtasks.forEach(subtask => {
        if (subtask.owner_id) userIds.add(subtask.owner_id)
        if (subtask.collaborators) {
          subtask.collaborators.forEach(id => userIds.add(id))
        }
      })
    }
  })
  
  const fetchPromises = Array.from(userIds).map(userid => fetchUserDetails(userid))
  await Promise.all(fetchPromises)
}

// Fetch team tasks
const fetchTeamTasks = async () => {
  if (!teamId.value) {
    console.log('No team ID for tasks')
    return
  }
  
  isLoadingTasks.value = true
  console.log('Fetching team tasks for team:', teamId.value)
  
  try {
    const response = await fetch(`http://localhost:5002/tasks/team/${teamId.value}`)
    console.log('Team tasks response status:', response.status)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    tasks.value = data.data || []
    console.log('Fetched team tasks:', tasks.value.length, tasks.value)
    
    await fetchTaskUsers()
  } catch (error) {
    console.error('Error fetching team tasks:', error)
    tasks.value = []
  } finally {
    isLoadingTasks.value = false
  }
}

// Workload management functions
const getMemberTasks = (memberId) => {
  return tasks.value.filter(task => 
    task.owner_id === memberId || 
    (task.collaborators && task.collaborators.includes(memberId))
  )
}

const getMemberTasksByStatus = (memberId, status) => {
  return getMemberTasks(memberId).filter(task => task.status === status)
}

const getMemberHighPriorityTasks = (memberId) => {
  return getMemberTasks(memberId).filter(task => parseInt(task.priority) >= 8).length
}

const getMemberUpcomingTasks = (memberId) => {
  const now = new Date()
  const threeDaysFromNow = new Date(now.getTime() + (3 * 24 * 60 * 60 * 1000))
  
  return getMemberTasks(memberId).filter(task => {
    if (!task.due_date || task.status === 'Completed') return false
    const dueDate = new Date(task.due_date)
    return dueDate >= now && dueDate <= threeDaysFromNow
  }).length
}

const getWorkloadClass = (member) => {
  const taskCount = getMemberTasks(member.userid).filter(task => task.status !== 'Completed').length
  const highPriorityCount = getMemberHighPriorityTasks(member.userid)
  
  if (taskCount >= 8 || highPriorityCount >= 4) return 'overload'
  if (taskCount >= 5 || highPriorityCount >= 2) return 'high'
  if (taskCount >= 3) return 'moderate'
  return 'low'
}

const getWorkloadLevel = (member) => {
  const workloadClass = getWorkloadClass(member)
  const levels = {
    'low': 'Light',
    'moderate': 'Moderate', 
    'high': 'Heavy',
    'overload': 'Overloaded'
  }
  return levels[workloadClass] || 'Light'
}

const filteredMembers = computed(() => {
  // Filter out the current user from the member list
  let membersExcludingCurrentUser = teamMembers.value.filter(member => member.userid !== userId.value)
  
  // Apply individual member filter
  if (selectedMember.value) {
    membersExcludingCurrentUser = membersExcludingCurrentUser.filter(member => member.userid === parseInt(selectedMember.value))
  }
  
  // Apply workload filter
  if (workloadFilter.value !== 'all') {
    membersExcludingCurrentUser = membersExcludingCurrentUser.filter(member => getWorkloadClass(member) === workloadFilter.value)
  }
  
  return membersExcludingCurrentUser
})

const viewMemberTasks = (memberId) => {
  viewMode.value = 'tasks'
  selectedTaskMember.value = memberId.toString()
}

const getWorkloadFilterLabel = (filter) => {
  const labels = {
    'low': 'Light Load',
    'moderate': 'Moderate Load',
    'high': 'Heavy Load',
    'overload': 'Overloaded'
  }
  return labels[filter] || 'All'
}



const isTaskOverdue = (task) => {
  if (!task.due_date || task.status === 'Completed') return false
  return new Date(task.due_date) < new Date()
}

const isTaskDueSoon = (task) => {
  if (!task.due_date || task.status === 'Completed') return false
  const dueDate = new Date(task.due_date)
  const now = new Date()
  const threeDaysFromNow = new Date(now.getTime() + (3 * 24 * 60 * 60 * 1000))
  return dueDate >= now && dueDate <= threeDaysFromNow
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const filteredTasks = computed(() => {
  let filtered = tasks.value
  
  if (activeFilter.value !== 'all') {
    filtered = filtered.filter(task => task.status === activeFilter.value)
  }
  
  if (selectedTaskMember.value) {
    const memberId = parseInt(selectedTaskMember.value)
    filtered = filtered.filter(task => 
      task.owner_id === memberId || 
      (task.collaborators && task.collaborators.includes(memberId))
    )
  }
  
  return filtered.sort((a, b) => {
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
        comparison = parseInt(b.priority) - parseInt(a.priority)
        break
      case 'status':
        const statusOrder = { 'Unassigned': 0, 'Ongoing': 1, 'Under Review': 2, 'Completed': 3 }
        comparison = statusOrder[a.status] - statusOrder[b.status]
        break
      case 'name':
        comparison = a.task_name.localeCompare(b.task_name)
        break
      case 'owner':
        const ownerA = getUserName(a.owner_id)
        const ownerB = getUserName(b.owner_id)
        comparison = ownerA.localeCompare(ownerB)
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
  router.push(`/tasks/${taskId}`)
}

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
  return status
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
    'all': 'No team tasks found.',
    'Ongoing': 'No ongoing team tasks.',
    'Under Review': 'No team tasks under review.',
    'Completed': 'No completed team tasks.',
    'Unassigned': 'No unassigned team tasks.'
  }
  return messages[activeFilter.value] || 'No team tasks found.'
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'Ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'Under Review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'Completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'Unassigned').length)
const overloadedMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'overload').length
})

const lightLoadMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'low').length
})

const moderateLoadMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'moderate').length
})

const heavyLoadMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'high').length
})

const memberTaskStats = computed(() => {
  if (!selectedTaskMember.value) {
    return {
      total: 0,
      ongoing: 0,
      underReview: 0,
      completed: 0,
      unassigned: 0
    }
  }
  
  const memberId = parseInt(selectedTaskMember.value)
  const memberTasks = getMemberTasks(memberId)
  
  return {
    total: memberTasks.length,
    ongoing: memberTasks.filter(task => task.status === 'Ongoing').length,
    underReview: memberTasks.filter(task => task.status === 'Under Review').length,
    completed: memberTasks.filter(task => task.status === 'Completed').length,
    unassigned: memberTasks.filter(task => task.status === 'Unassigned').length
  }
})
</script>