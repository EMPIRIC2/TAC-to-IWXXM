import { createClient } from "jsr:@supabase/supabase-js@2.49.8";
import * as kv from "./kv_store.tsx";
// SERVICE_ROLE client for database operations (bypasses RLS)
const supabase = createClient(Deno.env.get("SUPABASE_URL") ?? "", Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "");
// Create a new user with email verification
export async function registerUser(email, password, username) {
  try {
    // Create the user in Supabase Auth with metadata
    const { data: authData, error: authError } = await supabase.auth.admin.createUser({
      email,
      password,
      user_metadata: {
        username,
        created_at: new Date().toISOString()
      },
      app_metadata: {
        approval_status: 'pending',
        is_admin: false
      },
      // User must verify their email
      email_confirm: false
    });
    if (authError) {
      console.error('Registration error during user creation:', authError);
      return {
        error: authError.message
      };
    }
    if (!authData.user) {
      console.error('Registration error: No user data returned');
      return {
        error: 'Failed to create user'
      };
    }
    // Also store in KV store for easier queries (backup/cache)
    const userProfile = {
      user_id: authData.user.id,
      email,
      username,
      approval_status: 'pending',
      is_admin: false,
      created_at: new Date().toISOString()
    };
    await kv.set(`user_profile:${authData.user.id}`, userProfile);
    console.log(`User registered: ${email}, status: pending approval`);
    return {
      data: {
        user: authData.user,
        profile: userProfile
      }
    };
  } catch (error) {
    console.error('Registration error:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error during registration'
    };
  }
}
// Check if user is approved
export async function checkUserApproval(userId) {
  try {
    // Get user from Supabase Auth - this is the source of truth
    const { data: authData, error: authError } = await supabase.auth.admin.getUserById(userId);
    if (authError || !authData.user) {
      console.error('Error checking user approval - auth lookup failed:', authError);
      return {
        approved: false,
        status: 'pending',
        emailVerified: false,
        isAdmin: false
      };
    }
    const emailVerified = authData.user.email_confirmed_at !== null;
    const appMetadata = authData.user.app_metadata || {};
    const userMetadata = authData.user.user_metadata || {};
    const approvalStatus = appMetadata.approval_status || 'pending';
    const isAdmin = appMetadata.is_admin === true;
    const username = userMetadata.username || '';
    const approved = approvalStatus === 'approved' && emailVerified;
    console.log(`User ${userId} approval check - Status: ${approvalStatus}, Email Verified: ${emailVerified}, Admin: ${isAdmin}`);
    return {
      approved,
      status: approvalStatus,
      emailVerified,
      isAdmin,
      username
    };
  } catch (error) {
    console.error('Error checking user approval:', error);
    return {
      approved: false,
      status: 'pending',
      emailVerified: false,
      isAdmin: false
    };
  }
}
// Approve a user (admin function)
export async function approveUser(userId, adminUserId) {
  try {
    // Get current user data from Supabase
    const { data: userData, error: getUserError } = await supabase.auth.admin.getUserById(userId);
    if (getUserError || !userData.user) {
      console.error(`Cannot approve user: User not found in Supabase for user_id: ${userId}`);
      return {
        error: 'User not found'
      };
    }
    // Update Supabase app_metadata (source of truth)
    const { data: updatedUser, error: updateError } = await supabase.auth.admin.updateUserById(userId, {
      app_metadata: {
        ...userData.user.app_metadata,
        approval_status: 'approved',
        approved_at: new Date().toISOString(),
        approved_by: adminUserId
      }
    });
    if (updateError) {
      console.error('Error updating Supabase user metadata:', updateError);
      return {
        error: 'Failed to update user approval status'
      };
    }
    // Also update KV store (cache)
    const profile = await kv.get(`user_profile:${userId}`);
    if (profile) {
      const updatedProfile = {
        ...profile,
        approval_status: 'approved',
        approved_at: new Date().toISOString(),
        approved_by: adminUserId
      };
      await kv.set(`user_profile:${userId}`, updatedProfile);
    }
    console.log(`User approved: ${userData.user.email} by admin: ${adminUserId}`);
    return {
      data: profile
    };
  } catch (error) {
    console.error('Error approving user:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error during approval'
    };
  }
}
// Resend verification email
export async function resendVerificationEmail(email) {
  try {
    // Supabase will automatically send verification email when user tries to sign in
    // or we can use the resend endpoint
    const { error } = await supabase.auth.resend({
      type: 'signup',
      email
    });
    if (error) {
      console.error('Error resending verification email:', error);
      return {
        error: error.message
      };
    }
    console.log(`Verification email resent to: ${email}`);
    return {
      data: {
        message: 'Verification email sent'
      }
    };
  } catch (error) {
    console.error('Error resending verification email:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error resending verification email'
    };
  }
}
// Reject a user (admin function)
export async function rejectUser(userId, adminUserId) {
  try {
    // Get current user data from Supabase
    const { data: userData, error: getUserError } = await supabase.auth.admin.getUserById(userId);
    if (getUserError || !userData.user) {
      console.error(`Cannot reject user: User not found in Supabase for user_id: ${userId}`);
      return {
        error: 'User not found'
      };
    }
    // Update Supabase app_metadata (source of truth)
    const { data: updatedUser, error: updateError } = await supabase.auth.admin.updateUserById(userId, {
      app_metadata: {
        ...userData.user.app_metadata,
        approval_status: 'rejected',
        rejected_at: new Date().toISOString(),
        rejected_by: adminUserId
      }
    });
    if (updateError) {
      console.error('Error updating Supabase user metadata:', updateError);
      return {
        error: 'Failed to update user rejection status'
      };
    }
    // Also update KV store (cache)
    const profile = await kv.get(`user_profile:${userId}`);
    if (profile) {
      const updatedProfile = {
        ...profile,
        approval_status: 'rejected',
        approved_at: new Date().toISOString(),
        approved_by: adminUserId
      };
      await kv.set(`user_profile:${userId}`, updatedProfile);
    }
    console.log(`User rejected: ${userData.user.email} by admin: ${adminUserId}`);
    return {
      data: profile
    };
  } catch (error) {
    console.error('Error rejecting user:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error during rejection'
    };
  }
}
// Get all pending users (admin function)
export async function getPendingUsers() {
  try {
    const allProfiles = await kv.getByPrefix('user_profile:');
    const pendingUsers = allProfiles.filter((profile)=>profile.approval_status === 'pending');
    console.log(`Retrieved ${pendingUsers.length} pending users`);
    return {
      data: pendingUsers
    };
  } catch (error) {
    console.error('Error getting pending users:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error getting pending users'
    };
  }
}
// Get all users (admin function)
export async function getAllUsers() {
  try {
    const allProfiles = await kv.getByPrefix('user_profile:');
    console.log(`Retrieved ${allProfiles.length} total users`);
    return {
      data: allProfiles
    };
  } catch (error) {
    console.error('Error getting all users:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error getting all users'
    };
  }
}
// Check if user is admin
export async function isUserAdmin(userId) {
  try {
    console.log(`🔍 isUserAdmin: Checking admin status for user ${userId}`);
    // Query the database directly since KV store may not be populated
    const { data, error } = await supabase.from('user_profiles').select('is_admin').eq('id', userId).single();
    if (error) {
      console.error(`❌ isUserAdmin: Database error for user ${userId}:`, error);
      return false;
    }
    console.log(`📋 isUserAdmin: User ${userId} is_admin=${data?.is_admin}`);
    return data?.is_admin === true;
  } catch (error) {
    console.error('❌ isUserAdmin: Exception checking admin status:', error);
    return false;
  }
}
// Toggle admin status (super admin function)
export async function toggleAdminStatus(userId, isAdmin, adminUserId) {
  try {
    // Check if the requesting user is an admin using Supabase
    const { data: adminData, error: adminError } = await supabase.auth.admin.getUserById(adminUserId);
    if (adminError || !adminData.user || adminData.user.app_metadata?.is_admin !== true) {
      return {
        error: 'Only administrators can modify admin status'
      };
    }
    // Get current user data from Supabase
    const { data: userData, error: getUserError } = await supabase.auth.admin.getUserById(userId);
    if (getUserError || !userData.user) {
      console.error(`Cannot modify admin status: User not found in Supabase for user_id: ${userId}`);
      return {
        error: 'User not found'
      };
    }
    // Update Supabase app_metadata (source of truth)
    const { data: updatedUser, error: updateError } = await supabase.auth.admin.updateUserById(userId, {
      app_metadata: {
        ...userData.user.app_metadata,
        is_admin: isAdmin
      }
    });
    if (updateError) {
      console.error('Error updating Supabase user metadata:', updateError);
      return {
        error: 'Failed to update admin status'
      };
    }
    // Also update KV store (cache)
    const profile = await kv.get(`user_profile:${userId}`);
    if (profile) {
      const updatedProfile = {
        ...profile,
        is_admin: isAdmin
      };
      await kv.set(`user_profile:${userId}`, updatedProfile);
    }
    console.log(`Admin status ${isAdmin ? 'granted to' : 'revoked from'}: ${userData.user.email} by admin: ${adminUserId}`);
    return {
      data: profile
    };
  } catch (error) {
    console.error('Error toggling admin status:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error toggling admin status'
    };
  }
}
// Get user profile (for authenticated users)
export async function getUserProfile(userId) {
  try {
    // Get user from Supabase Auth
    const { data: authData, error: authError } = await supabase.auth.admin.getUserById(userId);
    if (authError || !authData.user) {
      console.error('Error getting user profile:', authError);
      return {
        error: 'User not found'
      };
    }
    const appMetadata = authData.user.app_metadata || {};
    const userMetadata = authData.user.user_metadata || {};
    const profile = {
      user_id: authData.user.id,
      email: authData.user.email || '',
      username: userMetadata.username || '',
      approval_status: appMetadata.approval_status || 'pending',
      is_admin: appMetadata.is_admin === true,
      email_verified: authData.user.email_confirmed_at !== null,
      created_at: userMetadata.created_at || authData.user.created_at,
      approved_at: appMetadata.approved_at,
      last_login: authData.user.last_sign_in_at
    };
    console.log(`Retrieved profile for user: ${profile.email}`);
    return {
      data: profile
    };
  } catch (error) {
    console.error('Error getting user profile:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error getting user profile'
    };
  }
}
// Update user profile (for authenticated users)
export async function updateUserProfile(userId, updates) {
  try {
    // Get current user data
    const { data: userData, error: getUserError } = await supabase.auth.admin.getUserById(userId);
    if (getUserError || !userData.user) {
      console.error('Cannot update profile: User not found');
      return {
        error: 'User not found'
      };
    }
    const updatePayload = {};
    // Update email if provided
    if (updates.email && updates.email !== userData.user.email) {
      updatePayload.email = updates.email;
      // Email change requires re-verification
      updatePayload.email_confirm = false;
    }
    // Update username in user_metadata
    if (updates.username) {
      updatePayload.user_metadata = {
        ...userData.user.user_metadata,
        username: updates.username
      };
    }
    if (Object.keys(updatePayload).length === 0) {
      return {
        data: {
          message: 'No changes to update'
        }
      };
    }
    // Update Supabase user
    const { data: updatedUser, error: updateError } = await supabase.auth.admin.updateUserById(userId, updatePayload);
    if (updateError) {
      console.error('Error updating user profile:', updateError);
      return {
        error: 'Failed to update profile'
      };
    }
    // Also update KV store cache
    const kvProfile = await kv.get(`user_profile:${userId}`);
    if (kvProfile) {
      const updatedKvProfile = {
        ...kvProfile,
        ...updates.username && {
          username: updates.username
        },
        ...updates.email && {
          email: updates.email
        }
      };
      await kv.set(`user_profile:${userId}`, updatedKvProfile);
    }
    console.log(`Profile updated for user: ${userId}`);
    // If email was changed, return a message about verification
    if (updates.email && updates.email !== userData.user.email) {
      return {
        data: {
          message: 'Profile updated. Please verify your new email address.',
          emailChanged: true
        }
      };
    }
    return {
      data: {
        message: 'Profile updated successfully'
      }
    };
  } catch (error) {
    console.error('Error updating user profile:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error updating profile'
    };
  }
}
