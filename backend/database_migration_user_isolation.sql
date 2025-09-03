-- ===============================================
-- DATABASE MIGRATION: USER ISOLATION WITH RLS
-- Voice Booking App - Production-ready data isolation
-- ===============================================

-- PHASE 1: Add created_by columns to user-specific tables
-- ===============================================

-- Add created_by column to user-specific tables
ALTER TABLE clients ADD COLUMN IF NOT EXISTS created_by uuid;
ALTER TABLE services ADD COLUMN IF NOT EXISTS created_by uuid;
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS created_by uuid; 
ALTER TABLE business_settings ADD COLUMN IF NOT EXISTS created_by uuid;

-- PHASE 2: Populate existing data with fallback owner
-- ===============================================
-- This assigns existing data to a fallback UUID to prevent data loss
-- Replace 'YOUR_USER_UUID' with your actual admin user UUID from auth.users

-- Update existing records to have an owner (prevents RLS hiding them)
UPDATE clients SET created_by = COALESCE(created_by, '00000000-0000-0000-0000-000000000000'::uuid) 
WHERE created_by IS NULL;

UPDATE services SET created_by = COALESCE(created_by, '00000000-0000-0000-0000-000000000000'::uuid) 
WHERE created_by IS NULL;

UPDATE appointments SET created_by = COALESCE(created_by, '00000000-0000-0000-0000-000000000000'::uuid) 
WHERE created_by IS NULL;

UPDATE business_settings SET created_by = COALESCE(created_by, '00000000-0000-0000-0000-000000000000'::uuid) 
WHERE created_by IS NULL;

-- PHASE 3: Enable Row Level Security
-- ===============================================

ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE services ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_settings ENABLE ROW LEVEL SECURITY;

-- PHASE 4: Create RLS Policies for user isolation
-- ===============================================

-- CLIENTS table policies
CREATE POLICY "clients_read_own" ON clients
  FOR SELECT USING (created_by = auth.uid());
  
CREATE POLICY "clients_insert_own" ON clients
  FOR INSERT WITH CHECK (created_by = auth.uid());
  
CREATE POLICY "clients_update_own" ON clients
  FOR UPDATE USING (created_by = auth.uid());
  
CREATE POLICY "clients_delete_own" ON clients
  FOR DELETE USING (created_by = auth.uid());

-- SERVICES table policies  
CREATE POLICY "services_read_own" ON services
  FOR SELECT USING (created_by = auth.uid());
  
CREATE POLICY "services_insert_own" ON services
  FOR INSERT WITH CHECK (created_by = auth.uid());
  
CREATE POLICY "services_update_own" ON services
  FOR UPDATE USING (created_by = auth.uid());
  
CREATE POLICY "services_delete_own" ON services
  FOR DELETE USING (created_by = auth.uid());

-- APPOINTMENTS table policies
CREATE POLICY "appointments_read_own" ON appointments
  FOR SELECT USING (created_by = auth.uid());
  
CREATE POLICY "appointments_insert_own" ON appointments
  FOR INSERT WITH CHECK (created_by = auth.uid());
  
CREATE POLICY "appointments_update_own" ON appointments
  FOR UPDATE USING (created_by = auth.uid());
  
CREATE POLICY "appointments_delete_own" ON appointments
  FOR DELETE USING (created_by = auth.uid());

-- BUSINESS_SETTINGS table policies
CREATE POLICY "business_settings_read_own" ON business_settings
  FOR SELECT USING (created_by = auth.uid());
  
CREATE POLICY "business_settings_insert_own" ON business_settings
  FOR INSERT WITH CHECK (created_by = auth.uid());
  
CREATE POLICY "business_settings_update_own" ON business_settings
  FOR UPDATE USING (created_by = auth.uid());
  
CREATE POLICY "business_settings_delete_own" ON business_settings
  FOR DELETE USING (created_by = auth.uid());

-- PHASE 5: Auto-set created_by trigger function
-- ===============================================

-- Function to automatically set created_by on INSERT
CREATE OR REPLACE FUNCTION set_created_by()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  -- Only set created_by if it's not already provided
  IF NEW.created_by IS NULL THEN
    NEW.created_by := auth.uid();
  END IF;
  RETURN NEW;
END;
$$;

-- Apply triggers to all user-specific tables
CREATE TRIGGER trigger_clients_set_created_by
  BEFORE INSERT ON clients
  FOR EACH ROW EXECUTE PROCEDURE set_created_by();

CREATE TRIGGER trigger_services_set_created_by  
  BEFORE INSERT ON services
  FOR EACH ROW EXECUTE PROCEDURE set_created_by();

CREATE TRIGGER trigger_appointments_set_created_by
  BEFORE INSERT ON appointments
  FOR EACH ROW EXECUTE PROCEDURE set_created_by();

CREATE TRIGGER trigger_business_settings_set_created_by
  BEFORE INSERT ON business_settings  
  FOR EACH ROW EXECUTE PROCEDURE set_created_by();

-- ===============================================
-- VERIFICATION QUERIES (run after migration)
-- ===============================================

-- Check RLS is enabled
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN ('clients', 'services', 'appointments', 'business_settings');

-- Check policies exist
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies 
WHERE tablename IN ('clients', 'services', 'appointments', 'business_settings');

-- Check triggers exist  
SELECT trigger_name, event_object_table, action_timing, event_manipulation
FROM information_schema.triggers
WHERE trigger_name LIKE '%created_by%';

-- ===============================================
-- NOTES FOR IMPLEMENTATION:
-- ===============================================
-- 1. Run this script in Supabase SQL Editor
-- 2. Replace fallback UUID with real admin UUID if needed
-- 3. Test with different user logins to verify isolation
-- 4. Backend will need updates to pass user JWT to operations
-- 5. Agent tables (agent_state, agent_activity_log) remain shared
-- ===============================================