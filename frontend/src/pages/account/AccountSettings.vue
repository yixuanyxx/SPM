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
          <!-- Loading State -->
          <div v-if="loading && !userid" class="task-card">
            <div class="task-main" style="cursor: default; text-align: center; padding: 2rem;">
              <div style="color: #6b7280;">
                <i class="bi bi-hourglass-split" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                Loading your account settings...
              </div>
            </div>
          </div>

          <!-- Main Content -->
          <div v-else class="task-card">
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

                  <!-- Notification Preferences -->
                  <div style="display:grid; grid-template-columns: 1fr auto; align-items:start; gap:0.5rem;">
                    <div>
                      <label style="display:block; font-size: 0.85rem; color:#6b7280; margin-bottom: 0.5rem;">Notification Preferences</label>
                      <div style="display:flex; flex-direction:column; gap:0.75rem;">
                        <label style="display:flex; align-items:center; gap:0.5rem; cursor:pointer;">
                          <input 
                            type="checkbox" 
                            v-model="notificationPreferences.in_app" 
                            :disabled="isEditingPreferences"
                            style="margin:0;"
                          />
                          <span style="font-size: 0.9rem;">In-app notifications</span>
                        </label>
                        <label style="display:flex; align-items:center; gap:0.5rem; cursor:pointer;">
                          <input 
                            type="checkbox" 
                            v-model="notificationPreferences.email" 
                            :disabled="isEditingPreferences"
                            style="margin:0;"
                          />
                          <span style="font-size: 0.9rem;">Email notifications</span>
                        </label>
                      </div>
                    </div>
                    <div style="display:flex; gap:0.5rem; margin-top: 1.35rem">
                      <button 
                        type="button" 
                        @click="saveNotificationPreferences" 
                        :disabled="loading || isEditingPreferences"
                        class="secondary-button"
                      >
                        {{ isEditingPreferences ? 'Saving...' : 'Save Preferences' }}
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
import { ref, onMounted, watch } from "vue";
import SideNavbar from '../../components/SideNavbar.vue'
import './account.css'
import { supabase } from "../../services/supabase";
import { resetPasswordForEmail } from "../../services/auth.js";
import { userPreferencesService } from "../../services/notifications.js";
import { sessionState } from "../../services/session.js";

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
const notificationPreferences = ref({ in_app: true, email: true });
const isEditingPreferences = ref(false);

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

// Watch for changes in session state
watch(() => sessionState.userid, (newUserid) => {
  if (newUserid && !userid.value) {
    userid.value = newUserid;
    onFetch();
  } else if (!newUserid && userid.value) {
    // User logged out
    userid.value = null;
    name.value = "";
    email.value = "";
    role.value = "";
    team_id.value = null;
    dept_id.value = null;
    teamName.value = "";
    departmentName.value = "";
    message.value = 'Please log in to access account settings';
    error.value = true;
    loading.value = false;
  }
}, { immediate: true });

onMounted(async () => {
  loading.value = true;
  
  // Check if user is authenticated
  try {
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) {
      console.warn('User not authenticated, redirecting to login');
      message.value = 'Please log in to access account settings';
      error.value = true;
      loading.value = false;
      return;
    }
    console.log('User authenticated:', user.id);
  } catch (e) {
    console.error('Authentication check failed:', e);
    loading.value = false;
    return;
  }

  // Use session state if available, otherwise fallback to localStorage
  if (sessionState.userid) {
    userid.value = sessionState.userid;
    await onFetch();
  } else {
    // Get user ID from localStorage with multiple fallbacks
    const stored = localStorage.getItem('spm_userid') || 
                   localStorage.getItem('UID') || 
                   localStorage.getItem('userId') || 
                   localStorage.getItem('user_id');
    
    if (stored) {
      userid.value = Number(stored);
      await onFetch();
    } else {
      message.value = 'User ID not found. Please log in again.';
      error.value = true;
      loading.value = false;
    }
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
    
    console.log('Fetching user data for userid:', userid.value);
    const res = await fetch(`${API}/users/${userid.value}`);
    if (!res.ok) {
      if (res.status === 404) {
        throw new Error('User not found. Please log in again.');
      }
      throw new Error(`Failed to fetch user data (HTTP ${res.status})`);
    }
    
    const data = await res.json();
    console.log('User data received:', data);
    
    const u = data?.data || {};
    name.value = u.name || "";
    email.value = u.email || "";
    role.value = u.role || "";
    team_id.value = u.team_id ?? null;
    dept_id.value = u.dept_id ?? null;
    nameDraft.value = name.value;
    
    // Set notification preferences
    notificationPreferences.value = u.notification_preferences || { in_app: true, email: true };
    
    // Fetch team and department names in parallel
    const promises = [];
    if (team_id.value) {
      promises.push(getTeamNameById(team_id.value).then(name => teamName.value = name));
    }
    if (dept_id.value) {
      promises.push(getDepartmentNameById(dept_id.value).then(name => departmentName.value = name));
    }
    
    if (promises.length > 0) {
      await Promise.all(promises);
    }
    
    console.log('Account settings loaded successfully');
    error.value = false;
  } catch (e) {
    console.error('Failed to fetch user data:', e);
    message.value = e.message || 'Failed to fetch user data. Please try again.';
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

async function saveNotificationPreferences() {
  try {
    message.value = '';
    error.value = false;
    if (!userid.value) throw new Error('userid is required');
    isEditingPreferences.value = true;
    
    await userPreferencesService.updateNotificationPreferences(userid.value, notificationPreferences.value);
    
    message.value = 'Notification preferences updated successfully!';
    error.value = false;
    
    // Clear success message after a few seconds
    setTimeout(() => {
      if (message.value && message.value.includes('preferences updated')) {
        message.value = '';
      }
    }, 3000);
    
  } catch (e) {
    message.value = e.message || 'Failed to update notification preferences.';
    error.value = true;
  } finally {
    isEditingPreferences.value = false;
  }
}
</script>
