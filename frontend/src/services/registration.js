import { supabase } from "./supabase";

// API base URLs for backend services
const DEPT_API = 'http://127.0.0.1:5005';
const TEAM_API = 'http://127.0.0.1:5004';

// Helper function to get all departments
async function getAllDepartments() {
  try {
    const response = await fetch(`${DEPT_API}/departments`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return data.data || [];
  } catch (error) {
    console.warn('Failed to fetch departments:', error);
    return [];
  }
}

// Helper function to get all teams
async function getAllTeams() {
  try {
    const response = await fetch(`${TEAM_API}/teams`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    return data.data || [];
  } catch (error) {
    console.warn('Failed to fetch teams:', error);
    return [];
  }
}

// Helper function to get team ID by name
async function getTeamIdByName(teamName) {
  if (!teamName) return null;
  
  const teams = await getAllTeams();
  const team = teams.find(t => t.name === teamName);
  return team?.id || null;
}

// Helper function to get department ID by name
async function getDeptIdByName(deptName) {
  if (!deptName) return null;
  
  const departments = await getAllDepartments();
  const dept = departments.find(d => d.name === deptName);
  return dept?.id || null;
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

// Enhanced registration function that handles team/dept mapping
export async function registerWithMapping(email, password, role, name, teamName = null, departmentName = null) {
  try {
    // First, register with Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          role: role,
          name: name,
        },
      },
    });

    if (authError) throw authError;

    // If registration successful, create user record with proper foreign keys
    if (authData.user) {
      // Map team/department names to IDs
      let team_id = null;
      let dept_id = null;
      
      if (teamName) {
        // For staff and managers, get team_id and derive dept_id from team
        team_id = await getTeamIdByName(teamName);
        if (team_id) {
          // Get the team details to find its dept_id
          const teams = await getAllTeams();
          const team = teams.find(t => t.id === team_id);
          dept_id = team?.dept_id || null;
        }
      } else if (departmentName) {
        // For directors, get dept_id directly
        dept_id = await getDeptIdByName(departmentName);
      }
      
      // Generate unique userid
      const userid = await generateUserId();

      // Create user record via user controller (bypasses RLS)
      try {
        const userData = {
          id: authData.user.id,
          userid: userid,
          role: role,
          name: name,
          email: email,
          team_id: team_id,
          dept_id: dept_id
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

        const result = await response.json();
        console.log('User created successfully:', result);

      } catch (userError) {
        console.error('Failed to create user record via user controller:', userError);
        throw userError;
      }
    }

    return { data: authData, error: null };
  } catch (error) {
    return { data: null, error };
  }
}

// Export helper functions for use elsewhere
export { getAllDepartments, getAllTeams, getTeamIdByName, getDeptIdByName };
