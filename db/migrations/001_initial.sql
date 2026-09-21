-- ============================================================
-- RAMS AI Demo — 001_initial.sql
-- Core tables per PRD §25 + stripe_events (webhook idempotency §16)
-- Run in Supabase SQL Editor (database: public schema)
-- ============================================================

-- ---------- Helper: updated_at trigger ----------
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ---------- profiles ----------
create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  email text,
  full_name text,
  company_name text,
  company_address text,
  company_postcode text,
  company_phone text,
  logo_path text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_profiles_updated_at on public.profiles;
create trigger trg_profiles_updated_at
  before update on public.profiles
  for each row execute function public.set_updated_at();

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'full_name', '')
  );
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------- subscriptions ----------
-- One row per user; webhook upserts keep it in sync (idempotent by design).
create table if not exists public.subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users (id) on delete cascade,
  stripe_customer_id text,
  stripe_subscription_id text unique,
  stripe_price_id text,
  status text not null,
  current_period_start timestamptz,
  current_period_end timestamptz,
  cancel_at_period_end boolean not null default false,
  canceled_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_subscriptions_stripe_customer
  on public.subscriptions (stripe_customer_id);

drop trigger if exists trg_subscriptions_updated_at on public.subscriptions;
create trigger trg_subscriptions_updated_at
  before update on public.subscriptions
  for each row execute function public.set_updated_at();

-- ---------- rams ----------
-- status: draft | generating | ready | failed
create table if not exists public.rams (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  document_number text,
  project_name text not null,
  site_address text,
  client_name text,
  project_reference text,
  status text not null default 'draft',
  input_data jsonb not null default '{}'::jsonb,
  generated_data jsonb,
  docx_path text,
  pdf_path text,
  generation_error text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_rams_user_created
  on public.rams (user_id, created_at desc);

drop trigger if exists trg_rams_updated_at on public.rams;
create trigger trg_rams_updated_at
  before update on public.rams
  for each row execute function public.set_updated_at();

-- ---------- generation_jobs ----------
-- status: pending | running | succeeded | failed
create table if not exists public.generation_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  rams_id uuid not null references public.rams (id) on delete cascade,
  status text not null default 'pending',
  attempts integer not null default 0,
  started_at timestamptz,
  completed_at timestamptz,
  error_code text,
  error_message text,
  created_at timestamptz not null default now()
);

create index if not exists idx_generation_jobs_rams
  on public.generation_jobs (rams_id);
create index if not exists idx_generation_jobs_user_status
  on public.generation_jobs (user_id, status);

-- Partial unique index: only ONE active job per RAMS (duplicate generation
-- protection, PRD §44). Partial index allows historical failed/succeeded rows.
create unique index if not exists uq_generation_jobs_active_per_rams
  on public.generation_jobs (rams_id)
  where status in ('pending', 'running');

-- ---------- stripe_events (webhook idempotency, PRD §16) ----------
create table if not exists public.stripe_events (
  id text primary key,                      -- Stripe event id (evt_...)
  type text not null,
  processed_at timestamptz not null default now()
);
