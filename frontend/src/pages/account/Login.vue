<template>
  <div class="auth-page">
    <h2>Login</h2>
    <div v-if="verified" class="message success">
      Your account has been verified. Please log in.
    </div>
    <form @submit.prevent="onLogin">
      <label>Email
        <input v-model="email" type="email" required placeholder="Enter your email"/>
      </label>
      <label>Password
        <input v-model="password" :type="show ? 'text' : 'password'" required placeholder="Enter your password"/>
      </label>
      <div class="checkbox-wrapper">
        <input type="checkbox" id="show-password" v-model="show" />
        <label for="show-password">Show password</label>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
      <p v-if="message" :class="['message', error ? 'error' : 'success']">{{ message }}</p>
    </form>
    <div class="auth-footer">
      <p>Don't have an account?</p>
      <button class="secondary-button" @click="router.push({ name: 'Register' })">
        Create new account
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { login } from "../../services/auth.js";
import '../../assets/auth.css';

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
    if (err) throw err;

    message.value = "Login successful!";
    
    // Wait for a short moment to show success message
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // Redirect to landing page
    await router.push({ name: "Landing" });
    
  } catch (err) {
    message.value = err.message;
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>
