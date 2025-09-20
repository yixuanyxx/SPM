<script setup>
import { useRouter } from 'vue-router'
import { task, today, dateError, addStep, removeStep, addSubtask, removeSubtask, saveTask, cancelEditTask } from './updateTask.js'

const router = useRouter()

const cancelEdit = () => {
  const shouldNavigate = cancelEditTask()
  if (shouldNavigate) router.push('/tasks')
}
</script>

<template>
  <div class="container py-5">
    <h1 class="text-center text-primary fw-bold mb-3">Update Task</h1>
    <form @submit.prevent="saveTask" class="card p-4 shadow-lg rounded-4 mb-4">
      <!-- Title -->
      <div class="mb-3">
        <label class="form-label fw-semibold">Title</label>
        <input v-model="task.title" type="text" class="form-control" required />
      </div>

      <!-- Steps -->
      <div class="mb-3">
        <label class="form-label fw-semibold">Steps</label>
        <div v-for="(step, index) in task.steps" :key="index" class="d-flex mb-2 align-items-center">
          <span class="me-2 text-muted fw-bold">{{ index + 1 }}.</span>
          <input v-model="task.steps[index]" type="text" class="form-control" placeholder="Enter step..." @keydown.enter.prevent="addStep(index)" />
          <button v-if="task.steps.length > 1" type="button" class="btn btn-outline-danger ms-2 btn-sm" @click="removeStep(index)">✕</button>
        </div>
      </div>

      <!-- Status -->
      <div class="mb-3">
        <label class="form-label fw-semibold">Status</label>
        <select v-model="task.status" class="form-select" required>
          <option value="ongoing">In Progress</option>
          <option value="under-review">Review</option>
          <option value="done">Done</option>
        </select>
      </div>

      <!-- Due Date -->
      <div class="mb-3">
        <label class="form-label fw-semibold">Due Date</label>
        <input v-model="task.dueDate" type="date" class="form-control" :min="today" required />
        <div v-if="dateError" class="text-danger mt-1">{{ dateError }}</div>
      </div>

      <!-- Subtasks (inside the same card) -->
      <div class="mb-4">
        <label class="form-label fw-semibold">Subtasks</label>
        <div v-if="task.subtasks.length === 0" class="text-muted mb-2">No subtasks available. Add one below.</div>

        <div v-for="(subtask, index) in task.subtasks" :key="subtask.id" class="input-group mb-2">
          <input v-model="subtask.title" type="text" class="form-control" placeholder="Subtask title" />
          <select v-model="subtask.status" class="form-select">
            <option value="pending">Pending</option>
            <option value="in-progress">In Progress</option>
            <option value="done">Done</option>
          </select>
          <button class="btn btn-outline-danger" type="button" @click="removeSubtask(index)">Remove</button>
        </div>

        <button class="btn btn-outline-success mt-2" type="button" @click="addSubtask">+ Add Subtask</button>
      </div>

      <!-- Actions -->
      <div class="d-flex justify-content-end gap-2">
        <button type="button" class="btn btn-outline-secondary px-4" @click="cancelEdit">Cancel</button>
        <button type="submit" class="btn btn-primary px-4">Save Changes</button>
      </div>
    </form>
  </div>
</template>
