<script setup>
import './UpdateTask.css'
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

      <!-- Description -->
      <div class="mb-3">
        <label class="form-label fw-semibold">Description</label>
        <div
          v-for="(step, index) in task.steps"
          :key="index"
          class="mb-3"
        >
          <textarea
            v-model="task.steps[index]"
            class="form-control"
            rows="3"
            placeholder="Enter step description..."
            @keydown.enter.prevent="addStep(index)"
          ></textarea>
          <div class="d-flex justify-content-end mt-1">
            <button
              v-if="task.steps.length > 1"
              type="button"
              class="btn btn-outline-danger btn-sm"
              @click="removeStep(index)"
            >
              ✕ Remove
            </button>
          </div>
        </div>
      </div>

      <!-- Description
      <div class="mb-3">
        <label class="form-label fw-semibold">Description</label>
        <div v-for="(step, index) in task.steps" :key="index" class="d-flex mb-2 align-items-center">
          <span class="me-2 text-muted fw-bold">{{ index + 1 }}.</span>
          <input v-model="task.steps[index]" type="text" class="form-control" placeholder="Enter step..." @keydown.enter.prevent="addStep(index)" />
          <button v-if="task.steps.length > 1" type="button" class="btn btn-outline-danger ms-2 btn-sm" @click="removeStep(index)">✕</button>
        </div>
      </div> -->

      <!-- Status -->
      <div class="mb-3 d-flex align-items-center">
        <label class="form-label fw-semibold me-3 mb-0">Status:</label>

        <div class="d-flex gap-2">
          <div
            class="task-status ongoing"
            :class="{ selected: task.status === 'ongoing' }"
            @click="task.status = 'ongoing'"
          >
            <i class="bi bi-play-circle"></i>
            <span>In Progress</span>
          </div>

          <div
            class="task-status under-review"
            :class="{ selected: task.status === 'under-review' }"
            @click="task.status = 'under-review'"
          >
            <i class="bi bi-eye"></i>
            <span>Review</span>
          </div>

          <div
            class="task-status completed"
            :class="{ selected: task.status === 'completed' }"
            @click="task.status = 'completed'"
          >
            <i class="bi bi-check-circle-fill"></i>
            <span>Done</span>
          </div>
        </div>
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
