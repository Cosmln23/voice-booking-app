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
    await supabase.auth.signInAnonymously()
  }
}

export async function getAccessToken() {
  await ensureSession()
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token ?? ''
}

export async function getAuthHeaders() {
  const token = await getAccessToken()
  return {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
}