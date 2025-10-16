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
            <div class="priority-slider-wrapper">
              <input
                id="priority"
                type="range"
                min="1"
                max="10"
                v-model="editedTask.priority"
                :disabled="isLoading"
                class="priority-slider"
              />
              <div class="priority-range-labels">
                <span>1 - Least Important</span>
                <span>10 - Most Important</span>
              </div>
            </div>
          </div>

          <!-- Project Selection -->
          <div class="form-group">
            <label for="project">Project</label>
            <select
              id="project"
              v-model="editedTask.project_id"
              :disabled="isLoading"
              class="form-select"
            >
              <option :value="null">No Project</option>
              <option
                v-for="proj in projects"
                :key="proj.id || proj.project_id"
                :value="proj.id || proj.project_id"
              >
                {{ proj.proj_name }}
              </option>
            </select>
          </div>

          <!-- Collaborators Section -->
          <div class="form-group">
            <label>Collaborators</label>
            <div class="collaborator-management">
              <!-- Add Collaborator Input -->
              <div class="add-collaborator">
                <input 
                  type="text"
                  v-model="collaboratorQuery"
                  placeholder="Search by email to add collaborators..."
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
                    <div class="user-info">
                      <span class="user-name">{{ user.name }}</span>
                      <span class="user-email">{{ user.email }}</span>
                      <span class="user-role">{{ user.role }}</span>
                    </div>
                  </li>
                </ul>
              </div>

              <!-- Current Collaborators -->
              <div class="current-collaborators">
                <div v-if="selectedCollaborators.length === 0" class="no-collaborators">
                  No collaborators assigned
                </div>
                <div
                  v-for="collaborator in selectedCollaborators"
                  :key="collaborator.id"
                  class="collaborator-item"
                >
                  <div class="collaborator-info">
                    <span class="collaborator-name">{{ collaborator.name }}</span>
                    <span class="collaborator-email">{{ collaborator.email }}</span>
                    <span class="role-badge" :class="collaborator.role">{{ collaborator.role }}</span>
                    <span v-if="collaborator.userid == editedTask.owner_id" class="owner-badge">Owner</span>
                  </div>
                  <button
                    v-if="collaborator.userid != editedTask.owner_id"
                    type="button"
                    @click="removeCollaborator(collaborator)"
                    class="remove-btn"
                    :disabled="isLoading"
                  >
                    <i class="bi bi-x"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Attachments Section -->
          <div class="form-group">
            <label>Attachments</label>
            <div class="attachment-section">
              <!-- Current Attachments -->
              <div v-if="currentAttachments.length > 0" class="current-attachments">
                <div
                  v-for="(attachment, index) in currentAttachments"
                  :key="index"
                  class="attachment-item"
                >
                  <div class="attachment-info">
                    <i class="bi bi-file-earmark-pdf"></i>
                    <span class="attachment-name">{{ attachment.name || `Attachment ${index + 1}` }}</span>
                  </div>
                  <div class="attachment-actions">
                    <a 
                      :href="attachment.url" 
                      target="_blank" 
                      class="view-btn"
                      title="View PDF"
                    >
                      <i class="bi bi-eye"></i>
                    </a>
                    <button
                      type="button"
                      @click="removeAttachment(index)"
                      class="remove-btn"
                      :disabled="isLoading"
                      title="Remove attachment"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Add New Attachment -->
              <div class="add-attachment">
                <input 
                  type="file" 
                  @change="handleFileUpload" 
                  accept="application/pdf" 
                  class="file-input"
                  :disabled="isLoading"
                />
                <span class="file-hint">Only PDF files are allowed</span>
              </div>
            </div>
          </div>

          <!-- Task Type Information -->
          <div v-if="isSubtask" class="info-box">
            <i class="bi bi-info-circle"></i>
            <span>This is a subtask of "{{ parentTaskTitle }}". Adding collaborators here will also add them to the parent task.</span>
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
import { enhancedNotificationService } from '../services/notifications'

export default {
  name: "TaskEditPopup",
  emits: ['close', 'update-success'],
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
        owner_id: null,
        project_id: null,
        collaborators: [],
        attachments: [],
      },
      originalTask: null,
      selectedCollaborators: [],
      currentAttachments: [],
      newAttachmentFile: null,
      projects: [],
      collaboratorQuery: '',
      collaboratorSuggestions: [],
      isLoading: false,
      successMessage: "",
      errorMessage: "",
      showUnsavedDialog: false,
      pendingClose: false,
    };
  },
  computed: {
    isFormValid() {
      return (
        this.editedTask.task_name?.trim() &&
        this.editedTask.status
      );
    },
    hasChanges() {
      const current = {
        ...this.editedTask,
        collaborators: this.selectedCollaborators.map(c => c.userid),
        attachments: this.currentAttachments
      };
      const original = {
        ...this.originalTask,
        collaborators: this.originalTask?.collaborators || [],
        attachments: this.originalTask?.attachments || []
      };
      
      // Also check if there's a new file to upload
      const hasNewFile = this.newAttachmentFile !== null;
      
      return JSON.stringify(current) !== JSON.stringify(original) || hasNewFile;
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
          this.fetchUserProjects();
        }
      },
      immediate: true
    },
    collaboratorQuery: {
      handler(query) {
        this.fetchCollaboratorSuggestions(query);
      },
      immediate: false
    }
  },
  methods: {
    getCurrentDate() {
      const today = new Date();
      const year = today.getFullYear();
      const month = String(today.getMonth() + 1).padStart(2, '0');
      const day = String(today.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
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
          owner_id: task.owner_id || this.currentOwner,
          project_id: task.project_id || null,
          collaborators: Array.isArray(task.collaborators) 
            ? task.collaborators.map(c => parseInt(c))
            : [],
          attachments: task.attachments || [],
        };

        // Load current attachments
        this.currentAttachments = Array.isArray(task.attachments) ? [...task.attachments] : [];
        console.log('Loaded attachments:', this.currentAttachments);

        // Fetch collaborator details
        await this.fetchCollaboratorDetails();

        this.originalTask = JSON.parse(JSON.stringify({
          ...this.editedTask,
          collaborators: this.selectedCollaborators.map(c => c.userid),
          attachments: [...this.currentAttachments]
        }));
      } catch (err) {
        console.error("Error fetching task details:", err);
        this.errorMessage = "Failed to load task details. Please try again.";
      } finally {
        this.isLoading = false;
      }
    },

    async fetchUserProjects() {
      try {
        const currentUserId = localStorage.getItem('spm_userid');
        if (!currentUserId) return;

        const resp = await fetch(`http://127.0.0.1:5001/projects/user/${currentUserId}`);
        if (!resp.ok) return;

        const data = await resp.json();
        // projects may be in data.data or data.projects or raw array
        const list = data.data || data.projects || data || [];
        this.projects = Array.isArray(list) ? list : [];
      } catch (err) {
        console.error('Failed to fetch user projects:', err);
        this.projects = [];
      }
    },

    async fetchCollaboratorDetails() {
      if (!this.editedTask.collaborators || this.editedTask.collaborators.length === 0) {
        this.selectedCollaborators = [];
        return;
      }

      try {
        const collaboratorPromises = this.editedTask.collaborators.map(async (userId) => {
          const response = await fetch(`http://localhost:5003/users/${userId}`);
          if (response.ok) {
            const data = await response.json();
            return data.data;
          }
          return null;
        });

        const collaborators = await Promise.all(collaboratorPromises);
        this.selectedCollaborators = collaborators.filter(c => c !== null);
      } catch (error) {
        console.error('Error fetching collaborator details:', error);
      }
    },

    async fetchCollaboratorSuggestions(query) {
      if (!query || query.length < 2) {
        this.collaboratorSuggestions = [];
        return;
      }

      try {
        const response = await fetch(`http://localhost:5003/users/search?email=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Failed to fetch user suggestions');
        
        const data = await response.json();
        const allUsers = data.data || [];
        
        // Filter out already selected collaborators
        const selectedIds = this.selectedCollaborators.map(c => c.userid);
        this.collaboratorSuggestions = allUsers.filter(user => 
          !selectedIds.includes(user.userid)
        ).slice(0, 10); // Limit to 10 suggestions
      } catch (error) {
        console.error('Error fetching collaborator suggestions:', error);
        this.collaboratorSuggestions = [];
      }
    },

    addCollaborator(user) {
      if (!this.selectedCollaborators.find(c => c.userid === user.userid)) {
        this.selectedCollaborators.push(user);
      }
      this.collaboratorQuery = '';
      this.collaboratorSuggestions = [];
    },

    removeCollaborator(user) {
      this.selectedCollaborators = this.selectedCollaborators.filter(c => c.userid !== user.userid);
    },

    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file && file.type === "application/pdf") {
        this.newAttachmentFile = file;
      } else {
        alert("Only PDF files are allowed");
        event.target.value = null;
        this.newAttachmentFile = null;
      }
    },

    removeAttachment(index) {
      console.log('Removing attachment at index:', index);
      console.log('Before removal:', this.currentAttachments);
      this.currentAttachments.splice(index, 1);
      console.log('After removal:', this.currentAttachments);
    },

    async handleUpdate() {
      if (!this.isFormValid) return;
      
      this.clearMessages();
      this.isLoading = true;

      try {
        // Prepare collaborator IDs
        const collaboratorIds = this.selectedCollaborators.map(c => c.userid);

        // Use FormData for file uploads
        const formData = new FormData();
        
        // Add basic task fields
        formData.append('task_id', this.taskId);
        formData.append('task_name', this.editedTask.task_name);
        formData.append('description', this.editedTask.description);
        formData.append('status', this.editedTask.status);
        formData.append('due_date', this.editedTask.due_date);
        formData.append('priority', this.editedTask.priority);
        // Include project association
        if (this.editedTask.project_id) {
          formData.append('project_id', this.editedTask.project_id);
        }
        
        // Add collaborators
        if (collaboratorIds.length > 0) {
          formData.append('collaborators', collaboratorIds.join(','));
        }

        // Add current attachments as JSON (this will replace all attachments)
        formData.append('attachments', JSON.stringify(this.currentAttachments));

        // Add new attachment file if exists (this will be merged with existing)
        if (this.newAttachmentFile) {
          formData.append('attachment', this.newAttachmentFile);
        }

        console.log('EditPopup sending update for task:', this.taskId);
        console.log('Current attachments being sent:', this.currentAttachments);
        console.log('New attachment file:', this.newAttachmentFile ? this.newAttachmentFile.name : 'None');

        const response = await fetch("http://localhost:5002/tasks/update", {
          method: "PUT",
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.Message || `HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('EditPopup received:', result);

        // Update current attachments with the result from backend
        if (result.data && result.data.attachments) {
          this.currentAttachments = result.data.attachments;
        }

        // Clear the new attachment file since it's now been uploaded
        this.newAttachmentFile = null;
        // Clear the file input
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
          fileInput.value = '';
        }

        // If this is a subtask, sync collaborators with parent task
        if (this.isSubtask && this.parentTaskId) {
          await this.syncParentTaskCollaborators(collaboratorIds);
        }
        
        // If this task is attached to a project, sync collaborators with project
        if (this.editedTask.project_id) {
          await this.syncProjectCollaborators(collaboratorIds);
        }
        
        // Trigger notifications for task updates
        await this.triggerTaskUpdateNotifications();
        
        // Update the original task data
        this.originalTask = JSON.parse(JSON.stringify({
          ...this.editedTask,
          collaborators: collaboratorIds,
          attachments: this.currentAttachments
        }));
        
        this.isLoading = false;
        
        // Close the popup
        this.$emit("close");
        
        // Show success message and emit update
        setTimeout(() => {
          this.successMessage = "Task updated successfully!";
          
          this.$emit("update-success", {
            task_name: this.editedTask.task_name,
            description: this.editedTask.description,
            status: this.editedTask.status,
            due_date: this.editedTask.due_date,
            priority: this.editedTask.priority,
            collaborators: collaboratorIds,
            attachments: this.currentAttachments,
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

    async syncParentTaskCollaborators(subtaskCollaboratorIds) {
      try {
        // Get current parent task details
        const parentResponse = await fetch(`http://localhost:5002/tasks/${this.parentTaskId}`);
        if (!parentResponse.ok) return;
        
        const parentData = await parentResponse.json();
        const parentTask = parentData.task || parentData;
        
        // Merge parent collaborators with subtask collaborators
        const parentCollaborators = Array.isArray(parentTask.collaborators) 
          ? parentTask.collaborators.map(c => parseInt(c))
          : [];
        
        const mergedCollaborators = [...new Set([...parentCollaborators, ...subtaskCollaboratorIds])];
        
        // Update parent task if there are new collaborators
        if (mergedCollaborators.length > parentCollaborators.length) {
          const updateData = {
            task_id: this.parentTaskId,
            collaborators: mergedCollaborators.join(',')
          };

          await fetch("http://localhost:5002/tasks/update", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updateData),
          });
          
          console.log('Parent task collaborators synced successfully');
        }
      } catch (error) {
        console.error('Error syncing parent task collaborators:', error);
        // Don't throw error to avoid breaking the main update flow
      }
    },

    async syncProjectCollaborators(taskCollaboratorIds) {
      try {
        // Only sync if task is attached to a project
        if (!this.editedTask.project_id) return;

        // Get current project details
        const projectResponse = await fetch(`http://127.0.0.1:5001/projects/${this.editedTask.project_id}`);
        if (!projectResponse.ok) return;
        
        const projectData = await projectResponse.json();
        const project = projectData.data || projectData;
        
        // Merge project collaborators with task collaborators
        const projectCollaborators = Array.isArray(project.collaborators) 
          ? project.collaborators.map(c => parseInt(c))
          : [];
        
        const mergedCollaborators = [...new Set([...projectCollaborators, ...taskCollaboratorIds])];
        
        // Update project if there are new collaborators
        if (mergedCollaborators.length > projectCollaborators.length) {
          const updateData = {
            project_id: this.editedTask.project_id,
            collaborators: mergedCollaborators
          };

          await fetch("http://127.0.0.1:5001/projects/update", {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updateData),
          });
          
          console.log('Project collaborators synced successfully');
        }
      } catch (error) {
        console.error('Error syncing project collaborators:', error);
        // Don't throw error to avoid breaking the main update flow
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
        this.collaboratorQuery = '';
        this.collaboratorSuggestions = [];
        this.newAttachmentFile = null;
        // Clear the file input
        const fileInput = document.querySelector('input[type="file"]');
        if (fileInput) {
          fileInput.value = '';
        }
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

    async triggerTaskUpdateNotifications() {
      try {
        // Get current user info
        const currentUserId = localStorage.getItem('spm_userid');
        const currentUserName = localStorage.getItem('spm_username') || 'System';
        
        if (!currentUserId || !this.originalTask) return;

        // Get collaborators to notify (exclude current user)
        const collaboratorsToNotify = this.selectedCollaborators
          .map(c => c.userid)
          .filter(collaboratorId => String(collaboratorId) !== String(currentUserId));

        if (collaboratorsToNotify.length === 0) return;

        // Collect all changes for consolidated notification
        const changes = [];

        // Status change
        if (this.originalTask.status !== this.editedTask.status) {
          changes.push({
            field: 'status',
            old_value: this.originalTask.status,
            new_value: this.editedTask.status,
            field_name: 'Status'
          });
        }

        // Due date change
        if (this.originalTask.due_date !== this.editedTask.due_date) {
          const oldDate = this.originalTask.due_date || 'No due date';
          const newDate = this.editedTask.due_date || 'No due date';
          changes.push({
            field: 'due_date',
            old_value: oldDate,
            new_value: newDate,
            field_name: 'Due Date'
          });
        }

        // Description change
        if (this.originalTask.description !== this.editedTask.description) {
          changes.push({
            field: 'description',
            old_value: this.originalTask.description || 'No description',
            new_value: this.editedTask.description || 'No description',
            field_name: 'Description'
          });
        }

        // Priority change (if priority field exists)
        if (this.originalTask.priority !== this.editedTask.priority) {
          changes.push({
            field: 'priority',
            old_value: this.originalTask.priority || 'Not set',
            new_value: this.editedTask.priority || 'Not set',
            field_name: 'Priority'
          });
        }

        // Task name change (if task_name field exists)
        if (this.originalTask.task_name !== this.editedTask.task_name) {
          changes.push({
            field: 'task_name',
            old_value: this.originalTask.task_name || 'No title',
            new_value: this.editedTask.task_name || 'No title',
            field_name: 'Task Title'
          });
        }

        // Send consolidated notification if there are changes
        if (changes.length > 0) {
          await enhancedNotificationService.triggerConsolidatedTaskUpdateNotification(
            this.taskId,
            collaboratorsToNotify,
            changes,
            currentUserName
          );
        }

        // Handle collaborator changes separately (assignment notifications)
        const originalCollaborators = this.originalTask.collaborators || [];
        const newCollaborators = this.editedTask.collaborators || [];
        
        // Find newly added collaborators
        const addedCollaborators = newCollaborators.filter(
          collabId => !originalCollaborators.includes(collabId)
        );
        
        // Send notifications to newly added collaborators
        if (addedCollaborators.length > 0) {
          const addPromises = addedCollaborators.map(collaboratorId =>
            enhancedNotificationService.triggerTaskAssignmentNotification(
              this.taskId,
              collaboratorId,
              currentUserName
            )
          );
          await Promise.all(addPromises);
        }

        console.log('Consolidated task update notifications sent successfully');

      } catch (error) {
        console.error('Failed to send task update notifications:', error);
        // Don't throw error to avoid breaking the main update flow
      }
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

/* Collaborator Management Styles */
.collaborator-management {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  background-color: #f9fafb;
}

.add-collaborator {
  position: relative;
  margin-bottom: 1rem;
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
  margin: 0;
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

.user-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.user-name {
  font-weight: 500;
  color: #111827;
}

.user-email {
  font-size: 0.875rem;
  color: #6b7280;
}

.user-role {
  font-size: 0.75rem;
  color: #9ca3af;
  text-transform: capitalize;
}

.current-collaborators {
  min-height: 100px;
  max-height: 200px;
  overflow-y: auto;
}

.no-collaborators {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 2rem;
}

.collaborator-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  border-radius: 6px;
  background-color: white;
  border: 1px solid #e5e7eb;
  margin-bottom: 0.5rem;
}

.collaborator-item:last-child {
  margin-bottom: 0;
}

.collaborator-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.collaborator-name {
  font-weight: 500;
  color: #111827;
}

.collaborator-email {
  font-size: 0.875rem;
  color: #6b7280;
}

.remove-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-btn:hover {
  background-color: #fee2e2;
  color: #dc2626;
}

.remove-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Attachment Management Styles */
.attachment-section {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  background-color: #f9fafb;
}

.current-attachments {
  margin-bottom: 1rem;
}

.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.attachment-item:last-child {
  margin-bottom: 0;
}

.attachment-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.attachment-info i {
  color: #ef4444;
  font-size: 1.25rem;
}

.attachment-name {
  font-weight: 500;
  color: #111827;
}

.attachment-actions {
  display: flex;
  gap: 0.5rem;
}

.view-btn {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-btn:hover {
  background-color: #dbeafe;
  color: #2563eb;
}

.add-attachment {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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
  font-size: 0.875rem;
  color: #6b7280;
  font-style: italic;
}

/* Updated Role Badge Styles */
.role-badge.director {
  background-color: #fef3c7;
  color: #d97706;
}

/* Enhanced Info Box for Subtasks */
.info-box {
  margin-top: 1rem;
  padding: 1rem;
  background: linear-gradient(145deg, #dbeafe 0%, #bfdbfe 100%);
  border: 1px solid #93c5fd;
  border-radius: 8px;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  color: #1e40af;
  font-size: 0.875rem;
  line-height: 1.5;
}

.info-box i {
  color: #3b82f6;
  font-size: 1rem;
  margin-top: 0.125rem;
  flex-shrink: 0;
}
</style>