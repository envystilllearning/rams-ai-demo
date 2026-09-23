"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CreditCard, FilePlus2, Settings } from "lucide-react";
import { apiFetch, type Profile } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";

interface Subscription {
  status: string;
  can_generate: boolean;
  price_label: string;
}

export default function DashboardPage() {
  const [name, setName] = useState<string>("there");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [sub, setSub] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const supabase = createClient();
        const {
          data: { user },
        } = await supabase.auth.getUser();

        const p = await apiFetch<Profile>("/api/profile");
        setProfile(p);
        const first =
          p.full_name?.split(" ")[0] ||
          user?.user_metadata?.full_name?.split(" ")[0] ||
          user?.email ||
          "there";
        setName(first);
        try {
          const s = await apiFetch<Subscription>("/api/subscription");
          setSub(s);
        } catch {
          // subscription endpoint may fail before billing phase is wired
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <LoadingState label="Loading dashboard..." />;
  if (error)
    return <ErrorState title="Failed to load dashboard" message={error} onRetry={() => window.location.reload()} />;

  const isActive = sub?.can_generate ?? false;

  return (
    <div>
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Welcome back, {name}</h1>
          <p className="mt-1 text-sm text-muted">
            Your dashboard is under construction — full features arriving in the
            next phase.
          </p>
        </div>
        <Link
          href="/dashboard/settings/company"
          className="inline-flex h-9 items-center gap-2 rounded-lg border border-border bg-surface px-3 text-sm transition-colors hover:bg-surface-muted"
        >
          <Settings className="h-4 w-4" aria-hidden />
          Company Profile
        </Link>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-3">
        <Card>
          <CardContent>
            <CardTitle>Subscription</CardTitle>
            <CardDescription>
              {sub ? `${sub.price_label} plan` : "Professional plan · £9.95/month"}
            </CardDescription>
            <div className="mt-3 flex items-center gap-3">
              <StatusBadge status={sub?.status && sub.status !== "none" ? sub.status : "canceled"} />
              <Link
                href="/dashboard/settings/billing"
                className="inline-flex items-center gap-1.5 text-sm font-medium text-foreground underline-offset-4 hover:underline"
              >
                <CreditCard className="h-3.5 w-3.5" aria-hidden />
                {isActive ? "Manage" : "Subscribe"}
              </Link>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <CardTitle>Company</CardTitle>
            <CardDescription>
              {profile?.company_name
                ? profile.company_name
                : "No company details yet"}
            </CardDescription>
            <Link
              href="/dashboard/settings/company"
              className="mt-3 inline-block text-sm font-medium text-foreground underline-offset-4 hover:underline"
            >
              {profile?.company_name ? "Edit profile" : "Add company details"}
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <CardTitle>RAMS</CardTitle>
            <CardDescription>Risk assessments & method statements.</CardDescription>
            <div className="mt-3 flex flex-wrap gap-2">
              <Link
                href="/dashboard/rams/new"
                className="inline-flex items-center gap-1.5 rounded-lg bg-accent px-3 py-1.5 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
              >
                <FilePlus2 className="h-3.5 w-3.5" aria-hidden />
                Create New RAMS
              </Link>
              <Link
                href="/dashboard/rams"
                className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm font-medium transition-colors hover:bg-surface-muted"
              >
                View all
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
