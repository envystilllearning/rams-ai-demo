"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Sparkles } from "lucide-react";
import { getRams, type Rams } from "@/lib/rams";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { Alert } from "@/components/ui/alert";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { useToast } from "@/components/ui/toast";

export default function RamsDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { toast } = useToast();
  const [rams, setRams] = useState<Rams | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRams(id)
      .then(setRams)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingState label="Loading RAMS..." />;
  if (error || !rams)
    return (
      <ErrorState
        title="RAMS not found"
        message={error ?? "This document may have been deleted."}
        onRetry={() => window.location.reload()}
      />
    );

  const entries = Object.entries(rams.input_data ?? {}).filter(
    ([, v]) => typeof v === "string" && v.trim()
  );

  return (
    <div className="mx-auto max-w-3xl">
      <Link
        href="/dashboard/rams"
        className="mb-6 inline-flex items-center gap-2 text-sm text-muted transition-colors hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" aria-hidden />
        Back to RAMS list
      </Link>

      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{rams.project_name}</h1>
          <p className="mt-1 text-sm text-muted">
            {rams.document_number ?? "—"}
            {rams.client_name ? ` · ${rams.client_name}` : ""}
          </p>
        </div>
        <StatusBadge status={rams.status} />
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Submitted information</CardTitle>
          <CardDescription>Exactly what was entered in the wizard.</CardDescription>
        </CardHeader>
        <CardContent>
          {entries.length === 0 ? (
            <p className="text-sm text-muted">No details recorded.</p>
          ) : (
            <dl className="space-y-3">
              {entries.map(([key, value]) => (
                <div key={key} className="grid gap-1 sm:grid-cols-3">
                  <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                    {key.replace(/_/g, " ")}
                  </dt>
                  <dd className="whitespace-pre-wrap text-sm sm:col-span-2">
                    {String(value)}
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>AI generation</CardTitle>
          <CardDescription>
            Structured content, DOCX and PDF are produced in the next phase.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {rams.status === "draft" ? (
            <Alert variant="info" title="Ready to generate">
              AI generation arrives in the next phase. For now the draft is
              safely stored.
            </Alert>
          ) : (
            <p className="text-sm text-muted">Status: {rams.status}</p>
          )}
          <Button
            variant="accent"
            size="lg"
            className="mt-4 w-full"
            disabled
            onClick={() =>
              toast({ title: "Coming in the AI phase", variant: "info" })
            }
          >
            <Sparkles className="h-5 w-5" aria-hidden />
            Generate RAMS (coming soon)
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
