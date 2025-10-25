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
            <option value="pdf">PDF</option>
            <option value="excel">Excel</option>
          </select>

          <button type="submit" class="report-btn">Generate {{ currentReportType }} Report</button>
        </form>
      </div>

      <!-- Report Status Message -->
      <div v-if="reportStatus" class="report-status">
        <p>{{ reportStatus }}</p>
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
const userRole = localStorage.getItem('spm_role')?.toLowerCase()
const currentReportType = ref(null)
const reportForm = ref({ startDate: '', endDate: '', format: 'pdf' })
const reportStatus = ref('')

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
      alert('Please select both start and end dates')
      return
    }
    
    const queryParams = new URLSearchParams({ format, start_date: startDate, end_date: endDate }).toString()
    let endpoint = ''

    if (currentReportType.value === 'personal') {
      endpoint = `http://localhost:5007/reports/personal/${userId}`
    } else if (currentReportType.value === 'team') {
      endpoint = `http://localhost:5007/reports/team/${userId}`
    } else if (currentReportType.value === 'department') {
      endpoint = `http://localhost:5007/reports/department/${userId}`
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
</script>



