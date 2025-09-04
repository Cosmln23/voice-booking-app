'use client';

import { useEffect } from 'react';
import { ensureSession } from '@/lib/auth';

export default function SessionProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    ensureSession();
  }, []);

  return <>{children}</>;
}