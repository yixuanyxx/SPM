import { reactive } from "vue";
import { supabase } from "./supabase";
import { ensureUserRow } from "./auth";

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

  if (session?.user) {
    // Create/Update users row with role after initial session fetch
    ensureUserRow(session.user).catch(() => {});
  }

  // Listen for changes (login, logout, refresh)
  supabase.auth.onAuthStateChange((_event, newSession) => {
    sessionState.session = newSession;
    sessionState.user = newSession?.user ?? null;

    if (newSession?.user) {
      ensureUserRow(newSession.user).catch(() => {});
    }
  });
}
