<template>
  <div class="container" style="min-height:100vh; display:flex; flex-direction:column; padding:2rem;">
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Reset Password</h1>
          <p class="page-subtitle">Enter your email to receive a password reset link</p>
        </div>
      </div>

      <div class="main-content">
        <div class="tasks-container" style="max-width: 640px;">
          <div class="task-card">
            <div class="task-main" style="cursor: default; border-bottom: 1px solid #f3f4f6;">
              <div class="task-content" style="width: 100%">
                <form @submit.prevent="onResetPassword" style="display: grid; gap: 1rem;">
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Email</label>
                    <input 
                      v-model="email" 
                      type="email" 
                      required 
                      placeholder="Enter your email address" 
                      style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;"
                    />
                  </div>
                  
                  <div style="display:flex; gap:0.5rem;">
                    <button type="submit" :disabled="loading">
                      {{ loading ? 'Sending...' : 'Send Reset Link' }}
                    </button>
                    <button class="secondary-button" type="button" @click="router.push({ name: 'Login' })">
                      Back to Login
                    </button>
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
import { useRouter } from 'vue-router';
import { resetPasswordForEmail } from "../../services/auth.js";
import './account.css'

const router = useRouter();
const email = ref("");
const message = ref("");
const error = ref(false);
const loading = ref(false);

async function onResetPassword() {
  try {
    message.value = "";
    error.value = false;
    loading.value = true;

    if (!email.value) {
      throw new Error("Please enter your email address");
    }

    // Send password reset email with redirect URL
    const redirectTo = `${window.location.origin}/account/update-password`;
    const { error: resetError } = await resetPasswordForEmail(email.value, redirectTo);
    
    if (resetError) throw resetError;

    message.value = "Password reset link sent! Please check your email and follow the instructions.";
    error.value = false;
    
    // Clear email field
    email.value = "";
    
  } catch (err) {
    message.value = err.message || "Failed to send reset email. Please try again.";
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>
