import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
  auth: { 
    persistSession: true, 
    autoRefreshToken: true, 
    detectSessionInUrl: false 
  },
})

export async function ensureSession() {
  const { data: { session } } = await supabase.auth.getSession()
  if (!session) {
    // Login anonymous provizoriu sau sign-in cu email existent
    const { data, error } = await supabase.auth.signInWithPassword({
      email: 'scinterim09@gmail.com',
      password: 'temporary123' // sau orice parolă pentru acest user
    })
    if (error) {
      // Fallback la anonymous
      const { data: anonData, error: anonError } = await supabase.auth.signInAnonymously()
      if (anonError) throw anonError
      return anonData.session
    }
    return data.session
  }
  return session
}

export async function getAuthHeaders() {
  const session = await ensureSession()
  return {
    Authorization: `Bearer ${session?.access_token}`,
    'Content-Type': 'application/json'
  }
}