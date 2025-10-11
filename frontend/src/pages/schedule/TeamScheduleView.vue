<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />

    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Team Schedule</h1>
          <p class="page-subtitle">View and manage your team's schedule</p>
        </div>
        <div class="header-actions">
          <button
            class="view-toggle-btn"
            :class="{ active: viewMode === 'members' }"
            @click="showMemberView"
          >
            <i class="bi bi-people-fill"></i>
            Member View
          </button>
          <button
            class="view-toggle-btn"
            :class="{ active: viewMode === 'schedule' && !selectedMemberSchedule }"
            @click="showTeamScheduleView"
          >
            <i class="bi bi-calendar3"></i>
            Schedule View
          </button>
        </div>
      </div>

      <!-- Stats Section -->
      <div class="stats-section" :class="{ 'stats-section-member': viewMode === 'members' }">
        <div class="stats-container">
          <!-- Member Workload Stats -->
          <div v-if="viewMode === 'members'" class="workload-stats">
            <div
              class="stat-card workload-stat"
              @click="workloadFilter = 'all'"
              :class="{ active: workloadFilter === 'all' }"
            >
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

            <div
              class="stat-card workload-light"
              @click="workloadFilter = 'low'"
              :class="{ active: workloadFilter === 'low' }"
            >
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

            <div
              class="stat-card workload-moderate"
              @click="workloadFilter = 'moderate'"
              :class="{ active: workloadFilter === 'moderate' }"
            >
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

            <div
              class="stat-card workload-heavy"
              @click="workloadFilter = 'high'"
              :class="{ active: workloadFilter === 'high' }"
            >
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

            <div
              class="stat-card overload-stat"
              @click="workloadFilter = 'overload'"
              :class="{ active: workloadFilter === 'overload' }"
            >
              <div class="stat-content">
                <div class="stat-icon overload">
                  <i class="bi bi-exclamation-triangle-fill"></i>
                </div>
                <div class="stat-info">
                  <div class="stat-number">{{ overloadedMembers }}</div>
                  <div class="stat-title">Overload</div>
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
            <div class="sort-container d-flex align-items-center justify-content-between">
              <!-- Member Filter -->
              <div class="filter-group ms-4">
                <label for="memberFilter">Filter by member:</label>
                <select id="memberFilter" v-model="selectedMember" class="filter-dropdown">
                  <option value="">All Members</option>
                  <option v-for="member in filteredMembers" :key="member.userid" :value="member.userid">
                    {{ member.name }}
                  </option>
                </select>
              </div>

              <!-- Workload Legend -->
              <div class="workload-legend ms-4">
                <div class="legend-item">
                  <span class="legend-color low"></span> Light
               </div>
               <div class="legend-item">
                 <span class="legend-color moderate"></span> Moderate
               </div>
                <div class="legend-item">
                  <span class="legend-color high"></span> Heavy
                </div>
                <div class="legend-item">
                  <span class="legend-color overload"></span> Overloaded
                </div>
              </div>
            </div>
          </div>

          <!-- Member Cards -->
          <!-- Loading Spinner -->
          <div class="members-container-wrapper">
          <div v-if="!isMemberDataReady" class="members-loading">
            <div class="loading-spinner"></div>
            <p>Loading team members and tasks...</p>
          </div>

          <div v-else class="members-container">
            <div
              v-for="(member, index) in teamMembers.filter(m => m.userid !== currentUserId)"
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

              <!-- Member Actions -->
              <div class="member-actions">
                <button class="view-schedule-btn" @click="viewMemberSchedule(member.userid)">
                    <i class="bi bi-calendar3"></i>
                    View Schedule
                </button>
              </div>
            </div>
          </div>

          <div v-if="teamMembers.length < 0" class="empty-state">
            <p>No members match the filter.</p>
          </div>
        </div>
        </div>

        <!-- Schedule View -->
        <div v-if="viewMode === 'schedule' || selectedMemberSchedule">
        <div class="calendar-controls">
          <div class="view-toggle">
            <button 
              v-for="view in views" 
              :key="view.value"
              @click="currentView = view.value"
              :class="['view-btn', { active: currentView === view.value }]"
            >
              <i :class="view.icon"></i>
              {{ view.label }}
            </button>
          </div>
        
          <div class="date-navigation">
            <button @click="previousPeriod" class="nav-btn">
              <i class="bi bi-chevron-left"></i>
            </button>
            <h2 class="current-period">{{ currentPeriodTitle }}</h2>
            <button @click="nextPeriod" class="nav-btn">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        
          <div class="action-buttons">
            <button @click="toggleShowCompleted" class="toggle-completed-btn">
              <i :class="showCompleted ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
              {{ showCompleted ? 'Hide Completed' : 'Show Completed' }}
            </button>
            <button @click="toggleFilterPopup" class="filter-button">
              <i class="bi bi-funnel"></i>
              Filter
              <span v-if="hasActiveFilters" class="filter-badge">{{ activeFilterCount }}</span>
            </button>
            <button @click="goToToday" class="today-button">
              <i class="bi bi-calendar-check"></i>
              Today
            </button>
          </div>
        </div>

        <!-- Calendar Content -->
        <div class="calendar-container">
          <!-- Loading State -->
          <div v-if="loading" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading your tasks...</p>
          </div>
        
          <!-- Empty State -->
          <div v-else-if="!loading && tasks.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="bi bi-calendar-x"></i>
            </div>
            <h3>No tasks found</h3>
            <p>You don't have any tasks scheduled yet.</p>
          </div>
          <!-- Calendar Views -->
          <div v-else>
            <!-- Daily View -->
            <div v-if="currentView === 'day'" class="daily-view">
            <div class="day-header">
              <h3>{{ formatDate(currentDate, 'EEEE, MMMM d, yyyy') }}</h3>
              <div class="day-stats">
                <span class="task-count">{{ getTasksForDate(currentDate).length }} tasks</span>
              </div>
            </div>
          
            <div class="day-timeline">
              <div v-for="hour in 24" :key="hour" class="time-slot">
                <div class="time-label">{{ formatHour(hour - 1) }}</div>
                <div class="time-content">
                  <div 
                    v-for="task in getTasksForDateAndHour(currentDate, hour - 1)" 
                    :key="task.id"
                    class="task-event"
                    :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                    @click="selectTask(task)"
                  >
                    <div v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</div>
                    <div class="task-title">{{ task.task_name }}</div>
                    <div class="task-meta">
                      <div class="task-status-badge" :class="getTaskStatusClass(task.status)">
                        {{ task.status }}
                      </div>
                      <div class="task-time">{{ formatTime(task.due_date) }}</div>
                    </div>
                    <button 
                      v-if="isTaskOverdue(task)" 
                      class="reschedule-btn" 
                      @click.stop="openRescheduleModal(task)"
                    >
                      Reschedule
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Weekly View -->
          <div v-if="currentView === 'week'" class="weekly-view">
            <div class="week-header">
              <div class="day-header" v-for="day in weekDays" :key="day.date">
                <div class="day-name">{{ formatDate(day.date, 'EEE') }}</div>
                <div class="day-number" :class="{ today: isToday(day.date) }">
                  {{ formatDate(day.date, 'd') }}
                </div>
                <div class="day-tasks-count">{{ getTasksForDate(day.date).length }}</div>
              </div>
            </div>
          
            <div class="week-grid">
              <div v-for="day in weekDays" :key="day.date" class="day-column">
                <div 
                  v-for="task in getTasksForDate(day.date)" 
                  :key="task.id"
                  class="task-item"
                  :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                  @click="onTaskClick(task, $event)"
                >
                  <span v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</span>
                  <div class="task-title">{{ task.task_name }}</div>
                  <div class="task-status-badge" :class="getTaskStatusClass(task.status)">
                    {{ task.status }}
                  </div>
                  <div class="task-time">{{ formatTime(task.due_date) }}</div>
                  <button 
                    v-if="isTaskOverdue(task)" 
                    class="reschedule-btn" 
                    @click.stop="openRescheduleModal(task)"
                  >
                  Reschedule
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Monthly View -->
          <div v-if="currentView === 'month'" class="monthly-view">
            <div class="month-grid">
              <div 
                v-for="day in monthDays" 
                :key="day.date" 
                class="month-day"
                :class="{ 
                  'other-month': !day.isCurrentMonth,
                  'today': isToday(day.date),
                  'has-tasks': getTasksForDate(day.date).length > 0
                }"
                @click="selectDate(day.date)"
              >
                <div class="day-number">{{ formatDate(day.date, 'd') }}</div>
                <div class="day-tasks">
                  <div 
                    v-for="task in getTasksForDate(day.date)" 
                    :key="task.id"
                    class="task-box"
                    :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                    :title="`${task.task_name} - ${task.status}`"
                  >
                    <span v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</span>
                    <div class="task-box-name">{{ task.task_name }}</div>
                    <div class="task-box-status">{{ task.status }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>
        </div>
        </div>

        <!-- Task Details Modal -->
        <div v-if="selectedTask" class="task-modal-overlay" @click="selectedTaskForDetails = null">
          <div class="task-modal" @click.stop>
            <div class="modal-header">
              <h3>{{ selectedTask.task_name }}</h3>
              <button @click="closeTaskModal" class="close-btn">
                <i class="bi bi-x"></i>
              </button>
           </div>
            <div class="modal-content">
              <div class="task-details">
                <div class="detail-row">
                  <span class="label">Status:</span>
                  <span class="value" :class="getTaskStatusClass(selectedTask.status)">
                    {{ selectedTask.status }}
                  </span>
                </div>
                <div class="detail-row">
                  <span class="label">Type:</span>
                  <span class="value">{{ selectedTask.type || 'N/A' }}</span>
                </div>
                <div class="detail-row" v-if="selectedTask.project_id">
                  <span class="label">Project ID:</span>
                  <span class="value">{{ selectedTask.project_id }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Due Date:</span>
                  <span class="value">{{ formatDate(selectedTask.due_date, 'EEEE, MMMM d, yyyy') }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Time:</span>
                  <span class="value">{{ formatTime(selectedTask.due_date) }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Description:</span>
                  <span class="value">{{ selectedTask.description || 'No description' }}</span>
                </div>
                <div class="detail-row" v-if="selectedTask.collaborators && selectedTask.collaborators.length > 0">
                  <span class="label">Collaborators:</span>
                  <span class="value">{{ getCollaboratorNames(selectedTask.collaborators) }}</span>
                </div>
                <div class="detail-row" v-if="selectedTask.attachments && selectedTask.attachments.length > 0">
                  <span class="label">Attachments:</span>
                  <span class="value">
                    <div v-for="attachment in selectedTask.attachments" :key="attachment.name">
                        {{ attachment.name }}
                    </div>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Reschedule Modal -->
        <div v-if="showRescheduleModal" class="modal-overlay">
          <div class="modal-content">
            <h3>Reschedule Task</h3>
            <p><strong>{{ selectedTaskForReschedule?.task_name }}</strong></p>

            <label for="newDueDate">New Due Date:</label>
            <input id="newDueDate" type="datetime-local" v-model="newDueDate" class="date-picker" :min="todayString" />

            <div class="modal-actions">
              <button class="confirm-btn" @click="confirmReschedule">Save</button>
              <button class="cancel-btn" @click="closeRescheduleModal">Cancel</button>
            </div>
          </div>
        </div>
        <!-- Success Popup -->
        <div v-if="successMessage" class="success-popup">
          {{ successMessage }}
        </div>

        <!-- Error Popup -->
        <div v-if="errorMessage" class="error-popup">
          <span>{{ errorMessage }}</span>
          <button class="close-btn" @click="errorMessage = ''">&times;</button>
        </div>

        <!-- Filter Popup -->
        <div v-if="showFilterPopup" class="filter-popup-overlay" @click="closeFilterPopup">
          <div class="filter-popup" @click.stop>
            <div class="filter-header">
              <h3>Filter Tasks</h3>
              <button @click="closeFilterPopup" class="close-btn">
                <i class="bi bi-x"></i>
              </button>
            </div>
          
            <div class="filter-body">
              <!-- Project Filter -->
              <div class="filter-section">
                <label class="filter-label">
                  <i class="bi bi-folder"></i>
                  Project
                </label>
                <select v-model="selectedProjectFilter" class="filter-select">
                  <option value="">All Projects</option>
                  <option v-for="project in projects" :key="project.id" :value="project.id">
                    {{ project.name }}
                  </option>
                </select>
              </div>

              <!-- Status Filter -->
              <div class="filter-section">
                <label class="filter-label">
                  <i class="bi bi-check-circle"></i>
                  Status
                </label>
                <div class="status-checkboxes">
                  <label class="checkbox-label">
                    <input type="checkbox" value="Unassigned" v-model="selectedStatusFilters" />
                    <span class="status-indicator status-unassigned"></span>
                   Unassigned
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" value="Ongoing" v-model="selectedStatusFilters" />
                    <span class="status-indicator status-ongoing"></span>
                    Ongoing
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" value="Under Review" v-model="selectedStatusFilters" />
                    <span class="status-indicator status-under-review"></span>
                    Under Review
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" value="Completed" v-model="selectedStatusFilters" />
                    <span class="status-indicator status-completed"></span>
                    Completed
                  </label>
                </div>
              </div>
            </div>

            <div class="filter-actions">
              <button @click="clearFilters" class="clear-btn">Clear All</button>
              <button @click="applyFilters" class="apply-btn">Apply Filters</button>
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
import { getCurrentUserData, sessionState } from '../../services/session.js'

/* ----------------------------------------------------------
   State
---------------------------------------------------------- */
const viewMode = ref('members')
const selectedMember = ref('')
const workloadFilter = ref('all')
const tasks = ref([])
const teamMembers = ref([])
const users = ref({})
const userId = ref(null)
const teamId = ref(null)
const isLoadingTasks = ref(false)
const isLoadingMembers = ref(false)
const isLoading = computed(() => {
  return isLoadingTasks.value || teamMembers.value.length === 0
})
const isMemberDataReady = computed(() => {
  // Only true if tasks and members are both loaded
  return !isLoadingTasks.value && teamMembers.value.length > 0
})
const userRole = ref('')
const currentUserId = ref(null)

/* ----------------------------------------------------------
   Lifecycle: Fetch user, team, and tasks
---------------------------------------------------------- */
onMounted(async () => {
  const userData = getCurrentUserData()
  currentUserId.value = userData?.userid || null
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

/* ----------------------------------------------------------
   Data Fetching
---------------------------------------------------------- */
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

const fetchTasks = async () => {
  try {
    // Get user ID from session
    const userId = sessionState.userid
    if (!userId) {
      console.warn('No user ID found in session')
      tasks.value = []
      return
    }
    
    // Fetch tasks directly from API endpoint
    const response = await fetch(`http://127.0.0.1:5002/tasks/user-task/${userId}`, {
      headers: { 'Content-Type': 'application/json' }
    })
    
    if (!response.ok) {
      const msg = await response.text().catch(() => response.statusText)
      throw new Error(msg || `HTTP ${response.status}`)
    }
    
    const data = await response.json()
    console.log('API Response:', data)
    
    if (data.data) {
      const allTasks = []
      
      // Process parent tasks and their subtasks
      data.data.forEach(parentTask => {
        // Add parent task
        allTasks.push(parentTask)
        
        // Add subtasks if they exist
        if (parentTask.subtasks && Array.isArray(parentTask.subtasks)) {
          parentTask.subtasks.forEach(subtask => {
            allTasks.push(subtask)
          })
        }
      })
      
      tasks.value = allTasks
      console.log('Loaded tasks:', allTasks.length, 'total tasks')
      
      // Fetch user details for all unique collaborators
      const uniqueUserIds = new Set()
      allTasks.forEach(task => {
        if (task.collaborators && Array.isArray(task.collaborators)) {
          task.collaborators.forEach(id => uniqueUserIds.add(id))
        }
      })
      
      // Fetch user details for each unique user ID
      for (const userId of uniqueUserIds) {
        await fetchUserDetails(userId)
      }
      
      console.log('Fetched user details for', uniqueUserIds.size, 'users')
      
      // Debug timezone handling
      allTasks.forEach(task => {
        if (task.due_date) {
          const taskDate = new Date(task.due_date)
          const sgDateString = taskDate.toLocaleDateString('en-CA', { timeZone: 'Asia/Singapore' })
          const sgTimeString = taskDate.toLocaleTimeString('en-US', { timeZone: 'Asia/Singapore' })
          console.log(`Task "${task.task_name}": UTC ${task.due_date} -> SG ${sgDateString} ${sgTimeString}`)
        }
      })
    } else {
      console.warn('Unexpected API response format:', data)
      tasks.value = []
    }
  } catch (error) {
    console.error('Error fetching tasks:', error)
    tasks.value = []
  }
}

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

/* ----------------------------------------------------------
   View switching
---------------------------------------------------------- */
const selectedMemberSchedule = ref(null)
const scheduleViewMode = ref('team')

const viewMemberSchedule = (memberId) => {
  selectedMemberSchedule.value = memberId
  viewMode.value = 'schedule'
  scheduleViewMode.value = 'member'
}

const showTeamScheduleView = () => {
  viewMode.value = 'schedule'
  selectedMemberSchedule.value = null
  scheduleViewMode.value = 'team'
}

const showMemberView = () => {
  viewMode.value = 'members'
  selectedMemberSchedule.value = null
  scheduleViewMode.value = 'team'
}

/* ----------------------------------------------------------
   Workload Helpers
---------------------------------------------------------- */
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

/* ----------------------------------------------------------
   Computed Members and Workload Filters
---------------------------------------------------------- */
const filteredMembers = computed(() => {
  let members = teamMembers.value.filter(m => m.userid !== userId.value)
  if (selectedMember.value) {
    members = members.filter(m => m.userid === parseInt(selectedMember.value))
  }
  if (workloadFilter.value !== 'all') {
    members = members.filter(m => getWorkloadClass(m) === workloadFilter.value)
  }
  return members
})

const overloadedMembers = computed(() =>
  filteredMembers.value.filter(m => getWorkloadClass(m) === 'overload').length
)
const lightLoadMembers = computed(() =>
  filteredMembers.value.filter(m => getWorkloadClass(m) === 'low').length
)
const moderateLoadMembers = computed(() =>
  filteredMembers.value.filter(m => getWorkloadClass(m) === 'moderate').length
)
const heavyLoadMembers = computed(() =>
  filteredMembers.value.filter(m => getWorkloadClass(m) === 'high').length
)

const getCollaboratorNames = (collaboratorIds) => {
  if (!Array.isArray(collaboratorIds)) return "None";
  return collaboratorIds
    .map((id) => {
      const member = teamMembers.value.find((m) => m.userid === id);
      return member ? member.name : "Unknown";
    })
    .join(", ");
};

const displayedTasks = computed(() => {
  if (scheduleViewMode.value === 'team') {
    return filteredTasks.value
  } else if (scheduleViewMode.value === 'member' && selectedMemberSchedule.value) {
    // Only tasks assigned to this member
    return filteredTasks.value.filter(task => 
      task.owner_id === selectedMemberSchedule.value ||
      (task.collaborators && task.collaborators.includes(selectedMemberSchedule.value))
    )
  }
  return []
})


/* ----------------------------------------------------------
   Filters & Calendar View Setup
---------------------------------------------------------- */
const showFilterPopup = ref(false)
const projects = ref([])
const selectedProjectFilter = ref('')
const selectedStatusFilters = ref([])
const appliedProjectFilter = ref('')
const appliedStatusFilters = ref([])
const showCompleted = ref(true)

const views = [
  { value: 'day', label: 'Day', icon: 'bi bi-calendar-day' },
  { value: 'week', label: 'Week', icon: 'bi bi-calendar-week' },
  { value: 'month', label: 'Month', icon: 'bi bi-calendar-month' }
]

const isToday = (date) => {
  const today = new Date()
  const d = new Date(date)
  return d.toDateString() === today.toDateString()
}
/* ----------------------------------------------------------
   Date Utilities and Formatting
---------------------------------------------------------- */
const currentDate = ref(new Date())
const currentView = ref('week')

const formatDate = (date, format = 'yyyy-MM-dd') => {
  if (!date) return ''
  const d = new Date(date)
  const opts = { timeZone: 'Asia/Singapore' }

  switch (format) {
    case 'EEEE, MMMM d, yyyy':
      return d.toLocaleDateString('en-US', {
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', ...opts
      })
    case 'EEE':
      return d.toLocaleDateString('en-US', { weekday: 'short', ...opts })
    case 'd':
      return d.getDate().toString()
    case 'MMM d':
      return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', ...opts })
    case 'MMMM yyyy':
      return d.toLocaleDateString('en-US', { month: 'long', year: 'numeric', ...opts })
    default:
      return d.toLocaleDateString('en-US', opts)
  }
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Singapore'
  })
}

const formatHour = (hour) => `${hour.toString().padStart(2, '0')}:00`

const getWeekStart = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day
  return new Date(d.setDate(diff))
}

/* ----------------------------------------------------------
   Calendar Navigation
---------------------------------------------------------- */
const previousPeriod = () => {
  if (currentView.value === 'day') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() - 1))
  } else if (currentView.value === 'week') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() - 7))
  } else if (currentView.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() - 1))
  }
}

const nextPeriod = () => {
  if (currentView.value === 'day') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() + 1))
  } else if (currentView.value === 'week') {
    currentDate.value = new Date(currentDate.value.setDate(currentDate.value.getDate() + 7))
  } else if (currentView.value === 'month') {
    currentDate.value = new Date(currentDate.value.setMonth(currentDate.value.getMonth() + 1))
  }
}

const goToToday = () => {
  currentDate.value = new Date()
}

/* ----------------------------------------------------------
   Calendar Computed Properties
---------------------------------------------------------- */
const currentPeriodTitle = computed(() => {
  switch (currentView.value) {
    case 'day':
      return formatDate(currentDate.value, 'EEEE, MMMM d, yyyy')
    case 'week':
      const weekStart = getWeekStart(currentDate.value)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekStart.getDate() + 6)
      return `${formatDate(weekStart, 'MMM d')} - ${formatDate(weekEnd, 'MMM d, yyyy')}`
    case 'month':
      return formatDate(currentDate.value, 'MMMM yyyy')
    default:
      return ''
  }
})

const weekDays = computed(() => {
  const weekStart = getWeekStart(currentDate.value)
  return Array.from({ length: 7 }, (_, i) => {
    const date = new Date(weekStart)
    date.setDate(weekStart.getDate() + i)
    return { date }
  })
})

const monthDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)

  const startDate = new Date(firstDay)
  startDate.setDate(startDate.getDate() - firstDay.getDay())
  const endDate = new Date(lastDay)
  endDate.setDate(endDate.getDate() + (6 - lastDay.getDay()))

  const totalWeeks = Math.ceil((endDate - startDate) / (7 * 24 * 60 * 60 * 1000))
  const totalDays = totalWeeks * 7

  const days = []
  const current = new Date(startDate)
  for (let i = 0; i < totalDays; i++) {
    days.push({ date: new Date(current), isCurrentMonth: current.getMonth() === month })
    current.setDate(current.getDate() + 1)
  }
  return days
})

/* ----------------------------------------------------------
   Filtering and Task Utilities
---------------------------------------------------------- */
const filteredTasks = computed(() => {
  let filtered = [...tasks.value]
  if (!showCompleted.value) {
    filtered = filtered.filter(task => task.status?.toLowerCase() !== 'completed')
  }
  if (appliedProjectFilter.value) {
    filtered = filtered.filter(task =>
      String(task.project_id) === String(appliedProjectFilter.value)
    )
  }
  if (appliedStatusFilters.value.length > 0) {
    filtered = filtered.filter(task =>
      appliedStatusFilters.value.includes(task.status)
    )
  }
  return filtered
})

const hasActiveFilters = computed(() =>
  appliedProjectFilter.value !== '' || appliedStatusFilters.value.length > 0
)

const activeFilterCount = computed(() => {
  let count = 0
  if (appliedProjectFilter.value) count++
  if (appliedStatusFilters.value.length > 0) count += appliedStatusFilters.value.length
  return count
})

/* ----------------------------------------------------------
   Task Helpers
---------------------------------------------------------- */
const getTasksForDate = (date) => {
  if (!date || !displayedTasks.value?.length) return []
  const targetDateString = new Date(date).toLocaleDateString('en-CA', { timeZone: 'Asia/Singapore' })

  return displayedTasks.value.filter(task => {
    if (!task.due_date) return false
    const taskDateString = new Date(task.due_date).toLocaleDateString('en-CA', { timeZone: 'Asia/Singapore' })
    return taskDateString === targetDateString
  }).sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
}

const getTasksForDateAndHour = (date, hour) => {
  return getTasksForDate(date).filter(task => {
    if (!task.due_date) return false
    const h = parseInt(new Date(task.due_date).toLocaleTimeString('en-US', {
      timeZone: 'Asia/Singapore', hour12: false, hour: '2-digit'
    }))
    return h === hour
  })
}


const getTaskStatusClass = (status) => {
  switch (status?.toLowerCase()) {
    case 'unassigned': return 'status-unassigned'
    case 'ongoing': return 'status-ongoing'
    case 'under review': return 'status-under-review'
    case 'completed': return 'status-completed'
    default: return 'status-default'
  }
}

const isTaskOverdue = (task) => {
  if (!task.due_date) return false
  const now = new Date()
  const due = new Date(task.due_date)
  return due < now && task.status?.toLowerCase() !== 'completed'
}

/* ----------------------------------------------------------
   Task Modal & Reschedule
---------------------------------------------------------- */
const selectedTask = ref(null)
const showRescheduleModal = ref(false)
const newDueDate = ref(new Date().toISOString().slice(0, 16));
const todayString = ref(new Date().toISOString().slice(0, 16));
const successMessage = ref('')
const errorMessage = ref('')
const selectedTaskForReschedule = ref(null)

const openRescheduleModal = (task) => {
  selectedTaskForReschedule.value = task
  newDueDate.value = task.due_date ? task.due_date.split('T')[0] : todayString.value
  showRescheduleModal.value = true
}

const closeRescheduleModal = () => {
  showRescheduleModal.value = false
  selectedTaskForReschedule.value = null
  newDueDate.value = ''
}

const showSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = ''), 3000)
}

const showError = (msg) => {
  errorMessage.value = msg
  setTimeout(() => (errorMessage.value = ''), 5000)
}

const confirmReschedule = async () => {
  if (!newDueDate.value) return showError('Please select a new due date.')
  if (newDueDate.value < todayString.value) return showError('Cannot reschedule to a date before today.')

  try {
    const utcDateString = new Date(newDueDate.value).toISOString()
    const payload = {
      task_id: selectedTaskForReschedule.value.id,
      due_date: utcDateString
    }

    const res = await fetch('http://127.0.0.1:5002/tasks/update', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const data = await res.json()

    if (data.Code === 200) {
      selectedTaskForReschedule.value.due_date = newDueDate.value
      showSuccess('Task rescheduled successfully!')
    } else {
      showError(`Failed to reschedule: ${data.Message}`)
    }
  } catch (err) {
    console.error(err)
    showError('Error rescheduling task.')
  } finally {
    closeRescheduleModal()
  }
}

/* ----------------------------------------------------------
   Filter Controls
---------------------------------------------------------- */
const toggleShowCompleted = () => (showCompleted.value = !showCompleted.value)

const toggleFilterPopup = () => {
  showFilterPopup.value = !showFilterPopup.value
  if (showFilterPopup.value && projects.value.length === 0) fetchProjects()
}

const closeFilterPopup = () => (showFilterPopup.value = false)

const clearFilters = () => {
  selectedProjectFilter.value = ''
  selectedStatusFilters.value = []
  appliedProjectFilter.value = ''
  appliedStatusFilters.value = []
}

const applyFilters = () => {
  appliedProjectFilter.value = selectedProjectFilter.value
  appliedStatusFilters.value = [...selectedStatusFilters.value]
  closeFilterPopup()
}

const fetchProjects = async () => {
  try {
    const userId = sessionState.userid
    if (!userId) return console.warn('No user ID found in session')

    const res = await fetch(`http://127.0.0.1:5001/projects/user/${userId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    const data = await res.json()
    projects.value = Array.isArray(data.data)
      ? data.data.map(p => ({ id: p.id, name: p.proj_name }))
      : []
  } catch (err) {
    console.error('Error fetching projects:', err)
    projects.value = []
  }
}

/* ----------------------------------------------------------
   Lifecycle and Watchers
---------------------------------------------------------- */

watch(() => sessionState.userid, (newUserId) => {
  if (newUserId) fetchTasks()
})

/* ----------------------------------------------------------
   Debug Helpers
---------------------------------------------------------- */
window.debugCalendar = {
  getTasksForDate: (d) => getTasksForDate(new Date(d)),
  goToDate: (d) => {
    currentDate.value = new Date(d)
    console.log(`Navigated to: ${new Date(d).toDateString()}`)
  }
}
</script>


<style scoped>
@import './scheduleview.css';
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;
}

/* Loading state specific to member view */
.members-view .loading-state {
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f4f6;
  border-top: 3px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem auto;
}

.sort-container {
  display: flex;
  align-items: center;
  justify-content: space-between; /* filter on left, legend on right */
  width: 100%;
}

.header-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-content {
  display: flex;
  flex-direction: column;
}

.header-actions {
  display: flex;
  gap: 0.75rem; /* space between the two buttons */
  align-items: center;
  justify-content: flex-end;
}

.view-schedule-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: #f3f4f6;
  color: #374151;
}

.view-schedule-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.members-container-wrapper {
  position: relative;
  min-height: 300px; /* keeps height consistent even while loading */
}

.members-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #4b5563; /* subtle gray */
  font-size: 0.95rem;
  gap: 0.75rem;
}

.loading-spinner {
  border: 3px solid #e5e7eb;
  border-top: 3px solid #3b82f6; /* blue accent */
  border-radius: 50%;
  width: 28px;
  height: 28px;
  animation: spin 0.8s linear infinite;
}


.workload-legend {
  display: flex;
  align-items: center;
  gap: 1rem; /* space between legend items */
  font-size: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  display: inline-block;
}

.legend-color.low { background: #d1fae5; color: #065f46; }
.legend-color.moderate { background: #fef3c7; color: #92400e;} 
.legend-color.high { background: #fecaca; color: #991b1b;}
.legend-color.overload { background: #fee2e2; color: #7f1d1d;} 

@keyframes spin {
  to { transform: rotate(360deg); }
}


</style>
