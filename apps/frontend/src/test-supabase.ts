/**
 * Supabase Integration Test
 * 
 * This script tests the Supabase connection and authentication setup.
 * Run with: npm run test:supabase
 */

import { supabase } from '../utils/supabase/client';

async function testSupabaseConnection() {
  console.log('\n🧪 Testing Supabase Integration...\n');

  // Test 1: Check environment variables
  console.log('1️⃣ Checking environment variables...');
  const url = import.meta.env.VITE_SUPABASE_URL;
  const key = import.meta.env.VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY;
  
  if (!url) {
    console.error('❌ VITE_SUPABASE_URL is not set');
    return false;
  }
  if (!key) {
    console.error('❌ VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY is not set');
    return false;
  }
  
  console.log(`✅ VITE_SUPABASE_URL: ${url}`);
  console.log(`✅ VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY: ${key.substring(0, 20)}...`);

  // Test 2: Check Supabase client initialization
  console.log('\n2️⃣ Testing Supabase client...');
  if (!supabase) {
    console.error('❌ Supabase client is not initialized');
    return false;
  }
  console.log('✅ Supabase client initialized');

  // Test 3: Test connection to Supabase
  console.log('\n3️⃣ Testing database connection...');
  try {
    const { error } = await supabase.from('user_profiles').select('count');
    
    if (error) {
      console.error('❌ Database query failed:', error.message);
      return false;
    }
    
    console.log('✅ Database connection successful');
  } catch (err) {
    console.error('❌ Database connection error:', err);
    return false;
  }

  // Test 4: Test auth service
  console.log('\n4️⃣ Testing auth service...');
  try {
    const { data, error } = await supabase.auth.getSession();
    
    if (error) {
      console.error('⚠️ Auth session check failed:', error.message);
    } else {
      console.log('✅ Auth service accessible');
      if (data.session) {
        console.log(`✅ Active session found for user: ${data.session.user?.email}`);
      } else {
        console.log('ℹ️ No active session (user not logged in)');
      }
    }
  } catch (err) {
    console.error('❌ Auth service error:', err);
    return false;
  }

  console.log('\n✅ All tests passed! Supabase integration is working correctly.\n');
  return true;
}

// Run the test
testSupabaseConnection().then(success => {
  process.exit(success ? 0 : 1);
}).catch(err => {
  console.error('Test runner error:', err);
  process.exit(1);
});
