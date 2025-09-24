import { createRouter, createWebHistory } from "vue-router";
import { watch } from "vue";
import LandingPage from "../pages/LandingPage.vue";
import Login from "../pages/account/Login.vue";
import Register from "../pages/account/Register.vue";
import AccountSettings from "../pages/account/AccountSettings.vue";
import { sessionState } from "../services/session";
const TaskView = () => import('../pages/taskview/TaskView.vue')
const TaskDetail = () => import('../pages/taskdetails/TaskDetails.vue')
const ProjectView = () => import('../pages/projectview/ProjectView.vue')

const routes = [
  { path: "/login", name: "Login", component: Login },
  { path: "/", name: "Landing", component: LandingPage, meta: { requiresAuth: true } },
  { path: "/register", name: "Register", component: Register },
  { path: "/verify-email", name: "VerifyEmail", component: () => import('../components/VerifyEmail.vue') },
  { path: "/account", name: "AccountSettings", component: AccountSettings, meta: { requiresAuth: true } },
  {
    path: '/tasks/:id',  // new route with dynamic segment
    name: 'task-detail', 
    component: TaskDetail,
    props: true  // allows route params to be passed as props to the component
    // ,meta: { requiresAuth: true }
  },
  
  { path: '/tasks',  // change to '/tasks/:id'
    name: 'task-view', 
    component: TaskView 
    // ,meta: { requiresAuth: true }
  },

  { path: '/projects',  // change to '/projects/:id'
    name: 'project-view', 
    component: ProjectView
    // ,meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() { return { top: 0 } }
})

router.beforeEach((to, from, next) => {
  if (sessionState.loading) {
    // Wait until session is initialized
    const unwatch = watch(
      () => sessionState.loading,
      (loading) => {
        if (!loading) {
          unwatch();
          next(to.fullPath);
        }
      }
    );
    return;
  }

  const loggedIn = !!sessionState.session;

  // If trying to access a protected route while not logged in
  if (to.meta.requiresAuth && !loggedIn) {
    return next({ name: "Login" });
  }

  // If trying to access login page while logged in, redirect to landing
  if (to.path === "/login" && loggedIn) {
    return next({ name: "Landing" });
  }

  return next();
});

export default router;