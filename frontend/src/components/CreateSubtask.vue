<template>
  <div class="subtasks-section" ref="subtasksSectionRef">
    <!-- Toast Notification -->
    <transition name="toast">
      <div v-if="toast.show" :class="['toast-notification', toast.type]">
        <i :class="toast.icon"></i>
        <span>{{ toast.message }}</span>
      </div>
    </transition>

    <div class="subtasks-header">
      <label>Subtasks</label>
      <button 
        type="button"
        @click="toggleSubtaskForm" 
        class="add-subtask-btn"
      >
        <i class="bi bi-plus-lg"></i>
        {{ showSubtaskForm ? 'Close Form' : 'Add Subtask' }}
      </button>
    </div>

    <!-- Inline Subtask Form -->
    <div v-if="showSubtaskForm" class="subtask-form">
      <div class="form-group">
        <label :class="{ 'error-label': showErrors && !currentSubtask.task_name.trim() }">
          Subtask Name<span class="required">*</span>
        </label>
        <input 
          v-model="currentSubtask.task_name" 
          placeholder="Enter subtask name..."
          type="text"
          :class="{ 'input-error': showErrors && !currentSubtask.task_name.trim() }"
        />
      </div>

      <div class="form-group">
        <label :class="{ 'error-label': showErrors && !currentSubtask.description.trim() }">
          Description<span class="required">*</span>
        </label>
        <textarea 
          v-model="currentSubtask.description" 
          placeholder="Enter description..."
          rows="3"
          :class="{ 'input-error': showErrors && !currentSubtask.description.trim() }"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="status">Status</label>
        <select
          id="status"
          v-model="currentSubtask.status"
          class="form-select"
        >
          <option v-if="userRole === 'manager' || userRole === 'director'" value="Unassigned">Unassigned</option>
          <option value="Ongoing">Ongoing</option>
          <option value="Under Review">Under Review</option>
          <option value="Completed">Completed</option>
        </select>
      </div>

      <div class="form-group">
        <label :class="{ 'error-label': showErrors && !currentSubtask.due_date }">
          Due Date & Time<span class="required">*</span>
        </label>
        <input 
          type="datetime-local" 
          v-model="currentSubtask.due_date"
          :min="getTodayDateTime()"
          :class="{ 'input-error': showErrors && !currentSubtask.due_date }"
        />
      </div>

      <div class="form-group">
        <label for="priority-subtask">Priority Level: {{ currentSubtask.priority }}</label>
        <div class="priority-slider-wrapper">
          <input
            id="priority-subtask"
            type="range"
            min="1"
            max="10"
            v-model="currentSubtask.priority"
            class="priority-slider"
          />
          <div class="priority-range-labels">
            <span>1 - Least Important</span>
            <span>10 - Most Important</span>
          </div>
        </div>
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
              v-for="(user, index) in selectedCollaborators" 
              :key="index"
              :class="['selected-email', { 'creator-locked': user.isCreator }]"
            >
              {{ user.email }} 
              <i v-if="user.isCreator" class="bi bi-lock-fill" title="Subtask creator (cannot be removed)"></i>
              <i v-else class="bi bi-x" @click="removeCollaborator(user)"></i>
            </span>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label for="recurrence_type">Recurrence</label>
        <select id="recurrence_type" v-model="currentSubtask.recurrence_type" :disabled="isLoading" class="form-select">
          <option :value="null">-- None --</option>
          <option value="daily">Daily</option>
          <option value="weekly">Weekly</option>
          <option value="bi-weekly">Bi-Weekly</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
          <option value="custom">Custom</option>
        </select>
      </div>

      <div
        v-if="currentSubtask.recurrence_type === 'custom'"
        class="form-group"
      >
        <label for="recurrence_interval_days">Repeat Every (Days)<span style="color: red">*</span></label>
        <input
          type="number"
          id="recurrence_interval_days"
          v-model.number="currentSubtask.recurrence_interval_days"
          min="1"
          placeholder="Enter number of days (e.g. 10)"
          :disabled="isLoading"
          :required="currentSubtask.recurrence_type === 'custom'"
          class="form-input"
        />
      </div>

      <div v-if="currentSubtask.recurrence_type !== null" class="form-group">
        <label for="recurrenceEnd">Recurrence End Date</label>
        <input
          type="datetime-local"
          id="recurrenceEnd"
          v-model="currentSubtask.recurrence_end_date"
          :disabled="isLoading"
          :min="getTodayDateTime()"
        />
      </div>

      <div class="form-actions">
        <button type="button" @click="addSubtask" class="btn-primary">
          <i class="bi bi-plus-circle"></i>
          Create Subtask
        </button>
        <button type="button" @click="cancelForm" class="btn-secondary">
          Cancel
        </button>
      </div>
    </div>

    <!-- Subtask List - Sorted by Priority (High to Low) -->
    <div v-if="sortedSubtasks.length > 0" class="subtask-list">
      <div 
        v-for="(subtask, index) in sortedSubtasks" 
        :key="subtask.id"
        class="subtask-item"
      >
        <div class="subtask-content">
          <div class="subtask-header-info">
            <span class="subtask-number">#{{ index + 1 }}</span>
            <strong>{{ subtask.task_name }}</strong>
          </div>
          <p class="subtask-description">{{ subtask.description }}</p>
          <div class="subtask-meta">
            <span class="subtask-badge" :class="getStatusClass(subtask.status)">
              <i :class="getStatusIcon(subtask.status)"></i>
              {{ subtask.status }}
            </span>
            <span class="subtask-badge" :class="getPriorityClass(subtask.priority)">
              <i class="bi bi-flag-fill"></i>
              Priority {{ subtask.priority }}
            </span>
            <span class="subtask-badge date-badge">
              <i class="bi bi-calendar3"></i>
              {{ formatDateTime(subtask.due_date) }}
            </span>
          </div>
        </div>
        <div class="subtask-actions">
          <button 
            type="button"
            @click="editSubtask(index)" 
            class="edit-subtask-btn"
            title="Edit subtask"
          >
            <i class="bi bi-pencil"></i>
          </button>
          <button 
            type="button"
            @click="removeSubtask(index)" 
            class="remove-subtask-btn"
            title="Remove subtask"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Only show if there are no subtasks AND the form is closed -->
    <p v-if="sortedSubtasks.length === 0 && !showSubtaskForm" class="no-subtasks">
      <i class="bi bi-clipboard"></i>
      No subtasks added yet. Click "Add Subtask" to create one.
    </p>

  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  autoOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const showSubtaskForm = ref(false)
const showErrors = ref(false)
const editingIndex = ref(null)
const collaboratorQuery = ref('')
const selectedCollaborators = ref([])
const collaboratorSuggestions = ref([])
const userRole = ref('')
const currentUserEmail = ref('')
const currentUserId = ref(null)
const subtasksSectionRef = ref(null)
const isLoading = ref(false)

// Get user role and email on component mount
import { getCurrentUserData } from '../services/session.js'

const initUserRole = () => {
  try {
    const userData = getCurrentUserData()
    console.log('User data loaded:', userData)
    userRole.value = userData.role?.toLowerCase() || ''
    currentUserEmail.value = userData.email || ''
    currentUserId.value = userData.id || userData.userid || null
    console.log('Initialized user:', { 
      role: userRole.value, 
      email: currentUserEmail.value, 
      id: currentUserId.value 
    })
  } catch (err) {
    console.error('Error getting user data:', err)
    userRole.value = ''
    currentUserEmail.value = ''
    currentUserId.value = null
  }
}

// Initialize on setup
initUserRole()

// Helper function to get default status based on user role
const getDefaultStatus = () => {
  if (userRole.value === 'manager' || userRole.value === 'director') {
    return 'Unassigned'
  }
  return 'Ongoing'
}

// Scroll to form function
const scrollToForm = () => {
  if (subtasksSectionRef.value) {
    setTimeout(() => {
      const formElement = subtasksSectionRef.value.querySelector('.subtask-form')
      if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 0)
  }
}

// Watch for autoOpen prop and automatically open the form
watch(() => props.autoOpen, (newValue) => {
  if (newValue) {
    openFormWithCreator()
  }
}, { immediate: true })

// Watch for collaborator query changes
watch(collaboratorQuery, async (query) => {
  if (!query) {
    collaboratorSuggestions.value = []
    return
  }

  try {
    const res = await fetch(`http://localhost:5003/users/search?email=${encodeURIComponent(query)}`)
    if (!res.ok) throw new Error('Failed to fetch user emails')
    const data = await res.json()
    collaboratorSuggestions.value = data.data || []
  } catch (err) {
    console.error(err)
    collaboratorSuggestions.value = []
  }
})

const currentSubtask = ref({
  task_name: '',
  description: '',
  due_date: '',
  priority: 5,
  status: getDefaultStatus(),
  collaborators: [],
  recurrence_type: null,
  recurrence_interval_days: null,
  recurrence_end_date: null
})

const toast = ref({
  show: false,
  message: '',
  type: 'error',
  icon: ''
})

// Computed property to sort subtasks by priority (highest to lowest)
const sortedSubtasks = computed(() => {
  return [...props.modelValue].sort((a, b) => {
    return parseInt(b.priority) - parseInt(a.priority)
  })
})

const showToast = (message, type = 'error') => {
  const icons = {
    error: 'bi bi-exclamation-circle-fill',
    success: 'bi bi-check-circle-fill',
    warning: 'bi bi-exclamation-triangle-fill'
  }
  
  toast.value = {
    show: true,
    message,
    type,
    icon: icons[type]
  }
  
  setTimeout(() => {
    toast.value.show = false
  }, 3500)
}

const addCollaborator = (user) => {
  if (!selectedCollaborators.value.find(u => u.userid === user.userid)) {
    selectedCollaborators.value.push(user)
  }
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
}

const removeCollaborator = (user) => {
  // Prevent removing creator
  if (user.isCreator) {
    showToast('Cannot remove subtask creator from collaborators', 'warning')
    return
  }
  selectedCollaborators.value = selectedCollaborators.value.filter(u => u.userid !== user.userid)
}

const addSubtask = () => {
  // Validate required fields
  if (!currentSubtask.value.task_name.trim() || 
      !currentSubtask.value.description.trim() || 
      !currentSubtask.value.due_date) {
    showErrors.value = true
    showToast('Please fill out all required subtask fields', 'error')
    return
  }

const validateRecurrence = () => {
  // Validate recurrence end date if set
  if (currentSubtask.value.recurrence_type && currentSubtask.value.recurrence_end_date) {
    const endDate = new Date(currentSubtask.value.recurrence_end_date)
    const startDate = new Date(currentSubtask.value.due_date)
    
    if (endDate < startDate) {
      showToast("Recurrence end date cannot be before the subtask's due date.", 'error')
      return false
    }
  }

  // Validate custom recurrence interval
  if (
    currentSubtask.value.recurrence_type === 'custom' &&
    (!currentSubtask.value.recurrence_interval_days || currentSubtask.value.recurrence_interval_days < 1)
  ) {
    showToast('Please enter a valid recurrence interval (in days) for custom recurrence.', 'error')
    return false
  }

  return true
}

  // Validate for duplicate subtask name
  const taskNameLower = currentSubtask.value.task_name.trim().toLowerCase()
  const isDuplicate = props.modelValue.some((subtask, index) => {
    if (editingIndex.value !== null && index === editingIndex.value) {
      return false
    }
    return subtask.task_name.toLowerCase() === taskNameLower
  })

  if (isDuplicate) {
    showToast('A subtask with this name already exists. Please use a different name.', 'error')
    return
  }

  const selectedDate = new Date(currentSubtask.value.due_date)
  const now = new Date()
  
  if (selectedDate < now) {
    showToast('Due date cannot be in the past. Please select today or a future date.', 'error')
    return
  }

    // ✅ ADD THIS: Validate recurrence
  if (!validateRecurrence()) {
    return
  }

  // Create new subtask
  const newSubtask = { 
    task_name: currentSubtask.value.task_name,
    description: currentSubtask.value.description,
    due_date: currentSubtask.value.due_date
      ? new Date(currentSubtask.value.due_date).toISOString()
      : null,
    priority: parseInt(currentSubtask.value.priority),
    status: currentSubtask.value.status,
    collaborators: selectedCollaborators.value.map(u => ({
      userid: parseInt(u.userid),
      email: u.email,
      isCreator: u.isCreator || false
    })),
    recurrence_type: currentSubtask.value.recurrence_type || null,
    recurrence_interval_days: (currentSubtask.value.recurrence_type === 'custom' && currentSubtask.value.recurrence_interval_days) 
      ? parseInt(currentSubtask.value.recurrence_interval_days) 
      : null,
    recurrence_end_date: currentSubtask.value.recurrence_type ? currentSubtask.value.recurrence_end_date : null,
    id: Date.now()
  }

  if (editingIndex.value !== null) {
    // Update existing subtask
    newSubtask.id = props.modelValue[editingIndex.value].id
    const updatedSubtasks = [...props.modelValue]
    updatedSubtasks[editingIndex.value] = newSubtask
    emit('update:modelValue', updatedSubtasks)
    showToast('Subtask updated!', 'success')
    editingIndex.value = null
  } else {
    // Add new subtask
    emit('update:modelValue', [...props.modelValue, newSubtask])
    showToast('Subtask added to form!', 'success')
  }
  
  resetForm()
  showSubtaskForm.value = false
  showErrors.value = false
  currentSubtask.value.recurrence_type = null
  currentSubtask.value.recurrence_end_date = null
  currentSubtask.value.recurrence_interval_days = null
} 

const editSubtask = async (sortedIndex) => {
  // Get the actual subtask from sorted list
  const subtaskToEdit = sortedSubtasks.value[sortedIndex]
  
  // Find its index in the original unsorted array
  const originalIndex = props.modelValue.findIndex(s => s.id === subtaskToEdit.id)
  
  currentSubtask.value = {
    task_name: subtaskToEdit.task_name,
    description: subtaskToEdit.description,
    due_date: subtaskToEdit.due_date,
    priority: subtaskToEdit.priority,
    status: subtaskToEdit.status,
    collaborators: subtaskToEdit.collaborators || [],
    recurrence_type: subtaskToEdit.recurrence_type || null,
    recurrence_end_date: subtaskToEdit.recurrence_end_date || null
  }
  
  // Load existing collaborators
  if (subtaskToEdit.collaborators && subtaskToEdit.collaborators.length > 0) {
    try {
      const collaboratorDetails = await Promise.all(
        subtaskToEdit.collaborators.map(collaboratorId => {
          if (typeof collaboratorId === 'object' && collaboratorId.userid) {
            return Promise.resolve({
              userid: collaboratorId.userid,
              email: collaboratorId.email,
              isCreator: collaboratorId.isCreator || false
            });
          }
          
          return fetch(`http://localhost:5003/users/${collaboratorId}`)
            .then(res => {
              if (!res.ok) throw new Error(`Failed to fetch user ${collaboratorId}`);
              return res.json();
            })
            .then(data => ({
              userid: data.data.id || collaboratorId,
              email: data.data.email || `User ${collaboratorId}`,
              isCreator: false
            }))
            .catch(err => {
              console.error(`Error fetching user ${collaboratorId}:`, err);
              return {
                userid: collaboratorId,
                email: `User ${collaboratorId}`,
                isCreator: false
              };
            });
        })
      );
      
      console.log('Loaded collaborators:', collaboratorDetails);
      selectedCollaborators.value = collaboratorDetails;
    } catch (err) {
      console.error('Error loading collaborators:', err);
      selectedCollaborators.value = [];
    }
  } else {
    selectedCollaborators.value = [];
  }
  
  editingIndex.value = originalIndex
  showSubtaskForm.value = true
  showErrors.value = false

  scrollToForm()
}

const resetForm = () => {
  currentSubtask.value = {
    task_name: '',
    description: '',
    due_date: '',
    priority: 5,
    status: getDefaultStatus(),
    collaborators: [], 
    recurrence_type: null,
    recurrence_interval_days: null,
    recurrence_end_date: null
  }
  // Only auto-add creator for staff
  if (userRole.value === 'staff' && currentUserEmail.value && currentUserId.value) {
    selectedCollaborators.value = [{
      userid: currentUserId.value,
      email: currentUserEmail.value,
      isCreator: true
    }]
  } else {
    selectedCollaborators.value = []
  }
  
  collaboratorQuery.value = ''
  collaboratorSuggestions.value = []
  editingIndex.value = null
}

const cancelForm = () => {
  resetForm()
  showSubtaskForm.value = false
  showErrors.value = false
}

// Extracted function to open form with creator
const openFormWithCreator = () => {
  console.log('Opening form with creator check - role:', userRole.value)
  
  if (userRole.value === 'staff' && currentUserEmail.value && currentUserId.value) {
    selectedCollaborators.value = [{
      userid: currentUserId.value,
      email: currentUserEmail.value,
      isCreator: true
    }]
    console.log('Creator added:', selectedCollaborators.value)
  } else {
    selectedCollaborators.value = []
    console.log('Manager/Director - no auto-collaborator. Role is:', userRole.value)
  }
  
  showSubtaskForm.value = true
  scrollToForm()
}

const toggleSubtaskForm = () => {
  if (showSubtaskForm.value) {
    resetForm()
    showErrors.value = false
    showSubtaskForm.value = false
  } else {
    // When opening the form
    console.log('🔍 TOGGLE FORM - User Role:', userRole.value)
    console.log('🔍 TOGGLE FORM - Is Staff?', userRole.value === 'staff')
    
    if (userRole.value === 'staff' && currentUserEmail.value && currentUserId.value) {
      selectedCollaborators.value = [{
        userid: currentUserId.value,
        email: currentUserEmail.value,
        isCreator: true
      }]
      console.log('✅ Staff - Creator added as collaborator')
    } else {
      selectedCollaborators.value = []
      console.log('✅ Manager/Director - No auto-collaborator')
    }
    showSubtaskForm.value = true
    scrollToForm()
  }
}

const removeSubtask = (index) => {
  const updatedSubtasks = [...props.modelValue]
  updatedSubtasks.splice(index, 1)
  emit('update:modelValue', updatedSubtasks)
  showToast('Subtask removed', 'success')
}

const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return 'No date'
  const date = new Date(dateTimeString)
  return date.toLocaleDateString('en-SG', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

const getTodayDateTime = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day}T${hours}:${minutes}`
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

const getPriorityClass = (priority) => {
  const level = parseInt(priority)
  if (level >= 8) return 'priority-high'
  if (level >= 5) return 'priority-medium'
  return 'priority-low'
}
</script>

<style>
.subtasks-section {
  margin-top: 1.5rem;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  background-color: #f9fafb;
  position: relative;
}

/* Toast Notification Styles */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  font-weight: 500;
  font-size: 0.9rem;
  z-index: 9999;
  min-width: 300px;
  max-width: 500px;
  backdrop-filter: blur(10px);
}

.toast-notification i {
  font-size: 1.25rem;
  flex-shrink: 0;
}

.toast-notification.error {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
  border-left: 4px solid #dc2626;
}

.toast-notification.success {
  background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
  color: #065f46;
  border-left: 4px solid #10b981;
}

.toast-notification.warning {
  background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
  color: #92400e;
  border-left: 4px solid #f59e0b;
}

/* Toast Animation */
.toast-enter-active {
  animation: toast-in 0.3s ease-out;
}

.toast-leave-active {
  animation: toast-out 0.3s ease-in;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateX(100%) scale(0.8);
  }
}

.subtasks-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.subtasks-header label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
}

.add-subtask-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.add-subtask-btn:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.subtask-form {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #374151;
  transition: color 0.2s;
}

.form-group label.error-label {
  color: #dc2626;
}

.required {
  color: #dc2626;
  margin-left: 2px;
}

.form-group input,
.form-group textarea,
.form-group select,
.form-input {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: border-color 0.15s ease-in-out;
  width: 100%;
}

.form-select {
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: border-color 0.15s ease-in-out;
  width: 100%;
  cursor: pointer;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus,
.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.form-group input.input-error,
.form-group textarea.input-error {
  border-color: #dc2626;
  background-color: #fee2e2;
}

.form-group input.input-error:focus,
.form-group textarea.input-error:focus {
  border-color: #dc2626;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.1);
}

/* Autocomplete Styles */
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
  transition: background-color 0.2s;
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

.selected-email.creator-locked {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fbbf24;
}

.selected-email i {
  cursor: pointer;
  font-weight: bold;
}

.selected-email.creator-locked i.bi-lock-fill {
  cursor: not-allowed;
  font-size: 0.75rem;
}

.selected-email i:hover {
  color: #1e3a8a;
}

.selected-email.creator-locked i.bi-lock-fill:hover {
  color: #92400e;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
}

.form-actions button {
  flex: 1;
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: #e5e7eb;
  color: #374151;
}

.btn-secondary:hover {
  background: #d1d5db;
}

.subtask-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 0.25rem;
}

.subtask-item {
  display: flex;
  justify-content: space-between;
  align-items: start;
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  background: white;
  transition: all 0.2s;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.subtask-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: #d1d5db;
}

.subtask-content {
  flex: 1;
  min-width: 0;
}

.subtask-header-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.subtask-number {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 600;
  background: #e5e7eb;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
}

.subtask-header-info strong {
  color: #1f2937;
  font-size: 0.95rem;
}

.subtask-description {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0.75rem;
  line-height: 1.5;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.subtask-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.subtask-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.subtask-badge i {
  font-size: 0.7rem;
}

.subtask-badge.ongoing {
  background: #dbeafe;
  color: #1e40af;
}

.subtask-badge.under-review {
  background: #fef3c7;
  color: #92400e;
}

.subtask-badge.completed {
  background: #d1fae5;
  color: #065f46;
}

.subtask-badge.unassigned {
  background: #f3f4f6;
  color: #4b5563;
}

.subtask-badge.priority-high {
  background: #fee2e2;
  color: #991b1b;
}

.subtask-badge.priority-medium {
  background: #fed7aa;
  color: #9a3412;
}

.subtask-badge.priority-low {
  background: #d1fae5;
  color: #065f46;
}

.subtask-badge.date-badge {
  background: #f3f4f6;
  color: #4b5563;
}

.subtask-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.edit-subtask-btn,
.remove-subtask-btn {
  padding: 0.5rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.edit-subtask-btn {
  color: #3b82f6;
}

.edit-subtask-btn:hover {
  background: #dbeafe;
  transform: scale(1.1);
}

.remove-subtask-btn {
  color: #ef4444;
}

.remove-subtask-btn:hover {
  background: #fee2e2;
  transform: scale(1.1);
}

.no-subtasks {
  text-align: center;
  padding: 2.5rem 1rem;
  color: #9ca3af;
  font-size: 0.875rem;
  background: white;
  border: 1px dashed #d1d5db;
  border-radius: 0.5rem;
  margin: 0;
}

.no-subtasks i {
  display: block;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  opacity: 0.5;
}

.priority-slider-wrapper {
  margin-top: 8px;
  position: relative;
}

.priority-slider {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: transparent;
  outline: none !important;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
  border: none !important;
  box-shadow: none !important;
}

.priority-slider:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.priority-slider:focus {
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
}

.priority-slider:active {
  outline: none !important;
  border: none !important;
  box-shadow: none !important;
}

/* Webkit browsers (Chrome, Safari, Edge) */
.priority-slider::-webkit-slider-runnable-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(to right, #10b981 0%, #34d399 20%, #fbbf24 40%, #fb923c 60%, #f97316 80%, #ef4444 100%);
  border: none;
  outline: none;
  box-shadow: none;
}

.priority-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid #6b7280;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  margin-top: -6px;
  transition: all 0.2s ease;
  outline: none;
}

.priority-slider::-webkit-slider-thumb:active {
  cursor: grabbing;
  outline: none !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
}

.priority-slider::-webkit-slider-thumb:hover {
  border-color: #374151;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
  transform: scale(1.1);
  outline: none;
}

.priority-slider::-webkit-slider-thumb:focus {
  outline: none !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

/* Firefox */
.priority-slider::-moz-range-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(to right, #10b981 0%, #34d399 20%, #fbbf24 40%, #fb923c 60%, #f97316 80%, #ef4444 100%);
  border: none;
  outline: none;
  box-shadow: none;
}

.priority-slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 3px solid #6b7280;
  cursor: grab;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  outline: none;
}

.priority-slider::-moz-range-thumb:active {
  cursor: grabbing;
  outline: none !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
}

.priority-slider::-moz-range-thumb:hover {
  border-color: #374151;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.3);
  transform: scale(1.1);
  outline: none;
}

.priority-slider::-moz-range-thumb:focus {
  outline: none !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.priority-range-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 0.875rem;
  color: #6b7280;
}
</style>