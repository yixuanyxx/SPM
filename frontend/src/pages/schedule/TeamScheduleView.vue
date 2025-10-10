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
            @click="viewMode = 'members'"
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
            <div class="sort-container">
              <div class="filter-group ms-4">
                <label for="memberFilter">Filter by member:</label>
                <select id="memberFilter" v-model="selectedMember" class="filter-dropdown">
                  <option value="">All Members</option>
                  <option v-for="member in filteredMembers" :key="member.userid" :value="member.userid">
                    {{ member.name }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- Member Cards -->
          <div v-if="filteredMembers.length > 0" class="members-container">
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
              <!-- Member Actions -->
              <div class="member-actions">
                <button class="view-schedule-btn" @click="viewMemberSchedule(member.userid)">
                    <i class="bi bi-calendar3"></i>
                    View Schedule
                </button>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <p>No members match the filter.</p>
          </div>
        </div>

        <!-- Schedule View -->
        <div v-else-if="viewMode === 'schedule'">
          <ScheduleView
            :tasks="scheduleViewMode === 'team'
                      ? tasks
                      : tasks.filter(t => t.owner_id === selectedMemberSchedule
                                        || t.collaborators?.includes(selectedMemberSchedule))"
            :team-members="teamMembers"
            :user-id="userId"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SideNavbar from '../../components/SideNavbar.vue'
import ScheduleView from '../schedule/ScheduleView.vue'
import { getCurrentUserData } from '../../services/session.js'

const viewMode = ref('members')
const selectedMember = ref('')
const workloadFilter = ref('all')
const tasks = ref([])
const teamMembers = ref([])
const users = ref({})
const userId = ref(null)
const teamId = ref(null)
const isLoadingTasks = ref(false)

// Fetch user data and team info
onMounted(async () => {
  const userData = getCurrentUserData()
  userId.value = parseInt(userData.userid)
  if (!userId.value) return

  // Fetch teamId from user details
  try {
    const res = await fetch(`http://localhost:5003/users/${userId.value}`)
    const data = await res.json()
    teamId.value = data.data?.team_id
    if (teamId.value) {
      await Promise.all([fetchTeamTasks(), fetchTeamMembers()])
    }
  } catch (error) {
    console.error(error)
  }
})

const fetchTeamMembers = async () => {
  if (!teamId.value) return
  try {
    const res = await fetch(`http://localhost:5003/users/team/${teamId.value}`)
    const data = await res.json()
    teamMembers.value = data.data || []
  } catch (err) {
    console.error(err)
    teamMembers.value = []
  }
}

const fetchTeamTasks = async () => {
  if (!teamId.value) return
  isLoadingTasks.value = true
  try {
    const res = await fetch(`http://localhost:5002/tasks/team/${teamId.value}`)
    const data = await res.json()
    tasks.value = data.data || []
  } catch (err) {
    console.error(err)
    tasks.value = []
  } finally {
    isLoadingTasks.value = false
  }
}

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

// Workload helpers
const getMemberTasks = (memberId) =>
  tasks.value.filter(task => task.owner_id === memberId || (task.collaborators?.includes(memberId)))

const getWorkloadClass = (member) => {
  const taskCount = getMemberTasks(member.userid).length
  if (taskCount >= 8) return 'overload'
  if (taskCount >= 5) return 'high'
  if (taskCount >= 3) return 'moderate'
  return 'low'
}

const getWorkloadLevel = (member) => {
  const levels = { low: 'Light', moderate: 'Moderate', high: 'Heavy', overload: 'Overloaded' }
  return levels[getWorkloadClass(member)] || 'Light'
}

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
</script>

<style scoped>
/* You can import teamTaskView.css and schedule view CSS as needed */
</style>
