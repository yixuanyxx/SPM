<!-- dummy sample, can change name later, this can be home page w all the user's tasks instead, just rmb to change all the names in router/index.js -->
<!-- idk how yall do it, mayb instead of this we can have one folder for one page then put one vue file and one css file in each folder -->

 <script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { sessionState } from '../services/session'
import { logout } from '../services/auth'
import '../assets/auth.css'

const router = useRouter()
const now = ref(new Date())
const greeting = computed(() => {
  const hour = now.value.getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
})

onMounted(() => {
  const timer = setInterval(() => (now.value = new Date()), 60000)
  // cleanup
  window.addEventListener('beforeunload', () => clearInterval(timer))
})

async function onLogout() {
  await logout()
  router.push({ name: 'Login' })
}
</script>

<template>
  <div class="dashboard">
    <header class="app-header">
      <div class="brand">
        <div class="logo">AIO</div>
        <div class="brand-text">
          <h1>All‑In‑One</h1>
          <p>Smart Task Manager</p>
        </div>
      </div>
      <div class="header-actions">
        <div class="user-chip">
          <span class="avatar">{{ sessionState.user?.email?.charAt(0)?.toUpperCase() || 'U' }}</span>
          <span class="user-meta">
            <strong>{{ sessionState.user?.user_metadata?.name || 'User' }}</strong>
            <small>{{ sessionState.user?.email }}</small>
          </span>
        </div>
        <button class="secondary-button" @click="router.push({ name: 'AccountSettings' })">Account</button>
        <button @click="onLogout">Logout</button>
      </div>
    </header>

    <main class="content">
      <section class="hero">
        <div>
          <h2>{{ greeting }}, {{ sessionState.user?.user_metadata?.name || 'there' }} 👋</h2>
          <p>Stay on top of your tasks, deadlines, and team collaboration.</p>
        </div>
      </section>

      <section class="grid">
        <article class="card kpi">
          <h3>My Tasks</h3>
          <p>Quick access to your assigned tasks.</p>
          <button class="secondary-button" aria-label="View my tasks">Open</button>
        </article>
        <article class="card kpi">
          <h3>Calendar</h3>
          <p>See upcoming deadlines and events.</p>
          <button class="secondary-button" aria-label="Open calendar">Open</button>
        </article>
        <article class="card kpi">
          <h3>Reports</h3>
          <p>Generate progress and workload reports.</p>
          <button class="secondary-button" aria-label="Open reports">Open</button>
        </article>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  grid-template-rows: auto 1fr;
  min-height: 100vh;
  background: var(--bg-secondary);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
}

.brand { display: flex; align-items: center; gap: 0.75rem; }
.logo {
  width: 40px; height: 40px; border-radius: 10px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  display: grid; place-items: center; color: #fff; font-weight: 700;
}
.brand-text h1 { margin: 0; font-size: 1rem; color: var(--text-primary); }
.brand-text p { margin: 0; font-size: 0.75rem; color: var(--text-secondary); }

.header-actions { display: flex; align-items: center; gap: 0.5rem; }
.user-chip { display: flex; align-items: center; gap: 0.5rem; padding-right: 0.5rem; border-right: 1px solid var(--border-color); }
.avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--bg-secondary); display: grid; place-items: center; color: var(--primary-color); font-weight: 700; }
.user-meta { display: flex; flex-direction: column; }
.user-meta strong { color: var(--text-primary); line-height: 1; }
.user-meta small { color: var(--text-secondary); }

.content { padding: 1.25rem; max-width: 1200px; width: 100%; margin: 0 auto; }
.hero { background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1.25rem; box-shadow: var(--shadow-sm); }
.hero h2 { margin: 0 0 0.25rem 0; color: var(--text-primary); }
.hero p { margin: 0; color: var(--text-secondary); }

.grid { margin-top: 1rem; display: grid; grid-template-columns: repeat(12, 1fr); gap: 1rem; }
.card { background: var(--bg-primary); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem; box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 0.5rem; }
.kpi { grid-column: span 4; }

@media (max-width: 1024px) {
  .kpi { grid-column: span 6; }
}
@media (max-width: 640px) {
  .content { padding: 1rem; }
  .grid { grid-template-columns: repeat(6, 1fr); }
  .kpi { grid-column: span 6; }
}
</style>
