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
              @click="showMemberView"
            >
              <i class="bi bi-people-fill"></i>
              Member View
            </button>
            <button 
              class="view-toggle-btn" 
              :class="{ active: viewMode === 'tasks' }"
              @click="showTaskView"
            >
              <i class="bi bi-list-task"></i>
              Task View
            </button>
            <button 
              class="view-toggle-btn" 
              :class="{ active: viewMode === 'schedule' }"
              @click="showScheduleView"
            >
              <i class="bi bi-calendar3"></i>
              Schedule View
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
              <div class="stat-number">{{ teamMembers.length }}</div>
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
        <div v-else-if="viewMode === 'tasks'" class="task-stats">
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
                <option v-for="member in teamMembers" :key="member.userid" :value="member.userid">
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
          <div class="loading-spinner"></div>
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
                <button class="view-schedule-btn" @click="viewMemberSchedule(member.userid)">
                  <i class="bi bi-calendar3"></i>
                  View Schedule
                </button>
              </div>
          </div>
        </div>
      </div>

      <!-- Task View -->
      <div v-else-if="viewMode === 'tasks'" class="tasks-view">

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
                <option v-for="member in teamMembers" :key="member.userid" :value="member.userid">
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

      <!-- Schedule View -->
      <div v-else-if="viewMode === 'schedule'" class="schedule-view">
        <!-- Calendar Controls -->
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
                    :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
                    @click="selectTask(task)"
                  >
                    <span v-if="isTaskOverdue(task)" class="overdue-badge">Overdue</span>
                    <div class="task-title">{{ task.task_name }}</div>
                    <div class="task-status-badge" :class="getTaskStatusClass(task.status)">
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
                      :class="[getTaskStatusClass(task.status), { 'overdue-task': isTaskOverdue(task) }]"
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
          <!-- Member Filter -->
          <div class="filter-section">
            <label class="filter-label">
              <i class="bi bi-person"></i>
              Member
            </label>
            <select v-model="selectedMemberFilter" class="filter-select">
              <option value="">All Members</option>
              <option v-for="member in teamMembers" :key="member.userid" :value="member.userid">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SideNavbar from '../../components/SideNavbar.vue'
import { getCurrentUserData } from '../../services/session.js'
import "../taskview/taskview.css"
import "../schedule/scheduleview.css"

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
const selectedScheduleMember = ref('')
const workloadFilter = ref('all')

// Schedule-related reactive variables
const currentDate = ref(new Date())
const currentView = ref('week')
const selectedTask = ref(null)
const showRescheduleModal = ref(false)
const selectedTaskForReschedule = ref(null)
const newDueDate = ref('')
const todayString = ref(new Date().toISOString().slice(0, 16))
const successMessage = ref('')
const errorMessage = ref('')
const showCompleted = ref(true)

// Filter-related reactive variables
const showFilterPopup = ref(false)
const projects = ref([])
const selectedProjectFilter = ref('')
const selectedStatusFilters = ref([])
const selectedMemberFilter = ref('')
const appliedProjectFilter = ref('')
const appliedStatusFilters = ref([])
const appliedMemberFilter = ref('')

const calendarViews = [
  { value: 'day', label: 'Day', icon: 'bi bi-calendar-day' },
  { value: 'week', label: 'Week', icon: 'bi bi-calendar-week' },
  { value: 'month', label: 'Month', icon: 'bi bi-calendar-month' }
]

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
  if (!userid) return 'Unknown User';

  // Check cached users first
  if (users.value[userid]?.name) return users.value[userid].name;

  // Fallback: search teamMembers array
  const member = teamMembers.value.find(u => u.id === userid);
  if (member?.name) {
    // Cache it for future use
    users.value[userid] = member;
    return member.name;
  }

  return `User ${userid}`;
};

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
  // Include all members including the current user
  let filteredMembersList = teamMembers.value
  
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

const showMemberView = () => {
  viewMode.value = 'members'
  selectedTaskMember.value = ''
  selectedMemberFilter.value = ''
  appliedMemberFilter.value = ''
}

const showTaskView = () => {
  viewMode.value = 'tasks'
  selectedMemberFilter.value = ''
  appliedMemberFilter.value = ''
}

const showScheduleView = () => {
  viewMode.value = 'schedule'
  selectedTaskMember.value = ''
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
  return teamMembers.value.filter(member => getWorkloadClass(member) === 'overload').length
})

const lightLoadMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => getWorkloadClass(member) === 'low').length
})

const moderateLoadMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => getWorkloadClass(member) === 'moderate').length
})

const heavyLoadMembers = computed(() => {
  if (!teamMembers.value || teamMembers.value.length === 0) return 0
  return teamMembers.value.filter(member => getWorkloadClass(member) === 'high').length
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

const activeFilterCount = computed(() => {
  let count = 0
  if (appliedProjectFilter.value) count++
  if (appliedStatusFilters.value.length > 0) count += appliedStatusFilters.value.length
  if (appliedMemberFilter.value) count++
  return count
})

// Date formatting and utilities
const formatDate = (date, format = 'default') => {
  if (!date) return format === 'default' ? 'No date' : ''
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
    case 'default':
    case 'yyyy-MM-dd':
    default:
      return d.toLocaleDateString('en-SG', { 
        timeZone: 'Asia/Singapore',
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      })
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

// Task helpers for calendar
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

const toggleShowCompleted = () => {
  showCompleted.value = !showCompleted.value
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

// Filter functionality
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

const fetchProjects = async () => {
  try {
    const userData = getCurrentUserData()
    const userId = userData?.userid
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

const getCollaboratorNames = (collaboratorIds) => {
  if (!Array.isArray(collaboratorIds)) return "None"
  return collaboratorIds
    .map((id) => {
      const member = teamMembers.value.find((m) => m.userid === id)
      return member ? member.name : "Unknown"
    })
    .join(", ")
}
</script>

<style scoped>
/* Additional styles for the combined view */
.member-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.view-tasks-btn,
.view-schedule-btn {
  flex: 1;
  min-width: 120px;
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
}

.view-tasks-btn {
  background: #f3f4f6;
  color: #374151;
}

.view-tasks-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.view-schedule-btn {
  background: #f3f4f6;
  color: #374151;
}

.view-schedule-btn:hover {
  background: #e5e7eb;
  color: #1f2937;
}

.header-right-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.view-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  color: #6b7280;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
  justify-content: center;
}

.view-toggle-btn:hover {
  background: #f9fafb;
  border-color: #d1d5db;
}

.view-toggle-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

/* Schedule view specific styles */
.schedule-view .filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.schedule-view .filter-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  white-space: nowrap;
}

.schedule-view .filter-dropdown {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background: white;
  min-width: 150px;
}

.task-owner {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.task-box-owner {
  font-size: 0.65rem;
  color: #6b7280;
  margin-top: 0.125rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
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

/* Calendar controls responsive improvements */
.calendar-controls {
  flex-wrap: wrap;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* ==================== RESPONSIVE DESIGN ==================== */

/* Large Desktop (1440px+) */
@media (min-width: 1440px) {
  .members-container {
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  }
}

/* Desktop (1024px - 1439px) */
@media (min-width: 1024px) and (max-width: 1439px) {
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
  
  .header-right-actions {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .view-toggle-btn {
    flex: 1;
    min-width: 100px;
    font-size: 0.85rem;
    padding: 0.6rem 0.75rem;
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
  
  .header-right-actions {
    width: 100%;
    justify-content: center;
    flex-direction: column;
  }
  
  .view-toggle-btn {
    width: 100%;
    font-size: 0.8rem;
    padding: 0.5rem;
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
  
  .view-tasks-btn, .view-schedule-btn {
    width: 100%;
    font-size: 0.8rem;
    padding: 0.6rem;
    min-width: auto;
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
    align-items: stretch;
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
    justify-content: center;
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
}
</style>