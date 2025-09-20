<template>
  <div class="auth-page">
    <h2>Account Settings</h2>
    <form @submit.prevent="onUpdate">
      <label>Name
        <input v-model="name" type="text" placeholder="Enter your name" />
      </label>
      <div class="divider"></div>
      <label>New Password
        <input v-model="newPassword" :type="show ? 'text' : 'password'" placeholder="Enter new password" />
      </label>
      <label>Confirm Password
        <input v-model="confirmPassword" :type="show ? 'text' : 'password'" placeholder="Confirm new password" />
      </label>
      <div class="checkbox-wrapper">
        <input type="checkbox" id="show-password" v-model="show" />
        <label for="show-password">Show password</label>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Updating...' : 'Update Profile' }}
      </button>
    </form>
    <p v-if="message" :class="['message', error ? 'error' : 'success']">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getUser, updateProfile } from "../../services/auth.js";

const name = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const show = ref(false);
const message = ref("");
const error = ref(false);
let currentUserId = null;

onMounted(async () => {
  try {
    const user = await getUser();
    currentUserId = user.id;
    // fetch name from "profiles" table if you store it there
    name.value = user.user_metadata?.name || "";
  } catch (e) {
    message.value = "Failed to load user.";
    error.value = true;
  }
});

async function onUpdate() {
  message.value = "";
  error.value = false;

  // update profile table (for name etc.)
  if (name.value) {
    await updateProfile(currentUserId, { name: name.value });
  }

  // update password (Supabase provides a method)
  if (newPassword.value) {
    if (newPassword.value !== confirmPassword.value) {
      message.value = "Passwords do not match";
      error.value = true;
      return;
    }
    const { error: err } = await supabase.auth.updateUser({ password: newPassword.value });
    if (err) {
      message.value = err.message;
      error.value = true;
      return;
    }
  }

  message.value = "Account updated!";
  error.value = false;
}
</script>
