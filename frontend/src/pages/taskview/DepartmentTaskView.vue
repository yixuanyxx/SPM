<template>
  <div class="app-layout ms-2">
    <!-- Side Navigation -->
    <SideNavbar />
    
    <!-- Main Content Area -->
    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">{{ selectedTeamId ? `${selectedTeamName} Workload` : 'Department Teams' }}</h1>
          <p class="page-subtitle">{{ selectedTeamId ? 'Monitor and manage team member task distribution' : 'Select a team to view member workloads and tasks' }}</p>
        </div>
        <div class="header-actions">
          <div class="header-left-actions" v-if="selectedTeamId">
            <button class="back-btn" @click="goBackToTeams">
              <i class="bi bi-arrow-left"></i>
              Back to Teams
            </button>
          </div>
          
          <div class="header-right-actions" v-if="selectedTeamId">
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
            <button 
              class="view-toggle-btn" 
              :class="{ active: viewMode === 'schedule' }"
              @click="viewMode = 'schedule'"
            >
              <i class="bi bi-list-task"></i>
              Schedule View
            </button>
          </div>
        </div>
      </div>
      
      <!-- Content when no team selected - Show team grid -->
      <div v-if="!selectedTeamId" class="teams-grid-container">
        <!-- Loading state -->
        <div v-if="isLoadingTeams" class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">Loading department teams and statistics...</p>
        </div>

        <!-- No teams state -->
        <div v-else-if="departmentTeams.length === 0" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-diagram-3"></i>
          </div>
          <div class="empty-title">No Teams Found</div>
          <p class="empty-subtitle">No teams found in this department. Contact your administrator to create teams.</p>
        </div>

        <!-- Teams grid -->
        <div v-else class="teams-grid">
          <h2 class="section-title">Choose a Team to View Workload</h2>
          <div class="teams-container">
            <div 
              v-for="(team, index) in departmentTeams" 
              :key="team.id"
              class="team-card"
              :style="{ animationDelay: `${index * 0.1}s` }"
              @click="selectTeam(team.id, team.name)"
            >
              <div class="team-header">
                <div class="team-icon">
                  <i class="bi bi-diagram-3-fill"></i>
                </div>
                <div class="team-info">
                  <h3 class="team-name">{{ team.name }}</h3>
                  <p class="team-dept">Department Team</p>
                </div>
              </div>
              
              <div class="team-meta">
                <div class="meta-item">
                  <i class="bi bi-people"></i>
                  <span>{{ getTeamMemberCount(team.id) }} members</span>
                </div>
                <div class="meta-item">
                  <i class="bi bi-list-task"></i>
                  <span>{{ getTeamTaskCount(team.id) }} tasks</span>
                </div>
              </div>

              <div class="team-workload-preview">
                <div class="workload-summary">
                  <div class="workload-item overload" v-if="getTeamWorkloadCount(team.id, 'overload') > 0">
                    <span class="count">{{ getTeamWorkloadCount(team.id, 'overload') }}</span>
                    <span class="label">Overloaded</span>
                  </div>
                  <div class="workload-item high" v-if="getTeamWorkloadCount(team.id, 'high') > 0">
                    <span class="count">{{ getTeamWorkloadCount(team.id, 'high') }}</span>
                    <span class="label">Heavy</span>
                  </div>
                  <div class="workload-item moderate" v-if="getTeamWorkloadCount(team.id, 'moderate') > 0">
                    <span class="count">{{ getTeamWorkloadCount(team.id, 'moderate') }}</span>
                    <span class="label">Moderate</span>
                  </div>
                  <div class="workload-item low" v-if="getTeamWorkloadCount(team.id, 'low') > 0">
                    <span class="count">{{ getTeamWorkloadCount(team.id, 'low') }}</span>
                    <span class="label">Light</span>
                  </div>
                </div>
              </div>
              
              <div class="team-action">
                <span class="action-text">Click to view team workload</span>
                <i class="bi bi-arrow-right"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    <!-- Stats Section - only show when team is selected -->
    <div v-if="selectedTeamId" class="stats-section" :class="{ 'stats-section-member': viewMode === 'members' }">
      <div class="stats-container">
        <!-- Member View Stats -->
        <div v-if="viewMode === 'members'" class="workload-stats">
          <div class="stat-card workload-stat" @click="workloadFilter = 'all'" :class="{ active: workloadFilter === 'all' }">
            <div class="stat-content">
              <div class="stat-icon members">
                <i class="bi bi-people"></i>
              </div>
              <div class="stat-info">
                <div class="stat-number">{{ departmentMembers.filter(m => m.userid !== userId).length }}</div>
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

    <!-- Main Content - only show when team is selected -->
    <div v-if="selectedTeamId" class="main-content" :class="{ 'main-content-member': viewMode === 'members' }">

      
      <!-- Member View -->
      <div v-if="viewMode === 'members'" class="members-view">
        <!-- Filter Controls for Member View -->
        <div class="sort-controls">
          <div class="sort-container">
            <div class="filter-group ms-4">
              <label for="memberFilter">Filter by member:</label>
              <select id="memberFilter" v-model="selectedMember" class="filter-dropdown">
                <option value="">All Members</option>
                <option v-for="member in departmentMembers.filter(m => m.userid !== userId)" :key="member.userid" :value="member.userid">
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
          </div>
          <p class="loading-text">Loading department members and tasks...</p>
        </div>

        <!-- Empty State for No Members -->
        <div v-else-if="departmentMembers.length === 0 && !isLoadingTasks" class="empty-state">
          <div class="empty-icon">
            <i class="bi bi-people"></i>
          </div>
          <div class="empty-title">No department members found</div>
          <p class="empty-subtitle">No team members found in this department.</p>
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
      <div v-if="viewMode === 'tasks'" class="tasks-view">

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
                <option v-for="member in departmentMembers.filter(m => m.userid !== userId)" :key="member.userid" :value="member.userid">
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
          <p class="loading-text">Loading department tasks...</p>
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

      <!-- Department Schedule View -->
      <div v-if="viewMode === 'schedule'" class="department-schedule-view">
        <div class="calendar-controls">
          <div class="view-toggle">
            <button 
              v-for="view in calendarViews" 
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
          <div v-if="isLoadingTasks" class="loading-state">
            <div class="loading-spinner"></div>
            <p>Loading team schedule...</p>
          </div>
        
          <!-- Empty State -->
          <div v-else-if="!isLoadingTasks && displayedTasks.length === 0" class="empty-state">
            <div class="empty-icon">
              <i class="bi bi-calendar-x"></i>
            </div>
            <h3>No tasks found</h3>
            <p>{{ appliedMemberFilter.value ? 'This member has no scheduled tasks.' : 'Your team has no scheduled tasks.' }}</p>
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
                      class="task-card"
                      :class="[getStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                      @click="selectTask(task)"
                    >
                      <div v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</div>
                      <div class="task-title">{{ task.task_name}}</div>
                      <div class="task-meta">
                        <div class="task-status-badge" :class="getStatusClass(task.status)">
                          {{ task.status }}
                        </div>
                        <div class="task-time">{{ formatTime(task.due_date) }}</div>
                        <div v-if="task.owner_id" class="task-owner">
                          <i class="bi bi-person"></i>
                          {{ getUserName(task.owner_id) }}
                        </div>
                      </div>
                      <button 
                        v-if="isTaskOverdue(task)&& task.owner_id === userId" 
                        class="reschedule-btn" 
                        @click.stop="openRescheduleModal(task)"
                      >
                        Reschedule
                      </button>

                      <button
                        v-if="isTaskOverdue(task)&& task.owner_id === userId"
                        @click="markAsCompleted(task)"
                        class="btn-complete"
                      >
                        Mark as Completed
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
                    :class="[getStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                    @click="selectTask(task)"
                  >
                    <span v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</span>
                    <div class="task-title">{{ task.task_name }}</div>
                    <div class="task-status-badge" :class="getStatusClass(task.status)">
                      {{ task.status }}
                    </div>
                    <div class="task-time">{{ formatTime(task.due_date) }}</div>
                    <div v-if="task.owner_id" class="task-owner">
                      <i class="bi bi-person"></i>
                      {{ getUserName(task.owner_id) }}
                    </div>
                    <button 
                      v-if="isTaskOverdue(task)&& task.owner_id === userId" 
                      class="reschedule-btn" 
                      @click.stop="openRescheduleModal(task)"
                    >
                      Reschedule
                    </button>

                    <button
                      v-if="isTaskOverdue(task)&& task.owner_id === userId"
                      @click="markAsCompleted(task)"
                      class="btn-complete"
                    >
                      Mark as Completed
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
                      :class="[getStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                      :title="`${task.task_name} - ${task.status} - ${getUserName(task.owner_id)}`"
                      @click.stop="selectTask(task)"
                    >
                      <span v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</span>
                      <div class="task-box-name">{{ task.task_name }}</div>
                      <div class="task-box-status">{{ task.status }}</div>
                      <div class="task-box-owner">{{ getUserName(task.owner_id) }}</div>
                    </div>
                  </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../../components/SideNavbar.vue'
import { getCurrentUserData } from '../../services/session.js'
import "../taskview/taskview.css"
import '../schedule/scheduleview.css'

const activeFilter = ref('all')
const sortBy = ref('due_date')
const sortOrder = ref('asc')
const expandedTasks = ref([])
const userRole = ref('')
const userId = ref(null)
const deptId = ref(null)
const viewMode = ref('members')
const selectedMember = ref('')
const selectedTaskMember = ref('')
const selectedTeamId = ref('')
const selectedTeamName = ref('')
const workloadFilter = ref('all')

const tasks = ref([])
const users = ref({})
const departmentMembers = ref([]) // Currently selected team members
const allDepartmentMembers = ref([]) // All department members for statistics
const departmentTeams = ref([])
const teamStats = ref({}) // Store team statistics
const isLoadingTasks = ref(false)
const isLoadingTeams = ref(false)

const showCompleted = ref(true)
const selectedMemberFilter = ref('')     
const appliedMemberFilter = ref('')
const appliedProjectFilter = ref('')
const appliedStatusFilters = ref([])
const currentView = ref('week')
const currentDate = ref(new Date())

// Get user data from session
onMounted(async () => {
  const userData = getCurrentUserData()
  userRole.value = userData.role?.toLowerCase() || ''
  userId.value = parseInt(userData.userid) || null
  
  console.log('Department Task View - User data from session:', userData)
  
  // Get user's dept_id
  if (userId.value) {
    try {
      const response = await fetch(`http://localhost:5003/users/${userId.value}`)
      if (response.ok) {
        const data = await response.json()
        deptId.value = data.data?.dept_id
        console.log('User dept_id:', deptId.value)
        
        if (deptId.value) {
          await fetchDepartmentTeams()
        } else {
          console.log('No department ID found for user')
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

// Function to fetch department members
const fetchDepartmentMembers = async () => {
  if (!deptId.value) {
    console.log('No department ID available')
    return
  }
  
  console.log('Fetching department members for dept:', deptId.value)
  
  try {
    // Use the correct endpoint to get users by department ID
    const response = await fetch(`http://localhost:5003/users/department/${deptId.value}`)
    if (response.ok) {
      const data = await response.json()
      departmentMembers.value = data.data || []
      console.log('Fetched department members:', departmentMembers.value.length, departmentMembers.value)
    } else {
      console.error('Failed to fetch department members:', response.status)
      departmentMembers.value = []
    }
  } catch (error) {
    console.error('Error fetching department members:', error)
    departmentMembers.value = []
  }
}

// Function to fetch department teams (optimized for speed)
const fetchDepartmentTeams = async () => {
  isLoadingTeams.value = true
  if (!deptId.value) {
    console.log('No department ID available for teams')
    return
  }
  
  isLoadingTeams.value = true
  console.log('Fetching department teams for dept:', deptId.value)
  
  try {
    // Fetch department members and teams in parallel (faster)
    console.log('Loading department data in parallel...')
    const [membersResult, teamsResult] = await Promise.all([
      fetchAllDepartmentMembers(),
      fetch(`http://localhost:5004/teams/department/${deptId.value}`).then(response => {
        if (response.ok) {
          return response.json()
        }
        throw new Error(`Failed to fetch teams: ${response.status}`)
      })
    ])
    
    // Process teams data
    departmentTeams.value = teamsResult.data || []
    console.log('Fetched department teams:', departmentTeams.value.length, 'teams')
    
    // Only fetch statistics if we have teams
    if (departmentTeams.value.length > 0) {
      console.log('Fetching workload statistics...')
      await fetchTeamStatistics()
    } else {
      console.log('No teams found, skipping statistics')
    }
    
  } catch (error) {
    console.error('Error fetching department teams:', error)
    departmentTeams.value = []
  } finally {
    isLoadingTeams.value = false
  }
}

// Function to fetch statistics for all teams (optimized for speed and accuracy)
const fetchTeamStatistics = async () => {
  if (!departmentTeams.value.length) return
  
  try {
    console.log(`Optimizing load for ${departmentTeams.value.length} teams...`)
    
    // Step 1: Parallel fetch of all team tasks
    const teamTaskPromises = departmentTeams.value.map(async (team) => {
      try {
        const response = await fetch(`http://localhost:5002/tasks/team/${team.id}`)
        if (response.ok) {
          const data = await response.json()
          return { teamId: team.id, tasks: data.data || [] }
        }
        return { teamId: team.id, tasks: [] }
      } catch (error) {
        console.error(`Error fetching tasks for team ${team.id}:`, error)
        return { teamId: team.id, tasks: [] }
      }
    })
    
    const teamTasksResults = await Promise.all(teamTaskPromises)
    console.log('Team tasks fetched in parallel')
    
    // Step 2: Build member task requests in parallel (optimized for empty teams)
    const allMemberTaskPromises = []
    const teamMemberMapping = {}
    let teamsWithMembers = 0
    
    // Pre-calculate team member mappings and build all member task requests
    departmentTeams.value.forEach(team => {
      const teamMembers = allDepartmentMembers.value.filter(member => member.team_id === team.id)
      teamMemberMapping[team.id] = teamMembers
      
      if (teamMembers.length > 0) {
        teamsWithMembers++
        // Add parallel requests for all members of this team
        teamMembers.forEach(member => {
          allMemberTaskPromises.push(
            fetch(`http://localhost:5002/tasks/user-task/${member.userid}`)
              .then(response => response.ok ? response.json() : null)
              .then(data => ({
                teamId: team.id,
              memberId: member.userid,
              tasks: data?.data || []
            }))
            .catch(error => {
              console.error(`Error fetching tasks for member ${member.userid}:`, error)
              return { teamId: team.id, memberId: member.userid, tasks: [] }
            })
        )
      })
      }
    })
    
    console.log(`Optimized: ${teamsWithMembers} teams with members, ${allMemberTaskPromises.length} total member requests`)
    
    // Step 3: Execute all member task requests in parallel
    const memberTasksResults = await Promise.all(allMemberTaskPromises)
    console.log(`Member tasks fetched in parallel for ${allMemberTaskPromises.length} members`)
    
    // Step 4: Process all results efficiently
    const finalStats = {}
    
    departmentTeams.value.forEach(team => {
      // Get team task count
      const teamTaskResult = teamTasksResults.find(result => result.teamId === team.id)
      const taskCount = teamTaskResult ? teamTaskResult.tasks.length : 0
      
      // Calculate workload distribution
      const workloadCounts = { low: 0, moderate: 0, high: 0, overload: 0 }
      const teamMembers = teamMemberMapping[team.id] || []
      
      // Process each team member's workload
      teamMembers.forEach(member => {
        const memberTaskResult = memberTasksResults.find(
          result => result.teamId === team.id && result.memberId === member.userid
        )
        
        if (memberTaskResult && memberTaskResult.tasks.length > 0) {
          const memberTasks = memberTaskResult.tasks
          
          // Calculate workload for this member (same logic, more efficient)
          const activeTasks = memberTasks.filter(task => task.status !== 'Completed')
          const highPriorityTasks = memberTasks.filter(task => parseInt(task.priority) >= 8)
          
          let workloadLevel = 'low'
          if (activeTasks.length >= 8 || highPriorityTasks.length >= 4) {
            workloadLevel = 'overload'
          } else if (activeTasks.length >= 5 || highPriorityTasks.length >= 2) {
            workloadLevel = 'high'
          } else if (activeTasks.length >= 3) {
            workloadLevel = 'moderate'
          }
          
          workloadCounts[workloadLevel]++
        } else {
          // Member has no tasks, so they have low workload
          workloadCounts['low']++
        }
      })
      
      finalStats[team.id] = {
        taskCount,
        workloadCounts
      }
    })
    
    // Step 5: Store results
    teamStats.value = finalStats
    console.log('Optimized team statistics completed:', teamStats.value)
    
  } catch (error) {
    console.error('Error fetching team statistics:', error)
  }
}

// Function to fetch all department members (for team stats calculation)
const fetchAllDepartmentMembers = async () => {
  if (!deptId.value) {
    console.log('No department ID available')
    return
  }
  
  try {
    const response = await fetch(`http://localhost:5003/users/department/${deptId.value}`)
    if (response.ok) {
      const data = await response.json()
      allDepartmentMembers.value = data.data || []
      
      // Fetch user details for workload calculation
      const userPromises = allDepartmentMembers.value.map(member => fetchUserDetails(member.userid))
      await Promise.all(userPromises)
      
      console.log('Fetched all department members for stats:', allDepartmentMembers.value.length)
    } else {
      console.error('Failed to fetch all department members:', response.status)
    }
  } catch (error) {
    console.error('Error fetching all department members:', error)
  }
}

// Function to select a team and load its data
const selectTeam = async (teamId, teamName) => {
  selectedTeamId.value = teamId
  selectedTeamName.value = teamName
  await onTeamChange()
}

// Function to go back to teams
const goBackToTeams = () => {
  selectedTeamId.value = ''
  selectedTeamName.value = ''
  departmentMembers.value = []
  tasks.value = []
  // Reset filters
  selectedMember.value = ''
  selectedTaskMember.value = ''
  workloadFilter.value = 'all'
  activeFilter.value = 'all'
  viewMode.value = 'members'
}

// Function to handle team change
const onTeamChange = async () => {
  if (!selectedTeamId.value) {
    departmentMembers.value = []
    tasks.value = []
    return
  }
  
  // Reset filters
  selectedMember.value = ''
  selectedTaskMember.value = ''
  workloadFilter.value = 'all'
  activeFilter.value = 'all'
  viewMode.value = 'members'
  
  // Fetch team members and tasks
  await Promise.all([
    fetchTeamMembers(selectedTeamId.value),
    fetchTeamTasks(selectedTeamId.value)
  ])
}

// Function to fetch team members
const fetchTeamMembers = async (teamId) => {
  if (!teamId) return
  
  try {
    const response = await fetch(`http://localhost:5003/users/team/${teamId}`)
    if (response.ok) {
      const data = await response.json()
      departmentMembers.value = data.data || []
      console.log('Fetched team members:', departmentMembers.value.length, departmentMembers.value)
    } else {
      console.error('Failed to fetch team members:', response.status)
      departmentMembers.value = []
    }
  } catch (error) {
    console.error('Error fetching team members:', error)
    departmentMembers.value = []
  }
}

// Function to fetch team tasks
const fetchTeamTasks = async (teamId) => {
  if (!teamId) return
  
  isLoadingTasks.value = true
  
  try {
    const response = await fetch(`http://localhost:5002/tasks/team/${teamId}`)
    if (response.ok) {
      const data = await response.json()
      tasks.value = data.data || []
      console.log('Fetched team tasks:', tasks.value.length, tasks.value)
      
      await fetchTaskUsers()
    } else {
      console.error('Failed to fetch team tasks:', response.status)
      tasks.value = []
    }
  } catch (error) {
    console.error('Error fetching team tasks:', error)
    tasks.value = []
  } finally {
    isLoadingTasks.value = false
  }
}

// Team helper functions
const getTeamMemberCount = (teamId) => {
  if (!teamId || !allDepartmentMembers.value.length) return 0
  return allDepartmentMembers.value.filter(member => member.team_id === teamId).length
}

const getTeamTaskCount = (teamId) => {
  if (!teamId || !teamStats.value[teamId]) return 0
  return teamStats.value[teamId].taskCount || 0
}

const getTeamWorkloadCount = (teamId, workloadLevel) => {
  if (!teamId || !teamStats.value[teamId]) return 0
  return teamStats.value[teamId].workloadCounts?.[workloadLevel] || 0
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
  let membersExcludingCurrentUser = departmentMembers.value.filter(member => member.userid !== userId.value)
  
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

const viewMemberSchedule = (memberId) => {
  viewMode.value = 'schedule'
  selectedMemberFilter.value = memberId.toString()
  appliedMemberFilter.value = memberId.toString()
}

const toggleShowCompleted = () => {
  showCompleted.value = !showCompleted.value
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

const formatDate = (date, formatStr = 'd MMM yyyy') => {
  if (!date) return ''
  const d = new Date(date)

  // simple formatter
  const options = {}
  if (formatStr === 'EEE') {
    options.weekday = 'short'
  } else if (formatStr === 'd') {
    options.day = 'numeric'
  } else if (formatStr === 'd MMM yyyy') {
    options.day = 'numeric'
    options.month = 'short'
    options.year = 'numeric'
  }

  return d.toLocaleDateString('en-US', options)
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Singapore'
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
    'all': 'No department tasks found.',
    'Ongoing': 'No ongoing department tasks.',
    'Under Review': 'No department tasks under review.',
    'Completed': 'No completed department tasks.',
    'Unassigned': 'No unassigned department tasks.'
  }
  return messages[activeFilter.value] || 'No department tasks found.'
}

const totalTasks = computed(() => tasks.value.length)
const ongoingTasks = computed(() => tasks.value.filter(task => task.status === 'Ongoing').length)
const underReviewTasks = computed(() => tasks.value.filter(task => task.status === 'Under Review').length)
const completedTasks = computed(() => tasks.value.filter(task => task.status === 'Completed').length)
const unassignedTasks = computed(() => tasks.value.filter(task => task.status === 'Unassigned').length)
const overloadedMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'overload').length
})

const lightLoadMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'low').length
})

const moderateLoadMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'moderate').length
})

const heavyLoadMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => member.userid !== userId.value && getWorkloadClass(member) === 'high').length
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

const calendarViews = [
  { value: 'day', label: 'Day', icon: 'bi bi-calendar-day' },
  { value: 'week', label: 'Week', icon: 'bi bi-calendar-week' },
  { value: 'month', label: 'Month', icon: 'bi bi-calendar-month' }
]

const formatHour = (hour) => `${hour.toString().padStart(2, '0')}:00`

const isToday = (date) => {
  const today = new Date()
  const d = new Date(date)
  return d.toDateString() === today.toDateString()
}

const getWeekStart = (date) => {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day
  return new Date(d.setDate(diff))
}

// Calendar navigation
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

// Calendar computed properties
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
// Schedule view computed properties
const displayedTasks = computed(() => {
  let filtered = [...tasks.value]
  
  if (!showCompleted.value) {
    filtered = filtered.filter(task => task.status?.toLowerCase() !== 'completed')
  }
  
  if (appliedMemberFilter.value) {
    const memberId = parseInt(appliedMemberFilter.value)
    filtered = filtered.filter(task => 
      task.owner_id === memberId || 
      (task.collaborators && task.collaborators.includes(memberId))
    )
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
  appliedProjectFilter.value !== '' || appliedStatusFilters.value.length > 0 || appliedMemberFilter.value !== ''
)

// Add a computed property for calendar-compatible tasks
const calendarTasks = computed(() => {
  return displayedTasks.value.map(task => ({
    id: task.id,
    title: task.task_name || 'No Title',
    start: task.due_date ? new Date(task.due_date) : null,
    end: task.due_date ? new Date(task.due_date) : null,
    status: task.status,
    owner_id: task.owner_id,
    collaborators: task.collaborators || [],
  }))
})

// Example: get tasks for a day
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

const selectedTask = ref(null)

// Task modal and actions
const selectTask = (task) => {
  selectedTask.value = task
}

const selectDate = (date) => {
  currentDate.value = new Date(date)
  currentView.value = 'day'
}

// Reschedule functionality
const openRescheduleModal = (task) => {
  selectedTaskForReschedule.value = task
  newDueDate.value = task.due_date ? new Date(task.due_date).toISOString().slice(0, 16) : todayString.value
  showRescheduleModal.value = true
}

const closeRescheduleModal = () => {
  showRescheduleModal.value = false
  selectedTaskForReschedule.value = null
  newDueDate.value = ''
}

const confirmReschedule = async () => {
  if (!newDueDate.value) {
    showError('Please select a new due date.')
    return
  }
  
  if (newDueDate.value < todayString.value) {
    showError('Cannot reschedule to a date before today.')
    return
  }

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
      await fetchTeamTasks() // Refresh tasks
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

const showSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = ''), 3000)
}

const showError = (msg) => {
  errorMessage.value = msg
  setTimeout(() => (errorMessage.value = ''), 5000)
}

// Mark as Completed
const markAsCompleted = async (task) => {
  if (!task?.id) return;

  const previousStatus = task.status;
  task.status = 'Completed'; // optimistic update
  showSuccess(`Task "${task.task_name}" marked as completed!`);

  try {
    const payload = {
      task_id: task.id,
      status: 'Completed'
    };

    const response = await fetch(`http://localhost:5002/tasks/update`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (data.Code !== 200) {
      task.status = previousStatus; // revert if API fails
      showError(`Failed to update task: ${data.Message || 'Unknown error'}`);
    } else {
      // ✅ Important: refresh the task list to reflect the next instance / updated status
      await fetchTeamTasks();
    }
  } catch (err) {
    task.status = previousStatus; // revert
    console.error(err);
    showError('Error marking task as completed.');
  }
};

</script>

<style scoped>
/* Team Grid Styles */
.teams-grid-container {
  padding: 2rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 2rem;
  text-align: center;
}

.teams-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.team-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transform: translateY(20px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.team-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.team-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1rem;
}

.team-icon {
  font-size: 2.5rem;
  color: #3b82f6;
  min-width: 3rem;
}

.team-info {
  flex: 1;
}

.team-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 0.25rem 0;
  line-height: 1.3;
}

.team-dept {
  font-size: 0.875rem;
  color: #6b7280;
  margin: 0;
}

.team-meta {
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

.team-workload-preview {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 8px;
}

.workload-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.workload-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.workload-item.low {
  background: #d1fae5;
  color: #065f46;
}

.workload-item.moderate {
  background: #fef3c7;
  color: #92400e;
}

.workload-item.high {
  background: #fed7aa;
  color: #c2410c;
}

.workload-item.overload {
  background: #fecaca;
  color: #dc2626;
}

.workload-item .count {
  font-weight: 600;
}

.team-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
  font-size: 0.875rem;
  color: #6b7280;
  transition: color 0.2s ease;
}

.team-card:hover .team-action {
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
  min-height: 400px;
  color: #6b7280;
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
  font-size: 3rem;
  color: #d1d5db;
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

.task-item.ongoing { background: #fef3c7;
  color: #d97706; }

.task-item.under-review { background: #e0e7ff;
  color: #6366f1;}

.task-item.completed { 
  background: #d1fae5;
  color: #059669;
  opacity: 0.6;}

.task-item.completed .task-title{
  text-decoration: line-through;
}

.task-item.unassigned { background: #f3f4f6;
  color: #374151; }
.task-card.overdue-task,
.task-item.overdue-task,
.task-box.overdue-task {
  background-color:#fee2e2; ; 
  color: #dc2626; 
}

.task-status-badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  text-transform: capitalize;
  white-space: nowrap;
}

.task-status-badge.unassigned {
  background: #6b7280;
  color: white;
}

.task-status-badge.ongoing {
  background: #d97706;
  color: white;
}

.task-status-badge.under-review {
  background: #6366f1;
  color: white;
}

.task-status-badge.completed {
  background: #059669;
  color: white;
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
  .teams-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .teams-grid-container {
    padding: 1rem;
  }
  
  .team-card {
    padding: 1rem;
  }
}
</style>