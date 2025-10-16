<template>
  <!-- Mobile Menu Overlay -->
  <div 
    v-if="isMobileMenuOpen" 
    class="mobile-overlay"
    @click="closeMobileMenu"
  ></div>

  <!-- Mobile Header (visible only on small screens) -->
  <div class="mobile-header">
    <button class="mobile-menu-btn" @click="toggleMobileMenu">
      <i class="bi bi-list"></i>
    </button>
    <div class="mobile-brand">
      <div class="brand-icon">
        <i class="bi bi-heart mt-1"></i>
      </div>
      <span class="brand-text">9-5planner</span>
    </div>
  </div>

  <!-- Side Navigation -->
  <nav class="side-navbar" :class="{ 'mobile-open': isMobileMenuOpen }">
    <div class="navbar-content ms-3 me-3">
      <!-- Logo/Brand -->
      <div class="navbar-brand">
        <div class="brand-icon">
          <i class="bi bi-heart mt-1"></i>
        </div>
        <span class="brand-text">9-5planner</span>
        <!-- Close button for mobile -->
        <button class="mobile-close-btn" @click="closeMobileMenu">
          <i class="bi bi-x"></i>
        </button>
      </div>

      <!-- Navigation Items -->
      <div class="nav-items">
        <!-- Home -->
        <div class="nav-item">
          <router-link to="/" class="nav-link" @click="handleNavItemClick">
            <div class="nav-icon">
              <i class="bi bi-house"></i>
            </div>
            <span class="nav-text">Home</span>
          </router-link>
        </div>

        <!-- My Tasks -->
         <div class="nav-item">
          <router-link to="/tasks" class="nav-link" @click="handleNavItemClick">
            <div class="nav-icon">
              <i class="bi bi-person-check"></i>
            </div>
            <span class="nav-text">My Tasks</span>
          </router-link>
        </div>

        <!-- Projects -->
        <div class="nav-item">
          <router-link to="/projects" class="nav-link" @click="handleNavItemClick"> <!-- UPDATE THIS -->
            <div class="nav-icon">
              <i class="bi bi-folder"></i>
            </div>
            <span class="nav-text">Projects</span>
          </router-link>
        </div>

        <!-- Team/Dept Workload -->
        <div v-if="userRole.toLowerCase() === 'manager' || userRole.toLowerCase() === 'director'" class="nav-item">
          <router-link :to="teamTasksRoute" class="nav-link" @click="handleNavItemClick"> 
            <div class="nav-icon">
              <i :class="teamTasksIcon"></i>
            </div>
            <span class="nav-text">{{teamTasksLabel}}</span>
          </router-link>
        </div>

        <!-- Schedule -->
        <div class="nav-item">
          <router-link to="/schedule" class="nav-link" @click="handleNavItemClick"> <!-- UPDATE THIS -->
            <div class="nav-icon">
              <i class="bi bi-calendar"></i>
            </div>
            <span class="nav-text">My Schedule</span>
          </router-link>
        </div>

        <!-- Profile with dropdown -->
        <div class="nav-item" :class="{ expanded: expandedMenus.includes('profile') }">
          <div class="nav-link" @click="toggleMenu('profile')">
            <div class="nav-icon">
              <i class="bi bi-person-circle"></i>
            </div>
            <span class="nav-text">Profile</span>
            <div class="nav-arrow" :class="{ rotated: expandedMenus.includes('profile') }">
              <i class="bi bi-chevron-down"></i>
            </div>
          </div>

          <transition name="dropdown">
            <div v-if="expandedMenus.includes('profile')" class="nav-dropdown">
              <router-link :to="{ name: 'AccountSettings' }" class="dropdown-item" @click="handleNavItemClick">
                <i class="bi bi-gear"></i>
                <span>Account Settings</span>
              </router-link>
              <a href="#" class="dropdown-item" @click.prevent="onLogout">
                <i class="bi bi-box-arrow-right"></i>
                <span @click="onLogout">Logout</span>
              </a>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </nav>

</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { logout } from '../services/auth'

const expandedMenus = ref([])
const userRole = ref('')
const userId = ref(null)
const isMobileMenuOpen = ref(false)
const windowWidth = ref(window.innerWidth) // Track window width reactively
const router = useRouter()
const route = useRoute()

onMounted(async () => {
  // Get user ID from localStorage
  const storedUserId = localStorage.getItem('spm_userid') || localStorage.getItem('UID') || localStorage.getItem('userId') || localStorage.getItem('user_id')
  userId.value = storedUserId

  // get role from localStorage if available
  const storedUserRole = localStorage.getItem('spm_userrole') || localStorage.getItem('userRole') || localStorage.getItem('role')
  if (storedUserRole) {
    userRole.value = storedUserRole
  }
})

onMounted(() => {
  // Add resize listener to close mobile menu on desktop and prevent content blocking
  window.addEventListener('resize', handleResize)
  
  // Also check initial state
  handleResize()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  // Update reactive window width
  windowWidth.value = window.innerWidth
  
  // Collapse sidebar when screen gets too small to accommodate both sidebar and content
  // 1024px ensures sufficient space for content when sidebar is 250px wide
  // This prevents sidebar from blocking main content
  if (windowWidth.value <= 1024) {
    // Ensure sidebar is collapsed on smaller screens
    if (isMobileMenuOpen.value) {
      isMobileMenuOpen.value = false
    }
  }
}

const toggleMenu = (menuName) => {
  const index = expandedMenus.value.indexOf(menuName)
  if (index > -1) {
    expandedMenus.value.splice(index, 1)
  } else {
    expandedMenus.value.push(menuName)
  }
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const handleNavItemClick = () => {
  // Close mobile menu when a nav item is clicked (on smaller screens)
  if (isMobileMode.value) {
    closeMobileMenu()
  }
  // Don't auto-close expanded menus - let them stay open to show current page
}


// Watch for route changes to auto-expand relevant menus
watch(() => route.path, (newPath) => {
  // Auto-expand tasks menu if on any tasks page
  if (newPath.startsWith('/tasks')) {
    if (!expandedMenus.value.includes('tasks')) {
      expandedMenus.value.push('tasks')
    }
  }
  // Auto-expand profile menu if on account settings
  if (newPath === '/account') {
    if (!expandedMenus.value.includes('profile')) {
      expandedMenus.value.push('profile')
    }
  }
}, { immediate: true })

// Computed properties for role-based navigation (CHANGE THIS ALSO!!!!!)
const teamTasksRoute = computed(() => {
  return userRole.value?.toLowerCase() === 'director' ? '/tasks/department' : '/tasks/team'
})

const teamTasksLabel = computed(() => {
  return userRole.value?.toLowerCase() === 'director' ? "Dept's Workload" : "Team's Workload"
})

const teamTasksIcon = computed(() => {
  return userRole.value?.toLowerCase() === 'director' ? 'bi bi-building' : 'bi bi-people'
})

//ADD ROLE-BASED NAVIGATION FOR PROJECTS ALSO (TO BE DONE)

async function onLogout() {
  try {
    console.log('Logging out...');
    await logout();
    console.log('Logout successful, redirecting to login...');
    router.push({ name: 'Login' });
  } catch (error) {
    console.error('Logout failed:', error);
    // Still redirect to login even if logout fails
    router.push({ name: 'Login' });
  }
}
</script>

<style scoped>
/* Mobile Header */
.mobile-header {
  display: none;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.mobile-menu-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #374151;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  transition: color 0.2s ease;
}

.mobile-menu-btn:hover {
  color: #1a1a1a;
}

.mobile-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mobile-brand .brand-icon {
  width: 28px;
  height: 28px;
  background: #3b82f6;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1rem;
}

.mobile-brand .brand-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1a1a1a;
}

/* Mobile Overlay */
.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
  display: none;
}

/* Side Navigation */
.side-navbar {
  width: 250px;
  height: 200vh;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
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
  position: relative;
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
  flex-shrink: 0;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1a1a1a;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mobile-close-btn {
  display: none;
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.25rem;
  margin-left: auto;
  width: 32px;
  height: 32px;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.mobile-close-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

/* Navigation Items */
.nav-items {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
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
  min-width: 0;
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
  flex-shrink: 0;
}

.nav-text {
  flex: 1;
  font-size: 0.9rem;
  font-weight: 500;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-arrow {
  transition: transform 0.2s ease;
  font-size: 0.8rem;
  color: #9ca3af;
  flex-shrink: 0;
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
  min-width: 0;
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
  flex-shrink: 0;
}

.dropdown-item span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

/* Responsive Breakpoints */

/* Tablet */
@media (max-width: 768px) {
  .side-navbar {
    width: 200px;
  }
  
  .navbar-brand {
    padding: 1.25rem 0.75rem;
  }
  
  .brand-icon {
    width: 28px;
    height: 28px;
    font-size: 1rem;
  }
  
  .brand-text {
    font-size: 1.1rem;
  }
  
  .nav-text {
    font-size: 0.85rem;
  }
  
  .nav-link {
    padding: 0.75rem;
  }
  
  .dropdown-item {
    padding: 0.75rem 0.75rem 0.75rem 2.5rem;
    font-size: 0.8rem;
  }
}

/* Tablet and smaller screens - Sidebar should collapse to prevent content blocking */
@media (max-width: 1024px) {
  .mobile-header {
    display: flex;
  }
  
  .mobile-overlay {
    display: block;
  }
  
  .mobile-close-btn {
    display: flex;
  }
  
  .side-navbar {
    width: 280px;
    transform: translateX(-100%);
    z-index: 1200;
    top: 0;
  }
  
  .side-navbar.mobile-open {
    transform: translateX(0);
  }
  
  .navbar-brand {
    padding: 1rem;
  }
  
  /* Add padding to body content when mobile header is visible */
  :global(body) {
    padding-top: 68px;
  }
}

/* Mobile fine-tuning */
@media (max-width: 640px) {
  .side-navbar {
    width: 260px; /* Slightly smaller on very small screens */
  }
  
  .mobile-header {
    padding: 0 0.75rem; /* Adjust padding for smaller screens */
  }
  
  .mobile-brand .brand-text {
    font-size: 1rem; /* Smaller text on mobile */
  }
}

/* Small Mobile */
@media (max-width: 480px) {
  .side-navbar {
    width: 260px;
  }
  
  .navbar-brand {
    padding: 0.75rem;
  }
  
  .brand-text {
    font-size: 1rem;
  }
  
  .nav-text {
    font-size: 0.8rem;
  }
  
  .dropdown-item {
    font-size: 0.75rem;
  }
  
  .mobile-brand .brand-text {
    font-size: 1rem;
  }
}


/* Extra Small Mobile */
@media (max-width: 360px) {
  .side-navbar {
    width: 240px;
  }
  
  .brand-text {
    font-size: 0.95rem;
  }
  
  .nav-text {
    font-size: 0.75rem;
  }
  
  .mobile-brand .brand-text {
    font-size: 0.95rem;
  }
}
</style>