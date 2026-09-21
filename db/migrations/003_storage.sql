-- ============================================================
-- RAMS AI Demo — 003_storage.sql
-- Storage buckets + access policies per PRD §14:
--   company-assets  : public (company logos shown in UI)
--   rams-documents  : private (downloads ONLY via backend signed URLs)
-- Path convention: {user_id}/... (PRD §14)
-- Run AFTER 002_rls.sql
-- ============================================================

-- ---------- Buckets ----------
insert into storage.buckets (id, name, public)
values ('company-assets', 'company-assets', true)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('rams-documents', 'rams-documents', false)
on conflict (id) do nothing;

-- ---------- company-assets: owner-only write, public read ----------
drop policy if exists "company_assets_public_read" on storage.objects;
create policy "company_assets_public_read"
  on storage.objects for select
  using (bucket_id = 'company-assets');

drop policy if exists "company_assets_owner_insert" on storage.objects;
create policy "company_assets_owner_insert"
  on storage.objects for insert
  with check (
    bucket_id = 'company-assets'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "company_assets_owner_update" on storage.objects;
create policy "company_assets_owner_update"
  on storage.objects for update
  using (
    bucket_id = 'company-assets'
    and auth.uid()::text = (storage.foldername(name))[1]
  )
  with check (
    bucket_id = 'company-assets'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

drop policy if exists "company_assets_owner_delete" on storage.objects;
create policy "company_assets_owner_delete"
  on storage.objects for delete
  using (
    bucket_id = 'company-assets'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

-- ---------- rams-documents: NO client policies ----------
-- Zero policies for rams-documents means anon/authenticated clients are
-- fully denied. The backend (service role) bypasses RLS and is the only
-- writer/reader; users download via authenticated endpoint returning
-- short-lived signed URLs (PRD §15). This guarantees cross-user file
-- isolation (Risk 5, PRD §55).
