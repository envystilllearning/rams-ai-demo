"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Settings } from "lucide-react";
import { apiFetch, type Profile } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";

export default function DashboardPage() {
  const [name, setName] = useState<string>("there");
  const [profile, setProfile] = useState<Profile | null>(null);
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

      <Card className="mt-8">
        <CardContent>
          <CardTitle>Session verified</CardTitle>
          <CardDescription>
            You are authenticated as {profile?.email || "a registered user"}.
            {profile?.company_name
              ? ` Company profile loaded: ${profile.company_name}.`
              : " No company details yet — add them in Company Profile."}
          </CardDescription>
        </CardContent>
      </Card>
    </div>
  );
}
