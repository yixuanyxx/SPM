<template>
  <div class="auth-page">
    <h2>Create New Account</h2>
    <form @submit.prevent="onRegister">
      <label>Email
        <input v-model="email" type="email" required placeholder="Enter your email" />
      </label>
      <label>Role
        <select v-model="role" required class="role-select">
          <option value="" disabled>Select your role</option>
          <option value="staff">Staff</option>
          <option value="manager">Manager/Director</option>
          <option value="hr">HR/Senior Management</option>
        </select>
      </label>
      <label>Password
        <input v-model="password" :type="show ? 'text' : 'password'" required placeholder="Choose a password" />
      </label>
      <label>Confirm Password
        <input v-model="confirmPassword" :type="show ? 'text' : 'password'" required placeholder="Confirm your password" />
      </label>
      <div class="checkbox-wrapper">
        <input type="checkbox" id="show-password" v-model="show" />
        <label for="show-password">Show password</label>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Registering...' : 'Create Account' }}
      </button>
      <p v-if="message" :class="['message', error ? 'error' : 'success']">
        {{ message }}
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { register } from "../../services/auth.js";
import { useRouter } from 'vue-router';
import '../../assets/auth.css';

const router = useRouter();
const email = ref("");
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

    const { data, error: err } = await register(email.value, password.value, role.value);
    if (err) throw err;

    message.value = "Please check your email to verify your account.";
    error.value = false;

    // Clear form
    email.value = "";
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
