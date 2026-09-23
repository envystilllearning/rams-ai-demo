"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CreditCard, Download, FilePlus2, FileText, Settings } from "lucide-react";
import { apiFetch, type Profile } from "@/lib/api";
import { createClient } from "@/lib/supabase/client";
import { downloadStored, listRams, type Rams } from "@/lib/rams";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { useToast } from "@/components/ui/toast";

interface Subscription {
  status: string;
  can_generate: boolean;
  price_label: string;
}

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

interface Subscription {
  status: string;
  can_generate: boolean;
  price_label: string;
}

export default function DashboardPage() {
  const { toast } = useToast();
  const [name, setName] = useState<string>("there");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [sub, setSub] = useState<Subscription | null>(null);
  const [recent, setRecent] = useState<Rams[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

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
        const r = await listRams(5, 0);
        setRecent(r.items);
        setTotal(r.total);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function onDownload(r: Rams, kind: "docx" | "pdf") {
    setDownloading(`${r.id}-${kind}`);
    try {
      await downloadStored(r, kind);
    } catch (e) {
      toast({
        title: "Download failed",
        description: e instanceof Error ? e.message : "Please try again.",
        variant: "danger",
      });
    } finally {
      setDownloading(null);
    }
  }

  if (loading) return <LoadingState label="Loading dashboard..." />;
  if (error)
    return <ErrorState title="Failed to load dashboard" message={error} onRetry={() => window.location.reload()} />;

  const isActive = sub?.can_generate ?? false;

  return (
    <div>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Welcome back, {name}</h1>
          <p className="mt-1 text-sm text-muted">
            {total === 0
              ? "Create your first RAMS to get started."
              : `${total} RAMS document${total === 1 ? "" : "s"} in your library.`}
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            href="/dashboard/rams/new"
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
          >
            <FilePlus2 className="h-4 w-4" aria-hidden />
            Create New RAMS
          </Link>
          <Link
            href="/dashboard/settings/company"
            aria-label="Company profile settings"
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-surface transition-colors hover:bg-surface-muted"
          >
            <Settings className="h-4 w-4" aria-hidden />
          </Link>
        </div>
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
            <CardTitle>RAMS created</CardTitle>
            <CardDescription>Documents in your library</CardDescription>
            <p className="mt-3 text-3xl font-bold">{total}</p>
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
      </div>

      <div className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Recent RAMS</h2>
          {total > 5 && (
            <Link
              href="/dashboard/rams"
              className="text-sm font-medium text-foreground underline-offset-4 hover:underline"
            >
              View all →
            </Link>
          )}
        </div>

        {recent.length === 0 ? (
          <EmptyState
            icon={<FileText className="h-8 w-8" aria-hidden />}
            title="No RAMS yet"
            description="Create your first RAMS — it takes a couple of minutes."
            action={
              <Link
                href="/dashboard/rams/new"
                className="inline-flex h-10 items-center gap-2 rounded-lg bg-accent px-4 text-sm font-semibold text-accent-foreground shadow-sm transition-colors hover:bg-accent-hover"
              >
                <FilePlus2 className="h-4 w-4" aria-hidden />
                Create New RAMS
              </Link>
            }
          />
        ) : (
          <div className="overflow-hidden rounded-xl border border-border bg-surface">
            <ul className="divide-y divide-border">
              {recent.map((r) => (
                <li
                  key={r.id}
                  className="flex items-center justify-between gap-4 px-5 py-4 transition-colors hover:bg-surface-muted/50"
                >
                  <div className="min-w-0">
                    <Link
                      href={`/dashboard/rams/${r.id}`}
                      className="truncate font-medium text-foreground underline-offset-4 hover:underline"
                    >
                      {r.project_name}
                    </Link>
                    <p className="mt-0.5 text-xs text-muted">
                      {r.document_number ?? "—"} · {formatDate(r.created_at)}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-1">
                    <StatusBadge status={r.status} />
                    {r.status === "ready" && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          aria-label={`Download DOCX for ${r.project_name}`}
                          title="Download DOCX"
                          onClick={() => onDownload(r, "docx")}
                          loading={downloading === `${r.id}-docx`}
                        >
                          <Download className="h-4 w-4" aria-hidden />
                          <span className="hidden sm:inline">DOCX</span>
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          aria-label={`Download PDF for ${r.project_name}`}
                          title="Download PDF"
                          onClick={() => onDownload(r, "pdf")}
                          loading={downloading === `${r.id}-pdf`}
                        >
                          <Download className="h-4 w-4" aria-hidden />
                          <span className="hidden sm:inline">PDF</span>
                        </Button>
                      </>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
