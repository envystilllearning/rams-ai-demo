-- ============================================================
-- RAMS AI Demo — 002_rls.sql
-- Row Level Security per PRD §26:
-- users can only access their own records.
-- Backend uses service-role key which bypasses RLS.
-- Run AFTER 001_initial.sql
-- ============================================================

alter table public.profiles enable row level security;
alter table public.subscriptions enable row level security;
alter table public.rams enable row level security;
alter table public.generation_jobs enable row level security;
alter table public.stripe_events enable row level security;

-- ---------- profiles: own profile only ----------
drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own"
  on public.profiles for select
  using (auth.uid() = id);

drop policy if exists "profiles_insert_own" on public.profiles;
create policy "profiles_insert_own"
  on public.profiles for insert
  with check (auth.uid() = id);

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- No delete policy: profiles are not deletable via client API.

-- ---------- subscriptions: own subscription only ----------
drop policy if exists "subscriptions_select_own" on public.subscriptions;
create policy "subscriptions_select_own"
  on public.subscriptions for select
  using (auth.uid() = user_id);

-- No insert/update/delete via client: subscription rows are written
-- exclusively by the backend (service role) from verified Stripe webhooks.

-- ---------- rams: own RAMS only ----------
drop policy if exists "rams_select_own" on public.rams;
create policy "rams_select_own"
  on public.rams for select
  using (auth.uid() = user_id);

drop policy if exists "rams_insert_own" on public.rams;
create policy "rams_insert_own"
  on public.rams for insert
  with check (auth.uid() = user_id);

drop policy if exists "rams_update_own" on public.rams;
create policy "rams_update_own"
  on public.rams for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "rams_delete_own" on public.rams;
create policy "rams_delete_own"
  on public.rams for delete
  using (auth.uid() = user_id);

-- ---------- generation_jobs: own jobs only ----------
drop policy if exists "generation_jobs_select_own" on public.generation_jobs;
create policy "generation_jobs_select_own"
  on public.generation_jobs for select
  using (auth.uid() = user_id);

drop policy if exists "generation_jobs_insert_own" on public.generation_jobs;
create policy "generation_jobs_insert_own"
  on public.generation_jobs for insert
  with check (auth.uid() = user_id);

-- Job state transitions (pending -> running -> succeeded/failed) are owned
-- by the backend; no update policy for the client on purpose.

-- ---------- stripe_events: no client access at all ----------
-- Table is only touched by backend service role. RLS enabled above with
-- zero policies = fully denied for anon/authenticated clients.
