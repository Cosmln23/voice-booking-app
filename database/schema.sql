-- ============================================================================
-- VOICE BOOKING APP - SUPABASE SCHEMA
-- FAZA 2: Database Integration
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- USERS TABLE
-- ============================================================================
CREATE TABLE public.users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email TEXT UNIQUE NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    role TEXT NOT NULL DEFAULT 'staff' CHECK (role IN ('admin', 'staff', 'owner')),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- ============================================================================
-- CLIENTS TABLE
-- ============================================================================
CREATE TABLE public.clients (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    phone TEXT NOT NULL CHECK (phone ~ '^\+?[1-9]\d{1,14}$'),
    email TEXT CHECK (email IS NULL OR email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    notes TEXT CHECK (length(notes) <= 500),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    avatar TEXT, -- URL or initials
    total_appointments INTEGER DEFAULT 0,
    last_appointment TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SERVICES TABLE
-- ============================================================================
CREATE TABLE public.services (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    price DECIMAL(10,2) NOT NULL CHECK (price > 0),
    currency TEXT NOT NULL DEFAULT 'RON',
    duration TEXT NOT NULL CHECK (duration ~ '^\d+min$'),
    category TEXT NOT NULL DEFAULT 'individual' CHECK (category IN ('individual', 'package')),
    description TEXT CHECK (length(description) <= 500),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    popularity_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- APPOINTMENTS TABLE
-- ============================================================================
CREATE TABLE public.appointments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    client_id UUID REFERENCES public.clients(id) ON DELETE CASCADE,
    service_id UUID REFERENCES public.services(id) ON DELETE SET NULL,
    client_name TEXT NOT NULL CHECK (length(client_name) >= 1 AND length(client_name) <= 100),
    phone TEXT NOT NULL CHECK (phone ~ '^\+?[1-9]\d{1,14}$'),
    service_name TEXT NOT NULL CHECK (length(service_name) >= 1 AND length(service_name) <= 100),
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration TEXT NOT NULL CHECK (duration ~ '^\d+min$'),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('confirmed', 'pending', 'in-progress', 'completed', 'cancelled', 'no-show')),
    type TEXT NOT NULL DEFAULT 'manual' CHECK (type IN ('voice', 'manual')),
    priority TEXT NOT NULL DEFAULT 'normal' CHECK (priority IN ('urgent', 'high', 'normal')),
    notes TEXT CHECK (length(notes) <= 500),
    price TEXT, -- Only for completed appointments (e.g., "120 RON")
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint to prevent double booking
    UNIQUE(appointment_date, appointment_time)
);

-- ============================================================================
-- BUSINESS SETTINGS TABLE
-- ============================================================================
CREATE TABLE public.business_settings (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(name) >= 1 AND length(name) <= 100),
    address TEXT NOT NULL CHECK (length(address) >= 1 AND length(address) <= 200),
    phone TEXT NOT NULL CHECK (phone ~ '^\+?[1-9]\d{1,14}$'),
    email TEXT NOT NULL CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    timezone TEXT NOT NULL DEFAULT 'Europe/Bucharest',
    settings_data JSONB DEFAULT '{}', -- Store working hours, notifications, agent config
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- AGENT ACTIVITY LOG TABLE
-- ============================================================================
CREATE TABLE public.agent_activity_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    type TEXT NOT NULL CHECK (type IN ('incoming_call', 'booking_success', 'booking_failed', 'system_status')),
    message TEXT NOT NULL,
    client_info TEXT,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON public.users(email);
CREATE INDEX idx_users_role ON public.users(role);

-- Clients indexes
CREATE INDEX idx_clients_name ON public.clients(name);
CREATE INDEX idx_clients_phone ON public.clients(phone);
CREATE INDEX idx_clients_email ON public.clients(email);
CREATE INDEX idx_clients_status ON public.clients(status);

-- Services indexes
CREATE INDEX idx_services_name ON public.services(name);
CREATE INDEX idx_services_category ON public.services(category);
CREATE INDEX idx_services_status ON public.services(status);
CREATE INDEX idx_services_popularity ON public.services(popularity_score DESC);

-- Appointments indexes
CREATE INDEX idx_appointments_client_id ON public.appointments(client_id);
CREATE INDEX idx_appointments_service_id ON public.appointments(service_id);
CREATE INDEX idx_appointments_date ON public.appointments(appointment_date);
CREATE INDEX idx_appointments_status ON public.appointments(status);
CREATE INDEX idx_appointments_type ON public.appointments(type);
CREATE INDEX idx_appointments_datetime ON public.appointments(appointment_date, appointment_time);

-- Agent activity log indexes
CREATE INDEX idx_agent_log_timestamp ON public.agent_activity_log(timestamp DESC);
CREATE INDEX idx_agent_log_type ON public.agent_activity_log(type);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_clients_updated_at BEFORE UPDATE ON public.clients FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON public.services FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_appointments_updated_at BEFORE UPDATE ON public.appointments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_business_settings_updated_at BEFORE UPDATE ON public.business_settings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FUNCTIONS FOR CLIENT APPOINTMENT STATS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_client_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Update client stats when appointment is created
        UPDATE public.clients SET 
            total_appointments = (
                SELECT COUNT(*) 
                FROM public.appointments 
                WHERE client_id = NEW.client_id
            ),
            last_appointment = (
                SELECT MAX(appointment_date) 
                FROM public.appointments 
                WHERE client_id = NEW.client_id
            )
        WHERE id = NEW.client_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        -- Update client stats when appointment is deleted
        UPDATE public.clients SET 
            total_appointments = (
                SELECT COUNT(*) 
                FROM public.appointments 
                WHERE client_id = OLD.client_id
            ),
            last_appointment = (
                SELECT MAX(appointment_date) 
                FROM public.appointments 
                WHERE client_id = OLD.client_id
            )
        WHERE id = OLD.client_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_client_appointment_stats 
    AFTER INSERT OR DELETE ON public.appointments 
    FOR EACH ROW EXECUTE FUNCTION update_client_stats();

-- ============================================================================
-- INSERT DEFAULT BUSINESS SETTINGS
-- ============================================================================

INSERT INTO public.business_settings (name, address, phone, email, settings_data) VALUES (
    'Salon Clasic',
    'Str. Victoriei nr. 25, București, România',
    '+40721234567',
    'contact@salonclasic.ro',
    '{
        "working_hours": [
            {"day_of_week": 0, "start_time": "09:00", "end_time": "18:00", "is_closed": false},
            {"day_of_week": 1, "start_time": "09:00", "end_time": "18:00", "is_closed": false},
            {"day_of_week": 2, "start_time": "09:00", "end_time": "18:00", "is_closed": false},
            {"day_of_week": 3, "start_time": "09:00", "end_time": "18:00", "is_closed": false},
            {"day_of_week": 4, "start_time": "09:00", "end_time": "19:00", "is_closed": false},
            {"day_of_week": 5, "start_time": "10:00", "end_time": "16:00", "is_closed": false},
            {"day_of_week": 6, "start_time": "09:00", "end_time": "17:00", "is_closed": true}
        ],
        "notifications": {
            "email_notifications": true,
            "sms_notifications": false,
            "appointment_reminders": true,
            "new_booking_alerts": true,
            "system_updates": true
        },
        "agent_config": {
            "enabled": false,
            "model": "gpt-4o-realtime-preview",
            "language": "ro-RO",
            "voice": "nova",
            "auto_booking": false,
            "confirmation_required": true
        }
    }'
);

-- ============================================================================
-- SCHEMA CREATION COMPLETE
-- ============================================================================