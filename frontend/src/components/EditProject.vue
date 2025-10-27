<template>
  <div v-if="isVisible" class="popup-overlay" @click.self="handleOverlayClick">
    <div class="popup-container">
      <!-- Header -->
      <div class="popup-header">
        <h3>Edit Project Details</h3>
        <button class="close-btn" @click="closePopup">&times;</button>
      </div>

      <div class="popup-content">
        <form @submit.prevent="handleUpdate">
          <!-- Project Name -->
          <div class="form-group">
            <label for="projectName">Project Name*</label>
            <input
              type="text"
              id="projectName"
              v-model="editedProject.proj_name"
              :disabled="isLoading"
              :class="{ 'input-error': showErrors && !editedProject.proj_name.trim() }"
              class="form-input"
              placeholder="Enter project name..."
            />
          </div>

          <!-- Collaborators -->
          <div class="form-group">
            <label>Collaborators (emails)</label>
            <div class="autocomplete">
              <input 
                type="text"
                v-model="collaboratorQuery"
                placeholder="Type email..."
                class="form-input"
                :disabled="isLoading"
              />

              <ul v-if="collaboratorSuggestions.length > 0" class="suggestions-list">
                <li 
                  v-for="user in collaboratorSuggestions" 
                  :key="user.id"
                  @click="addCollaborator(user)"
                  class="suggestion-item"
                >
                  {{ user.email }}
                </li>
              </ul>

              <div class="selected-collaborators">
                <span 
                  v-for="user in selectedCollaborators" 
                  :key="user.id" 
                  class="selected-email"
                >
                  {{ user.email }} <i class="bi bi-x" @click="removeCollaborator(user)"></i>
                </span>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <button 
              type="submit" 
              :disabled="isLoading || !isFormValid"
              class="btn-primary"
            >
              <i class="bi bi-check-circle" v-if="!isLoading"></i>
              <i class="bi bi-arrow-repeat spin" v-else></i>
              {{ isLoading ? 'Updating...' : 'Update Project' }}
            </button>
            <button 
              type="button" 
              @click="closePopup" 
              :disabled="isLoading"
              class="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Error Popup -->
  <div v-if="errorMessage" class="error-popup">
    <i class="bi bi-exclamation-triangle-fill"></i>
    <span>{{ errorMessage }}</span>
    <button class="close-btn" @click="errorMessage = ''">&times;</button>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  isVisible: { type: Boolean, default: false },
  projectId: { type: [String, Number], required: true },
  currentProjectName: { type: String, default: '' },
  currentCollaborators: { type: Array, default: () => [] }
})

const emit = defineEmits(['close', 'update-success'])

// Form data
const editedProject = ref({
  proj_name: ''
})

// Collaborator management
const collaboratorQuery = ref('')
const selectedCollaborators = ref([])
const collaboratorSuggestions = ref([])

// UI state
const isLoading = ref(false)
const showErrors = ref(false)
const errorMessage = ref('')

// Form validation
const isFormValid = computed(() => {
  return editedProject.value.proj_name.trim() !== ''
})

// Watch for collaborator query changes
watch(collaboratorQuery, async (query) => {
  if (!query) {
    collaboratorSuggestions.value = []
    return
  }

  try {
    const res = await fetch(`http://localhost:5003/users/search?q=${encodeURIComponent(query)}`)
    if (!res.ok) throw new Error('Failed to fetch user emails')
    const data = await res.json()
    collaboratorSuggestions.value = data.data || []
  } catch (err) {
    console.error(err)
    collaboratorSuggestions.value = []
  }
})

// Collaborator management methods
const addCollaborator = (user) => {
  if (!selectedCollaborators.value.find(u => u.id === user.id)) {
    selectedCollaborators.value.push(user)
  }
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
}

const removeCollaborator = (user) => {
  selectedCollaborators.value = selectedCollaborators.value.filter(u => u.id !== user.id)
}

// Initialize form with current project data
const initializeForm = async () => {
  editedProject.value.proj_name = props.currentProjectName
  
  // Load current collaborators
  if (props.currentCollaborators && props.currentCollaborators.length > 0) {
    try {
      // Fetch user details for current collaborators
      const collaboratorPromises = props.currentCollaborators.map(async (collabId) => {
        const response = await fetch(`http://localhost:5003/users/${collabId}`)
        if (response.ok) {
          const data = await response.json()
          return data.data
        }
        return null
      })
      
      const collaboratorDetails = await Promise.all(collaboratorPromises)
      selectedCollaborators.value = collaboratorDetails.filter(collab => collab !== null)
    } catch (error) {
      console.error('Error loading current collaborators:', error)
    }
  }
}

// Watch for visibility changes to initialize form
watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    initializeForm()
  }
})

// Handle form submission
const handleUpdate = async () => {
  if (!isFormValid.value) {
    showErrors.value = true
    errorMessage.value = "Please fill out all required fields."
    return
  }

  isLoading.value = true
  errorMessage.value = ""
  showErrors.value = false

  try {
    // Build collaborator IDs from selected users
    const collaboratorIds = selectedCollaborators.value
      .map(user => parseInt(user.userid || user.id))
      .filter(id => !isNaN(id))

    const payload = {
      project_id: props.projectId,
      proj_name: editedProject.value.proj_name,
      collaborators: collaboratorIds
    }

    const response = await fetch('http://localhost:5001/projects/update', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (response.ok) {
      emit('update-success', data)
      closePopup()
    } else {
      errorMessage.value = data.error || data.message || data.Message || 'Failed to update project'
    }
  } catch (error) {
    console.error('Error updating project:', error)
    errorMessage.value = 'Error updating project. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// Popup management
const closePopup = () => {
  // Reset form
  editedProject.value = { proj_name: '' }
  selectedCollaborators.value = []
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
  errorMessage.value = ''
  showErrors.value = false
  
  emit('close')
}

const handleOverlayClick = () => {
  if (!isLoading.value) closePopup()
}
</script>

<style scoped>
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.popup-container {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.popup-header h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.popup-content {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: border-color 0.15s ease-in-out;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.autocomplete {
  position: relative;
}

.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
  list-style: none;
  padding: 0;
  margin: 4px 0 0 0;
}

.suggestion-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
}

.suggestion-item:hover {
  background-color: #f3f4f6;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.selected-collaborators {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.selected-email {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #dbeafe;
  color: #1e40af;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
}

.selected-email i {
  cursor: pointer;
  font-weight: bold;
}

.selected-email i:hover {
  color: #1e3a8a;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: white;
  color: #4b5563;
  border: 1px solid #e5e7eb;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-popup {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #f44336;
  color: white;
  padding: 16px 24px;
  border-radius: 8px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  z-index: 1000;
  min-width: 280px;
  max-width: 90%;
  text-align: center;
}

.error-popup .close-btn {
  background: transparent;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  margin-left: auto;
}

.spin {
  animation: spin 1s linear infinite;
}

.input-error {
  background-color: #ffe5e5 !important;
  border: 1px solid #ff4d4d !important;
}

.input-error:focus {
  outline: none;
  border-color: #ff0000 !important;
  box-shadow: 0 0 4px rgba(255, 0, 0, 0.3);
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
