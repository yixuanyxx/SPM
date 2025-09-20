<template>
  <nav class="side-navbar">
    <div class="navbar-content">
      <!-- Logo/Brand -->
      <div class="navbar-brand">
        <div class="brand-icon">
          <i class="bi bi-heart"></i>
        </div>
        <span class="brand-text">whatisourname</span>
      </div>

      <!-- Navigation Items -->
      <div class="nav-items">
        <!-- Tasks -->
        <div class="nav-item" :class="{ expanded: expandedMenus.includes('tasks') }">
          <div class="nav-link" @click="toggleMenu('tasks')">
            <div class="nav-icon">
              <i class="bi bi-list-task"></i>
            </div>
            <span class="nav-text">Tasks</span>
            <div class="nav-arrow" :class="{ rotated: expandedMenus.includes('tasks') }">
              <i class="bi bi-chevron-down"></i>
            </div>
          </div>
          
          <transition name="dropdown">
            <div v-if="expandedMenus.includes('tasks')" class="nav-dropdown">
              <router-link to="/tasks" class="dropdown-item">
                <i class="bi bi-person-check"></i>
                <span>My Tasks</span>
              </router-link>
              <router-link :to="teamTasksRoute" class="dropdown-item">
                <i :class="teamTasksIcon"></i>
                <span>{{ teamTasksLabel }}</span>
              </router-link>
            </div>
          </transition>
        </div>

        <!-- Projects -->
        <div class="nav-item">
          <router-link to="/projects" class="nav-link">
            <div class="nav-icon">
              <i class="bi bi-folder"></i>
            </div>
            <span class="nav-text">Projects</span>
          </router-link>
        </div>

        <!-- Schedule -->
        <div class="nav-item">
          <router-link to="/" class="nav-link"> <!-- UPDATE THIS -->
            <div class="nav-icon">
              <i class="bi bi-calendar3"></i>
            </div>
            <span class="nav-text">Schedule</span>
          </router-link>
        </div>

        <!-- Profile -->
        <div class="nav-item">
          <router-link to="/" class="nav-link"> <!-- UPDATE THIS -->
            <div class="nav-icon">
              <i class="bi bi-person-circle"></i>
            </div>
            <span class="nav-text">Profile</span>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const expandedMenus = ref([])
const userRole = ref('')
const userId = ref(null)

onMounted(async () => {
  // Get user ID from localStorage
  const storedUserId = localStorage.getItem('UID') || localStorage.getItem('userId') || localStorage.getItem('user_id')
  userId.value = storedUserId

  // Fetch user role from backend
  if (storedUserId) {
    try {
      const response = await fetch(`........`) // UPDATE THIS
      if (response.ok) {
        const userData = await response.json()
        userRole.value = userData.role || ''
      }
    } catch (error) {
      console.error('Error fetching user role:', error)
    }
  }
})

const toggleMenu = (menuName) => {
  const index = expandedMenus.value.indexOf(menuName)
  if (index > -1) {
    expandedMenus.value.splice(index, 1)
  } else {
    expandedMenus.value.push(menuName)
  }
}

// Computed properties for role-based navigation (CHANGE THIS ALSO!!!!!)
const teamTasksRoute = computed(() => {
  return userRole.value?.toLowerCase() === 'director' ? '/tasks/department' : '/tasks/team'
})

const teamTasksLabel = computed(() => {
  return userRole.value?.toLowerCase() === 'director' ? "Dept's Tasks" : "Team's Tasks"
})

const teamTasksIcon = computed(() => {
  return userRole.value?.toLowerCase() === 'director' ? 'bi bi-building' : 'bi bi-people'
})


//ADD ROLE-BASED NAVIGATION FOR PROJECTS ALSO (TO BE DONE)

</script>

<style scoped>
.side-navbar {
  width: 250px;
  height: 100vh;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.navbar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Brand */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1rem;
  border-bottom: 1px solid #f3f4f6;
}

.brand-icon {
  width: 32px;
  height: 32px;
  background: #3b82f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.1rem;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
}

/* Navigation Items */
.nav-items {
  flex: 1;
  padding: 1rem 0;
}

.nav-item {
  margin: 0.25rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #374151;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 0;
}

.nav-link:hover {
  background: #f9fafb;
  color: #1a1a1a;
}

.nav-link.router-link-active {
  background: #f8faff;
  color: #3b82f6;
  border-right: 3px solid #3b82f6;
}

.nav-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.nav-text {
  flex: 1;
  font-size: 0.9rem;
  font-weight: 500;
}

.nav-arrow {
  transition: transform 0.2s ease;
  font-size: 0.8rem;
  color: #9ca3af;
}

.nav-arrow.rotated {
  transform: rotate(180deg);
}

/* Dropdown */
.nav-dropdown {
  background: #f9fafb;
  border-top: 1px solid #f3f4f6;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem 0.75rem 3rem;
  color: #6b7280;
  text-decoration: none;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background: #f3f4f6;
  color: #374151;
}

.dropdown-item.router-link-active {
  background: #e0e7ff;
  color: #6366f1;
  font-weight: 500;
}

.dropdown-item i {
  font-size: 0.9rem;
}

/* Dropdown Animation */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.dropdown-enter-from,
.dropdown-leave-to {
  max-height: 0;
  opacity: 0;
}

.dropdown-enter-to,
.dropdown-leave-from {
  max-height: 200px;
  opacity: 1;
}

/* Expanded state */
.nav-item.expanded .nav-link {
  background: #f9fafb;
}

/* Responsive */
@media (max-width: 768px) {
  .side-navbar {
    width: 200px;
  }
  
  .brand-text {
    font-size: 1.1rem;
  }
  
  .nav-text {
    font-size: 0.85rem;
  }
}

@media (max-width: 640px) {
  .side-navbar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .side-navbar.mobile-open {
    transform: translateX(0);
  }
}
</style>