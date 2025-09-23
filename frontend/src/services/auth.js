import { supabase } from "./supabase";

// Register
export async function register(email, password, role, name) {
  return await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        role: role,
        name: name,
      },
    },
  });
}

// Login
export async function login(email, password) {
  return await supabase.auth.signInWithPassword({ email, password });
}

// Logout
export async function logout() {
  return await supabase.auth.signOut();
}

// Get current user
export async function getUser() {
  const { data, error } = await supabase.auth.getUser();
  if (error) throw error;
  return data.user;
}

// Update profile
export async function updateProfile(userId, updates) {
  return await supabase.from("profiles").update(updates).eq("id", userId);
}

// Verify email (using Supabase auth email redirect handler)
// If you're using confirmSignUp links, Supabase will hit your app with access_token in URL.
// Here we exchange it to finalize the verification implicitly by setting session.
export async function verifyEmail(accessToken) {
  // Set the session from the token if provided by the redirect (hash or query)
  // Supabase JS v2 supports setSession with access and refresh tokens.
  // Some email confirmation flows provide only access token; set it and refresh will be null.
  const { data, error } = await supabase.auth.setSession({
    access_token: accessToken,
    refresh_token: null,
  });
  if (error) throw error;
  return data;
}

// Ensure a row exists in public.users with the current user's id and role
export async function ensureUserRow(user) {
  if (!user?.id) return;
  const role = user.user_metadata?.role || null;

  // Upsert with RLS: only own id allowed; relies on being authenticated
  const { error } = await supabase
    .from('users')
    .upsert({ id: user.id, role }, { onConflict: 'id' });
  if (error) throw error;
}