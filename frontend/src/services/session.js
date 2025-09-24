import { reactive } from "vue";
import { supabase } from "./supabase";
import { ensureUserRow } from "./auth";

export const sessionState = reactive({
  session: null,
  user: null,
  userid: null,
  role: null,
  loading: true,
});

// LocalStorage keys
const USERID_KEY = 'spm_userid';
const ROLE_KEY = 'spm_role';

// Helper functions for localStorage
function setUserData(userid, role) {
  if (userid) localStorage.setItem(USERID_KEY, userid.toString());
  if (role) localStorage.setItem(ROLE_KEY, role);
  console.log('Stored in localStorage:', { userid, role });
}

function getUserData() {
  const data = {
    userid: localStorage.getItem(USERID_KEY),
    role: localStorage.getItem(ROLE_KEY)
  };
  console.log('Retrieved from localStorage:', data);
  return data;
}

function clearUserData() {
  localStorage.removeItem(USERID_KEY);
  localStorage.removeItem(ROLE_KEY);
  console.log('Cleared localStorage');
}

// Fetch user data from Supabase user table
async function fetchUserData(userId) {
  try {
    console.log('🔍 Fetching user data for userId:', userId);
    const { data, error } = await supabase
      .from('user')
      .select('userid, role')
      .eq('id', userId)
      .single();

    if (error) {
      console.error('Error fetching user data:', error);
      return null;
    }

    console.log('Fetched user data from database:', data);
    return data;
  } catch (error) {
    console.error('Error fetching user data:', error);
    return null;
  }
}

// Initialize session on app startup
export async function initSession() {
  console.log('Initializing session...');
  
  // First, try to restore user data from localStorage
  const storedUserData = getUserData();
  if (storedUserData.userid && storedUserData.role) {
    sessionState.userid = storedUserData.userid;
    sessionState.role = storedUserData.role;
    console.log('Restored from localStorage:', { userid: storedUserData.userid, role: storedUserData.role });
  }

  const {
    data: { session },
  } = await supabase.auth.getSession();

  sessionState.session = session;
  sessionState.user = session?.user ?? null;
  sessionState.loading = false;

  console.log('Session state:', { 
    hasSession: !!session, 
    userId: session?.user?.id,
    currentUserid: sessionState.userid,
    currentRole: sessionState.role 
  });

  if (session?.user) {
    console.log('User logged in, ensuring user row exists...');
    // Create/Update users row with role after initial session fetch
    await ensureUserRow(session.user);
    
    // Fetch and store user data
    const userData = await fetchUserData(session.user.id);
    if (userData) {
      sessionState.userid = userData.userid;
      sessionState.role = userData.role;
      setUserData(userData.userid, userData.role);
      console.log('Updated session state:', { userid: userData.userid, role: userData.role });
    }
  } else {
    console.log('No user session, clearing data...');
    // Clear user data if no session
    sessionState.userid = null;
    sessionState.role = null;
    clearUserData();
  }

  // Listen for changes (login, logout, refresh)
  supabase.auth.onAuthStateChange(async (event, newSession) => {
    console.log('Auth state changed:', event, { hasSession: !!newSession });
    
    sessionState.session = newSession;
    sessionState.user = newSession?.user ?? null;

    if (newSession?.user) {
      console.log('User logged in via auth change');
      // Create/Update users row with role
      await ensureUserRow(newSession.user);
      
      // Fetch and store user data
      const userData = await fetchUserData(newSession.user.id);
      if (userData) {
        sessionState.userid = userData.userid;
        sessionState.role = userData.role;
        setUserData(userData.userid, userData.role);
        console.log('Updated session state from auth change:', { userid: userData.userid, role: userData.role });
      }
    } else {
      console.log('User logged out, clearing data...');
      // Clear user data on logout
      sessionState.userid = null;
      sessionState.role = null;
      clearUserData();
    }
  });
}

// Utility function to get current user data
export function getCurrentUserData() {
  return {
    userid: sessionState.userid,
    role: sessionState.role,
    isLoggedIn: !!sessionState.session
  };
}

// Utility function to check if user has specific role
export function hasRole(role) {
  return sessionState.role === role;
}
