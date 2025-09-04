'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Dashboard from '../page';

export default function AdminPage() {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Auth error:', error);
          router.push('/login');
          return;
        }

        if (!session) {
          router.push('/login');
          return;
        }

        setAuthenticated(true);
      } catch (error) {
        console.error('Session check error:', error);
        router.push('/login');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === 'SIGNED_OUT' || !session) {
        router.push('/login');
        setAuthenticated(false);
      } else if (event === 'SIGNED_IN' && session) {
        setAuthenticated(true);
      }
    });

    return () => subscription.unsubscribe();
  }, [router]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Se verifică autentificarea...</p>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!authenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="text-muted-foreground">Redirecționare către login...</p>
        </div>
      </div>
    );
  }

  // Authenticated - render dashboard
  return <Dashboard />;
}