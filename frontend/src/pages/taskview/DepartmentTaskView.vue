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
            <!-- Directors Card (if directors exist without team_id) -->
            <div 
              v-if="hasDirectors"
              class="team-card directors-card"
              :style="{ animationDelay: '0s' }"
              @click="selectTeam('directors', 'Directors')"
            >
              <div class="team-header">
                <div class="team-icon">
                  <i class="bi bi-star-fill"></i>
                </div>
                <div class="team-info">
                  <h3 class="team-name">Directors</h3>
                  <p class="team-dept">Department Leadership</p>
                </div>
              </div>
              
              <div class="team-meta">
                <div class="meta-item">
                  <i class="bi bi-people"></i>
                  <span>{{ getTeamMemberCount('directors') }} members</span>
                </div>
                <div class="meta-item">
                  <i class="bi bi-list-task"></i>
                  <span>{{ getTeamTaskCount('directors') }} tasks</span>
                </div>
              </div>

              <div class="team-workload-preview">
                <div class="workload-summary">
                  <div class="workload-item overload" v-if="getTeamWorkloadCount('directors', 'overload') > 0">
                    <span class="count">{{ getTeamWorkloadCount('directors', 'overload') }}</span>
                    <span class="label">Overloaded</span>
                  </div>
                  <div class="workload-item high" v-if="getTeamWorkloadCount('directors', 'high') > 0">
                    <span class="count">{{ getTeamWorkloadCount('directors', 'high') }}</span>
                    <span class="label">Heavy</span>
                  </div>
                  <div class="workload-item moderate" v-if="getTeamWorkloadCount('directors', 'moderate') > 0">
                    <span class="count">{{ getTeamWorkloadCount('directors', 'moderate') }}</span>
                    <span class="label">Moderate</span>
                  </div>
                  <div class="workload-item low" v-if="getTeamWorkloadCount('directors', 'low') > 0">
                    <span class="count">{{ getTeamWorkloadCount('directors', 'low') }}</span>
                    <span class="label">Light</span>
                  </div>
                </div>
              </div>
              
              <div class="team-action">
                <span class="action-text">Click to view directors workload</span>
                <i class="bi bi-arrow-right"></i>
              </div>
            </div>

            <!-- Regular Team Cards -->
            <div 
              v-for="(team, index) in departmentTeams" 
              :key="team.id"
              class="team-card"
              :style="{ animationDelay: `${(index + (hasDirectors ? 1 : 0)) * 0.1}s` }"
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
              <div class="stat-number">{{ departmentMembers.length }}</div>
              <div class="stat-title">All Members</div>
            </div>
          </div>
        </div>          <div class="stat-card workload-light" @click="workloadFilter = 'low'" :class="{ active: workloadFilter === 'low' }">
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
                <option v-for="member in departmentMembers" :key="member.userid" :value="member.userid">
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
                <option v-for="member in departmentMembers" :key="member.userid" :value="member.userid">
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
                      class="task-event"
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
                      <div class="task-box-name" :class="getStatusClass(task.status)">{{ task.task_name }}</div>
                      <div class="task-box-status" :class="getStatusClass(task.status)">{{ task.status }}</div>
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

    <!-- Task Details Modal -->
    <div v-if="selectedTask" class="task-modal-overlay" @click="closeTaskModal">
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
              <span class="label">Priority:</span>
              <span class="value">{{ selectedTask.priority || 'N/A' }}</span>
            </div>
            <div class="detail-row" v-if="selectedTask.owner_id">
              <span class="label">Owner:</span>
              <span class="value">{{ getUserName(selectedTask.owner_id) }}</span>
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
          </div>
          <div class="modal-actions">
            <button @click="navigateToTask(selectedTask.id)" class="view-task-btn">
              <i class="bi bi-arrow-right"></i>
              View Task Details
            </button>
          </div>
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
          <!-- Member Filter -->
          <div class="filter-section">
            <label class="filter-label">
              <i class="bi bi-person"></i>
              Member
            </label>
            <select v-model="selectedMemberFilter" class="filter-select">
              <option value="">All Members</option>
              <option v-for="member in departmentMembers" :key="member.userid" :value="member.userid">
                {{ member.name }}
              </option>
            </select>
          </div>

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
const selectedTask = ref(null)
const showFilterPopup = ref(false) 
const projects = ref([])
const selectedProjectFilter = ref('')
const selectedStatusFilters = ref([])

const toggleFilterPopup = () => {
  showFilterPopup.value = !showFilterPopup.value
  if (showFilterPopup.value && projects.value.length === 0) fetchProjects()
}

const closeFilterPopup = () => (showFilterPopup.value = false)

const clearFilters = () => {
  selectedProjectFilter.value = ''
  selectedStatusFilters.value = []
  selectedMemberFilter.value = ''
  appliedProjectFilter.value = ''
  appliedStatusFilters.value = []
  appliedMemberFilter.value = ''
}

const applyFilters = () => {
  appliedProjectFilter.value = selectedProjectFilter.value
  appliedStatusFilters.value = [...selectedStatusFilters.value]
  appliedMemberFilter.value = selectedMemberFilter.value
  closeFilterPopup()
}

const activeFilterCount = computed(() => {
  let count = 0
  if (appliedProjectFilter.value) count++
  if (appliedStatusFilters.value.length > 0) count += appliedStatusFilters.value.length
  if (appliedMemberFilter.value) count++
  return count
})


const fetchProjects = async () => {
  try {
    if (!departmentMembers.value?.length) return

    // Fetch projects for each team member
    const projectPromises = departmentMembers.value.map(async member => {
      const res = await fetch(`http://127.0.0.1:5001/projects/user/${member.userid}`)
      if (!res.ok) return [] // skip if 404
      const data = await res.json()
      return Array.isArray(data.data)
        ? data.data.map(p => ({ id: p.id, name: p.proj_name }))
        : []
    })

    const projectsPerMember = await Promise.all(projectPromises)
    // Flatten and remove duplicates
    const allProjects = projectsPerMember.flat()
    const uniqueProjects = Array.from(
      new Map(allProjects.map(p => [p.id, p])).values()
    )

    projects.value = uniqueProjects
  } catch (err) {
    console.error('Error fetching projects:', err)
    projects.value = []
  }
}


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
  if (!departmentTeams.value.length && !allDepartmentMembers.value.some(m => !m.team_id)) return
  
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
    
    // Add directors (members without team_id) to a virtual "directors" team
    const directors = allDepartmentMembers.value.filter(member => !member.team_id && member.dept_id === deptId.value)
    if (directors.length > 0) {
      console.log(`Found ${directors.length} directors without team_id`)
      teamMemberMapping['directors'] = directors
      directors.forEach(director => {
        allMemberTaskPromises.push(
          fetch(`http://localhost:5002/tasks/user-task/${director.userid}`)
            .then(response => response.ok ? response.json() : null)
            .then(data => ({
              teamId: 'directors',
              memberId: director.userid,
              tasks: data?.data || []
            }))
            .catch(error => {
              console.error(`Error fetching tasks for director ${director.userid}:`, error)
              return { teamId: 'directors', memberId: director.userid, tasks: [] }
            })
        )
      })
    }
    
    console.log(`Optimized: ${teamsWithMembers} teams with members, ${allMemberTaskPromises.length} total member requests`)
    
    // Step 3: Execute all member task requests in parallel
    const memberTasksResults = await Promise.all(allMemberTaskPromises)
    console.log(`Member tasks fetched in parallel for ${allMemberTaskPromises.length} members`)
    
    // Step 4: Process all results efficiently
    const finalStats = {}
    
    // Helper function to calculate workload stats for a team/group
    const calculateWorkloadStats = (teamId, teamMembers) => {
      let taskCount = 0
      const workloadCounts = { low: 0, moderate: 0, high: 0, overload: 0 }
      
      teamMembers.forEach(member => {
        const memberTaskResult = memberTasksResults.find(
          result => result.teamId === teamId && result.memberId === member.userid
        )
        
        if (memberTaskResult && memberTaskResult.tasks.length > 0) {
          const memberTasks = memberTaskResult.tasks
          taskCount += memberTasks.length
          
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
      
      return { taskCount, workloadCounts }
    }
    
    // Process regular teams
    departmentTeams.value.forEach(team => {
      const teamMembers = teamMemberMapping[team.id] || []
      
      // For teams, also try to get team task count from team endpoint
      const teamTaskResult = teamTasksResults.find(result => result.teamId === team.id)
      const teamTaskCount = teamTaskResult ? teamTaskResult.tasks.length : 0
      
      const stats = calculateWorkloadStats(team.id, teamMembers)
      
      // Use the maximum of team tasks or sum of member tasks
      finalStats[team.id] = {
        taskCount: Math.max(teamTaskCount, stats.taskCount),
        workloadCounts: stats.workloadCounts
      }
    })
    
    // Process directors
    if (teamMemberMapping['directors'] && teamMemberMapping['directors'].length > 0) {
      const stats = calculateWorkloadStats('directors', teamMemberMapping['directors'])
      finalStats['directors'] = stats
    }
    
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
    // Special handling for directors
    if (teamId === 'directors') {
      // Get directors from allDepartmentMembers (members with dept_id but no team_id)
      departmentMembers.value = allDepartmentMembers.value.filter(
        member => !member.team_id && member.dept_id === deptId.value
      )
      console.log('Fetched directors:', departmentMembers.value.length, departmentMembers.value)
      return
    }
    
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
    // Special handling for directors
    if (teamId === 'directors') {
      // Get all tasks for directors (members without team_id)
      const directors = allDepartmentMembers.value.filter(
        member => !member.team_id && member.dept_id === deptId.value
      )
      
      // Fetch tasks for all directors in parallel
      const taskPromises = directors.map(async (director) => {
        try {
          const response = await fetch(`http://localhost:5002/tasks/user-task/${director.userid}`)
          if (response.ok) {
            const data = await response.json()
            return data.data || []
          }
          return []
        } catch (error) {
          console.error(`Error fetching tasks for director ${director.userid}:`, error)
          return []
        }
      })
      
      const allDirectorTasks = await Promise.all(taskPromises)
      tasks.value = allDirectorTasks.flat()
      console.log('Fetched director tasks:', tasks.value.length, tasks.value)
      
      await fetchTaskUsers()
      isLoadingTasks.value = false
      return
    }
    
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
  
  // Special handling for directors
  if (teamId === 'directors') {
    return allDepartmentMembers.value.filter(
      member => !member.team_id && member.dept_id === deptId.value
    ).length
  }
  
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

// Computed property to check if directors exist in department
const hasDirectors = computed(() => {
  if (!deptId.value || !allDepartmentMembers.value.length) return false
  return allDepartmentMembers.value.some(
    member => !member.team_id && member.dept_id === deptId.value
  )
})

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
  // Include all members including the current user
  let filteredMembersList = departmentMembers.value
  
  // Apply individual member filter
  if (selectedMember.value) {
    filteredMembersList = filteredMembersList.filter(member => member.userid === parseInt(selectedMember.value))
  }
  
  // Apply workload filter
  if (workloadFilter.value !== 'all') {
    filteredMembersList = filteredMembersList.filter(member => getWorkloadClass(member) === workloadFilter.value)
  }
  
  return filteredMembersList
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

  const options = {}

  switch (formatStr) {
    case 'EEE':
      options.weekday = 'short'
      break
    case 'EEEE, MMMM d, yyyy':
      options.weekday = 'long'
      options.month = 'long'
      options.day = 'numeric'
      options.year = 'numeric'
      break
    case 'd':
      options.day = 'numeric'
      break
    case 'd MMM yyyy':
      options.day = 'numeric'
      options.month = 'short'
      options.year = 'numeric'
      break
    default:
      options.day = 'numeric'
      options.month = 'short'
      options.year = 'numeric'
      break
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
  return departmentMembers.value.filter(member => getWorkloadClass(member) === 'overload').length
})

const lightLoadMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => getWorkloadClass(member) === 'low').length
})

const moderateLoadMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => getWorkloadClass(member) === 'moderate').length
})

const heavyLoadMembers = computed(() => {
  if (!departmentMembers.value || departmentMembers.value.length === 0) return 0
  return departmentMembers.value.filter(member => getWorkloadClass(member) === 'high').length
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
  const current = new Date(currentDate.value)

  if (currentView.value === 'day') {
    // Day view: Friday, October 24, 2025
    return current.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  if (currentView.value === 'week' && weekDays.value.length > 0) {
    const start = new Date(weekDays.value[0].date)
    const end = new Date(weekDays.value[weekDays.value.length - 1].date)

    const startDay = start.getDate()
    const endDay = end.getDate()
    const startMonth = start.toLocaleString('default', { month: 'short' })
    const endMonth = end.toLocaleString('default', { month: 'short' })
    const startYear = start.getFullYear()
    const endYear = end.getFullYear()

    // Same year
    if (startYear === endYear) {
      return `${startDay} ${startMonth} - ${endDay} ${endMonth} ${startYear}`
    } else {
      // Different years
      return `${startDay} ${startMonth} ${startYear} - ${endDay} ${endMonth} ${endYear}`
    }
  }

  // Month view fallback
  return current.toLocaleString('default', { month: 'long', year: 'numeric' })
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
const allScheduleTasks = computed(() => {
  const all = [];

  tasks.value.forEach((task) => {
    // Include parent task
    all.push({
      ...task,
      isSubtask: false,
      parentTaskName: null
    });

    // Include each subtask if it exists
    if (Array.isArray(task.subtasks)) {
      task.subtasks.forEach((sub) => {
        all.push({
          ...sub,
          isSubtask: true,
          parentTaskName: task.task_name || null
        });
      });
    }
  });

  return all;
});

const displayedTasks = computed(() => {
  let filtered = [...allScheduleTasks.value];

  if (!showCompleted.value) {
    filtered = filtered.filter(task => task.status?.toLowerCase() !== 'completed');
  }

  if (appliedMemberFilter.value) {
    const memberId = parseInt(appliedMemberFilter.value);
    filtered = filtered.filter(task => 
      task.owner_id === memberId ||
      (task.collaborators && task.collaborators.includes(memberId))
    );
  }

  if (appliedProjectFilter.value) {
    filtered = filtered.filter(task =>
      String(task.project_id) === String(appliedProjectFilter.value)
    );
  }

  if (appliedStatusFilters.value.length > 0) {
    filtered = filtered.filter(task =>
      appliedStatusFilters.value.includes(task.status)
    );
  }

  return filtered;
});


const hasActiveFilters = computed(() =>
  appliedProjectFilter.value !== '' || appliedStatusFilters.value.length > 0 || appliedMemberFilter.value !== ''
)

const getCollaboratorNames = (collaborators) => {
  if (!collaborators?.length) return ''
  return collaborators
    .map(id => getUserName(id))
    .join(', ')
}

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

// Task modal and actions
const selectTask = (task) => {
  selectedTask.value = task
}

const closeTaskModal = () => {
  selectedTask.value = null
}

const selectDate = (date) => {
  currentDate.value = new Date(date)
  currentView.value = 'day'
}


const showSuccess = (msg) => {
  successMessage.value = msg
  setTimeout(() => (successMessage.value = ''), 3000)
}

const showError = (msg) => {
  errorMessage.value = msg
  setTimeout(() => (errorMessage.value = ''), 5000)
}

const getTaskStatusClass = (status) => {
  if (!status) return ''
  switch (status.toLowerCase()) {
    case 'unassigned':
      return 'status-unassigned'
    case 'ongoing':
      return 'status-ongoing'
    case 'under review':
      return 'status-under-review'
    case 'completed':
      return 'status-completed'
    default:
      return ''
  }
}

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

.task-item.ongoing, 
.task-box.ongoing 
{ background: #fef3c7;
  color: #d97706; }

.task-item.under-review, 
.task-box.under-review  
{ background: #e0e7ff;
  color: #6366f1;}

.task-item.completed, 
.task-box.completed
{ 
  background: #d1fae5;
  color: #059669;
  opacity: 0.6;}

.task-item.completed .task-title,
.task-box-name.completed
{
  text-decoration: line-through;
}

.task-item.unassigned, 
.task-box.unassigned 
{ background: #f3f4f6;
  color: #374151; }

.task-event.ongoing { background: #fef3c7;
  color: #d97706; }

.task-event.under-review { background: #e0e7ff;
  color: #6366f1;}

.task-event.completed { 
  background: #d1fae5;
  color: #059669;
  opacity: 0.6;}

.task-event.completed .task-title{
  text-decoration: line-through;
}

.task-event.unassigned { background: #f3f4f6;
  color: #374151; }

.task-event.overdue-task,
.task-item.overdue-task,
.task-box.overdue-task {
  background-color:#fee2e2; ; 
  color: #dc2626; 
}

.task-status-badge,
.task-box-status {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  text-transform: capitalize;
  white-space: nowrap;
}

.task-status-badge.unassigned,
.task-box-status.unassigned {
  background: #6b7280;
  color: white;
}

.task-status-badge.ongoing, 
.task-box-status.ongoing {
  background: #d97706;
  color: white;
}

.task-status-badge.under-review,
.task-box-status.under-review {
  background: #6366f1;
  color: white;
}

.task-status-badge.completed, 
.task-box-status.completed {
  background: #059669;
  color: white;
}

.view-task-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.view-task-btn:hover {
  background: #2563eb;
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

/* ==================== RESPONSIVE DESIGN ==================== */

/* Large Desktop (1440px+) */
@media (min-width: 1440px) {
  .teams-container {
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    max-width: 1400px;
  }
  
  .members-container {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}

/* Desktop (1024px - 1439px) */
@media (min-width: 1024px) and (max-width: 1439px) {
  .teams-container {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
  
  .members-container {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-container {
    gap: 1rem;
  }
}

/* Tablet Landscape (768px - 1023px) */
@media (min-width: 768px) and (max-width: 1023px) {
  .app-container {
    padding: 1rem;
  }
  
  .header-section {
    padding: 1.5rem;
  }
  
  .page-title {
    font-size: 1.75rem;
  }
  
  .page-subtitle {
    font-size: 0.9rem;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .header-right-actions {
    flex-wrap: wrap;
    justify-content: flex-start;
  }
  
  .view-toggle-btn {
    flex: 1;
    min-width: 120px;
  }
  
  .teams-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
  
  .teams-grid-container {
    padding: 1rem;
  }
  
  .team-card {
    padding: 1.25rem;
  }
  
  .stats-container {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .members-container {
    grid-template-columns: 1fr;
  }
  
  .tasks-container {
    padding: 1rem;
  }
  
  .sort-controls {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .sort-container {
    flex-wrap: wrap;
    gap: 0.75rem;
  }
  
  .filter-group {
    width: 100%;
    margin: 0;
  }
  
  .workload-legend {
    width: 100%;
    justify-content: space-around;
    margin: 0;
  }
}

/* Tablet Portrait & Large Mobile (480px - 767px) */
@media (min-width: 480px) and (max-width: 767px) {
  .app-container {
    padding: 0.75rem;
  }
  
  .header-section {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .header-content {
    text-align: center;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .page-subtitle {
    font-size: 0.85rem;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
    gap: 0.75rem;
  }
  
  .header-left-actions, .header-right-actions {
    width: 100%;
    justify-content: center;
  }
  
  .header-right-actions {
    flex-wrap: wrap;
  }
  
  .view-toggle-btn {
    flex: 1;
    min-width: 100px;
    font-size: 0.85rem;
    padding: 0.6rem 0.75rem;
  }
  
  .back-btn {
    width: 100%;
    justify-content: center;
  }
  
  .teams-container {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .teams-grid-container {
    padding: 0.75rem;
  }
  
  .section-title {
    font-size: 1.25rem;
  }
  
  .team-card {
    padding: 1rem;
  }
  
  .team-icon {
    font-size: 2rem;
    min-width: 2.5rem;
  }
  
  .team-name {
    font-size: 1.1rem;
  }
  
  .stats-section {
    padding: 1rem 0.75rem;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.5rem;
  }
  
  .stat-card {
    padding: 0.75rem;
  }
  
  .stat-number {
    font-size: 1.5rem;
  }
  
  .stat-title {
    font-size: 0.75rem;
  }
  
  .stat-icon {
    font-size: 1.25rem;
    width: 2rem;
    height: 2rem;
  }
  
  .main-content {
    padding: 0.75rem;
  }
  
  .members-container {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .member-card {
    padding: 1rem;
  }
  
  .tasks-container {
    padding: 0.75rem;
  }
  
  .task-card {
    padding: 1rem;
  }
  
  .sort-controls {
    padding: 0.75rem;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .sort-container {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .filter-group {
    width: 100%;
    margin: 0;
  }
  
  .filter-dropdown, .sort-dropdown {
    width: 100%;
  }
  
  .workload-legend {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
    margin: 0;
    gap: 0.5rem;
  }
  
  .legend-item {
    font-size: 0.75rem;
  }
}

/* Mobile (320px - 479px) */
@media (max-width: 479px) {
  .app-layout {
    margin: 0;
  }
  
  .app-container {
    padding: 0.5rem;
  }
  
  .header-section {
    padding: 0.75rem;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .header-content {
    text-align: center;
  }
  
  .page-title {
    font-size: 1.25rem;
    line-height: 1.3;
  }
  
  .page-subtitle {
    font-size: 0.8rem;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
    gap: 0.5rem;
  }
  
  .header-left-actions, .header-right-actions {
    width: 100%;
    justify-content: center;
  }
  
  .header-right-actions {
    flex-direction: column;
  }
  
  .view-toggle-btn {
    width: 100%;
    font-size: 0.8rem;
    padding: 0.5rem;
  }
  
  .back-btn {
    width: 100%;
    justify-content: center;
    font-size: 0.85rem;
    padding: 0.6rem;
  }
  
  .teams-container {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .teams-grid-container {
    padding: 0.5rem;
  }
  
  .section-title {
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  .team-card {
    padding: 0.875rem;
  }
  
  .team-header {
    gap: 0.75rem;
  }
  
  .team-icon {
    font-size: 1.75rem;
    min-width: 2rem;
  }
  
  .team-name {
    font-size: 1rem;
  }
  
  .team-dept {
    font-size: 0.75rem;
  }
  
  .meta-item {
    font-size: 0.75rem;
  }
  
  .team-workload-preview {
    padding: 0.75rem;
  }
  
  .workload-item {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }
  
  .stats-section {
    padding: 0.75rem 0.5rem;
  }
  
  .stats-section-member {
    padding: 0.75rem 0.5rem;
  }
  
  .stats-container {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.4rem;
  }
  
  .stat-card {
    padding: 0.6rem;
  }
  
  .stat-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 0.5rem;
  }
  
  .stat-icon {
    font-size: 1.25rem;
    width: 2rem;
    height: 2rem;
    margin-bottom: 0;
  }
  
  .stat-info {
    align-items: center;
  }
  
  .stat-number {
    font-size: 1.25rem;
  }
  
  .stat-title {
    font-size: 0.7rem;
  }
  
  .main-content {
    padding: 0.5rem;
  }
  
  .main-content-member {
    padding-top: 0.5rem;
  }
  
  .members-container {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .member-card {
    padding: 0.875rem;
  }
  
  .member-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
  
  .member-info {
    flex-direction: row;
    width: 100%;
  }
  
  .member-avatar {
    font-size: 2rem;
  }
  
  .member-name {
    font-size: 1rem;
  }
  
  .member-role, .member-email {
    font-size: 0.75rem;
  }
  
  .workload-indicator {
    width: 100%;
    text-align: center;
  }
  
  .member-tasks-summary {
    gap: 0.75rem;
  }
  
  .task-breakdown {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .breakdown-item {
    font-size: 0.75rem;
  }
  
  .priority-breakdown {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .priority-item, .upcoming-tasks {
    font-size: 0.75rem;
  }
  
  .member-actions {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .view-tasks-btn {
    width: 100%;
    font-size: 0.8rem;
    padding: 0.6rem;
  }
  
  .tasks-container {
    padding: 0.5rem;
  }
  
  .task-card {
    padding: 0.875rem;
  }
  
  .task-header {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .task-title {
    font-size: 0.95rem;
  }
  
  .task-badges {
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  
  .task-status, .task-priority {
    font-size: 0.7rem;
    padding: 0.2rem 0.4rem;
  }
  
  .task-people {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .task-owner, .task-collaborators {
    font-size: 0.75rem;
  }
  
  .sort-controls {
    padding: 0.5rem;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .sort-container {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .filter-group {
    width: 100%;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .filter-group label {
    font-size: 0.8rem;
  }
  
  .filter-dropdown, .sort-dropdown {
    width: 100%;
    font-size: 0.8rem;
    padding: 0.5rem;
  }
  
  .sort-order-btn {
    width: 100%;
    padding: 0.6rem;
  }
  
  .workload-legend {
    width: 100%;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.4rem;
    margin: 0;
  }
  
  .legend-item {
    font-size: 0.7rem;
  }
  
  .legend-color {
    width: 10px;
    height: 10px;
  }
  
  .empty-state {
    padding: 2rem 1rem;
    min-height: 300px;
  }
  
  .empty-icon i {
    font-size: 2.5rem;
  }
  
  .empty-title {
    font-size: 1rem;
  }
  
  .empty-subtitle {
    font-size: 0.8rem;
  }
  
  .loading-state {
    min-height: 300px;
  }
  
  .loading-text {
    font-size: 0.85rem;
  }
  
  /* Calendar/Schedule View Responsive */
  .calendar-controls {
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.75rem;
  }
  
  .view-toggle, .date-navigation, .action-buttons {
    width: 100%;
  }
  
  .view-toggle {
    overflow-x: auto;
  }
  
  .view-btn {
    font-size: 0.75rem;
    padding: 0.5rem;
    white-space: nowrap;
  }
  
  .current-period {
    font-size: 1rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .toggle-completed-btn, .filter-button, .today-button {
    width: 100%;
    font-size: 0.8rem;
    padding: 0.6rem;
  }
  
  .calendar-container {
    padding: 0.5rem;
  }
  
  .monthly-view .month-grid {
    gap: 2px;
  }
  
  .month-day {
    padding: 0.25rem;
    min-height: 60px;
  }
  
  .day-number {
    font-size: 0.8rem;
  }
  
  .task-box {
    font-size: 0.65rem;
    padding: 0.2rem;
  }
  
  /* Modal Responsive */
  .task-modal-overlay {
    padding: 1rem;
  }
  
  .task-modal {
    width: calc(100% - 2rem);
    max-height: 90vh;
    margin: 1rem;
  }
  
  .modal-header h3 {
    font-size: 1rem;
  }
  
  .filter-popup {
    width: calc(100% - 2rem);
    max-width: none;
  }
  
  .filter-section {
    margin-bottom: 1rem;
  }
  
  .filter-label {
    font-size: 0.85rem;
  }
  
  .filter-select {
    font-size: 0.85rem;
    padding: 0.6rem;
  }
  
  .checkbox-label {
    font-size: 0.8rem;
  }
  
  .filter-actions {
    flex-direction: column-reverse;
    gap: 0.5rem;
  }
  
  .clear-btn, .apply-btn {
    width: 100%;
    padding: 0.75rem;
  }
}
</style>