'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabase';

export default function Home() {
  const [dbStatus, setDbStatus] = useState<string>('Checking Supabase connection...');

  useEffect(() => {
    const checkSupabase = async () => {
      try {
        // Simple auth check to verify network & keys
        const { error } = await supabase.auth.getSession();
        if (error) throw error;
        setDbStatus('Connected to Supabase ✓');
      } catch (err: any) {
        setDbStatus(`Error connecting to Supabase: ${err.message}`);
      }
    };
    checkSupabase();
  }, []);

  return (
    <div style={{ backgroundColor: '#0a1628' }} className="min-h-screen flex flex-col items-center justify-center text-white p-4 text-center">
      <h1 style={{ color: '#c9a84c' }} className="text-5xl md:text-7xl font-bold mb-8 tracking-tight">
        CMA AutoFill
      </h1>
      <h2 className="text-2xl md:text-3xl font-light mb-12 opacity-90">
        Coming Soon
      </h2>
      <div className="absolute bottom-8 left-0 right-0 text-center">
        <p className={`text-sm ${dbStatus.includes('✓') ? 'text-green-400' : 'text-red-400'}`}>
          {dbStatus}
        </p>
      </div>
    </div>
  );
}
