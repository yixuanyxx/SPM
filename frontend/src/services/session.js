import { reactive } from "vue";
import { supabase } from "./supabase";

export const sessionState = reactive({
  session: null,
  user: null,
  loading: true,
});

// Initialize session on app startup
export async function initSession() {
  const {
    data: { session },
  } = await supabase.auth.getSession();

  sessionState.session = session;
  sessionState.user = session?.user ?? null;
  sessionState.loading = false;

  // Listen for changes (login, logout, refresh)
  supabase.auth.onAuthStateChange((_event, newSession) => {
    sessionState.session = newSession;
    sessionState.user = newSession?.user ?? null;
  });
}
