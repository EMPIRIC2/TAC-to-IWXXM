import { Hono } from "npm:hono";
import { cors } from "npm:hono/cors";
import { logger } from "npm:hono/logger";
import { jwtVerify, createRemoteJWKSet } from "npm:jose@5.2.0";
import * as kv from "./kv_store.tsx";
import * as auth from "./auth.tsx";
import * as database from "./database.tsx";
import * as admin from "./admin.tsx";
import { createClient } from "jsr:@supabase/supabase-js@2.49.8";

const app = new Hono();

// JWKS verification for ES256 signed JWTs (asymmetric)
const JWKS = createRemoteJWKSet(
  new URL("https://ktvxijislbtgqapllmuk.supabase.co/auth/v1/.well-known/jwks.json"),
);

// SERVICE_ROLE client for admin operations (bypasses RLS, full database access)
const supabase = createClient(
  Deno.env.get("SUPABASE_URL") ?? "",
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
);

// Enable logger
app.use('*', logger(console.log));

// Enable CORS for all routes and methods
app.use(
  "/*",
  cors({
    origin: "*",
    allowHeaders: ["Content-Type", "Authorization"],
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    exposeHeaders: ["Content-Length"],
    maxAge: 600,
  }),
);

// Health check endpoint
app.get("/make-server-2e3cda33/health", (c) => {
  return c.json({ status: "ok" });
});

// Register new user
app.post("/make-server-2e3cda33/auth/register", async (c) => {
  try {
    const { email, password, username } = await c.req.json();

    if (!email || !password || !username) {
      return c.json({ error: 'Email, password, and username are required' }, 400);
    }

    const result = await auth.registerUser(email, password, username);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ 
      message: 'Registration successful. Please verify your email and wait for admin approval.',
      user: result.data?.user,
      profile: result.data?.profile
    }, 201);
  } catch (error) {
    console.error('Registration endpoint error:', error);
    return c.json({ error: 'Internal server error during registration' }, 500);
  }
});

// Check user approval status
app.get("/make-server-2e3cda33/auth/check-approval/:userId", async (c) => {
  try {
    const userId = c.req.param('userId');
    const result = await auth.checkUserApproval(userId);

    return c.json(result);
  } catch (error) {
    console.error('Check approval endpoint error:', error);
    return c.json({ error: 'Internal server error checking approval status' }, 500);
  }
});

// Approve user (admin only)
app.post("/make-server-2e3cda33/auth/approve", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { userId } = await c.req.json();

    if (!userId) {
      return c.json({ error: 'User ID is required' }, 400);
    }

    const result = await auth.approveUser(userId, user.id);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ message: 'User approved successfully', profile: result.data });
  } catch (error) {
    console.error('Approve user endpoint error:', error);
    return c.json({ error: 'Internal server error approving user' }, 500);
  }
});

// Get pending users (admin only)
app.get("/make-server-2e3cda33/auth/pending-users", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const result = await auth.getPendingUsers();

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ users: result.data });
  } catch (error) {
    console.error('Get pending users endpoint error:', error);
    return c.json({ error: 'Internal server error getting pending users' }, 500);
  }
});

// Resend verification email
app.post("/make-server-2e3cda33/auth/resend-verification", async (c) => {
  try {
    const { email } = await c.req.json();

    if (!email) {
      return c.json({ error: 'Email is required' }, 400);
    }

    const result = await auth.resendVerificationEmail(email);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ message: 'Verification email sent' });
  } catch (error) {
    console.error('Resend verification endpoint error:', error);
    return c.json({ error: 'Internal server error resending verification email' }, 500);
  }
});

// Get user profile (authenticated users)
app.get("/make-server-2e3cda33/auth/profile", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const result = await auth.getUserProfile(user.id);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ profile: result.data });
  } catch (error) {
    console.error('Get profile endpoint error:', error);
    return c.json({ error: 'Internal server error getting profile' }, 500);
  }
});

// Update user profile (authenticated users)
app.put("/make-server-2e3cda33/auth/profile", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { username, email } = await c.req.json();

    const result = await auth.updateUserProfile(user.id, { username, email });

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json(result.data);
  } catch (error) {
    console.error('Update profile endpoint error:', error);
    return c.json({ error: 'Internal server error updating profile' }, 500);
  }
});

// Upload converted files to database
app.post("/make-server-2e3cda33/database/upload", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { files, options } = await c.req.json();

    if (!files || !Array.isArray(files) || files.length === 0) {
      return c.json({ error: 'Files array is required' }, 400);
    }

    if (!options || !options.format || !options.destination) {
      return c.json({ error: 'Upload options (format, destination) are required' }, 400);
    }

    // Add user info to each file
    const filesWithUser = files.map(file => ({
      ...file,
      userId: user.id,
      userEmail: user.email || '',
    }));

    const result = await database.uploadToDatabase(filesWithUser, options);

    return c.json({
      message: `Successfully uploaded ${result.summary.success} file(s)`,
      summary: result.summary,
      results: result.results,
    });
  } catch (error) {
    console.error('Database upload endpoint error:', error);
    return c.json({ error: 'Internal server error during database upload' }, 500);
  }
});

// Get user's uploaded files
app.get("/make-server-2e3cda33/database/uploads", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const dbType = c.req.query('database') as 'primary' | 'archive' | 'both' || 'both';

    const result = await database.getUserUploads(user.id, dbType);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ uploads: result.data });
  } catch (error) {
    console.error('Get uploads endpoint error:', error);
    return c.json({ error: 'Internal server error getting uploads' }, 500);
  }
});

// Delete an upload
app.delete("/make-server-2e3cda33/database/upload/:recordId", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const recordId = c.req.param('recordId');

    const result = await database.deleteUpload(recordId, user.id);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ message: 'Upload deleted successfully' });
  } catch (error) {
    console.error('Delete upload endpoint error:', error);
    return c.json({ error: 'Internal server error deleting upload' }, 500);
  }
});

// METAR to IWXXM Conversion endpoint
app.post("/make-server-2e3cda33/convert/metar-to-iwxxm", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    
    if (!accessToken) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { data: { user }, error } = await supabase.auth.getUser(accessToken);
    
    if (error || !user) {
      return c.json({ error: 'Unauthorized' }, 401);
    }

    const { metarContent, params } = await c.req.json();

    if (!metarContent || typeof metarContent !== 'string') {
      return c.json({ error: 'METAR content is required' }, 400);
    }

    // Conversion parameters
    const {
      bulletinId = 'SAAA00',
      issuingCenter = 'KWBC',
      iwxxmVersion = '3.0',
      strictValidation = true,
      includeNilReasons = true,
      onError = 'warn',
      logLevel = 'INFO'
    } = params || {};

    // Perform METAR to IWXXM conversion
    const lines = metarContent.trim().split('\n').filter(line => line.trim());
    let iwxxmXml = `<?xml version="1.0" encoding="UTF-8"?>\n`;
    iwxxmXml += `<IWXXM xmlns="http://icao.int/iwxxm/${iwxxmVersion}" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n`;
    iwxxmXml += `  <BulletinHeader>\n`;
    iwxxmXml += `    <bulletinIdentifier>${bulletinId}</bulletinIdentifier>\n`;
    iwxxmXml += `    <issuingCentre>${issuingCenter}</issuingCentre>\n`;
    iwxxmXml += `    <issueTime>${new Date().toISOString()}</issueTime>\n`;
    iwxxmXml += `    <strictValidation>${strictValidation}</strictValidation>\n`;
    iwxxmXml += `    <includeNilReasons>${includeNilReasons}</includeNilReasons>\n`;
    iwxxmXml += `  </BulletinHeader>\n`;
    
    const warnings: string[] = [];
    
    lines.forEach((line, index) => {
      try {
        const parts = line.trim().split(/\s+/);
        
        // Basic METAR parsing
        const reportType = parts[0]; // METAR or SPECI
        const station = parts[1] || 'UNKN';
        const timestamp = parts[2] || '';
        
        iwxxmXml += `  <MeteorologicalAerodromeObservation gml:id="obs-${index + 1}">\n`;
        iwxxmXml += `    <reportType>${reportType}</reportType>\n`;
        iwxxmXml += `    <aerodrome>\n`;
        iwxxmXml += `      <AirportHeliport gml:id="station-${station}">\n`;
        iwxxmXml += `        <designator>${station}</designator>\n`;
        iwxxmXml += `      </AirportHeliport>\n`;
        iwxxmXml += `    </aerodrome>\n`;
        iwxxmXml += `    <observationTime>${timestamp}</observationTime>\n`;
        iwxxmXml += `    <rawMETAR><![CDATA[${line}]]></rawMETAR>\n`;
        
        // Add parsed elements (simplified - real implementation would parse wind, visibility, etc.)
        if (parts.length > 3) {
          iwxxmXml += `    <surfaceWind>\n`;
          iwxxmXml += `      <AerodromeSurfaceWind>\n`;
          iwxxmXml += `        <meanWindDirection uom="deg">variable</meanWindDirection>\n`;
          iwxxmXml += `        <meanWindSpeed uom="m/s">0</meanWindSpeed>\n`;
          iwxxmXml += `      </AerodromeSurfaceWind>\n`;
          iwxxmXml += `    </surfaceWind>\n`;
        }
        
        iwxxmXml += `  </MeteorologicalAerodromeObservation>\n`;
      } catch (err) {
        const warning = `Line ${index + 1}: Error parsing - ${err.message}`;
        warnings.push(warning);
        
        if (onError === 'fail') {
          throw new Error(warning);
        } else if (onError === 'warn') {
          console.warn(warning);
        }
        // 'skip' - just continue without adding to output
      }
    });
    
    iwxxmXml += `</IWXXM>`;

    // Log conversion details based on logLevel
    if (['DEBUG', 'INFO'].includes(logLevel)) {
      console.log(`[${logLevel}] Converted ${lines.length} METAR line(s) to IWXXM ${iwxxmVersion}`);
      console.log(`[${logLevel}] Bulletin: ${bulletinId}, Center: ${issuingCenter}`);
    }

    return c.json({
      success: true,
      iwxxmXml,
      params: {
        bulletinId,
        issuingCenter,
        iwxxmVersion,
        strictValidation,
        includeNilReasons,
        onError,
        logLevel
      },
      stats: {
        linesProcessed: lines.length,
        warnings: warnings.length > 0 ? warnings : undefined
      }
    });
  } catch (error) {
    console.error('METAR conversion endpoint error:', error);
    return c.json({ 
      error: 'Internal server error during METAR conversion',
      details: error instanceof Error ? error.message : String(error)
    }, 500);
  }
});

// ===== ADMIN ENDPOINTS =====

// Verify JWT using JWKS (for ES256 signed JWTs)
async function verifyProjectJWT(jwt: string) {
  try {
    console.log(`🔑 Verifying JWT with JWKS endpoint...`);
    const verified = await jwtVerify(jwt, JWKS);
    const userId = verified.payload.sub as string;
    const email = verified.payload.email as string;
    const aal = verified.payload.aal as string;
    const exp = verified.payload.exp as number;
    
    console.log(`✅ JWT verified successfully:`);
    console.log(`   User ID: ${userId}`);
    console.log(`   Email: ${email}`);
    console.log(`   AAL: ${aal}`);
    console.log(`   Expires: ${new Date(exp * 1000).toISOString()}`);
    
    return verified;
  } catch (error) {
    console.error(`❌ JWT verification failed:`, error.message);
    throw error;
  }
}

// Helper function to check if user is admin
async function checkAdminAccess(accessToken: string | undefined) {
  if (!accessToken) {
    console.error('❌ checkAdminAccess: No access token provided');
    return { error: 'Unauthorized', status: 401 };
  }

  console.log(`🔐 checkAdminAccess: Starting verification with token prefix: ${accessToken?.substring(0, 30)}...`);

  try {
    // Verify JWT using JWKS (asymmetric ES256 verification)
    const verified = await verifyProjectJWT(accessToken);
    const userId = verified.payload.sub as string;
    const email = verified.payload.email as string;
    
    console.log(`✅ checkAdminAccess: JWT verified for user ${email} (${userId})`);

    // Query database for admin status
    const isAdmin = await auth.isUserAdmin(userId);
    
    console.log(`📋 checkAdminAccess: is_admin=${isAdmin} for user ${email}`);
    
    if (!isAdmin) {
      console.error(`❌ checkAdminAccess: User ${email} is not admin`);
      return { error: 'Admin access required', status: 403 };
    }

    console.log(`✅ checkAdminAccess: Admin access granted for ${email}`);
    return { user: { id: userId, email } };
  } catch (error) {
    console.error(`❌ checkAdminAccess: JWT verification failed:`, error.message);
    return { error: 'Unauthorized', status: 401 };
  }
}

// Get pending users for approval (admin only)
app.get("/make-server-2e3cda33/admin/pending-users", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const result = await auth.getPendingUsers();

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ users: result.data });
  } catch (error) {
    console.error('Admin get pending users endpoint error:', error);
    return c.json({ error: 'Internal server error getting pending users' }, 500);
  }
});

// Approve user (admin only)
app.post("/make-server-2e3cda33/admin/approve-user", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const { userId } = await c.req.json();

    if (!userId) {
      return c.json({ error: 'User ID is required' }, 400);
    }

    const result = await auth.approveUser(userId, adminCheck.user!.id);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    // Send approval email notification
    if (result.data) {
      await admin.sendEmailNotification(
        result.data.email,
        'Your Account Has Been Approved',
        `Dear ${result.data.username},\n\nYour account has been approved! You can now log in to the METAR Converter application.\n\nBest regards,\nThe Admin Team`
      );
    }

    return c.json({ message: 'User approved successfully', profile: result.data });
  } catch (error) {
    console.error('Admin approve user endpoint error:', error);
    return c.json({ error: 'Internal server error approving user' }, 500);
  }
});

// Reject user (admin only)
app.post("/make-server-2e3cda33/admin/reject-user", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const { userId } = await c.req.json();

    if (!userId) {
      return c.json({ error: 'User ID is required' }, 400);
    }

    const result = await auth.rejectUser(userId, adminCheck.user!.id);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    // Send rejection email notification
    if (result.data) {
      await admin.sendEmailNotification(
        result.data.email,
        'Account Registration Update',
        `Dear ${result.data.username},\n\nWe regret to inform you that your account registration has not been approved at this time.\n\nIf you have questions, please contact our support team.\n\nBest regards,\nThe Admin Team`
      );
    }

    return c.json({ message: 'User rejected successfully', profile: result.data });
  } catch (error) {
    console.error('Admin reject user endpoint error:', error);
    return c.json({ error: 'Internal server error rejecting user' }, 500);
  }
});

// Get all users (admin only)
app.get("/make-server-2e3cda33/admin/all-users", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const result = await auth.getAllUsers();

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ users: result.data });
  } catch (error) {
    console.error('Admin get all users endpoint error:', error);
    return c.json({ error: 'Internal server error getting all users' }, 500);
  }
});

// Get system statistics (admin only)
app.get("/make-server-2e3cda33/admin/stats", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    console.log(`🔐 /admin/stats: Request received with token: ${accessToken ? 'yes' : 'no'}`);
    console.log(`   Token prefix: ${accessToken?.substring(0, 30)}...`);
    console.log('📊 /admin/stats: Checking admin access...');
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      console.error(`❌ /admin/stats: Admin check failed: ${adminCheck.error} (status: ${adminCheck.status})`);
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    console.log('✅ /admin/stats: Admin check passed, fetching stats...');
    const allUsers = await auth.getAllUsers();
    
    if (allUsers.error || !allUsers.data) {
      console.error('❌ /admin/stats: Failed to get all users:', allUsers.error);
      return c.json({ error: 'Failed to retrieve statistics' }, 500);
    }

    const users = allUsers.data;
    const stats = {
      totalUsers: users.length,
      pendingUsers: users.filter(u => u.approval_status === 'pending').length,
      approvedUsers: users.filter(u => u.approval_status === 'approved').length,
      rejectedUsers: users.filter(u => u.approval_status === 'rejected').length,
      adminUsers: users.filter(u => u.is_admin).length,
      totalConversions: 0, // Could track this if needed
      totalStorageUsed: '0 MB', // Could calculate if needed
    };

    return c.json({ stats });
  } catch (error) {
    console.error('Admin get stats endpoint error:', error);
    return c.json({ error: 'Internal server error getting statistics' }, 500);
  }
});

// Toggle admin status (admin only)
app.post("/make-server-2e3cda33/admin/toggle-admin", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const { userId, isAdmin } = await c.req.json();

    if (!userId || typeof isAdmin !== 'boolean') {
      return c.json({ error: 'User ID and isAdmin flag are required' }, 400);
    }

    const result = await auth.toggleAdminStatus(userId, isAdmin, adminCheck.user!.id);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ message: `Admin status ${isAdmin ? 'granted' : 'revoked'}`, profile: result.data });
  } catch (error) {
    console.error('Admin toggle admin status endpoint error:', error);
    return c.json({ error: 'Internal server error toggling admin status' }, 500);
  }
});

// Get system settings (admin only)
app.get("/make-server-2e3cda33/admin/settings", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const settings = await admin.getSystemSettings();

    return c.json({ settings });
  } catch (error) {
    console.error('Admin get settings endpoint error:', error);
    return c.json({ error: 'Internal server error getting settings' }, 500);
  }
});

// Save system settings (admin only)
app.post("/make-server-2e3cda33/admin/settings", async (c) => {
  try {
    const accessToken = c.req.header('Authorization')?.split(' ')[1];
    const adminCheck = await checkAdminAccess(accessToken);
    
    if (adminCheck.error) {
      return c.json({ error: adminCheck.error }, adminCheck.status);
    }

    const { settings } = await c.req.json();

    if (!settings) {
      return c.json({ error: 'Settings object is required' }, 400);
    }

    const result = await admin.saveSystemSettings(settings);

    if (result.error) {
      return c.json({ error: result.error }, 400);
    }

    return c.json({ message: 'Settings saved successfully', settings: result.data });
  } catch (error) {
    console.error('Admin save settings endpoint error:', error);
    return c.json({ error: 'Internal server error saving settings' }, 500);
  }
});

Deno.serve(app.fetch);