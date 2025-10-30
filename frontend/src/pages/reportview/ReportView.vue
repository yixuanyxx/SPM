<template>
  <div class="app-layout ms-2">
    <SideNavbar />

    <div class="app-container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Reports</h1>
          <p class="page-subtitle">Generate and view your reports</p>
        </div>
      </div>

      <!-- Report Buttons -->
      <div class="report-actions">
        <!-- Personal Report Button (Visible to all roles) -->
        <button 
          v-if="userRole === 'staff' || userRole === 'manager' || userRole === 'director'" 
          class="report-btn" 
          @click="showReportForm('personal')"
        >
          View Personal Report
        </button>

        <!-- Team Report Button (Visible to managers) -->
        <button 
          v-if="userRole === 'manager'" 
          class="report-btn" 
          @click="showReportForm('team')"
        >
          View Team Report
        </button>

        <!-- Department Report Button (Visible to directors) -->
        <button 
          v-if="userRole === 'director'" 
          class="report-btn" 
          @click="showReportForm('department')"
        >
          View Department Report
        </button>

        <!-- Company Report Button (Visible only to users with team_id 9) -->
        <button 
          v-if="teamId === 9 || (userRole === 'director' && deptId === 5) || userRole === 'managing_director'" 
          class="report-btn company-report-btn" 
          @click="showReportForm('company')"
        >
          View Company Report
        </button>
      </div>

      <!-- Dynamic Report Form -->
      <div v-if="currentReportType" class="report-form">
        <h3>Generate {{ currentReportType }} Report</h3>
        <form @submit.prevent="generateReport">
          <label for="start-date">Start Date:</label>
          <input 
            type="date" 
            id="start-date" 
            v-model="reportForm.startDate" 
            :max="todayDate"
            required
          />

          <label for="end-date">End Date:</label>
          <input 
            type="date" 
            id="end-date" 
            v-model="reportForm.endDate" 
            :max="todayDate"
            :min="reportForm.startDate"
            required
          />

          <label for="export-format">Export Format:</label>
          <select id="export-format" v-model="reportForm.format">
            <option value="pdf">PDF</option>
            <option value="excel">Excel</option>
          </select>

          <button type="submit" class="report-btn">Generate {{ currentReportType }} Report</button>
        </form>
      </div>

      <!-- Report Status Message -->
      <div 
        v-if="reportStatus" 
        :class="['report-status', reportStatusClass]"
      >
        <p>{{ reportStatus }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SideNavbar from '../../components/SideNavbar.vue'
import '../reportview/reportview.css'
import { useRouter } from 'vue-router'
import { getCurrentUserData } from '../../services/session.js'

const router = useRouter()

// State - Initialize as refs
const userId = ref(null)
const userRole = ref('')
const teamId = ref(null)
const deptId = ref(null)
const currentReportType = ref(null)
const reportForm = ref({ startDate: '', endDate: '', format: 'pdf' })
const reportStatus = ref('')

// Get user data from session on mount
onMounted(async () => {
  const userData = getCurrentUserData()
  userRole.value = userData.role?.toLowerCase() || ''
  userId.value = parseInt(userData.userid) || null
  

  // Get user's team_id
  if (userId.value) {
    try {
      const response = await fetch(`http://localhost:5003/users/${userId.value}`)
      if (response.ok) {
        const data = await response.json()
        teamId.value = data.data?.team_id
        deptId.value = data.data?.dept_id
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

// Get today's date in YYYY-MM-DD format
const todayDate = computed(() => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
})

// Show the form for the selected report type
const showReportForm = (reportType) => {
  currentReportType.value = reportType
  reportForm.value = { startDate: '', endDate: '', format: 'pdf' }
  reportStatus.value = ''
}

// Generate the selected report
const generateReport = async () => {
  try {
    const { startDate, endDate, format } = reportForm.value
    
    if (!startDate || !endDate) {
      reportStatus.value = 'Please select both start and end dates'
      setTimeout(() => {
        reportStatus.value = ''
      }, 3000)
      return
    }

    // Validate that end date is not before start date
    if (new Date(endDate) < new Date(startDate)) {
      reportStatus.value = 'End date cannot be before start date'
      setTimeout(() => {
        reportStatus.value = ''
      }, 3000)
      return
    }

    // Validate that dates are not in the future
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (new Date(startDate) > today || new Date(endDate) > today) {
      reportStatus.value = 'Dates cannot be in the future'
      setTimeout(() => {
        reportStatus.value = ''
      }, 3000)
      return
    }
    
    const queryParams = new URLSearchParams({ format, start_date: startDate, end_date: endDate }).toString()
    let endpoint = ''

    if (currentReportType.value === 'personal') {
      endpoint = `http://localhost:5007/reports/personal/${userId.value}`
    } else if (currentReportType.value === 'team') {
      endpoint = `http://localhost:5007/reports/team/${userId.value}`
    } else if (currentReportType.value === 'department') {
      endpoint = `http://localhost:5007/reports/department/${userId.value}`
    } else if (currentReportType.value === 'company') {
      endpoint = `http://localhost:5007/reports/company/${userId.value}`
    }

    console.log(`Generating report: ${endpoint}?${queryParams}`)
    reportStatus.value = 'Generating report...'

    const response = await fetch(`${endpoint}?${queryParams}`)
    if (!response.ok) {
      throw new Error(`Failed to generate ${currentReportType.value} report`)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const fileExtension = format === 'excel' ? 'xlsx' : format
    link.download = `${currentReportType.value}_report_${startDate}_to_${endDate}.${fileExtension}`
    link.click()
    window.URL.revokeObjectURL(url)
    
    reportStatus.value = `Report downloaded successfully as ${format.toUpperCase()}!`
    
    setTimeout(() => {
      reportStatus.value = ''
    }, 5000)

  } catch (error) {
    console.error(`Error generating ${currentReportType.value} report:`, error)
    reportStatus.value = `Failed to generate ${currentReportType.value} report`
    setTimeout(() => {
      reportStatus.value = ''
    }, 5000)
  }
}

const reportStatusClass = computed(() => {
  if (reportStatus.value.includes('successfully')) return 'success'
  if (reportStatus.value.includes('Failed') || reportStatus.value.includes('cannot')) return 'error'
  if (reportStatus.value.includes('Generating')) return 'loading'
  return ''
})
</script>



