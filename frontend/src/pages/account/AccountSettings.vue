<template>
  <div class="app-layout ms-2">
    <SideNavbar />

    <div class="app-container">
      <div class="header-section">
        <div class="header-content">
          <h1 class="page-title">Account Settings</h1>
          <p class="page-subtitle">Update your profile details</p>
        </div>
      </div>

      <div class="main-content">
        <div class="tasks-container" style="max-width: 720px;">
          <div class="task-card">
            <div class="task-main" style="cursor: default; border-bottom: 1px solid #f3f4f6;">
              <div class="task-content" style="width: 100%">
                <div style="display:grid; gap:1rem;">
                  <!-- User ID (readonly) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">User ID</label>
                      <div>{{ userid ?? '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Name (editable) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Name</label>
                      <div v-if="!isEditingName">{{ name || '-' }}</div>
                      <input v-else v-model="nameDraft" type="text" placeholder="Enter your name" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                    </div>
                    <div style="display:flex; gap:0.5rem; margin-top: 1.35rem">
                      <button v-if="!isEditingName" class="secondary-button" type="button" @click="startEditName">Edit</button>
                      <template v-else>
                        <button class="secondary-button" type="button" @click="cancelEditName">Cancel</button>
                        <button type="button" @click="saveName" :disabled="loading">{{ loading ? 'Saving...' : 'Save' }}</button>
                      </template>
                    </div>
                  </div>

                  <!-- Email (readonly) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Email</label>
                      <div>{{ email || '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Role (readonly) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Role</label>
                      <div style="text-transform: capitalize;">{{ role || '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Team ID (readonly) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Team ID</label>
                      <div>{{ team_id ?? '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Dept ID (readonly) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Department ID</label>
                      <div>{{ dept_id ?? '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Password (editable: change only) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Password</label>
                      <div v-if="!isEditingPassword" style="display:flex; align-items:center; gap:0.5rem;">
                        <span>{{ showCurrentPassword ? '••••••••' : '••••••••' }}</span>
                      </div>
                      <div v-else style="display:grid; gap:0.75rem;">
                        <input v-model="newPassword" :type="show ? 'text' : 'password'" placeholder="Enter new password" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                        <input v-model="confirmPassword" :type="show ? 'text' : 'password'" placeholder="Confirm new password" style="width:100%; padding:0.6rem 0.75rem; border:1px solid #e5e7eb; border-radius:8px;" />
                        <div class="checkbox-wrapper" style="display:flex; align-items:center; gap:0.5rem;">
                          <input type="checkbox" id="show-password" v-model="show" />
                          <label for="show-password" style="color:#6b7280;">Show password</label>
                        </div>
                      </div>
                    </div>
                    <div style="display:flex; gap:0.5rem; margin-top: 1.35rem">
                      <button v-if="!isEditingPassword" class="secondary-button" type="button" @click="startEditPassword">Change</button>
                      <template v-else style="display:flex; ">
                        <div style="display:flex; gap:0.5rem; margin-top: 1.35rem">
                          <button class="secondary-button" type="button" @click="cancelEditPassword">Cancel</button>
                          <button type="button" @click="savePassword" :disabled="loading">{{ loading ? 'Updating...' : 'Update' }}</button>
                        </div>
                        </template>
                    </div>
                  </div>

                  <!-- Actions -->
                  <div style="display:flex; gap:0.5rem;">
                    <button type="button" class="secondary-button" @click="onFetch" :disabled="loading">Reload</button>
                  </div>
                  <p v-if="message" :class="['message', error ? 'error' : 'success']" style="margin-top: 0.25rem;">{{ message }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import SideNavbar from '../../components/SideNavbar.vue'
import './account.css'
import { supabase } from "../../services/supabase";

const API = 'http://127.0.0.1:5003';

const userid = ref(null);
const name = ref("");
const email = ref("");
const role = ref("");
const team_id = ref(null);
const dept_id = ref(null);
const nameDraft = ref("");
const isEditingName = ref(false);
const newPassword = ref("");
const confirmPassword = ref("");
const isEditingPassword = ref(false);
const show = ref(false);
const showCurrentPassword = ref(false);
const message = ref("");
const error = ref(false);
const loading = ref(false);

onMounted(async () => {
  const stored = localStorage.getItem('spm_userid');
  if (stored) {
    userid.value = Number(stored);
    await onFetch();
  }
});

async function onFetch() {
  try {
    message.value = "";
    error.value = false;
    if (!userid.value) {
      message.value = 'Please provide a userid to fetch.';
      error.value = true;
      return;
    }
    loading.value = true;
    const res = await fetch(`${API}/users/${userid.value}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const u = data?.data || {};
    name.value = u.name || "";
    email.value = u.email || "";
    role.value = u.role || "";
    team_id.value = u.team_id ?? null;
    dept_id.value = u.dept_id ?? null;
    nameDraft.value = name.value;
    // No success message on initial load
    error.value = false;
  } catch (e) {
    message.value = e.message || 'Failed to fetch user.';
    error.value = true;
  } finally {
    loading.value = false;
  }
}

function startEditName() {
  isEditingName.value = true;
  nameDraft.value = name.value;
}

function cancelEditName() {
  isEditingName.value = false;
  nameDraft.value = name.value;
}

async function saveName() {
  try {
    message.value = '';
    error.value = false;
    if (!userid.value) throw new Error('userid is required');
    loading.value = true;
    const body = { userid: userid.value, name: nameDraft.value };
    const res = await fetch(`${API}/users/${userid.value}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const u = data?.data || {};
    name.value = u.name || nameDraft.value;
    isEditingName.value = false;
    message.value = data?.message || `Name updated.`;
  } catch (e) {
    message.value = e.message || 'Failed to update name.';
    error.value = true;
  } finally {
    loading.value = false;
  }
}

function startEditPassword() {
  isEditingPassword.value = true;
  newPassword.value = '';
  confirmPassword.value = '';
}

function cancelEditPassword() {
  isEditingPassword.value = false;
  newPassword.value = '';
  confirmPassword.value = '';
  show.value = false;
}

async function savePassword() {
  try {
    message.value = '';
    error.value = false;
    if (!newPassword.value) throw new Error('Enter a new password');
    if (newPassword.value !== confirmPassword.value) throw new Error('Passwords do not match');
    loading.value = true;
    const { error: err } = await supabase.auth.updateUser({ password: newPassword.value });
    if (err) throw err;
    isEditingPassword.value = false;
    message.value = 'Password updated!';
  } catch (e) {
    message.value = e.message || 'Failed to update password.';
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>
