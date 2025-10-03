<template>
  <div v-if="isVisible" class="popup-overlay" @click.self="handleOverlayClick">
    <div class="popup-container">
      <!-- Header -->
      <div class="popup-header">
        <h3>Edit Task Details</h3>
        <button class="close-btn" @click="closePopup">&times;</button>
      </div>

      <div class="popup-content">
        <form @submit.prevent="handleUpdate">
          <!-- Task Title -->
          <div class="form-group">
            <label for="title">Task Title</label>
            <input
              type="text"
              id="title"
              v-model="editedTask.task_name"
              :disabled="isLoading"
              class="form-input"
            />
          </div>

          <!-- Description -->
          <div class="form-group">
            <label for="description">Description</label>
            <textarea
              id="description"
              v-model="editedTask.description"
              rows="3"
              :disabled="isLoading"
              class="form-textarea"
              placeholder="Enter task description..."
            ></textarea>
          </div>

          <!-- Status -->
          <div class="form-group">
            <label for="status">Status</label>
            <select
              id="status"
              v-model="editedTask.status"
              :disabled="isLoading"
              class="form-select"
            >
              <option value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <!-- Due Date -->
          <div class="form-group">
            <label for="dueDate">Due Date</label>
            <input
              type="date"
              id="dueDate"
              v-model="editedTask.due_date"
              :disabled="isLoading"
              class="form-input"
              :min="isDateChanged ? getCurrentDate() : undefined"
            />
          </div>

          <!-- Priority Level -->
          <div class="form-group">
            <label for="priority">Priority Level: {{ editedTask.priority }}</label>
            <div class="priority-slider-container">
              <input
                id="priority"
                type="range"
                min="1"
                max="10"
                v-model="editedTask.priority"
                :disabled="isLoading"
                class="priority-slider"
              />
              <div class="priority-labels">
                <span class="priority-label-left">1 - Least Important</span>
                <span class="priority-label-right">10 - Most Important</span>
              </div>
            </div>
          </div>

          <!-- Collaborators -->
          <div class="form-group">
            <label>Collaborators</label>
            <div class="collaborators-list">
              <div
                v-for="member in teamMembers"
                :key="member.id"
                class="collaborator-item"
              >
                <input
                  type="checkbox"
                  :id="`collab-${member.id}`"
                  :value="member.id"
                  v-model="editedTask.collaborators"
                  :disabled="isLoading || member.id === editedTask.owner"
                  class="form-checkbox"
                />
                <label :for="`collab-${member.id}`" class="collaborator-label">
                  {{ member.name }}
                  <span class="role-badge" :class="member.role">{{ member.role }}</span>
                  <span v-if="member.id === editedTask.owner" class="owner-badge">Owner</span>
                </label>
              </div>
            </div>
          </div>

          <!-- Task Type Information -->
          <div v-if="isSubtask" class="info-box">
            <i class="bi bi-info-circle"></i>
            <span>This is a subtask of "{{ parentTaskTitle }}"</span>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <button 
              type="button" 
              @click="discardChanges" 
              :disabled="isLoading"
              class="btn-secondary"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              :disabled="isLoading || !isFormValid"
              class="btn-primary"
            >
              <i class="bi bi-save2" v-if="!isLoading"></i>
              <i class="bi bi-arrow-repeat spin" v-else></i>
              {{ isLoading ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>

      </div>
    </div>
  </div>

  <!-- Messages -->
  <div v-if="successMessage" class="message success">
    <div class="message-content">
      <i class="bi bi-check-circle-fill"></i>
      {{ successMessage }}
    </div>
  </div>
  <div v-if="errorMessage" class="message error">
    <div class="message-content">
      <i class="bi bi-exclamation-circle-fill"></i>
      {{ errorMessage }}
    </div>
  </div>

  <!-- Unsaved Changes Dialog -->
  <div v-if="showUnsavedDialog" class="dialog-overlay">
    <div class="dialog-container">
      <div class="dialog-content">
        <div class="dialog-header">
          <i class="bi bi-exclamation-triangle-fill warning-icon"></i>
          <h4>Unsaved Changes</h4>
        </div>
        <p>You have unsaved changes. Are you sure you want to discard them?</p>
        <div class="dialog-actions">
          <button 
            class="btn-secondary"
            @click="cancelClose"
          >
            Keep Editing
          </button>
          <button 
            class="btn-danger"
            @click="confirmClose"
          >
            Discard Changes
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "TaskEditPopup",
  emits: ['close', 'update-success'],  // ADD THIS LINE
  props: {
    isVisible: { type: Boolean, default: false },
    taskId: { type: [String, Number], required: true },
    taskTitle: { type: String, required: true },
    currentOwner: { type: String, default: '' },
    userRole: { type: String, default: '' },
    isSubtask: { type: Boolean, default: false },
    parentTaskId: { type: [String, Number], default: null },
    parentTaskTitle: { type: String, default: '' },
    teamMembers: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      editedTask: {
        id: null,
        task_name: "",
        description: "",
        status: "Unassigned",
        due_date: "",
        priority: "5",
        owner: "",
        collaborators: [],
      },
      originalTask: null,
      isLoading: false,
      successMessage: "",
      errorMessage: "",
      showUnsavedDialog: false,
      pendingClose: false,
    };
  },
  computed: {
    isFormValid() {
      // Only validate that required fields are filled
      return (
        this.editedTask.task_name?.trim() &&
        this.editedTask.status
      );
    },
    hasChanges() {
      return JSON.stringify(this.editedTask) !== JSON.stringify(this.originalTask);
    },
    isDateChanged() {
      return this.originalTask && this.editedTask.due_date !== this.originalTask.due_date;
    },
  },
  watch: {
    isVisible: {
      handler(newVal) {
        if (newVal) {
          this.clearMessages();
          this.fetchTaskDetails();
        }
      },
      immediate: true
    },
  },
  methods: {
    getCurrentDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-SG', { 
        timeZone: 'Asia/Singapore',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    async fetchTaskDetails() {
      if (!this.taskId) return;
      
      this.isLoading = true;
      this.clearMessages();

      try {
        const response = await fetch(`http://localhost:5002/tasks/${this.taskId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        const task = data.task || data;

        // Format the due date to YYYY-MM-DD format for the date input
        const dueDate = task.due_date ? new Date(task.due_date).toISOString().split('T')[0] : '';
        
        this.editedTask = {
          id: this.taskId,
          task_name: task.task_name || this.taskTitle,
          description: task.description || "",
          status: task.status || "Unassigned",
          due_date: dueDate,
          priority: task.priority || "5",
          owner: task.owner || this.currentOwner,
          collaborators: Array.isArray(task.collaborators) 
            ? task.collaborators.map(c => c.id || c)
            : [],
        };

        this.originalTask = JSON.parse(JSON.stringify(this.editedTask));
      } catch (err) {
        console.error("Error fetching task details:", err);
        this.errorMessage = "Failed to load task details. Please try again.";
      } finally {
        this.isLoading = false;
      }
    },
async handleUpdate() {
  if (!this.isFormValid) return;
  
  this.clearMessages();
  this.isLoading = true;

  try {
    // Prepare only the fields that can be updated
    const updateData = {
      task_id: this.taskId,
      task_name: this.editedTask.task_name,
      description: this.editedTask.description,
      status: this.editedTask.status,
      due_date: this.editedTask.due_date,
      priority: this.editedTask.priority,
      collaborators: this.editedTask.collaborators,
    };

    console.log('EditPopup sending:', updateData);

    const response = await fetch("http://localhost:5002/tasks/update", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.Message || `HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log('EditPopup received:', result);
    
    // Update the original task data
    this.originalTask = JSON.parse(JSON.stringify(this.editedTask));
    
    this.isLoading = false;
    
    // Close the popup
    this.$emit("close");
    
    // Emit success with just the fields that were updated (not the entire response)
    setTimeout(() => {
      this.successMessage = "Task updated successfully!";
      
      // FIXED: Emit only the update data, not the entire backend response
      this.$emit("update-success", {
        task_name: this.editedTask.task_name,
        description: this.editedTask.description,
        status: this.editedTask.status,
        due_date: this.editedTask.due_date,
        priority: this.editedTask.priority,
        collaborators: this.editedTask.collaborators,
      });
      
      setTimeout(() => {
        this.successMessage = "";
      }, 5000);
    }, 500);

  } catch (err) {
    console.error("Error updating task:", err);
    this.errorMessage = err.message || "Failed to update task. Please try again.";
    this.isLoading = false;
  }
},
    discardChanges() {
      if (this.hasChanges) {
        this.showUnsavedDialog = true;
      } else {
        this.closePopup();
      }
    },
    closePopup() {
      if (this.isLoading) return;
      
      if (this.hasChanges && !this.pendingClose) {
        this.showUnsavedDialog = true;
      } else {
        this.clearMessages();
        this.showUnsavedDialog = false;
        this.pendingClose = false;
        this.$emit("close");
      }
    },
    confirmClose() {
      this.pendingClose = true;
      this.closePopup();
    },
    cancelClose() {
      this.showUnsavedDialog = false;
      this.pendingClose = false;
    },
    clearMessages() {
      this.successMessage = "";
      this.errorMessage = "";
    },
    handleOverlayClick() {
      if (this.isLoading) return;
      if (this.showUnsavedDialog) return;
      
      if (this.hasChanges) {
        this.showUnsavedDialog = true;
      } else {
        this.closePopup();
      }
    },
  },
};
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
  max-width: 600px;
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
  padding: 0.25rem;
  border-radius: 4px;
}

.close-btn:hover {
  color: #111827;
  background-color: #f3f4f6;
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

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: border-color 0.15s ease-in-out;
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.original-date {
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.form-checkbox {
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
}

.collaborators-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 0.5rem;
}

.collaborator-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 4px;
}

.collaborator-item:hover {
  background-color: #f3f4f6;
}

.collaborator-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.role-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  text-transform: capitalize;
}

.role-badge.manager {
  background-color: #e0f2fe;
  color: #0369a1;
}

.role-badge.staff {
  background-color: #f3e8ff;
  color: #7e22ce;
}

.owner-badge {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  background-color: #fee2e2;
  color: #b91c1c;
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
  background-color: #6366f1;
  color: white;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4f46e5;
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



.message {
  position: fixed;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 1.25rem 1.5rem;
  border-radius: 12px;
  overflow: hidden;
  animation: slideUpAndFade 0.5s ease-out;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
  min-width: 320px;
  max-width: 520px;
  z-index: 1020;
}

.message-content {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  font-size: 1rem;
}

.message.success {
  background: linear-gradient(145deg, #f0fdf4 0%, #dcfce7 100%);
  color: #15803d;
  border: 1px solid #86efac;
  animation: successPulse 5s infinite;
}

.message.error {
  background-color: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translate(-50%, 100%);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}



@keyframes slideDown {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.info-box {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f3f4f6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4b5563;
  font-size: 0.875rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes slideUpAndFade {
  0% {
    opacity: 0;
    transform: translate(-50%, 100%);
  }
  50% {
    opacity: 1;
    transform: translate(-50%, -10%);
  }
  100% {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}

@keyframes successPulse {
  0% {
    box-shadow: 0 0 0 0 rgba(134, 239, 172, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(134, 239, 172, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(134, 239, 172, 0);
  }
}

/* Unsaved Changes Dialog Styles */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100;
  animation: fadeIn 0.2s ease-out;
}

.dialog-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 400px;
  width: 90%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  transform: translateY(0);
  animation: slideInDialog 0.3s ease-out;
}

.dialog-content {
  text-align: center;
}

.dialog-header {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.dialog-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
}

.warning-icon {
  font-size: 2rem;
  color: #f59e0b;
}

.dialog-content p {
  color: #4b5563;
  margin-bottom: 1.5rem;
  font-size: 0.975rem;
  line-height: 1.5;
}

.dialog-actions {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-danger:hover {
  background-color: #dc2626;
}

@keyframes slideInDialog {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.priority-slider-container {
  margin-top: 8px;
}

.priority-slider {
  width: 100%;
  height: 8px;
  border-radius: 5px;
  background: linear-gradient(to right, #9ca3af 0%, #fbbf24 50%, #ef4444 100%);
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  cursor: pointer;
}

.priority-slider:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

/* Webkit browsers (Chrome, Safari, Edge) */
.priority-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #374151;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.priority-slider::-webkit-slider-thumb:hover {
  border-color: #111827;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

/* Firefox */
.priority-slider::-moz-range-thumb {
  height: 20px;
  width: 20px;
  border-radius: 50%;
  background: #ffffff;
  border: 2px solid #374151;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.priority-slider::-moz-range-track {
  height: 8px;
  border-radius: 5px;
  background: linear-gradient(to right, #9ca3af 0%, #fbbf24 50%, #ef4444 100%);
  border: none;
}

.priority-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 4px;
  font-size: 0.875rem;
  color: #6b7280;
}

.priority-label-left,
.priority-label-right {
  font-size: 0.75rem;
}

</style>