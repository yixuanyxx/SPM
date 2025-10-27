<template>
  <teleport to="body">
    <div v-if="isVisible" class="modal-overlay" @click="emitClose">
      <div class="modal-content" @click.stop>
        <h2>Create New Project</h2>

        <label>Project Name* </label>
        <input v-model="form.proj_name" placeholder="Enter project name" :class="{ 'input-error': form.proj_name.trim() === '' }" required />

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
                  :key="user.id" 
                  class="selected-email"
                >
                  {{ user.email }} <i class="bi bi-x" @click="removeCollaborator(user)"></i>
                </span>
              </div>
            </div>
          </div>

        <div class="modal-actions">
          <button @click="submit" :disabled="!isFormValid" :class="{ 'btn-disabled': !isFormValid }">
            Create
          </button>
          <button @click="emitClose">Cancel</button>
        </div>

        <div v-if="error" class="error-popup">
          <p>{{ error }}</p>
          <button @click="error = ''" class="btn-close">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  isVisible: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'project-created'])

const emitClose = () => emit('close')

const form = ref({
  proj_name: ''
})

const collaboratorQuery = ref('')
const selectedCollaborators = ref([])
const collaboratorSuggestions = ref([])

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

const error = ref('')

const isFormValid = computed(() => form.value.proj_name.trim() !== '')

// Fetch collaborator suggestions by email (like CreateNewTask)
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

const submit = async () => {
  if (!isFormValid.value) return
  try {
    const owner_id = localStorage.getItem('spm_userid')
    const collaboratorIds = selectedCollaborators.value
      .map(user => parseInt(user.userid || user.id))
      .filter(id => !isNaN(id))
    const payload = {
      owner_id,
      proj_name: form.value.proj_name,
      collaborators: collaboratorIds,
      tasks: []
    }

    const response = await fetch('http://localhost:5001/projects/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (response.ok && (data.status === 201 || data.Code === 201)) {
      emit('project-created', data.data)
      form.value = { proj_name: '', collaborators: '' }
      emitClose()
    } else {
      error.value = data.error || data.message || data.Message || 'Failed to create project'
    }
  } catch (e) {
    error.value = 'Error creating project. Please try again.'
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 100%;
  max-width: 560px;
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}

.input-error {
  border: 1px solid #ef4444;
}

.btn-disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-popup {
  margin-top: 0.75rem;
  background: #fee2e2;
  color: #991b1b;
  padding: 0.75rem;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close {
  background: transparent;
  border: none;
  cursor: pointer;
}
</style>


