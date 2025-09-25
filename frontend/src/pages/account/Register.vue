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
                    <select v-model="role" required class="role-select" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;">
                      <option value="" disabled>Select your role</option>
                      <option value="staff">Staff</option>
                      <option value="manager">Manager/Director</option>
                      <option value="hr">HR/Senior Management</option>
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
import { register } from "../../services/auth.js";
import { useRouter } from 'vue-router';
import './account.css'

const router = useRouter();
const email = ref("");
const name = ref("");
const password = ref("");
const confirmPassword = ref("");
const role = ref("");
const show = ref(false);
const message = ref("");
const error = ref(false);
const loading = ref(false);

async function onRegister() {
  message.value = "";
  error.value = false;
  loading.value = true;

  try {
    if (!role.value) {
      throw new Error("Please select a role");
    }

    if (password.value !== confirmPassword.value) {
      throw new Error("Passwords do not match");
    }

    const { data, error: err } = await register(email.value, password.value, role.value, name.value);
    if (err) throw err;

    message.value = "Please check your email to verify your account.";
    error.value = false;

    // Clear form
    email.value = "";
    name.value = "";
    password.value = "";
    confirmPassword.value = "";
    
  } catch (err) {
    message.value = err.message;
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>

