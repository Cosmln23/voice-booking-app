-- ============================================================================
-- SEED DATA FOR VOICE BOOKING APP
-- FAZA 2: Database Integration - Test Data
-- ============================================================================

-- ============================================================================
-- SEED SERVICES
-- ============================================================================
INSERT INTO public.services (id, name, price, currency, duration, category, description, status, popularity_score) VALUES
(gen_random_uuid(), 'Tunsoare Clasică', 35.00, 'RON', '45min', 'individual', 'Tunsoare clasică pentru bărbați cu foarfecă și mașină', 'active', 85.5),
(gen_random_uuid(), 'Barbă Completă', 25.00, 'RON', '30min', 'individual', 'Aranjare și modelarea completă a bărbii', 'active', 72.3),
(gen_random_uuid(), 'Pachet Completă', 120.00, 'RON', '90min', 'package', 'Tunsoare + Barbă + Spălat + Styling complet', 'active', 95.2),
(gen_random_uuid(), 'Pachet Premium', 150.00, 'RON', '120min', 'package', 'Servicii complete + masaj facial + tratament păr', 'active', 68.9),
(gen_random_uuid(), 'Doar Spălat', 15.00, 'RON', '15min', 'individual', 'Spălat și uscat păr', 'active', 45.1),
(gen_random_uuid(), 'Tunsoare Retro', 40.00, 'RON', '60min', 'individual', 'Tunsoare în stil retro cu brici clasic', 'inactive', 32.4);

-- ============================================================================
-- SEED CLIENTS
-- ============================================================================
INSERT INTO public.clients (id, name, phone, email, notes, status, avatar, total_appointments, last_appointment) VALUES
(gen_random_uuid(), 'Alexandru Popescu', '+40721123456', 'alex.popescu@email.com', 'Client VIP, preferă programări dimineața', 'active', 'AP', 12, NOW() - INTERVAL '2 days'),
(gen_random_uuid(), 'Maria Ionescu', '+40722234567', 'maria.ionescu@email.com', NULL, 'active', 'MI', 8, NOW() - INTERVAL '1 week'),
(gen_random_uuid(), 'Ion Georgescu', '+40723345678', NULL, 'Doar tuns, niciodată barbă', 'active', 'IG', 15, NOW() - INTERVAL '3 days'),
(gen_random_uuid(), 'Elena Vasile', '+40724456789', 'elena.v@email.com', NULL, 'inactive', 'EV', 3, NOW() - INTERVAL '2 months'),
(gen_random_uuid(), 'Mihai Dumitrescu', '+40725567890', 'mihai.dumitrescu@email.com', 'Client nou, foarte punctual', 'active', 'MD', 2, NOW() - INTERVAL '5 days');

-- ============================================================================
-- SEED APPOINTMENTS
-- ============================================================================

-- Get service and client IDs for appointments
DO $$
DECLARE
    client_alex_id UUID;
    client_maria_id UUID;
    client_ion_id UUID;
    client_elena_id UUID;
    service_tuns_id UUID;
    service_barba_id UUID;
    service_complet_id UUID;
BEGIN
    -- Get client IDs
    SELECT id INTO client_alex_id FROM public.clients WHERE name = 'Alexandru Popescu';
    SELECT id INTO client_maria_id FROM public.clients WHERE name = 'Maria Ionescu';
    SELECT id INTO client_ion_id FROM public.clients WHERE name = 'Ion Georgescu';
    SELECT id INTO client_elena_id FROM public.clients WHERE name = 'Elena Vasile';
    
    -- Get service IDs
    SELECT id INTO service_tuns_id FROM public.services WHERE name = 'Tunsoare Clasică';
    SELECT id INTO service_barba_id FROM public.services WHERE name = 'Barbă Completă';
    SELECT id INTO service_complet_id FROM public.services WHERE name = 'Pachet Completă';
    
    -- Insert appointments
    INSERT INTO public.appointments (
        id, client_id, service_id, client_name, phone, service_name, 
        appointment_date, appointment_time, duration, status, type, priority, notes, price
    ) VALUES
    -- Today's appointments
    (gen_random_uuid(), client_alex_id, service_tuns_id, 'Alexandru Popescu', '+40721123456', 'Tunsoare Clasică', 
     CURRENT_DATE, '09:00', '45min', 'confirmed', 'voice', 'normal', 'Client preferat, punctual', NULL),
    
    (gen_random_uuid(), client_maria_id, service_barba_id, 'Maria Ionescu', '+40722234567', 'Barbă Completă', 
     CURRENT_DATE, '11:30', '30min', 'in-progress', 'manual', 'high', NULL, NULL),
    
    (gen_random_uuid(), client_ion_id, service_complet_id, 'Ion Georgescu', '+40723345678', 'Pachet Completă', 
     CURRENT_DATE, '14:00', '90min', 'completed', 'voice', 'normal', NULL, '120 RON'),
    
    (gen_random_uuid(), client_elena_id, service_tuns_id, 'Elena Vasile', '+40724456789', 'Tunsoare Clasică', 
     CURRENT_DATE, '16:30', '45min', 'pending', 'voice', 'urgent', 'Programare de urgență', NULL),
    
    -- Tomorrow's appointments
    (gen_random_uuid(), client_alex_id, service_complet_id, 'Alexandru Popescu', '+40721123456', 'Pachet Completă', 
     CURRENT_DATE + INTERVAL '1 day', '10:00', '90min', 'confirmed', 'manual', 'normal', NULL, NULL),
    
    (gen_random_uuid(), client_maria_id, service_tuns_id, 'Maria Ionescu', '+40722234567', 'Tunsoare Clasică', 
     CURRENT_DATE + INTERVAL '1 day', '15:00', '45min', 'confirmed', 'voice', 'normal', NULL, NULL),
    
    -- Past appointments
    (gen_random_uuid(), client_ion_id, service_tuns_id, 'Ion Georgescu', '+40723345678', 'Tunsoare Clasică', 
     CURRENT_DATE - INTERVAL '3 days', '11:00', '45min', 'completed', 'manual', 'normal', NULL, '35 RON'),
    
    (gen_random_uuid(), client_elena_id, service_barba_id, 'Elena Vasile', '+40724456789', 'Barbă Completă', 
     CURRENT_DATE - INTERVAL '1 week', '13:30', '30min', 'cancelled', 'voice', 'normal', 'Client a anulat', NULL),
    
    (gen_random_uuid(), NULL, NULL, 'Andrei Mihai', '+40726789012', 'Tunsoare Clasică', 
     CURRENT_DATE - INTERVAL '2 days', '16:00', '45min', 'no-show', 'voice', 'normal', 'Nu s-a prezentat', NULL);
END $$;

-- ============================================================================
-- SEED AGENT ACTIVITY LOG
-- ============================================================================
INSERT INTO public.agent_activity_log (timestamp, type, message, client_info, details) VALUES
(NOW() - INTERVAL '5 minutes', 'incoming_call', 'Apel primit de la +40721***456', 'Alexandru P.', 
 '{"duration": "2min 34s", "outcome": "success"}'::jsonb),

(NOW() - INTERVAL '12 minutes', 'booking_success', 'Programare confirmată pentru ' || CURRENT_DATE || ' la 14:00', 'Maria I.', 
 '{"service": "Tunsoare Clasică", "price": "35 RON"}'::jsonb),

(NOW() - INTERVAL '25 minutes', 'incoming_call', 'Apel primit de la +40722***789', 'Ion G.', 
 '{"duration": "1min 45s", "outcome": "success"}'::jsonb),

(NOW() - INTERVAL '43 minutes', 'booking_failed', 'Programare nereușită - slot ocupat', 'Elena V.', 
 '{"requested_time": "2024-08-31 15:00", "reason": "slot_occupied"}'::jsonb),

(NOW() - INTERVAL '1 hour 15 minutes', 'system_status', 'Agent vocal pornit', NULL, 
 '{"version": "1.0.0", "model": "gpt-4o-realtime-preview"}'::jsonb);

-- ============================================================================
-- UPDATE CLIENT STATS (trigger will handle this automatically for new appointments)
-- ============================================================================

-- Force update client stats for seeded data
UPDATE public.clients SET 
    total_appointments = (
        SELECT COUNT(*) 
        FROM public.appointments 
        WHERE client_id = clients.id
    ),
    last_appointment = (
        SELECT MAX(appointment_date) 
        FROM public.appointments 
        WHERE client_id = clients.id
    );

-- ============================================================================
-- SEED DATA INSERTION COMPLETE
-- ============================================================================