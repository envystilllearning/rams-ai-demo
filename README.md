# RAMS AI Demo

A demo B2B SaaS application for UK construction contractors: generate professional
Risk Assessments & Method Statements (RAMS) from structured project information with
AI-assisted content, then download production-style Word and PDF documents.

> **Demo disclaimer** — AI-generated RAMS are **draft documents** and must be
> reviewed and approved by a competent person before use. This is a portfolio
> demo; nothing produced here is legally or professionally certified.

## Overview

| | |
|---|---|
| Frontend | Next.js 15 (App Router) + TypeScript + Tailwind + shadcn/ui |
| Backend | FastAPI + Pydantic v2 + httpx |
| Auth | Supabase Auth (JWT verified server-side per request) |
| Database | Supabase PostgreSQL + Row Level Security |
| Storage | Supabase Storage (`company-assets`, `rams-documents`) |
| Payments | Stripe Checkout + Customer Portal + idempotent webhooks |
| AI | OpenRouter (OpenAI-compatible, structured JSON output) |
| Documents | python-docx + Gotenberg (LibreOffice) PDF conversion |
| Infra | Docker Compose (backend + Gotenberg) |

## Features

- Email/password authentication with protected dashboard
- Stripe recurring subscription (£9.95/month) with server-side entitlement enforcement
- Reusable company profile (name, address, logo) auto-filled into every RAMS
- 4-step guided RAMS creation wizard with client + server validation
- AI-assisted generation with strict Pydantic validation, bounded retries, and
  **atomic publishing** (a failed AI call never produces an incomplete document)
- Professional DOCX template + PDF conversion, stored persistently in Supabase Storage
- Authenticated downloads via short-lived signed URLs
- Duplicate-submission protection (one active generation job per RAMS)

## Architecture

```text
Next.js (Vercel)
  ↓  JWT
FastAPI (Docker)
  ├── Supabase Auth      → verify user
  ├── Supabase Postgres  → profiles / subscriptions / rams / generation_jobs
  ├── OpenRouter         → structured AI content (validated via Pydantic)
  ├── python-docx        → DOCX generation
  ├── Gotenberg (Docker) → DOCX → PDF
  └── Supabase Storage   → persistent file storage (signed URL downloads)

Stripe  ──webhooks──▶  FastAPI  ──▶  subscriptions table (idempotent)
```

## Project Structure

```text
rams-ai-demo/
├── frontend/            # Next.js app (Phase 1)
├── backend/             # FastAPI app (Phase 1)
├── db/migrations/       # SQL migrations, run in Supabase SQL Editor
├── docker-compose.yml   # backend + gotenberg
├── .env.example
└── README.md
```

## Screenshots

_TBD (Phase 17)_

## Demo Video

_TBD (Phase 17)_

## Local Development

_TBD (Phase 1)_

### 1. Database setup

Run these in order in the Supabase SQL Editor:

1. `db/migrations/001_initial.sql` — tables, triggers, indexes
2. `db/migrations/002_rls.sql` — Row Level Security policies
3. `db/migrations/003_storage.sql` — storage buckets + policies

### 2. Environment variables

Copy `.env.example`, fill in values from Supabase / Stripe / OpenRouter
dashboards. See `.env.example` comments for where each key comes from.

## Database Schema

| Table | Purpose |
|---|---|
| `profiles` | User + reusable company information (PRD §7) |
| `subscriptions` | Stripe subscription state, synced via webhooks (PRD §16) |
| `rams` | RAMS records: input, generated content, file paths, status |
| `generation_jobs` | Generation job tracking with duplicate protection (PRD §44) |
| `stripe_events` | Webhook event ids for idempotency (PRD §16) |

All user-facing tables are protected by RLS: users can only access their own rows.
`rams-documents` storage bucket has zero client policies — backend (service role) only.

## Stripe Setup

_TBD (Phase 7)_

## AI Generation

_TBD (Phase 9)_

## Document Generation

_TBD (Phase 10–11)_

## Testing

_TBD (Phase 14)_

## Deployment

_TBD (Phase 16)_

## Security

- Secrets live only in environment variables; `.env` is gitignored
- Backend verifies Supabase JWT on every protected request
- Server-side subscription enforcement — the frontend is never trusted for authorization
- Stripe webhook signature verification + idempotent handlers (`stripe_events` table)
- RLS on every user-facing table; ownership checked again at the API layer
- Generated documents are published atomically — partial documents are never exposed
- No stack traces, internal paths, or API keys are ever returned to clients

## Known Limitations

_TBD (Phase 17)_

## Future Improvements

- Saved RAMS templates, duplicate existing RAMS, revision history (V2)
- Multi-user companies, team roles, approval workflow (V3)
- CPP support, mobile application, enterprise SSO (V4)
