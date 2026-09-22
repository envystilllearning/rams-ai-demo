"use client";

import { createClient } from "@/lib/supabase/client";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** Authenticated fetch to the FastAPI backend with the Supabase access token. */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();

  if (!session) {
    throw new Error("Not authenticated");
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session.access_token}`,
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail || `Request failed (${res.status})`);
  }

  return res.json() as Promise<T>;
}

export interface Profile {
  id: string;
  email: string | null;
  full_name: string | null;
  company_name: string | null;
  company_address: string | null;
  company_postcode: string | null;
  company_phone: string | null;
  logo_path: string | null;
  created_at: string | null;
  updated_at: string | null;
}
