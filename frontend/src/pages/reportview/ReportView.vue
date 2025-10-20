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
      </div>

      <!-- Dynamic Report Form -->
      <div v-if="currentReportType" class="report-form">
        <h3>Generate {{ currentReportType }} Report</h3>
        <form @submit.prevent="generateReport">
          <label for="start-date">Start Date:</label>
          <input type="date" id="start-date" v-model="reportForm.startDate" />

          <label for="end-date">End Date:</label>
          <input type="date" id="end-date" v-model="reportForm.endDate" />

          <label for="export-format">Export Format:</label>
          <select id="export-format" v-model="reportForm.format">
            <option value="json">JSON</option>
            <option value="pdf">PDF</option>
            <option value="excel">Excel</option>
          </select>

          <button type="submit" class="report-btn">Generate {{ currentReportType }} Report</button>
        </form>
      </div>

      <!-- Report Display Section -->
      <div v-if="reportData && reportForm.format === 'json'" class="report-display">
        <h2>Report</h2>
        <div class="formatted-report">
          <pre>{{ formatReport(reportData) }}</pre>
          <pre>Raw Data: {{ reportData }}</pre> <!-- Debugging: Display raw data -->
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import SideNavbar from '../../components/SideNavbar.vue'
import '../reportview/reportview.css'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const userId = localStorage.getItem('spm_userid')
const userRole = localStorage.getItem('spm_role')?.toLowerCase() // 'staff', 'manager', or 'director'
const reportData = ref(null) // Reactive variable to store the report data
const currentReportType = ref(null) // Tracks the current report type being generated
const reportForm = ref({ startDate: '', endDate: '', format: 'json' }) // Form inputs

// Show the form for the selected report type
const showReportForm = (reportType) => {
  currentReportType.value = reportType
  reportForm.value = { startDate: '', endDate: '', format: 'json' } // Reset the form
}

// Generate the selected report
const generateReport = async () => {
  try {
    const { startDate, endDate, format } = reportForm.value
    const queryParams = new URLSearchParams({ format, start_date: startDate, end_date: endDate }).toString()
    let endpoint = ''

    // Determine the endpoint based on the report type
    if (currentReportType.value === 'personal') {
      endpoint = `http://localhost:5007/reports/personal/${userId}`
    } else if (currentReportType.value === 'team') {
      endpoint = `http://localhost:5007/reports/team/${userId}`
    } else if (currentReportType.value === 'department') {
      endpoint = `http://localhost:5007/reports/department/${userId}`
    }

    const response = await fetch(`${endpoint}?${queryParams}`)
    if (!response.ok) {
      throw new Error(`Failed to generate ${currentReportType.value} report`)
    }

    // Handle JSON response
    if (format === 'json') {
      const data = await response.json()
      reportData.value = data
    } else {
      // Handle file download for PDF/Excel
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `${currentReportType.value}_report.${format}`
      link.click()
      window.URL.revokeObjectURL(url)
    }
  } catch (error) {
    console.error(`Error generating ${currentReportType.value} report:`, error)
    alert(`Failed to generate ${currentReportType.value} report`)
  }
}

// Method to format the report data nicely
// Fixed formatReport method for ReportView.vue
const formatReport = (data) => {
  console.log('Formatting report data:', data) // Debug log
  if (!data) return 'No report data available.'

  let formatted = ''

  // Handle response message
  if (data.message) {
    formatted += `${data.message}\n\n`
  }

  // Check if data.data exists (the actual report data)
  const reportData = data.data
  if (!reportData) {
    return 'No report data available.'
  }

  // Handle Personal Report
  if (reportData.user_name && !reportData.team_report && !reportData.department_report) {
    formatted += `=== Personal Report ===\n\n`
    formatted += `Name: ${reportData.user_name}\n`
    formatted += `Role: ${reportData.user_role}\n\n`
    
    formatted += `Task Summary:\n`
    formatted += `  Total Tasks: ${reportData.total_tasks}\n`
    formatted += `  Completed Tasks: ${reportData.completed_tasks}\n`
    formatted += `  Overdue Tasks: ${reportData.overdue_tasks}\n`
    formatted += `  Completion Rate: ${reportData.completion_percentage}%\n`
    formatted += `  Overdue Rate: ${reportData.overdue_percentage}%\n\n`
    
    if (reportData.task_stats && Object.keys(reportData.task_stats).length > 0) {
      formatted += `Task Status Breakdown:\n`
      Object.entries(reportData.task_stats).forEach(([status, count]) => {
        formatted += `  ${status}: ${count}\n`
      })
      formatted += '\n'
    }
    
    if (reportData.project_stats && reportData.project_stats.length > 0) {
      formatted += `Projects (${reportData.total_projects}):\n`
      reportData.project_stats.forEach((project, index) => {
        formatted += `  ${index + 1}. ${project.project_name || 'Unknown'} - ${project.task_count || 0} tasks\n`
      })
      formatted += '\n'
    }
    
    if (reportData.average_task_duration) {
      formatted += `Average Task Duration: ${reportData.average_task_duration.toFixed(2)} days\n\n`
    }
  }

  // Handle Team Report
  if (reportData.team_report) {
    const team = reportData.team_report
    formatted += `=== Team Report ===\n\n`
    formatted += `Team: ${team.team_name || 'Unknown'}\n`
    formatted += `Department: ${team.dept_name || 'Unknown'}\n\n`
    
    formatted += `Team Summary:\n`
    formatted += `  Total Tasks: ${team.total_team_tasks}\n`
    formatted += `  Total Projects: ${team.total_team_projects}\n`
    formatted += `  Team Completion Rate: ${team.team_completion_percentage}%\n`
    formatted += `  Team Overdue Rate: ${team.team_overdue_percentage || 0}%\n\n`
    
    if (team.member_reports && team.member_reports.length > 0) {
      formatted += `Team Members (${team.member_reports.length}):\n`
      team.member_reports.forEach((member, index) => {
        formatted += `  ${index + 1}. ${member.user_name} (${member.user_role})\n`
        formatted += `     Tasks: ${member.total_tasks} total, ${member.completed_tasks} completed, ${member.overdue_tasks} overdue\n`
      })
      formatted += '\n'
    }
  }

  // Handle Department Report
  if (reportData.department_report) {
    const dept = reportData.department_report
    formatted += `=== Department Report ===\n\n`
    formatted += `Department: ${dept.dept_name || 'Unknown'}\n\n`
    
    formatted += `Department Summary:\n`
    formatted += `  Total Tasks: ${dept.total_team_tasks}\n`
    formatted += `  Total Projects: ${dept.total_team_projects}\n`
    formatted += `  Completion Rate: ${dept.team_completion_percentage}%\n`
    formatted += `  Overdue Rate: ${dept.team_overdue_percentage || 0}%\n\n`
    
    if (dept.member_reports && dept.member_reports.length > 0) {
      formatted += `Department Members (${dept.member_reports.length}):\n`
      dept.member_reports.forEach((member, index) => {
        formatted += `  ${index + 1}. ${member.user_name} (${member.user_role})\n`
        formatted += `     Tasks: ${member.total_tasks} total, ${member.completed_tasks} completed, ${member.overdue_tasks} overdue\n`
      })
      formatted += '\n'
    }
  }

  return formatted || 'No formatted data available.'
}
</script>


