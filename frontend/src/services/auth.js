import { supabase } from "./supabase";

// Register
export async function register(email, password, role) {
  return await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        role: role,
      }
    }
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