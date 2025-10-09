<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Project Workload</h1>
          <p class="page-subtitle">Monitor and manage project members' task distribution</p>
        </div>
        <div class="header-actions" v-if="selectedProjectId">
          <button class="back-btn" @click="goBackToProjects">
            <i class="bi bi-arrow-left"></i>
            Back to Projects
          </button>
          
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
      
      <!-- Content when no project selected - Show project grid -->
      <div v-if="!selectedProjectId" class="projects-grid-container">
        <!-- Loading state -->
        <div v-if="isLoadingProjects" class="loading-state">
          <div class="loading-spinner">
            <i class="bi bi-arrow-clockwise spin"></i>
          </div>
          <p class="loading-text">Loading your projects...</p>
        </div>

        <!-- No projects state -->
        <div v-else-if="userProjects.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-folder"></i>
          </div>
          <div class="empty-title">No Projects Found</div>
          <p class="empty-subtitle">You don't have any projects assigned. Contact your administrator to get added to projects.</p>
        </div>

        <!-- Projects grid -->
        <div v-else class="projects-grid">
          <h2 class="section-title">Choose a Project to View Workload</h2>
          <div class="projects-container">
            <div 
              v-for="(project, index) in userProjects" 
              :key="project.id"
              class="project-card"
              :style="{ animationDelay: `${index * 0.1}s` }"
              @click="selectProject(project.id)"
            >
              <div class="project-header">
                <div class="project-icon">
                  <i class="bi bi-folder-fill"></i>
                </div>
                <div class="project-info">
                  <h3 class="project-name">{{ project.proj_name || project.name }}</h3>
                  <!-- <p class="project-id">Project ID: {{ project.id }}</p> -->
                </div>
              </div>
              
              <div class="project-meta">
                <div class="meta-item">
                  <i class="bi bi-person-fill"></i>
                  <span>Owner: {{ project.owner_name || 'Unknown' }}</span>
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

              <div class="project-actions">
                <div class="action-hint">
                  <i class="bi bi-arrow-right"></i>
                  <span>Click to view workload</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content when project is selected -->
      <div v-else>
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
                    <div class="stat-number">{{ projectMembers.filter(m => m.userid !== userId).length }}</div>
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
            <div class="sort-controls">
              <div class="sort-container">
                <div class="filter-group">
                  <label for="memberFilter">Filter by member:</label>
                  <select id="memberFilter" v-model="selectedMember" class="filter-dropdown">
                    <option value="">All Members</option>
                    <option v-for="member in projectMembers.filter(m => m.userid !== userId)" :key="member.userid" :value="member.userid">
                      {{ member.name }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Loading state -->
            <div v-if="isLoadingTasks" class="loading-state">
              <div class="loading-spinner">
                <i class="bi bi-arrow-clockwise spin"></i>
              </div>
              <p class="loading-text">Loading project tasks...</p>
            </div>

            <!-- Members Grid -->
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
                      <p class="member-role">{{ member.role }}</p>
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
                <button @click="toggleSortOrder" class="sort-order-btn">
                  <i :class="sortOrder === 'asc' ? 'bi bi-sort-up' : 'bi bi-sort-down'"></i>
                </button>

                <div class="filter-group">
                  <label for="memberTaskFilter">Filter by member:</label>
                  <select id="memberTaskFilter" v-model="selectedTaskMember" class="filter-dropdown">
                    <option value="">All Members</option>
                    <option v-for="member in projectMembers.filter(m => m.userid !== userId)" :key="member.userid" :value="member.userid">
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
                <p class="loading-text">Loading project tasks...</p>
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
                        <div v-if="isTaskOverdue(task)" class="task-overdue">
                          <i class="bi bi-exclamation-triangle-fill"></i>
                          <span>Overdue</span>
                        </div>
                        <div v-else-if="isTaskDueSoon(task)" class="task-due-soon">
                          <i class="bi bi-clock"></i>
                          <span>Due Soon</span>
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
                    </div>
                  </div>
                </transition>
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
import SideNavbar from '../../components/SideNavbar.vue'
import { useRoute, useRouter } from 'vue-router'
import { getCurrentUserData } from '../../services/session.js'
import '../taskview/taskview.css'

const route = useRoute()
const router = useRouter()

// Reactive data
const viewMode = ref('members')
const selectedProjectId = ref('')
const selectedMember = ref('')
const selectedTaskMember = ref('')
const workloadFilter = ref('all')
const sortBy = ref('due_date')
const sortOrder = ref('asc')
const activeFilter = ref('all')
const expandedTasks = ref([])

const userProjects = ref([])
const projectMembers = ref([])
const tasks = ref([])
const users = ref({})
const isLoadingProjects = ref(false)
const isLoadingTasks = ref(false)

// Get current user data
const userData = getCurrentUserData()
const userId = parseInt(userData.userid) || localStorage.getItem('spm_userid')

// Computed properties
const filteredMembers = computed(() => {
  let filtered = projectMembers.value.filter(member => member.userid !== userId)
  
  if (selectedMember.value) {
    filtered = filtered.filter(member => member.userid === parseInt(selectedMember.value))
  }
  
  if (workloadFilter.value !== 'all') {
    filtered = filtered.filter(member => getWorkloadClass(member) === workloadFilter.value)
  }
  
  return filtered
})

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

// Member task statistics for task view
const memberTaskStats = computed(() => {
  if (!selectedTaskMember.value) return { total: 0, ongoing: 0, underReview: 0, completed: 0, unassigned: 0 }
  
  const memberTasks = filteredTasks.value
  return {
    total: memberTasks.length,
    ongoing: memberTasks.filter(task => task.status === 'Ongoing').length,
    underReview: memberTasks.filter(task => task.status === 'Under Review').length,
    completed: memberTasks.filter(task => task.status === 'Completed').length,
    unassigned: memberTasks.filter(task => task.status === 'Unassigned').length
  }
})

// Task statistics
const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'Ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'Under Review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'Completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'Unassigned').length)

// Workload statistics
const overloadedMembers = computed(() => {
  if (!projectMembers.value || projectMembers.value.length === 0) return 0
  return projectMembers.value.filter(member => member.userid !== userId && getWorkloadClass(member) === 'overload').length
})

const lightLoadMembers = computed(() => {
  if (!projectMembers.value || projectMembers.value.length === 0) return 0
  return projectMembers.value.filter(member => member.userid !== userId && getWorkloadClass(member) === 'low').length
})

const moderateLoadMembers = computed(() => {
  if (!projectMembers.value || projectMembers.value.length === 0) return 0
  return projectMembers.value.filter(member => member.userid !== userId && getWorkloadClass(member) === 'moderate').length
})

const heavyLoadMembers = computed(() => {
  if (!projectMembers.value || projectMembers.value.length === 0) return 0
  return projectMembers.value.filter(member => member.userid !== userId && getWorkloadClass(member) === 'high').length
})

// Methods
const fetchUserDetails = async (userid) => {
  if (!userid || users.value[userid]) return users.value[userid]
  
  try {
    const response = await fetch(`http://localhost:5003/users/${userid}`)
    if (response.ok) {
      const data = await response.json()
      users.value[userid] = data.data || data
      return users.value[userid]
    }
  } catch (error) {
    console.error('Error fetching user details:', error)
  }
  
  return null
}

const getUserName = (userid) => {
  if (!userid) return 'Unknown User'
  const user = users.value[userid]
  return user?.name || `User ${userid}`
}

// Fetch user's projects
const fetchUserProjects = async () => {
  if (!userId) return
  
  isLoadingProjects.value = true
  try {
    const response = await fetch(`http://localhost:5001/projects/user/${userId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    const projects = data.data || []
    
    // Fetch owner details for each project
    for (const project of projects) {
      if (project.owner_id) {
        const owner = await fetchUserDetails(project.owner_id)
        project.owner_name = owner?.name || 'Unknown'
      }
    }
    
    userProjects.value = projects
    console.log('Fetched user projects:', userProjects.value)
  } catch (error) {
    console.error('Error fetching user projects:', error)
    userProjects.value = []
  } finally {
    isLoadingProjects.value = false
  }
}

// Fetch project members
const fetchProjectMembers = async (projectId) => {
  if (!projectId) return
  
  try {
    const response = await fetch(`http://localhost:5001/projects/${projectId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    const project = data.data || data
    
    // Get project members (owner + collaborators)
    const memberIds = new Set()
    if (project.owner_id) memberIds.add(parseInt(project.owner_id))
    if (project.collaborators && Array.isArray(project.collaborators)) {
      project.collaborators.forEach(collaborator => {
        const id = typeof collaborator === 'object' ? collaborator.userid || collaborator.id : collaborator
        if (id) memberIds.add(parseInt(id))
      })
    }
    
    // Fetch user details for all members
    const memberPromises = Array.from(memberIds).map(id => fetchUserDetails(id))
    const memberDetails = await Promise.all(memberPromises)
    
    projectMembers.value = memberDetails.filter(member => member !== null)
    console.log('Fetched project members:', projectMembers.value)
  } catch (error) {
    console.error('Error fetching project members:', error)
    projectMembers.value = []
  }
}

// Fetch ALL tasks where project members are involved (like TeamTaskView does)
const fetchProjectMemberTasks = async (projectId) => {
  if (!projectId || projectMembers.value.length === 0) return
  
  isLoadingTasks.value = true
  try {
    // Get all tasks for each project member
    const allTasks = []
    const taskIds = new Set() // To avoid duplicates
    
    for (const member of projectMembers.value) {
      try {
        // Fetch all tasks where this member is owner or collaborator
        const response = await fetch(`http://localhost:5002/tasks/user-task/${member.userid}`)
        if (response.ok) {
          const data = await response.json()
          const memberTasks = data.data || []
          
          // Add tasks that aren't already in our collection
          memberTasks.forEach(task => {
            if (!taskIds.has(task.id)) {
              taskIds.add(task.id)
              allTasks.push(task)
            }
          })
        }
      } catch (error) {
        console.error(`Error fetching tasks for member ${member.userid}:`, error)
      }
    }
    
    tasks.value = allTasks
    console.log('Fetched project member tasks:', tasks.value.length, tasks.value)
    
    // Fetch user details for all users mentioned in tasks
    await fetchTaskUsers()
  } catch (error) {
    console.error('Error fetching project member tasks:', error)
    tasks.value = []
  } finally {
    isLoadingTasks.value = false
  }
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

// Project selection and navigation
const selectProject = async (projectId) => {
  selectedProjectId.value = projectId
  await onProjectChange()
}

const goBackToProjects = () => {
  selectedProjectId.value = ''
  projectMembers.value = []
  tasks.value = []
  // Reset filters
  selectedMember.value = ''
  selectedTaskMember.value = ''
  workloadFilter.value = 'all'
  activeFilter.value = 'all'
  viewMode.value = 'members'
}

const getProjectMemberCount = (project) => {
  let count = 1 // Owner
  if (project.collaborators && Array.isArray(project.collaborators)) {
    count += project.collaborators.length
  }
  return count
}

// Project change handler
const onProjectChange = async () => {
  if (!selectedProjectId.value) {
    projectMembers.value = []
    tasks.value = []
    return
  }
  
  // Reset filters
  selectedMember.value = ''
  selectedTaskMember.value = ''
  workloadFilter.value = 'all'
  activeFilter.value = 'all'
  viewMode.value = 'members'
  
  // Fetch project data
  await fetchProjectMembers(selectedProjectId.value)
  await fetchProjectMemberTasks(selectedProjectId.value)
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

// UI interaction methods
const viewMemberTasks = (memberId) => {
  viewMode.value = 'tasks'
  selectedTaskMember.value = memberId.toString()
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
}

const toggleSubtasks = (taskId) => {
  const index = expandedTasks.value.indexOf(taskId)
  if (index > -1) {
    expandedTasks.value.splice(index, 1)
  } else {
    expandedTasks.value.push(taskId)
  }
}

const navigateToTask = (taskId) => {
  router.push(`/tasks/${taskId}`)
}

// Task utility functions
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

const isTaskOverdue = (task) => {
  if (!task?.due_date || task.status === 'Completed') return false
  return new Date(task.due_date) < new Date()
}

const isTaskDueSoon = (task) => {
  if (!task?.due_date || task.status === 'Completed') return false
  const due = new Date(task.due_date)
  const now = new Date()
  const threeDaysFromNow = new Date(now.getTime() + (3 * 24 * 60 * 60 * 1000))
  return due >= now && due <= threeDaysFromNow
}

const getStatusClass = (status) => {
  const statusClasses = {
    'Ongoing': 'ongoing',
    'Under Review': 'under-review',
    'Completed': 'completed',
    'Unassigned': 'unassigned'
  }
  return statusClasses[status] || 'unassigned'
}

const getStatusIcon = (status) => {
  const statusIcons = {
    'Ongoing': 'bi-play-circle',
    'Under Review': 'bi-eye',
    'Completed': 'bi-check-circle-fill',
    'Unassigned': 'bi-person-dash'
  }
  return statusIcons[status] || 'bi-circle'
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
    'all': 'No project member tasks found.',
    'Ongoing': 'No ongoing tasks.',
    'Under Review': 'No tasks under review.',
    'Completed': 'No completed tasks.',
    'Unassigned': 'No unassigned tasks.'
  }
  return messages[activeFilter.value] || 'No tasks found.'
}

// Lifecycle
onMounted(async () => {
  await fetchUserProjects()
  
  // Check if there's a projectId in the query params
  const projectId = route.query.projectId
  if (projectId) {
    // Automatically select the project and load its data
    await selectProject(projectId)
  }
})
</script>

<style scoped>
.projects-grid-container {
  padding: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 2rem;
  text-align: center;
}

.projects-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.project-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
}

.project-card:hover {
  border-color: #3b82f6;
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.project-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.project-icon {
  font-size: 2.5rem;
  color: #3b82f6;
  min-width: 3rem;
}

.project-info {
  flex: 1;
}

.project-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.project-id {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.project-meta {
  margin-bottom: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  color: #4b5563;
}

.meta-item:last-child {
  margin-bottom: 0;
}

.meta-item i {
  color: #6b7280;
  width: 16px;
}

.project-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.action-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
  transition: color 0.2s ease;
}

.project-card:hover .action-hint {
  color: #3b82f6;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f3f4f6;
  border: none;
  border-radius: 6px;
  color: #374151;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-right: 1rem;
}

.back-btn:hover {
  background: #e5e7eb;
  color: #111827;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  text-align: center;
}

.loading-spinner {
  font-size: 2rem;
  color: #3b82f6;
  margin-bottom: 1rem;
}

.spin {
  animation: spin 1s linear infinite;
}

.empty-icon {
  font-size: 4rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-subtitle, .loading-text {
  color: #6b7280;
  font-size: 1rem;
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .projects-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .projects-grid-container {
    padding: 1rem;
  }
  
  .project-card {
    padding: 1rem;
  }
}
</style>
