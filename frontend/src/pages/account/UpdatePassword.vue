<template>
  <div class="container" style="min-height:100vh; display:flex; flex-direction:column; padding:2rem;">
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Update Password</h1>
          <p class="page-subtitle">Enter your new password</p>
        </div>
      </div>

      <div class="main-content">
        <div class="tasks-container" style="max-width: 640px;">
          <div class="task-card">
            <div class="task-main" style="cursor: default; border-bottom: 1px solid #f3f4f6;">
              <div class="task-content" style="width: 100%">
                <form @submit.prevent="onUpdatePassword" style="display: grid; gap: 1rem;">
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">New Password</label>
                    <input 
                      v-model="newPassword" 
                      :type="show ? 'text' : 'password'" 
                      required 
                      placeholder="Enter your new password" 
                      style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;"
                      @input="validatePassword"
                    />
                    <div v-if="passwordValidation.message" :class="['password-validation', passwordValidation.isValid ? 'valid' : 'invalid']" style="font-size: 0.8rem; margin-top: 0.5rem;">
                      {{ passwordValidation.message }}
                    </div>
                  </div>
                  
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Confirm New Password</label>
                    <input 
                      v-model="confirmPassword" 
                      :type="show ? 'text' : 'password'" 
                      required 
                      placeholder="Confirm your new password" 
                      style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;"
                    />
                  </div>
                  
                  <div class="checkbox-wrapper" style="display:flex; align-items:center; gap:0.5rem;">
                    <input type="checkbox" id="show-password" v-model="show" />
                    <label for="show-password" style="color:#6b7280;">Show password</label>
                  </div>
                  
                  <div style="display:flex; gap:0.5rem;">
                    <button type="submit" :disabled="loading || !passwordValidation.isValid">
                      {{ loading ? 'Updating...' : 'Update Password' }}
                    </button>
                    <button class="secondary-button" type="button" @click="router.push({ name: 'Login' })">
                      Cancel
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
import { ref, onMounted, onUnmounted } from "vue";
import { useRouter, useRoute } from 'vue-router';
import { updatePassword, getUser } from "../../services/auth.js";
import { supabase } from "../../services/supabase.js";
import './account.css'

const router = useRouter();
const route = useRoute();
const newPassword = ref("");
const confirmPassword = ref("");
const show = ref(false);
const message = ref("");
const error = ref(false);
const loading = ref(false);
const passwordValidation = ref({ message: "", isValid: false });
let authListener = null;

onMounted(async () => {
  // Check if user is authenticated (should be after clicking reset link)
  try {
    const user = await getUser();
    if (!user) {
      message.value = "Invalid or expired reset link. Please request a new password reset.";
      error.value = true;
      setTimeout(() => {
        router.push({ name: 'ResetPassword' });
      }, 3000);
      return;
    }
  } catch (e) {
    console.error('Authentication check failed:', e);
    message.value = "Invalid or expired reset link. Please request a new password reset.";
    error.value = true;
    setTimeout(() => {
      router.push({ name: 'ResetPassword' });
    }, 3000);
    return;
  }

  // Set up auth state listener to detect USER_UPDATED event
  authListener = supabase.auth.onAuthStateChange((event, session) => {
    console.log('Auth state changed:', event);
    
    if (event === 'USER_UPDATED') {
      console.log('User updated event detected');
      
      // Show success message
      message.value = "Password updated successfully! You can now log in with your new password.";
      error.value = false;
      loading.value = false;
      
      // Clear form
      newPassword.value = "";
      confirmPassword.value = "";
      passwordValidation.value = { message: "", isValid: false };
      show.value = false;
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push({ name: 'Login' });
      }, 3000);
    }
  });
});

onUnmounted(() => {
  // Clean up auth listener
  if (authListener) {
    authListener.data.subscription.unsubscribe();
  }
});

function validatePassword() {
  const password = newPassword.value;
  
  if (!password) {
    passwordValidation.value = { message: "", isValid: false };
    return;
  }
  
  // Check if password is alphanumeric (contains both letters and numbers)
  const hasLetter = /[a-zA-Z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const isAlphanumeric = hasLetter && hasNumber;
  const minLength = password.length >= 8;
  
  if (!minLength) {
    passwordValidation.value = { 
      message: "Password must be at least 8 characters long", 
      isValid: false 
    };
  } else if (!isAlphanumeric) {
    passwordValidation.value = { 
      message: "Password must contain both letters and numbers", 
      isValid: false 
    };
  } else {
    passwordValidation.value = { 
      message: "Password strength: Good", 
      isValid: true 
    };
  }
}

async function onUpdatePassword() {
  try {
    message.value = "";
    error.value = false;
    loading.value = true;

    if (!newPassword.value) {
      throw new Error("Please enter a new password");
    }

    if (!passwordValidation.value.isValid) {
      throw new Error("Please enter a valid password that meets the requirements");
    }

    if (newPassword.value !== confirmPassword.value) {
      throw new Error("Passwords do not match");
    }

    // Update password - the auth state listener will handle success
    const { error: updateError } = await updatePassword(newPassword.value);
    
    if (updateError) {
      throw updateError;
    }

    // Don't set success message here - let the auth state listener handle it
    // The loading state will be cleared by the auth listener when USER_UPDATED fires
    
  } catch (err) {
    message.value = err.message || "Failed to update password. Please try again.";
    error.value = true;
    loading.value = false;
  }
  // Note: Don't set loading.value = false in finally block
  // Let the auth state listener handle it on success
}
</script>
