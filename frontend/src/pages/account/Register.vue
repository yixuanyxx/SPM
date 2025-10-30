<template>
  <div class="container" style="min-height:100vh; display:flex; flex-direction:column; padding:2rem;">
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Create New Account</h1>
          <p class="page-subtitle">Join your team</p>
        </div>
      </div>

      <div class="main-content">
        <div class="tasks-container" style="max-width: 640px;">
          <div class="task-card">
            <div class="task-main" style="cursor: default; border-bottom: 1px solid #f3f4f6;">
              <div class="task-content" style="width: 100%">
                <form @submit.prevent="onRegister" style="display: grid; gap: 1rem;">
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Email</label>
                    <input v-model="email" type="email" required placeholder="Enter your email" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                  </div>
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Name</label>
                    <input v-model="name" type="text" required placeholder="Enter your full name" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                  </div>
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Role</label>
                    <select v-model="role" required class="role-select" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" @change="onRoleChange">
                      <option value="" disabled>Select your role</option>
                      <option value="staff">Staff</option>
                      <option value="manager">Manager</option>
                      <option value="director">Director</option>
                      <option value="managing_director">Managing Director</option>
                    </select>
                  </div>
                  <div v-if="role === 'staff' || role === 'manager'">
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Team</label>
                    <select v-model="team" required style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;">
                      <option value="" disabled>Select your team</option>
                      <option value="Sales Team">Sales Team</option>
                      <option value="Consultant">Consultant</option>
                      <option value="Developers">Developers</option>
                      <option value="Support Team">Support Team</option>
                      <option value="Senior Engineers">Senior Engineers</option>
                      <option value="Junior Engineers">Junior Engineers</option>
                      <option value="Call Centre">Call Centre</option>
                      <option value="Operation Planning Team">Operation Planning Team</option>
                      <option value="HR Team">HR Team</option>
                      <option value="L&D Team">L&D Team</option>
                      <option value="Admin Team">Admin Team</option>
                      <option value="Finance Team">Finance Team</option>
                      <option value="IT Team">IT Team</option>
                    </select>
                  </div>
                  <div v-if="role === 'director'">
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Department</label>
                    <select v-model="department" required style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;">
                      <option value="" disabled>Select your department</option>
                      <option value="Sales">Sales</option>
                      <option value="Consultancy">Consultancy</option>
                      <option value="System Solutioning">System Solutioning</option>
                      <option value="Engineering Operation">Engineering Operation</option>
                      <option value="HR and Admin">HR and Admin</option>
                      <option value="Finance">Finance</option>
                      <option value="IT">IT</option>
                    </select>
                  </div>
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Password</label>
                    <input v-model="password" :type="show ? 'text' : 'password'" required placeholder="Choose a password" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                  </div>
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Confirm Password</label>
                    <input v-model="confirmPassword" :type="show ? 'text' : 'password'" required placeholder="Confirm your password" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                  </div>
                  <div class="checkbox-wrapper" style="display:flex; align-items:center; gap:0.5rem;">
                    <input type="checkbox" id="show-password" v-model="show" />
                    <label for="show-password" style="color:#6b7280;">Show password</label>
                  </div>
                  <div style="display:flex; gap:0.5rem;">
                    <button type="submit" :disabled="loading">{{ loading ? 'Registering...' : 'Create Account' }}</button>
                    <button class="secondary-button" type="button" @click="router.push({ name: 'Login' })">Go to Login</button>
                  </div>
                  <p v-if="message" :class="['message', error ? 'error' : 'success']">{{ message }}</p>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
 </template>

<script setup>
import { ref } from "vue";
import { registerWithMapping } from "../../services/registration.js";
import { useRouter } from 'vue-router';
import './account.css'

const router = useRouter();
const email = ref("");
const name = ref("");
const password = ref("");
const confirmPassword = ref("");
const role = ref("");
const team = ref("");
const department = ref("");
const show = ref(false);
const message = ref("");
const error = ref(false);
const loading = ref(false);

function onRoleChange() {
  // Clear team/department when role changes
  team.value = "";
  department.value = "";
}

async function onRegister() {
  message.value = "";
  error.value = false;
  loading.value = true;

  try {
    if (!role.value) {
      throw new Error("Please select a role");
    }

    // Validate team/department selection based on role
    if ((role.value === 'staff' || role.value === 'manager') && !team.value) {
      throw new Error("Please select a team");
    }
    
    if (role.value === 'director' && !department.value) {
      throw new Error("Please select a department");
    }

    // Validate password strength
    const hasLetter = /[a-zA-Z]/.test(password.value);
    const hasNumber = /[0-9]/.test(password.value);
    const isAlphanumeric = hasLetter && hasNumber;
    const minLength = password.value.length >= 8;
    
    if (!minLength) {
      throw new Error("Password must be at least 8 characters long");
    }
    
    if (!isAlphanumeric) {
      throw new Error("Password must contain both letters and numbers");
    }

    if (password.value !== confirmPassword.value) {
      throw new Error("Passwords do not match");
    }

    // Determine team or department based on role
    const teamName = (role.value === 'staff' || role.value === 'manager') ? team.value : null;
    const departmentName = (role.value === 'director') ? department.value : null;

    const { data, error: err } = await registerWithMapping(
      email.value, 
      password.value, 
      role.value, 
      name.value, 
      teamName, 
      departmentName
    );
    if (err) throw err;

    message.value = "Please check your email to verify your account.";
    error.value = false;

    // Clear form
    email.value = "";
    name.value = "";
    password.value = "";
    confirmPassword.value = "";
    role.value = "";
    team.value = "";
    department.value = "";
    
  } catch (err) {
    message.value = err.message;
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>

