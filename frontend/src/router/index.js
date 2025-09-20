import { createRouter, createWebHistory } from "vue-router";
import LandingPage from "../pages/LandingPage.vue";
import Login from "../pages/account/Login.vue";
import Register from "../pages/account/Register.vue";
import AccountSettings from "../pages/account/AccountSettings.vue";
import { sessionState } from "../services/session";

const routes = [
  { path: "/", name: "Login", component: Login },
  { path: "/landing", name: "Landing", component: LandingPage, meta: { requiresAuth: true } },
  { path: "/register", name: "Register", component: Register },
  { path: "/verify-email", name: "VerifyEmail", component: () => import('../components/VerifyEmail.vue') },
  { path: "/account", name: "AccountSettings", component: AccountSettings, meta: { requiresAuth: true } },
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

  // If trying to access login page while logged in
  if (to.path === "/" && loggedIn) {
    return next({ name: "Landing" });
  }

  return next();
});

export default router;