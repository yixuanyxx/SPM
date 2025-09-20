import { reactive, ref } from "vue"

// Today's date
export const today = new Date().toISOString().split("T")[0]

// Reactive task
export const task = reactive({
  id: 1,
  title: "Complete project proposal",
  steps: ["Draft initial proposal"],
  status: "ongoing",
  dueDate: today,
  subtasks: [
    { id: 1, title: "Research requirements", status: "pending" },
    { id: 2, title: "Draft outline", status: "in-progress" }
  ]
})

// Error message
export const dateError = ref("")

// Steps
export const addStep = (index) => {
  if (task.steps[index].trim() !== "") task.steps.splice(index + 1, 0, "")
}
export const removeStep = (index) => task.steps.splice(index, 1)

// Subtasks
export const addSubtask = () => {
  task.subtasks.push({
    id: Date.now(),
    title: "",
    status: "pending"
  })
}
export const removeSubtask = (index) => task.subtasks.splice(index, 1)

// Task Save
export const saveTask = () => {
  if (new Date(task.dueDate) < new Date(today)) {
    dateError.value = "Due date must be today or a future date."
    return
  }
  dateError.value = ""
  alert("Task updated successfully!")
  console.log("Task updated:", task)
}

// Cancel
export const cancelEditTask = () => {
  return window.confirm(
    "Are you sure you want to cancel? You can come back later and your edits will be preserved."
  )
}
