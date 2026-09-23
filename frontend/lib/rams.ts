"use client";

import { apiFetch } from "@/lib/api";

export interface RamsInput {
  project_name: string;
  site_address: string;
  client_name: string;
  project_reference: string;
  start_date: string;
  planned_duration: string;
  work_description: string;
  work_location: string;
  materials: string;
  equipment: string;
  plant: string;
  tools: string;
  personnel: string;
  ppe: string;
  known_hazards: string;
  site_restrictions: string;
  existing_controls: string;
  emergency_info: string;
  additional_notes: string;
}

export interface Rams {
  id: string;
  document_number: string | null;
  project_name: string;
  site_address: string | null;
  client_name: string | null;
  project_reference: string | null;
  status: string;
  input_data: Record<string, unknown>;
  generated_data: Record<string, unknown> | null;
  docx_path: string | null;
  pdf_path: string | null;
  generation_error: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export const EMPTY_INPUT: RamsInput = {
  project_name: "",
  site_address: "",
  client_name: "",
  project_reference: "",
  start_date: "",
  planned_duration: "",
  work_description: "",
  work_location: "",
  materials: "",
  equipment: "",
  plant: "",
  tools: "",
  personnel: "",
  ppe: "",
  known_hazards: "",
  site_restrictions: "",
  existing_controls: "",
  emergency_info: "",
  additional_notes: "",
};

export function listRams(limit = 20, offset = 0) {
  return apiFetch<{ items: Rams[]; total: number }>(
    `/api/rams?limit=${limit}&offset=${offset}`
  );
}

export function createRams(input: RamsInput) {
  // Send only non-empty fields to keep payloads lean
  const payload: Record<string, string> = {};
  for (const [k, v] of Object.entries(input)) {
    if (v && v.trim()) payload[k] = v.trim();
  }
  return apiFetch<Rams>("/api/rams", { method: "POST", body: JSON.stringify(payload) });
}

export function getRams(id: string) {
  return apiFetch<Rams>(`/api/rams/${id}`);
}

export async function deleteRams(id: string) {
  const { createClient } = await import("@/lib/supabase/client");
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) throw new Error("Not authenticated");
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/rams/${id}`, {
    method: "DELETE",
    headers: { Authorization: `Bearer ${session.access_token}` },
  });
  if (!res.ok) throw new Error(`Delete failed (${res.status})`);
}
