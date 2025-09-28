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

                  <!-- Team (readonly) - Only show for staff and managers -->
                  <div v-if="role === 'staff' || role === 'manager'" style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Team</label>
                      <div>{{ teamName || '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Department (readonly) - Show for all roles -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Department</label>
                      <div>{{ departmentName || '-' }}</div>
                    </div>
                    <div></div>
                  </div>

                  <!-- Password (change via email) -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:center; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.25rem;">Password</label>
                      <div>••••••••</div>
                    </div>
                    <div style="display:flex; gap:0.5rem; margin-top: 1.35rem">
                      <button class="secondary-button" type="button" @click="sendPasswordResetEmail" :disabled="loading">
                        {{ loading ? 'Sending...' : 'Change Password' }}
                      </button>
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
import { resetPasswordForEmail } from "../../services/auth.js";

const API = 'http://127.0.0.1:5003';
const TEAM_API = 'http://127.0.0.1:5004';
const DEPT_API = 'http://127.0.0.1:5005';

const userid = ref(null);
const name = ref("");
const email = ref("");
const role = ref("");
const team_id = ref(null);
const dept_id = ref(null);
const teamName = ref("");
const departmentName = ref("");
const nameDraft = ref("");
const isEditingName = ref(false);
const message = ref("");
const error = ref(false);
const loading = ref(false);

// Helper function to get team name by ID
async function getTeamNameById(teamId) {
  if (!teamId) return '';
  try {
    const res = await fetch(`${TEAM_API}/teams/${teamId}`);
    if (!res.ok) return '';
    const data = await res.json();
    return data?.data?.name || '';
  } catch (e) {
    console.warn('Failed to fetch team name:', e);
    return '';
  }
}

// Helper function to get department name by ID
async function getDepartmentNameById(deptId) {
  if (!deptId) return '';
  try {
    const res = await fetch(`${DEPT_API}/departments/${deptId}`);
    if (!res.ok) return '';
    const data = await res.json();
    return data?.data?.name || '';
  } catch (e) {
    console.warn('Failed to fetch department name:', e);
    return '';
  }
}

onMounted(async () => {
  // Check if user is authenticated
  try {
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      console.warn('User not authenticated, redirecting to login');
      // You might want to redirect to login page here
      message.value = 'Please log in to access account settings';
      error.value = true;
      return;
    }
    console.log('User authenticated:', user.id);
  } catch (e) {
    console.error('Authentication check failed:', e);
  }

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
    
    // Fetch team and department names
    if (team_id.value) {
      teamName.value = await getTeamNameById(team_id.value);
    }
    if (dept_id.value) {
      departmentName.value = await getDepartmentNameById(dept_id.value);
    }
    
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

async function sendPasswordResetEmail() {
  try {
    message.value = '';
    error.value = false;
    loading.value = true;

    // Get user email from the current user data
    if (!email.value) {
      throw new Error('User email not found. Please reload the page.');
    }

    // Send password reset email
    const redirectTo = `${window.location.origin}/account/update-password`;
    const { error: resetError } = await resetPasswordForEmail(email.value, redirectTo);
    
    if (resetError) throw resetError;

    message.value = 'Password reset email sent! Please check your email and follow the instructions to change your password.';
    error.value = false;
    
    // Keep the success message visible for a few seconds
    setTimeout(() => {
      if (message.value && message.value.includes('reset email sent')) {
        message.value = '';
      }
    }, 8000);
    
  } catch (e) {
    console.error('Password reset email failed:', e);
    message.value = e.message || 'Failed to send password reset email.';
    error.value = true;
  } finally {
    loading.value = false;
  }
}
</script>
