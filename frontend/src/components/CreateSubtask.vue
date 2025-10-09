<template>
  <div class="subtasks-section">
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
        @click="showSubtaskForm = !showSubtaskForm" 
        class="add-subtask-btn"
      >
        <i class="bi bi-plus-lg"></i>
        {{ showSubtaskForm ? 'Close Form' : 'Add Subtask' }}
      </button>
    </div>

    <!-- Inline Subtask Form -->
    <div v-if="showSubtaskForm" class="subtask-form">
      <div class="form-group">
        <label>Subtask Name*</label>
        <input 
          v-model="currentSubtask.task_name" 
          placeholder="Enter subtask name..."
          type="text"
        />
      </div>

      <div class="form-group">
        <label>Description*</label>
        <textarea 
          v-model="currentSubtask.description" 
          placeholder="Enter description..."
          rows="3"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label>Status</label>
        <select v-model="currentSubtask.status">
        <option value="Ongoing">Ongoing</option>
        <option value="Under Review">Under Review</option>
        <option value="Completed">Completed</option>
        </select>
      </div>

      <div class="form-group">
        <label>Due Date*</label>
        <input 
          type="date" 
          v-model="currentSubtask.due_date"
          :min="getTodayDate()"
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
                :disabled="isLoading"
                class="priority-slider"
                />
                <div class="priority-range-labels">
                    <span>1 - Least Important</span>
                    <span>10 - Most Important</span>
                </div>
            </div>
        </div>

      <div class="form-actions">
        <button type="button" @click="addSubtask" class="btn-primary">
          <i class="bi bi-plus-circle"></i>
          Add Subtask
        </button>
        <button type="button" @click="cancelForm" class="btn-secondary">
          Cancel
        </button>
      </div>
    </div>

    <!-- Subtask List -->
    <div v-if="modelValue.length > 0" class="subtask-list">
      <div 
        v-for="(subtask, index) in modelValue" 
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
              {{ formatDate(subtask.due_date) }}
            </span>
          </div>
        </div>
        <button 
          type="button"
          @click="removeSubtask(subtask.id)" 
          class="remove-subtask-btn"
          title="Remove subtask"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>
    </div>

    <!-- Only show if there are no subtasks AND the form is closed -->
    <p v-if="modelValue.length === 0 && !showSubtaskForm" class="no-subtasks">
    <i class="bi bi-clipboard"></i>
    No subtasks added yet. Click "Add Subtask" to create one.
    </p>

  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

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

// Watch for autoOpen prop and automatically open the form
watch(() => props.autoOpen, (newValue) => {
  if (newValue) {
    showSubtaskForm.value = true
  }
}, { immediate: true })
const currentSubtask = ref({
  task_name: '',
  description: '',
  due_date: '',
  priority: 5,
  status: 'Ongoing'
})

const toast = ref({
  show: false,
  message: '',
  type: 'error',
  icon: ''
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

const addSubtask = () => {
  // Validate required fields
  if (!currentSubtask.value.task_name.trim() || 
      !currentSubtask.value.description.trim() || 
      !currentSubtask.value.due_date) {
    showToast('Please fill out all required subtask fields', 'error')
    return
  }

  // Validate that due date is not in the past
  const selectedDate = new Date(currentSubtask.value.due_date)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (selectedDate < today) {
    showToast('Due date cannot be in the past. Please select today or a future date.', 'error')
    return
  }

  // Create new subtask with proper data types
  const newSubtask = { 
    task_name: currentSubtask.value.task_name,
    description: currentSubtask.value.description,
    due_date: currentSubtask.value.due_date,
    priority: parseInt(currentSubtask.value.priority), // Convert to integer
    status: currentSubtask.value.status,
    id: Date.now() // Temporary ID for frontend display
  }

  // Emit to parent component
  emit('update:modelValue', [...props.modelValue, newSubtask])

  // Show success message
  showToast('Subtask added successfully!', 'success')
  
  // Reset form and close
  resetForm()
  showSubtaskForm.value = false
}

const formatDate = (dateString) => {
  if (!dateString) return 'No date'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-SG', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const getTodayDate = () => {
  const today = new Date()
  const year = today.getFullYear()
  const month = String(today.getMonth() + 1).padStart(2, '0')
  const day = String(today.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
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
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: 0.625rem 0.875rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
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
  -webkit-line-clamp: 2;
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

.remove-subtask-btn {
  padding: 0.5rem;
  background: transparent;
  color: #ef4444;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important; /* Keep only the thumb shadow */
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