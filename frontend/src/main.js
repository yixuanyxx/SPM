import { createApp } from 'vue'
import './style.css'
import router from './router'
import App from './App.vue'
import { initSession } from "./services/session";

async function startApp() {
  await initSession(); // sets up session persistence
  createApp(App).use(router).mount("#app");
}

startApp();
