<template>
  <div class="container" style="min-height:100vh; display:flex; flex-direction:column; padding:2rem;">
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Login</h1>
          <p class="page-subtitle">Access your workspace</p>
        </div>
      </div>

      <div class="main-content">
        <div class="tasks-container" style="max-width: 640px;">
          <div class="task-card">
            <div class="task-main" style="cursor: default; border-bottom: 1px solid #f3f4f6;">
              <div class="task-content" style="width: 100%">
                <div v-if="verified" class="message success" style="margin-bottom: 0.75rem;">
                  Your account has been verified. Please log in.
                </div>
                <form @submit.prevent="onLogin" style="display: grid; gap: 1rem;">
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Email</label>
                    <input v-model="email" type="email" required placeholder="Enter your email" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;"/>
                  </div>
                  <div>
                    <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Password</label>
                    <input v-model="password" :type="show ? 'text' : 'password'" required placeholder="Enter your password" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;"/>
                  </div>
                  <div class="checkbox-wrapper" style="display:flex; align-items:center; gap:0.5rem;">
                    <input type="checkbox" id="show-password" v-model="show" />
                    <label for="show-password" style="color:#6b7280;">Show password</label>
                  </div>
                  <div style="display:flex; gap:0.5rem;">
                    <button type="submit" :disabled="loading">{{ loading ? 'Logging in...' : 'Login' }}</button>
                    <button class="secondary-button" type="button" @click="router.push({ name: 'Register' })">Create new account</button>
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
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { login } from "../../services/auth.js";
import './account.css'

const router = useRouter();
const route = useRoute();
const email = ref("");
const password = ref("");
const show = ref(false);
const message = ref("");
const error = ref(false);
const verified = ref(false);
const loading = ref(false);

onMounted(() => {
  // Show verification success message if coming from email verification
  verified.value = route.query.verified === 'true';
  
  // Pre-fill email if provided (from verification)
  if (route.query.email) {
    email.value = route.query.email;
  }
});

async function onLogin() {
  try {
    message.value = "";
    error.value = false;
    loading.value = true;
    
    const { data, error: err } = await login(email.value, password.value);
    if (err) {
      throw err;
    }

    //Angela edited code to get the database user id and role
    // Check if we have user data
    if (data && data.user) {
      // Import supabase
      const { supabase } = await import("../../services/supabase");
      
      // Query the user table for the actual userid and role
      const { data: userData, error: userError } = await supabase
        .from('user')
        .select('userid, role, name')
        .eq('id', data.user.id)
        .single();

      if (userError) {
        if (userError.code === 'PGRST116') {
          throw new Error('User profile not found. Please contact administrator to set up your account.');
        } else {
          throw new Error('Database error: ' + userError.message);
        }
      }

      if (!userData || !userData.userid) {
        throw new Error('User profile data is incomplete. Please contact administrator.');
      }

      // Store the actual database values
      localStorage.setItem('userId', userData.userid.toString());
      localStorage.setItem('userRole', userData.role || 'staff');
    } else {
      throw new Error('No user data received from login');
    }

    //Angela end of edited code

    message.value = "Login successful!";
    
    // Wait for success message
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Redirect to landing page
    await router.push({ name: "Landing" });
    
  } catch (err) {
    message.value = err.message || 'Login failed';
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>
