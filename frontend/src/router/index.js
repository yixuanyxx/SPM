import { createRouter, createWebHistory } from "vue-router";
import { watch } from "vue";
import LandingPage from "../pages/LandingPage.vue";
import Login from "../pages/account/Login.vue";
import Register from "../pages/account/Register.vue";
import AccountSettings from "../pages/account/AccountSettings.vue";
import ResetPassword from "../pages/account/ResetPassword.vue";
import UpdatePassword from "../pages/account/UpdatePassword.vue";
import { sessionState } from "../services/session";
const TaskView = () => import('../pages/taskview/TaskView.vue')
const TeamTaskView = () => import('../pages/taskview/TeamTaskView.vue')
const DepartmentTaskView = () => import('../pages/taskview/DepartmentTaskView.vue')
const ProjectTaskView = () => import('../pages/taskview/ProjectTaskView.vue')
const TaskDetail = () => import('../pages/taskdetails/TaskDetails.vue')
const ProjectView = () => import('../pages/projectview/ProjectView.vue')
const ProjectDetail = () => import('../pages/projectdetails/ProjectDetails.vue')
const ScheduleView = () => import('../pages/schedule/ScheduleView.vue')
const ProjectMemberSchedule = () => import('../pages/schedule/ProjectMemberSchedule.vue')
const TeamScheduleView = () => import('../pages/schedule/TeamScheduleView.vue')
const ReportView = () => import('../pages/reportview/ReportView.vue')
const CompanyView = () => import('../pages/taskview/CompanyTaskView.vue')

const routes = [
  { path: "/login", name: "Login", component: Login },
  { path: "/", name: "Landing", component: LandingPage, meta: { requiresAuth: true } },
  { path: "/register", name: "Register", component: Register },
  { path: "/account", name: "AccountSettings", component: AccountSettings, meta: { requiresAuth: true } },
  { path: "/account/reset-password", name: "ResetPassword", component: ResetPassword },
  { path: "/account/update-password", name: "UpdatePassword", component: UpdatePassword },
  {
    path: "/tasks/:id",
    name: "task-detail",
    component: TaskDetail,
    props: true,
  },
  
  { path: '/tasks',  // Personal tasks (staff only)
    name: 'task-view', 
    component: TaskView 
    // ,meta: { requiresAuth: true }
  },

  { path: '/tasks/team',  // Team tasks (manager only)
    name: 'team-task-view', 
    component: TeamTaskView
    // ,meta: { requiresAuth: true }
  },

  { path: '/tasks/projects', // Project-based task overview
    name: 'project-task-view',
    component: ProjectTaskView
  },

  { path: '/tasks/department',  // Department tasks (director only)
    name: 'department-task-view', 
    component: DepartmentTaskView
    // ,meta: { requiresAuth: true }
  },

  { path: '/projects',  // change to '/projects/:id'
    name: 'project-view', 
    component: ProjectView
    // ,meta: { requiresAuth: true }
  },

  { path: '/projects/:id',
    name: 'project-detail',
    component: ProjectDetail
  },

  { path: '/schedule',
    name: 'schedule-view',
    component: ScheduleView
    // ,meta: { requiresAuth: true }
  },

  { path: '/schedule/project/:id',
    name: 'project-member-schedule',
    component: ProjectMemberSchedule
  },
  
  {
    path: '/schedule/team',
    name: 'TeamSchedule',
    component: TeamScheduleView
  },

  { path: '/reports',
    name: 'report-view',
    component: ReportView
  },

  { path: '/company',
    name: 'company-view',
    component: CompanyView
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach((to, from, next) => {
  if (sessionState.loading) {
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

  if (to.meta.requiresAuth && !loggedIn) {
    return next({ name: "Login" });
  }

  if (to.path === "/login" && loggedIn) {
    return next({ name: "Landing" });
  }

  return next();
});

export default router;
