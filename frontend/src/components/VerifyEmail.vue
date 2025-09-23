<template>
  <div class="auth-page">
    <h2>Email Verification</h2>
    <div class="verify-container">
      <div class="verify-icon" :class="error ? 'error' : success ? 'success' : ''">
        <svg v-if="success" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        <svg v-else-if="error" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="animate-spin">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </div>
      <div class="message" :class="{ success, error }">
        {{ message }}
      </div>
      <div v-if="success" class="redirect-message">
        Redirecting to login page...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { verifyEmail, ensureUserRow } from '../services/auth.js';
import { supabase } from '../services/supabase';
import '../assets/auth.css';

const router = useRouter();
const route = useRoute();
const message = ref('Verifying your email...');
const error = ref(false);
const success = ref(false);

onMounted(async () => {
  try {
    // Supabase email confirmation usually arrives with tokens in hash or query
    // Try to parse from hash first: #access_token=...&refresh_token=...&type=...
    let accessToken = route.query.access_token;
    let refreshToken = route.query.refresh_token;
    let email = route.query.email;

    if (!accessToken && window.location.hash) {
      const params = new URLSearchParams(window.location.hash.replace(/^#/, ''));
      accessToken = params.get('access_token');
      refreshToken = params.get('refresh_token');
      email = email || params.get('email');
    }

    if (!accessToken) throw new Error('No verification token found');

    await verifyEmail(accessToken, refreshToken || null);
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      // Upsert into public.users using user_metadata.role populated at signUp
      await ensureUserRow(user);
    }
    success.value = true;
    message.value = 'Your email has been verified successfully!';
    
    // Redirect to login page after 2 seconds
    // Extract email from token or URL if available
    
    setTimeout(() => {
      router.push({
        name: 'Login',
        query: { 
          verified: 'true',
          email: email // Pass email to login page for convenience
        }
      });
    }, 2000);

  } catch (err) {
    message.value = 'Failed to verify email: ' + err.message;
    error.value = true;
  }
});
</script>