import { createApp } from 'vue'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import 'bootstrap-icons/font/bootstrap-icons.css'
import router from './router'
import App from './App.vue'
import { initSession } from "./services/session";

async function startApp() {
  await initSession(); // sets up session persistence
  createApp(App).use(router).mount("#app");
}

startApp();
