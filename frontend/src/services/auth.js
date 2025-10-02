import { supabase } from "./supabase";

// Register
export async function register(email, password, role, name, additionalData = {}) {
  return await supabase.auth.signUp({
    email,
    password,
    options: {
      data: {
        role: role,
        name: name,
        team_name: additionalData.team || null,
        department_name: additionalData.department || null,
      },
    },
  });
}

// Login
export async function login(email, password) {
  return await supabase.auth.signInWithPassword({ email, password });
}

export async function logout() {
  // // Clear localStorage
  localStorage.removeItem('userId'); // angela
  localStorage.removeItem('userRole'); // angela
  
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

// Reset password - send reset email
export async function resetPasswordForEmail(email, redirectTo) {
  return await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: redirectTo
  });
}

// Update password (for authenticated users)
export async function updatePassword(newPassword) {
  return await supabase.auth.updateUser({ password: newPassword });
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

// Generate a random 3-digit userid starting from 100
async function generateUserId() {
  let userId;
  let isUnique = false;
  
  while (!isUnique) {
    // Generate random 3-digit number from 100-999
    userId = Math.floor(Math.random() * 900) + 100;
    
    // Check if this userId already exists
    const { data, error } = await supabase
      .from('user')
      .select('userid')
      .eq('userid', userId)
      .single();
    
    // If no data found, the userId is unique
    if (error && error.code === 'PGRST116') {
      isUnique = true;
    } else if (error) {
      throw error;
    }
  }
  
  return userId;
}

// Ensure a row exists in public.users with the current user's id and role
// This is mainly for users who registered before the new system
export async function ensureUserRow(user) {
  if (!user?.id) return;
  
  const role = user.user_metadata?.role || null;
  const name = user.user_metadata?.name || user.user_metadata?.full_name || null;
  const email = user.email || null;

  // Check if user already exists
  const { data: existingUser, error: fetchError } = await supabase
    .from('user')
    .select('*')
    .eq('id', user.id)
    .single();

  if (fetchError && fetchError.code !== 'PGRST116') {
    throw fetchError;
  }

  // If user doesn't exist, create new row with generated userid
  // This handles legacy users who registered before the new system
  if (!existingUser) {
    const userId = await generateUserId();
    
    try {
      const userData = {
        id: user.id,
        userid: userId,
        role: role,
        name: name,
        email: email,
        team_id: null,
        dept_id: null
      };

      const response = await fetch(`http://127.0.0.1:5003/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || errorData.message || 'Failed to create user record');
      }
    } catch (error) {
      console.error('Failed to create user record via user controller:', error);
      throw error;
    }
  }
}