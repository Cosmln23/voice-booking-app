-- ============================================================================
-- RLS POLICIES FOR SECURITY
-- FAZA 2: Database Integration - Security Layer
-- ============================================================================

-- Enable Row Level Security on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.services ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.business_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_activity_log ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- USERS TABLE POLICIES
-- ============================================================================

-- Allow authenticated users to read their own data
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.uid()::text = id::text);

-- Allow authenticated users to update their own data
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Allow admin/owner roles to manage all users
CREATE POLICY "Admins can manage all users" ON public.users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'owner')
        )
    );

-- ============================================================================
-- CLIENTS TABLE POLICIES
-- ============================================================================

-- Allow authenticated staff to view all clients
CREATE POLICY "Staff can view all clients" ON public.clients
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Allow authenticated staff to create clients
CREATE POLICY "Staff can create clients" ON public.clients
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Allow authenticated staff to update clients
CREATE POLICY "Staff can update clients" ON public.clients
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Only admin/owner can delete clients
CREATE POLICY "Admins can delete clients" ON public.clients
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'owner')
        )
    );

-- ============================================================================
-- SERVICES TABLE POLICIES
-- ============================================================================

-- Allow everyone to read active services
CREATE POLICY "Everyone can view active services" ON public.services
    FOR SELECT USING (status = 'active');

-- Allow authenticated users to view all services
CREATE POLICY "Staff can view all services" ON public.services
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Only admin/owner can manage services
CREATE POLICY "Admins can manage services" ON public.services
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'owner')
        )
    );

-- ============================================================================
-- APPOINTMENTS TABLE POLICIES
-- ============================================================================

-- Allow authenticated staff to view all appointments
CREATE POLICY "Staff can view all appointments" ON public.appointments
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Allow authenticated staff to create appointments
CREATE POLICY "Staff can create appointments" ON public.appointments
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Allow authenticated staff to update appointments
CREATE POLICY "Staff can update appointments" ON public.appointments
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Only admin/owner can delete appointments
CREATE POLICY "Admins can delete appointments" ON public.appointments
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'owner')
        )
    );

-- ============================================================================
-- BUSINESS SETTINGS TABLE POLICIES
-- ============================================================================

-- Allow authenticated users to read business settings
CREATE POLICY "Staff can view business settings" ON public.business_settings
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Only admin/owner can modify business settings
CREATE POLICY "Admins can manage business settings" ON public.business_settings
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'owner')
        )
    );

-- ============================================================================
-- AGENT ACTIVITY LOG TABLE POLICIES
-- ============================================================================

-- Allow authenticated users to read agent logs
CREATE POLICY "Staff can view agent logs" ON public.agent_activity_log
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND is_active = true
        )
    );

-- Allow system to insert agent logs
CREATE POLICY "System can create agent logs" ON public.agent_activity_log
    FOR INSERT WITH CHECK (true);

-- Only admin/owner can delete agent logs
CREATE POLICY "Admins can manage agent logs" ON public.agent_activity_log
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM public.users 
            WHERE id::text = auth.uid()::text 
            AND role IN ('admin', 'owner')
        )
    );

-- ============================================================================
-- ANONYMOUS ACCESS POLICIES (for voice bookings)
-- ============================================================================

-- Allow anonymous users to create appointments (voice bookings)
-- This policy is more permissive for voice integration
CREATE POLICY "Anonymous voice bookings allowed" ON public.appointments
    FOR INSERT WITH CHECK (
        type = 'voice' AND 
        status = 'pending'
    );

-- Allow anonymous users to read active services for voice bookings
-- This enables voice agent to access service catalog
CREATE POLICY "Anonymous can view services for voice" ON public.services
    FOR SELECT USING (status = 'active');

-- ============================================================================
-- RLS POLICIES SETUP COMPLETE
-- ============================================================================