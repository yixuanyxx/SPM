<template>
  <div v-if="isVisible" class="popup-overlay" @click.self="handleOverlayClick">
    <div class="popup-container">
      <!-- Header -->
      <div class="popup-header">
        <h3>Create New Task</h3>
        <button class="close-btn" @click="closePopup">&times;</button>
      </div>

      <div class="popup-content">
        <form @submit.prevent="handleCreate">
          <!-- Task Title -->
          <div class="form-group">
            <label for="title">Task Name*</label>
            <input
              type="text"
              id="title"
              v-model="newTask.task_name"
              :disabled="isLoading"
              :class="{ 'input-error': showErrors && !newTask.task_name }"
              placeholder="Enter task name..."
            />
          </div>

          <!-- Description -->
          <div class="form-group">
            <label for="description">Description*</label>
            <textarea
              id="description"
              v-model="newTask.description"
              rows="3"
              :disabled="isLoading"
              :class="{ 'input-error': showErrors && !newTask.description }"
              placeholder="Enter task description..."
            ></textarea>
          </div>

          <!-- Due Date -->
          <div class="form-group">
            <label for="dueDate">Due Date*</label>
            <input
              type="datetime-local"
              id="dueDate"
              v-model="newTask.due_date"
              :disabled="isLoading"
              :class="{ 'input-error': showErrors && !newTask.due_date }"
              :min="getTodayDateTime()"
            />
          </div>

          <!-- Status -->
          <div class="form-group">
            <label for="status">Status</label>
            <select
              id="status"
              v-model="newTask.status"
              :disabled="isLoading"
              class="form-select"
            >
              <option v-if="userRole === 'manager' || userRole === 'director'" value="Unassigned">Unassigned</option>
              <option value="Ongoing">Ongoing</option>
              <option value="Under Review">Under Review</option>
              <option value="Completed">Completed</option>
            </select>
          </div>

          <!-- Priority -->
          <div class="form-group">
            <label for="priority">Priority Level: {{ newTask.priority }}</label>
            <div class="priority-slider-wrapper">
              <input
                id="priority"
                type="range"
                min="1"
                max="10"
                v-model="newTask.priority"
                :disabled="isLoading"
                class="priority-slider"
              />
              <div class="priority-range-labels">
                <span>1 - Least Important</span>
                <span>10 - Most Important</span>
              </div>
            </div>
          </div>

          <!-- Projects -->
          <div class="form-group">
            <label>Project</label>
            <select v-model="newTask.project_id" class="form-select">
              <option value="">-- Select Project --</option>
              <template v-if="userProjects.length > 0">
                <option 
                  v-for="project in userProjects" 
                  :key="project.id" 
                  :value="project.id"
                >
                  {{ project.proj_name }}
                </option>
              </template>
              <option v-else disabled>No projects available</option>
            </select>
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
                  v-for="user in selectedCollaborators" 
                  :key="user.userid" 
                  class="selected-email"
                  :class="{ 'locked': user.isLockedOwner }"
                >
                  {{ user.email }}
                  <i 
                    v-if="!user.isLockedOwner"
                    class="bi bi-x" 
                    @click="removeCollaborator(user)"
                  ></i>
                  <i 
                    v-else
                    class="bi bi-lock-fill"
                    title="You are automatically added as a collaborator"
                  ></i>
                </span>
              </div>
            </div>
          </div>

          <!-- Subtasks Component -->
          <SubtaskForm 
            v-model="newTask.subtasks"
            :parentTaskName="newTask.task_name"
            :userRole="userRole"
          />
        
          <!-- Attachments -->
          <div class="form-group mt-4">
            <label>Attach PDF</label>
            <input
              type="file"
              @change="handleFileUpload"
              accept="application/pdf"
              :disabled="isLoading"
              class="file-input"
            />
            <span class="file-hint">Only PDF files allowed</span>
          </div>

          <!-- Recurrence -->
          <div class="form-group">
            <label for="recurrence_type">Recurrence</label>
            <select id="recurrence_type" v-model="newTask.recurrence_type" :disabled="isLoading" class="form-select">
              <option :value="null">-- None --</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="bi-weekly">Bi-Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div v-if="newTask.recurrence_type !== null" class="form-group">
            <label for="recurrenceEnd">Recurrence End Date</label>
            <input
              type="datetime-local"
              id="recurrenceEnd"
              v-model="newTask.recurrence_end_date"
              :disabled="isLoading"
              :min="getTodayDateTime()"
            />
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <button 
              type="submit" 
              :disabled="isLoading"
              class="btn-primary"
            >
              <i class="bi bi-plus-circle" v-if="!isLoading"></i>
              <i class="bi bi-arrow-repeat spin" v-else></i>
              {{ isLoading ? 'Creating...' : 'Create Task' }}
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

  <!-- Messages -->
  <!-- Success Popup -->
  <div v-if="successMessage" class="success-popup">
    <i class="bi bi-check-circle-fill"></i> {{ successMessage }}
  </div>

  <!-- Error Popup -->
  <div v-if="errorMessage" class="error-popup">
    <i class="bi bi-exclamation-triangle-fill"></i>
    <span>{{ errorMessage }}</span>
    <button class="close-btn" @click="errorMessage = ''">&times;</button>
  </div>

</template>

<script>
import { getCurrentUserData } from '../services/session.js'
import SubtaskForm from '../components/CreateSubtask.vue'

export default {
  name: "CreateNewTaskForm",
  components: {
    SubtaskForm
  },
  props: {
    isVisible: { type: Boolean, default: true }
  },
  emits: ["close", "task-created"],
  data() {
    return {
      userRole: '',
      userId: null,
      userEmail: '',
      userProjects: [],
      collaboratorQuery: '',
      selectedCollaborators: [],
      collaboratorSuggestions: [],
      newTask: {
        owner_id: null,
        task_name: "",
        description: "",
        type: "parent",
        status: "Ongoing",
        due_date: "",
        priority: 5,
        project_id: "",
        collaborators: "",
        parent_task: "",
        subtasks: [], 
        recurrence_type: null,      
        recurrence_end_date: null
      },
      newAttachmentFile: null,
      isLoading: false,
      showErrors: false,
      successMessage: "",
      errorMessage: ""
    };
  },
  computed: {
    isFormValid() {
      return this.newTask.task_name?.trim() && 
             this.newTask.description?.trim() && 
             this.newTask.due_date?.trim();
    }
  },
  watch: {
    async collaboratorQuery(query) {
      if (!query) {
        this.collaboratorSuggestions = [];
        return;
      }

      try {
        const res = await fetch(`http://localhost:5003/users/search?email=${encodeURIComponent(query)}`);
        if (!res.ok) throw new Error('Failed to fetch user emails');
        const data = await res.json();
        this.collaboratorSuggestions = data.data || [];
      } catch (err) {
        console.error(err);
        this.collaboratorSuggestions = [];
      }
    }
  },
  mounted() {
    const userData = getCurrentUserData();
    this.userRole = userData.role?.toLowerCase() || '';
    this.userId = parseInt(userData.userid) || null;
    this.newTask.owner_id = this.userId;
    this.userEmail = userData.email || '';

    // Set default status based on user role
    this.newTask.status = (this.userRole === 'manager' || this.userRole === 'director') ? 'Unassigned' : 'Ongoing';

    // If staff, add current user as locked collaborator
    if (this.userRole === 'staff' && this.userEmail) {
      this.selectedCollaborators.push({
        userid: this.userId,
        email: this.userEmail,
        isLockedOwner: true // Mark as locked
      });
    }

    console.log('CreateNewTaskForm mounted with userId:', this.userId);

    // Fetch projects owned by user
    if (this.userId) {
      fetch(`http://localhost:5001/projects/owner/${this.userId}`)
        .then(res => {
          if (!res.ok) {
            if (res.status === 404) {
              console.warn('No projects found for this user');
              this.userProjects = [];
              return null;
            }
            throw new Error(`HTTP error! status: ${res.status}`);
          }
          return res.json();
        })
        .then(data => {
          if (data) {
            const allProjects = data.data || [];
            this.userProjects = allProjects.filter(project => {
              const collabs = project.collaborators || [];
              return project.owner_id == this.userId || collabs.includes(Number(this.userId));
            });
            console.log('Filtered projects for dropdown:', this.userProjects);
          }
        })
        .catch(err => console.error('Error fetching projects:', err));
    }
  },
  methods: {
    getTodayDateTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      const hours = String(now.getHours()).padStart(2, '0');
      const minutes = String(now.getMinutes()).padStart(2, '0');
      return `${year}-${month}-${day}T${hours}:${minutes}`;
    },
    handleFileUpload(e) {
      const file = e.target.files[0];
      if (file && file.type === "application/pdf") {
        this.newAttachmentFile = file;
      } else {
        this.errorMessage = "Only PDF files are allowed";
        e.target.value = null;
        this.newAttachmentFile = null;
      }
    },
    addCollaborator(user) {
      if (!this.selectedCollaborators.find(u => u.userid === user.userid)) {
        this.selectedCollaborators.push(user);
      }
      this.collaboratorQuery = '';
      this.collaboratorSuggestions = [];
    },
    removeCollaborator(user) {
      // Prevent removal if locked
      if (user.isLockedOwner) {
        return;
      }
      this.selectedCollaborators = this.selectedCollaborators.filter(u => u.userid !== user.userid);
    },
    async handleCreate() {
      if (!this.isFormValid) {
        this.showErrors = true;
        this.errorMessage = "Please fill out all required fields: Task Name, Description, and Due Date.";
        return;
      }

      // Validate that due date is not in the past
      const selectedDate = new Date(this.newTask.due_date);
      const now = new Date();
      
      if (selectedDate < now) {
        this.errorMessage = "Due date cannot be in the past. Please select today or a future date.";
        return;
      }

      // Validate for duplicate task and subtask names
      const taskNameLower = this.newTask.task_name.trim().toLowerCase();
      const hasDuplicateSubtask = this.newTask.subtasks.some(subtask => 
        subtask.task_name.toLowerCase() === taskNameLower
      );

      if (hasDuplicateSubtask) {
        this.errorMessage = "A subtask cannot have the same name as the parent task. Please use different names.";
        return;
      }

      // Validate recurrence end date if set
      if (this.newTask.recurrence_type && this.newTask.recurrence_end_date) {
        const endDate = new Date(this.newTask.recurrence_end_date);
        const startDate = new Date(this.newTask.due_date);
        if (endDate < startDate) {
          this.errorMessage = "Recurrence end date cannot be before the task's due date.";
          return;
        }
      }

      this.isLoading = true;
      this.errorMessage = "";
      this.successMessage = "";

      try {
        // ===== STEP 1: Create Parent Task =====
        const formData = new FormData();
        formData.append("owner_id", this.newTask.owner_id);
        formData.append("task_name", this.newTask.task_name);
        formData.append("description", this.newTask.description);
        formData.append("type", "parent"); // Force parent type
        formData.append("status", this.newTask.status);
        formData.append("priority", this.newTask.priority);
        
        if (this.newTask.project_id) {
          formData.append("project_id", this.newTask.project_id);
        }

        if (this.newTask.due_date) {
          const localDate = new Date(this.newTask.due_date);
          const utcDateString = localDate.toISOString();
          formData.append('due_date', utcDateString);
        }
        
        if (this.newAttachmentFile) {
          formData.append("attachment", this.newAttachmentFile);
        }

        // Collaborators
        const collaboratorIds = this.selectedCollaborators.map(user => parseInt(user.userid));
        if (this.userRole === "staff" && !collaboratorIds.includes(this.newTask.owner_id)) {
          collaboratorIds.push(this.newTask.owner_id);
        }
        if (collaboratorIds.length > 0) {
          formData.append("collaborators", collaboratorIds.join(","));
        }

        // Recurrence
        if (this.newTask.recurrence_type) {
          formData.append("recurrence_type", this.newTask.recurrence_type);

          if (this.newTask.recurrence_end_date) {
            const endUTC = new Date(this.newTask.recurrence_end_date).toISOString();
            formData.append("recurrence_end_date", endUTC);
          } else {
            formData.append("recurrence_end_date", ""); // explicitly send null
          }
        } else {
          formData.append("recurrence_type", "None");
          formData.append("recurrence_end_date", "");
        }

        // Role-based endpoint for PARENT task
        let parentEndpoint = "";
        if (this.userRole === "manager" || this.userRole === "director") {
          parentEndpoint = "http://localhost:5002/tasks/manager-task/create";
        } else {
          parentEndpoint = "http://localhost:5002/tasks/staff-task/create";
        }

        console.log('Creating parent task...');
        const parentRes = await fetch(parentEndpoint, {
          method: "POST",
          body: formData
        });

        const parentData = await parentRes.json();

        if (!parentRes.ok || parentData.Code !== 201) {
          throw new Error(parentData.Message || 'Failed to create parent task');
        }

        const createdParentTask = parentData.data;
        console.log('Parent task created:', createdParentTask);

        // ===== STEP 2: Create Subtasks (if any) =====
        const createdSubtasks = [];
        
        if (this.newTask.subtasks && this.newTask.subtasks.length > 0) {
          console.log(`Creating ${this.newTask.subtasks.length} subtasks...`);
          
          // Determine subtask endpoint based on role
          let subtaskEndpoint = "";
          if (this.userRole === "manager" || this.userRole === "director") {
            subtaskEndpoint = "http://localhost:5002/tasks/manager-subtask/create";
          } else {
            subtaskEndpoint = "http://localhost:5002/tasks/staff-subtask/create";
          }

          for (const [index, subtask] of this.newTask.subtasks.entries()) {
            try {
              // Extract subtask's own collaborators (not parent's)
              let subtaskCollaboratorIds = [];
              if (subtask.collaborators && subtask.collaborators.length > 0) {
                subtaskCollaboratorIds = subtask.collaborators.map(collab => {
                  // Handle both formats: {userid, email} and just ID
                  if (typeof collab === 'object' && collab.userid) {
                    return parseInt(collab.userid);
                  }
                  return parseInt(collab);
                });
              }
              
              console.log(`Subtask ${index + 1} collaborators:`, subtaskCollaboratorIds);

              // Prepare subtask data
              const subtaskData = {
                owner_id: this.newTask.owner_id,
                task_name: subtask.task_name,
                description: subtask.description || '',
                due_date: subtask.due_date,
                priority: subtask.priority.toString(),
                status: subtask.status || 'Ongoing',
                project_id: this.newTask.project_id || null,
                parent_task: createdParentTask.id, // Link to parent
                // Use subtask's own collaborators, not parent's
                collaborators: subtaskCollaboratorIds.length > 0 ? subtaskCollaboratorIds.join(',') : ''
              };

              console.log(`Creating subtask ${index + 1}/${this.newTask.subtasks.length}:`, subtaskData);

              const subtaskRes = await fetch(subtaskEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subtaskData)
              });

              const subtaskResult = await subtaskRes.json();
              
              if (subtaskRes.ok && subtaskResult.Code === 201) {
                createdSubtasks.push(subtaskResult.data);
                console.log(`Subtask ${index + 1} created successfully`);
              } else {
                console.error(`Failed to create subtask ${index + 1}:`, subtaskResult.Message);
              }
            } catch (error) {
              console.error(`Error creating subtask ${index + 1}:`, error);
            }
          }

          console.log(`Created ${createdSubtasks.length}/${this.newTask.subtasks.length} subtasks`);
        }

        // Attach subtasks to parent task for emit
        createdParentTask.subtasks = createdSubtasks;

        // ===== Success =====
        this.successMessage = "Task created successfully!";
        this.$emit("task-created", createdParentTask);

        setTimeout(() => {
          this.successMessage = "";
          this.resetForm();
          this.closePopup();
        }, 1500);
        
      } catch (err) {
        console.error("Error creating task:", err);
        this.errorMessage = err.message || "Failed to create task";
      } finally {
        this.isLoading = false;
      }
    },

    resetForm() {
      const defaultStatus = (this.userRole === 'manager' || this.userRole === 'director') ? 'Unassigned' : 'Ongoing';
      this.newTask = {
        owner_id: this.userId,
        task_name: "",
        description: "",
        type: "parent",
        status: defaultStatus,
        due_date: "",
        priority: 5,
        project_id: "",
        collaborators: "",
        parent_task: "",
        subtasks: [], 
        recurrence_type: null, 
        recurrence_end_date: null
      };
      this.selectedCollaborators = [];
      this.newAttachmentFile = null;
      this.collaboratorQuery = '';
      this.collaboratorSuggestions = [];
    },
    closePopup() {
      this.resetForm();
      this.$emit("close");
    },
    handleOverlayClick() {
      if (!this.isLoading) this.closePopup();
    }
  }
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

.form-input,
.form-select,
textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #111827;
  background-color: white;
  transition: border-color 0.15s ease-in-out;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.form-input:focus,
.form-select:focus,
textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
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

.file-input {
  padding: 0.5rem;
  border: 2px dashed #d1d5db;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
}

.file-input:hover {
  border-color: #9ca3af;
}

.file-hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
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

.success-popup {
  position: fixed;
  top: 2rem;
  right: 2rem;
  background: #d1fae5;
  color: #059669;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1),
              0 4px 6px -2px rgba(0, 0, 0, 0.05);
  z-index: 1001;
  font-weight: 600;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  animation: slideInRight 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.2);
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

input.input-error,
textarea.input-error {
  background-color: #ffe5e5 !important;
  border: 1px solid #ff4d4d !important;
}

input.input-error:focus,
textarea.input-error:focus {
  outline: none;
  border-color: #ff0000 !important;
  box-shadow: 0 0 4px rgba(255, 0, 0, 0.3);
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
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

.mt-4 {
  margin-top: 1.5rem;
}

.selected-email.locked {
  background-color: #f3f4f6;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.selected-email.locked i {
  color: #6b7280;
  cursor: not-allowed;
}

.selected-email i {
  cursor: pointer;
  font-weight: bold;
}

.selected-email i:hover:not(.locked i) {
  color: #1e3a8a;
}
</style>